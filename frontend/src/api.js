const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options)
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    throw new Error(data?.error || `Request failed: ${res.status}`)
  }
  return data
}

export function listCandidates() {
  return request('/candidates')
}

export function getCandidate(id) {
  return request(`/candidates/${id}`)
}

export function requestDocuments(id) {
  return request(`/candidates/${id}/request-documents`, { method: 'POST' })
}

export function submitDocument(id, docType, file) {
  const formData = new FormData()
  formData.append('doc_type', docType)
  formData.append('file', file)
  return request(`/candidates/${id}/submit-documents`, { method: 'POST', body: formData })
}

// fetch() can't report upload progress, so this one uses XMLHttpRequest directly.
export function uploadResume(file, onProgress) {
  return new Promise((resolve, reject) => {
    const formData = new FormData()
    formData.append('resume', file)

    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${BASE}/candidates/upload`)

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    }

    xhr.onload = () => {
      let data = null
      try {
        data = JSON.parse(xhr.responseText)
      } catch {
        // non-JSON response, data stays null
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(data)
      } else {
        reject(new Error(data?.error || `Upload failed: ${xhr.status}`))
      }
    }
    xhr.onerror = () => reject(new Error('Network error during upload'))

    xhr.send(formData)
  })
}

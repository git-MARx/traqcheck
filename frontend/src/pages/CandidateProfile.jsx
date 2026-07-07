import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getCandidate, requestDocuments, submitDocument } from '../api'
import StatusBadge from '../components/StatusBadge'

const FIELDS = ['name', 'email', 'phone', 'company', 'designation']

function ConfidenceScores({ scores }) {
  if (!scores) return null
  return (
    <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-500">
      {Object.entries(scores).map(([field, { confidence, method }]) => (
        <span key={field} className="px-2 py-1 bg-gray-100 rounded">
          {field}: {Math.round(confidence * 100)}% ({method})
        </span>
      ))}
    </div>
  )
}

export default function CandidateProfile() {
  const { id } = useParams()
  const [candidate, setCandidate] = useState(null)
  const [requesting, setRequesting] = useState(false)
  const [requestResult, setRequestResult] = useState(null)
  const [requestError, setRequestError] = useState(null)
  const [docType, setDocType] = useState('PAN')
  const [uploading, setUploading] = useState(false)

  function refresh() {
    getCandidate(id).then(setCandidate)
  }

  useEffect(refresh, [id])

  async function handleRequestDocuments() {
    setRequesting(true)
    setRequestError(null)
    try {
      const result = await requestDocuments(id)
      setRequestResult(result)
    } catch (err) {
      setRequestError(err.message)
    } finally {
      setRequesting(false)
    }
  }

  async function handleDocUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    try {
      await submitDocument(id, docType, file)
      refresh()
    } catch (err) {
      alert(err.message)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  if (!candidate) return <div className="max-w-2xl mx-auto p-6">Loading...</div>

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Link to="/candidates" className="text-sm text-blue-600 hover:underline">&larr; Back to candidates</Link>

      <div className="flex items-center justify-between mt-4">
        <h1 className="text-2xl font-semibold">{candidate.name || '(no name)'}</h1>
        <StatusBadge status={candidate.status} />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        {FIELDS.map((field) => (
          <div key={field}>
            <div className="text-gray-500 capitalize">{field}</div>
            <div>{candidate[field] || '—'}</div>
          </div>
        ))}
      </div>

      {candidate.skills?.length > 0 && (
        <div className="mt-3 text-sm">
          <div className="text-gray-500">Skills</div>
          <div>{candidate.skills.join(', ')}</div>
        </div>
      )}

      <ConfidenceScores scores={candidate.confidence_scores} />

      <div className="mt-8 border-t pt-6">
        <h2 className="text-lg font-medium mb-2">Document Request</h2>
        <button
          onClick={handleRequestDocuments}
          disabled={requesting}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {requesting ? 'Requesting...' : 'Request Documents'}
        </button>

        {requestError && <p className="mt-3 text-sm text-red-600">{requestError}</p>}

        {requestResult && (
          <div className="mt-4 p-4 bg-gray-50 rounded border text-sm">
            <p className="text-gray-500 mb-1">
              {requestResult.status === 'existing' ? 'Existing request:' : 'Generated message:'}
            </p>
            <p className="whitespace-pre-wrap">{requestResult.message_body}</p>
            <p className="mt-2">
              Upload link:{' '}
              <a href={requestResult.upload_link} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                {requestResult.upload_link}
              </a>
            </p>
            <p className="mt-1 text-gray-500">Expires: {new Date(requestResult.token_expiry).toLocaleString()}</p>
          </div>
        )}
      </div>

      <div className="mt-8 border-t pt-6">
        <h2 className="text-lg font-medium mb-2">Documents</h2>

        {candidate.documents.filter((d) => d.is_latest).length === 0 && (
          <p className="text-sm text-gray-400 mb-3">No documents submitted yet.</p>
        )}
        <ul className="text-sm mb-4">
          {candidate.documents.filter((d) => d.is_latest).map((d) => (
            <li key={d.id}>
              {d.doc_type} — uploaded {new Date(d.uploaded_at).toLocaleString()}{' '}
              <a href={d.file_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                View
              </a>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-2">
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="PAN">PAN</option>
            <option value="Aadhaar">Aadhaar</option>
          </select>
          <label className="px-3 py-1.5 bg-gray-100 rounded cursor-pointer text-sm hover:bg-gray-200">
            {uploading ? 'Uploading...' : 'Upload on behalf of candidate'}
            <input type="file" accept="image/*,.pdf" className="hidden" onChange={handleDocUpload} disabled={uploading} />
          </label>
        </div>
      </div>
    </div>
  )
}

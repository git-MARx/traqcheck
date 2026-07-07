import { useState } from 'react'
import { uploadResume } from '../api'

export default function ResumeDropzone({ onUploaded }) {
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState(null)

  async function handleFile(file) {
    setError(null)
    setProgress(0)
    try {
      const candidate = await uploadResume(file, setProgress)
      onUploaded(candidate)
    } catch (err) {
      setError(err.message)
    } finally {
      setProgress(null)
    }
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        const file = e.dataTransfer.files[0]
        if (file) handleFile(file)
      }}
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors
        ${dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
    >
      <p className="text-gray-600 mb-2">Drag and drop a resume (PDF or DOCX), or</p>
      <label className="inline-block px-4 py-2 bg-blue-600 text-white rounded cursor-pointer hover:bg-blue-700">
        Browse file
        <input
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files[0]
            if (file) handleFile(file)
            e.target.value = ''
          }}
        />
      </label>

      {progress !== null && (
        <div className="mt-4 w-full bg-gray-200 rounded h-2">
          <div className="bg-blue-600 h-2 rounded transition-all" style={{ width: `${progress}%` }} />
        </div>
      )}

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  )
}

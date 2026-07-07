import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listCandidates } from '../api'
import ResumeDropzone from '../components/ResumeDropzone'
import StatusBadge from '../components/StatusBadge'

export default function Dashboard() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)

  function refresh() {
    setLoading(true)
    listCandidates()
      .then(setCandidates)
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Candidates</h1>

      <ResumeDropzone onUploaded={refresh} />

      <table className="w-full mt-8 border-collapse">
        <thead>
          <tr className="text-left text-sm text-gray-500 border-b">
            <th className="py-2">Name</th>
            <th className="py-2">Email</th>
            <th className="py-2">Company</th>
            <th className="py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {loading && (
            <tr><td colSpan={4} className="py-4 text-center text-gray-400">Loading...</td></tr>
          )}
          {!loading && candidates.length === 0 && (
            <tr><td colSpan={4} className="py-4 text-center text-gray-400">No candidates yet</td></tr>
          )}
          {candidates.map((c) => (
            <tr key={c.id} className="border-b hover:bg-gray-50">
              <td className="py-2">
                <Link to={`/candidates/${c.id}`} className="text-blue-600 hover:underline">
                  {c.name || '(no name)'}
                </Link>
              </td>
              <td className="py-2">{c.email || '—'}</td>
              <td className="py-2">{c.company || '—'}</td>
              <td className="py-2"><StatusBadge status={c.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

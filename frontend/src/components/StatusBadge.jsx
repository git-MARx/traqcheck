const COLORS = {
  uploaded: 'bg-gray-100 text-gray-700',
  extracted: 'bg-blue-100 text-blue-700',
  extraction_failed: 'bg-red-100 text-red-700',
  docs_requested: 'bg-amber-100 text-amber-700',
  docs_submitted: 'bg-emerald-100 text-emerald-700',
  verified: 'bg-purple-100 text-purple-700',
}

export default function StatusBadge({ status }) {
  const color = COLORS[status] || 'bg-gray-100 text-gray-700'
  return (
    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${color}`}>
      {status.replaceAll('_', ' ')}
    </span>
  )
}

import { Navigate, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CandidateProfile from './pages/CandidateProfile'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/candidates" replace />} />
      <Route path="/candidates" element={<Dashboard />} />
      <Route path="/candidates/:id" element={<CandidateProfile />} />
    </Routes>
  )
}

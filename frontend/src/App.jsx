import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Landing from './pages/Landing'
import InstructorLogin from './pages/instructor/Login'
import InstructorDashboard from './pages/instructor/Dashboard'
import StudentLogin from './pages/student/Login'
import StudentDashboard from './pages/student/Dashboard'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/instructor/login" element={<InstructorLogin />} />
          <Route path="/instructor/dashboard" element={<InstructorDashboard />} />
          <Route path="/student/login" element={<StudentLogin />} />
          <Route path="/student/dashboard" element={<StudentDashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

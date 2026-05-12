import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

function load(key) {
  try { return JSON.parse(localStorage.getItem(key)) } catch { return null }
}

export function AuthProvider({ children }) {
  const [instructorCredentials, setInstructorCredentials] = useState(() => load('instructorCredentials'))
  const [studentCredentials, setStudentCredentials] = useState(() => load('studentCredentials'))

  const loginInstructor = (email, password) => {
    const creds = { email, password }
    localStorage.setItem('instructorCredentials', JSON.stringify(creds))
    setInstructorCredentials(creds)
  }

  const loginStudent = (email, password) => {
    const creds = { email, password }
    localStorage.setItem('studentCredentials', JSON.stringify(creds))
    setStudentCredentials(creds)
  }

  const logout = () => {
    localStorage.removeItem('instructorCredentials')
    localStorage.removeItem('studentCredentials')
    setInstructorCredentials(null)
    setStudentCredentials(null)
  }

  return (
    <AuthContext.Provider value={{
      instructorCredentials,
      studentCredentials,
      loginInstructor,
      loginStudent,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

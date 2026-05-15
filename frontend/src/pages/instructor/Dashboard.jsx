import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../../context/AuthContext'
import AnimatedShaderBackground from '../../components/ui/animated-shader-background'

const API = 'http://localhost:8000'

// ---------------------------------------------------------------------------
// Toast system
// ---------------------------------------------------------------------------

function useToasts() {
  const [toasts, setToasts] = useState([])
  const id = useRef(0)

  const push = useCallback((message, type = 'success') => {
    const key = ++id.current
    setToasts(prev => [...prev, { key, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.key !== key)), 4000)
  }, [])

  return { toasts, push }
}

function ToastContainer({ toasts }) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map(t => (
        <div
          key={t.key}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl text-sm font-medium pointer-events-auto animate-fade-in
            ${t.type === 'success'
              ? 'bg-gray-900 border border-green-500/30 text-green-400'
              : 'bg-gray-900 border border-red-500/30 text-red-400'}`}
        >
          {t.type === 'success' ? (
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          ) : (
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
          )}
          {t.message}
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Status badge
// ---------------------------------------------------------------------------

const STATUS_CONFIG = {
  NOT_STARTED: { label: 'Not Started', classes: 'bg-gray-700/60 text-gray-400 border-gray-600/40' },
  ACTIVE:      { label: 'Active',       classes: 'bg-green-500/15 text-green-400 border-green-500/30' },
  ENDED:       { label: 'Ended',        classes: 'bg-red-500/15 text-red-400 border-red-500/30' },
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.NOT_STARTED
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${cfg.classes}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${
        status === 'ACTIVE' ? 'bg-green-400' : status === 'ENDED' ? 'bg-red-400' : 'bg-gray-500'
      }`} />
      {cfg.label}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Spinner
// ---------------------------------------------------------------------------

function Spinner({ className = 'w-4 h-4' }) {
  return (
    <svg className={`${className} animate-spin`} fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}

// ---------------------------------------------------------------------------
// Modal shell
// ---------------------------------------------------------------------------

function Modal({ title, onClose, children, size = 'md' }) {
  useEffect(() => {
    const onKey = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const maxW = size === 'lg' ? 'max-w-3xl' : 'max-w-lg'

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative w-full ${maxW} bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl`}>
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-800">
          <h2 className="text-base font-semibold text-white">{title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Create Activity Modal
// ---------------------------------------------------------------------------

function CreateActivityModal({ courseId, credentials, onClose, onCreated, toast }) {
  const [text, setText] = useState('')
  const [objectives, setObjectives] = useState([''])
  const [activityNo, setActivityNo] = useState('')
  const [loading, setLoading] = useState(false)
  const [validationError, setValidationError] = useState('')

  const addObjective = () => setObjectives(prev => [...prev, ''])
  const updateObjective = (i, val) => setObjectives(prev => prev.map((o, idx) => idx === i ? val : o))
  const removeObjective = (i) => setObjectives(prev => prev.filter((_, idx) => idx !== i))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setValidationError('')

    const filtered = objectives.filter(o => o.trim())
    if (!text.trim()) {
      setValidationError('Activity text is required.')
      return
    }
    if (filtered.length === 0) {
      setValidationError('Add at least one learning objective.')
      return
    }

    setLoading(true)
    try {
      const res = await axios.post(`${API}/instructor/create-activity`, {
        email: credentials.email,
        password: credentials.password,
        course_id: courseId,
        activity_text: text.trim(),
        learning_objectives: filtered,
        ...(activityNo ? { activity_no_optional: parseInt(activityNo, 10) } : {}),
      })

      if (res.data?.ok === false) {
        toast(res.data?.message || 'Failed to create activity.', 'error')
        return
      }

      toast(res.data?.message || 'Activity created successfully.')
      onCreated()
      onClose()
    } catch (err) {
      const msg = err.response?.data?.message
        || err.response?.data?.detail
        || 'Failed to create activity.'
      toast(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal title="Create New Activity" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Activity Text</label>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            required
            rows={4}
            placeholder="Describe the activity or topic..."
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm resize-none"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-sm font-medium text-gray-400">Learning Objectives</label>
            <button
              type="button"
              onClick={addObjective}
              className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Add objective
            </button>
          </div>
          <div className="space-y-2">
            {objectives.map((obj, i) => (
              <div key={i} className="flex gap-2">
                <input
                  type="text"
                  value={obj}
                  onChange={e => updateObjective(i, e.target.value)}
                  placeholder={`Objective ${i + 1}`}
                  className="flex-1 px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm"
                />
                {objectives.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeObjective(i)}
                    className="px-2.5 text-gray-600 hover:text-red-400 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Activity Number <span className="text-gray-600">(optional)</span></label>
          <input
            type="number"
            value={activityNo}
            onChange={e => setActivityNo(e.target.value)}
            placeholder="Auto-assigned if blank"
            min={1}
            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm"
          />
        </div>

        {validationError && (
          <div className="flex items-center gap-2 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            {validationError}
          </div>
        )}

        <div className="flex gap-3 pt-1">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium rounded-xl transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors text-sm flex items-center justify-center gap-2"
          >
            {loading ? <><Spinner />Creating…</> : 'Create Activity'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Reset Student Password Modal
// ---------------------------------------------------------------------------

function ResetStudentPasswordModal({ credentials, courses, onClose, toast }) {
  const [studentEmail, setStudentEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [courseId, setCourseId] = useState(courses[0]?.id ?? '')
  const [loading, setLoading] = useState(false)
  const [showPw, setShowPw] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await axios.post(`${API}/instructor/reset-student-password`, {
        email: credentials.email,
        password: credentials.password,
        course_id: courseId,
        student_email: studentEmail.trim(),
        new_password: newPassword,
      })
      toast('Student password reset successfully.')
      onClose()
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to reset password.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal title="Reset Student Password" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Course</label>
          <select
            value={courseId}
            onChange={e => setCourseId(e.target.value)}
            required
            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm appearance-none"
          >
            <option value="" disabled>Select a course</option>
            {courses.map(c => (
              <option key={c.id} value={c.id}>{c.name ?? c.id}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Student Email</label>
          <input
            type="email"
            value={studentEmail}
            onChange={e => setStudentEmail(e.target.value)}
            required
            placeholder="student@university.edu"
            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">New Password</label>
          <div className="relative">
            <input
              type={showPw ? 'text' : 'password'}
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm pr-11"
            />
            <button
              type="button"
              onClick={() => setShowPw(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                {showPw
                  ? <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                  : <><path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></>
                }
              </svg>
            </button>
          </div>
        </div>

        <div className="flex gap-3 pt-1">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium rounded-xl transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors text-sm flex items-center justify-center gap-2"
          >
            {loading ? <><Spinner />Resetting…</> : 'Reset Password'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Manual Grade Modal
// ---------------------------------------------------------------------------

function ManualGradeModal({ activity, courseId, credentials, onClose, toast }) {
  const [studentEmail, setStudentEmail] = useState('')
  const [score, setScore] = useState(1)
  const [meta, setMeta] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await axios.post(`${API}/instructor/manual-grade`, {
        email: credentials.email,
        password: credentials.password,
        course_id: courseId,
        activity_no: activity.activity_no,
        student_email: studentEmail.trim(),
        score: Number(score),
        meta: meta.trim() || null,
      })
      if (res.data?.ok === false) {
        toast(res.data.error || res.data.message || 'Failed to submit grade.', 'error')
        return
      }
      toast('Grade submitted successfully.')
      onClose()
    } catch (err) {
      toast(err.response?.data?.error || err.response?.data?.detail || 'Failed to submit grade.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal title={`Manual Grade — Activity #${activity.activity_no}`} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Student Email</label>
          <input
            type="email"
            value={studentEmail}
            onChange={e => setStudentEmail(e.target.value)}
            required
            placeholder="student@university.edu"
            className="w-full px-3 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm transition-colors"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Score</label>
          <input
            type="number"
            value={score}
            onChange={e => setScore(e.target.value)}
            min={0}
            step={0.1}
            required
            className="w-full px-3 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm transition-colors"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Note <span className="text-gray-600">(optional)</span></label>
          <input
            type="text"
            value={meta}
            onChange={e => setMeta(e.target.value)}
            placeholder="Reason for manual grade"
            className="w-full px-3 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm transition-colors"
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors">
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2 text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-colors"
          >
            {loading ? 'Submitting…' : 'Submit Grade'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Scores Modal
// ---------------------------------------------------------------------------

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean)
  if (lines.length === 0) return { headers: [], rows: [] }
  const parse = line => {
    const result = []
    let cur = ''
    let inQuote = false
    for (let i = 0; i < line.length; i++) {
      const ch = line[i]
      if (ch === '"') { inQuote = !inQuote }
      else if (ch === ',' && !inQuote) { result.push(cur.trim()); cur = '' }
      else { cur += ch }
    }
    result.push(cur.trim())
    return result
  }
  const headers = parse(lines[0])
  const rows = lines.slice(1).map(parse)
  return { headers, rows }
}

function ScoresModal({ activity, courseId, credentials, onClose, toast }) {
  const [loading, setLoading] = useState(true)
  const [parsed, setParsed] = useState({ headers: [], rows: [] })
  const [csvBlob, setCsvBlob] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const res = await axios.post(
          `${API}/instructor/export-scores`,
          { email: credentials.email, password: credentials.password, course_id: courseId, activity_no: activity.activity_no }
        )
        if (cancelled) return
        const csvText = res.data?.csv ?? ''
        if (csvText) {
          const blob = new Blob([csvText], { type: 'text/csv' })
          setCsvBlob(blob)
        }
        setParsed(parseCSV(csvText))
      } catch (err) {
        if (!cancelled) toast('Failed to load scores.', 'error')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [activity.activity_no, courseId, credentials, toast])

  const downloadCSV = () => {
    if (!csvBlob) return
    const url = URL.createObjectURL(csvBlob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scores_${courseId}_activity${activity.activity_no}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Normalise headers for display
  const HEADER_LABELS = {
    student_email: 'Student Email', email: 'Student Email',
    score: 'Score',
    meta: 'Meta',
    created_at: 'Date', date: 'Date', timestamp: 'Date',
  }
  const displayHeader = h => HEADER_LABELS[h.toLowerCase()] ?? h

  return (
    <Modal title={`Activity Scores — Activity #${activity.activity_no}`} onClose={onClose} size="lg">
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Spinner className="w-6 h-6 text-indigo-400" />
        </div>
      ) : parsed.rows.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-sm text-gray-500">No scores recorded yet.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-800/60">
                {parsed.headers.map((h, i) => (
                  <th key={i} className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider whitespace-nowrap">
                    {displayHeader(h)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {parsed.rows.map((row, ri) => (
                <tr key={ri} className="hover:bg-gray-800/30 transition-colors">
                  {row.map((cell, ci) => (
                    <td key={ci} className="px-4 py-3 text-gray-300 whitespace-nowrap">
                      {cell || <span className="text-gray-600">—</span>}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between mt-5 pt-4 border-t border-gray-800">
        <span className="text-xs text-gray-600">
          {parsed.rows.length} score record{parsed.rows.length !== 1 ? 's' : ''}
        </span>
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium rounded-xl transition-colors"
          >
            Close
          </button>
          <button
            onClick={downloadCSV}
            disabled={!csvBlob}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            Download CSV
          </button>
        </div>
      </div>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Edit Activity Modal
// ---------------------------------------------------------------------------

function EditActivityModal({ activity, courseId, credentials, onClose, onUpdated, toast }) {
  const [text, setText] = useState(activity.activity_text ?? '')
  const [objectives, setObjectives] = useState(
    activity.learning_objectives?.length > 0 ? [...activity.learning_objectives] : ['']
  )
  const [loading, setLoading] = useState(false)
  const [validationError, setValidationError] = useState('')

  const addObjective = () => setObjectives(prev => [...prev, ''])
  const updateObjective = (i, val) => setObjectives(prev => prev.map((o, idx) => idx === i ? val : o))
  const removeObjective = (i) => setObjectives(prev => prev.filter((_, idx) => idx !== i))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setValidationError('')
    const filtered = objectives.filter(o => o.trim())
    if (!text.trim()) { setValidationError('Activity text is required.'); return }
    if (filtered.length === 0) { setValidationError('Add at least one learning objective.'); return }

    setLoading(true)
    try {
      const res = await axios.post(`${API}/instructor/update-activity`, {
        email: credentials.email,
        password: credentials.password,
        course_id: courseId,
        activity_no: activity.activity_no,
        patch: { activity_text: text.trim(), learning_objectives: filtered },
      })
      if (res.data?.ok === false) {
        toast(res.data?.message || 'Failed to update activity.', 'error')
        return
      }
      toast(res.data?.message || 'Activity updated successfully.')
      onUpdated()
      onClose()
    } catch (err) {
      toast(err.response?.data?.message || err.response?.data?.detail || 'Failed to update activity.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal title={`Edit Activity #${activity.activity_no}`} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Activity Text</label>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            rows={4}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm resize-none"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-sm font-medium text-gray-400">Learning Objectives</label>
            <button
              type="button"
              onClick={addObjective}
              className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Add objective
            </button>
          </div>
          <div className="space-y-2">
            {objectives.map((obj, i) => (
              <div key={i} className="flex gap-2">
                <input
                  type="text"
                  value={obj}
                  onChange={e => updateObjective(i, e.target.value)}
                  placeholder={`Objective ${i + 1}`}
                  className="flex-1 px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors text-sm"
                />
                {objectives.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeObjective(i)}
                    className="px-2.5 text-gray-600 hover:text-red-400 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {validationError && (
          <div className="flex items-center gap-2 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            {validationError}
          </div>
        )}

        <div className="flex gap-3 pt-1">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium rounded-xl transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors text-sm flex items-center justify-center gap-2"
          >
            {loading ? <><Spinner />Saving…</> : 'Save Changes'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Activity Card
// ---------------------------------------------------------------------------

function ActivityCard({ activity, courseId, credentials, onRefresh, toast }) {
  const [loading, setLoading] = useState(null)
  const [showScores, setShowScores] = useState(false)
  const [showEdit, setShowEdit] = useState(false)
  const [showManualGrade, setShowManualGrade] = useState(false)

  const act = async (endpoint, label) => {
    setLoading(label)
    try {
      await axios.post(`${API}/instructor/${endpoint}`, {
        email: credentials.email,
        password: credentials.password,
        course_id: courseId,
        activity_no: activity.activity_no,
      })
      toast(`Activity ${label.toLowerCase()}d.`)
      onRefresh()
    } catch (err) {
      toast(err.response?.data?.detail || `Failed to ${label.toLowerCase()}.`, 'error')
    } finally {
      setLoading(null)
    }
  }

  const status = activity.status ?? 'NOT_STARTED'
  const canEdit = status !== 'ACTIVE'

  const restart = async () => {
    setLoading('Restart')
    try {
      const base = { email: credentials.email, password: credentials.password, course_id: courseId, activity_no: activity.activity_no }
      await axios.post(`${API}/instructor/reset-activity`, base)
      await axios.post(`${API}/instructor/start-activity`, base)
      toast('Activity restarted.')
      onRefresh()
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to restart activity.', 'error')
    } finally {
      setLoading(null)
    }
  }

  return (
    <>
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1.5">
            <span className="text-xs font-mono text-gray-600 bg-gray-800 px-2 py-0.5 rounded-md">
              #{activity.activity_no}
            </span>
            <StatusBadge status={status} />
          </div>
          <p className="text-sm text-gray-300 leading-relaxed line-clamp-2">
            {activity.activity_text ?? 'No description provided.'}
          </p>
          {activity.learning_objectives?.length > 0 && (
            <p className="text-xs text-gray-600 mt-1.5">
              {activity.learning_objectives.length} objective{activity.learning_objectives.length !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        <div className="flex flex-wrap gap-2 flex-shrink-0">
          {/* Edit button — always visible, disabled unless NOT_STARTED */}
          <button
            onClick={() => canEdit && setShowEdit(true)}
            disabled={!canEdit}
            title={canEdit ? 'Edit activity' : 'Cannot edit a running activity'}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg border text-xs font-semibold transition-all
              ${canEdit
                ? 'bg-gray-700/40 hover:bg-gray-700/70 text-gray-400 border-gray-600/40 hover:border-gray-500/60 hover:text-gray-200'
                : 'bg-gray-800/30 text-gray-700 border-gray-700/30 cursor-not-allowed'
              }`}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125" />
            </svg>
            Edit
          </button>

          {status === 'NOT_STARTED' && (
            <ActionButton
              label="Start"
              loading={loading === 'Start'}
              onClick={() => act('start-activity', 'Start')}
              color="green"
            />
          )}
          {status === 'ACTIVE' && (
            <ActionButton
              label="End"
              loading={loading === 'End'}
              onClick={() => act('end-activity', 'End')}
              color="red"
            />
          )}
          {status === 'ENDED' && (
            <>
              <ActionButton
                label="Scores"
                loading={false}
                onClick={() => setShowScores(true)}
                color="indigo"
                icon={
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
                  </svg>
                }
              />
              <ActionButton
                label="Manual Grade"
                loading={false}
                onClick={() => setShowManualGrade(true)}
                color="gray"
                icon={
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                  </svg>
                }
              />
              <ActionButton
                label="Restart"
                loading={loading === 'Restart'}
                onClick={restart}
                color="amber"
                icon={
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                  </svg>
                }
              />
              <ActionButton
                label="Reset"
                loading={loading === 'Reset'}
                onClick={() => act('reset-activity', 'Reset')}
                color="gray"
              />
            </>
          )}
        </div>
      </div>

      {showScores && (
        <ScoresModal
          activity={activity}
          courseId={courseId}
          credentials={credentials}
          onClose={() => setShowScores(false)}
          toast={toast}
        />
      )}

      {showManualGrade && (
        <ManualGradeModal
          activity={activity}
          courseId={courseId}
          credentials={credentials}
          onClose={() => setShowManualGrade(false)}
          toast={toast}
        />
      )}

      {showEdit && (
        <EditActivityModal
          activity={activity}
          courseId={courseId}
          credentials={credentials}
          onClose={() => setShowEdit(false)}
          onUpdated={onRefresh}
          toast={toast}
        />
      )}
    </>
  )
}

function ActionButton({ label, loading, onClick, color, icon }) {
  const colors = {
    green:  'bg-green-600/20 hover:bg-green-600/30 text-green-400 border-green-500/30 hover:border-green-500/50',
    red:    'bg-red-600/20 hover:bg-red-600/30 text-red-400 border-red-500/30 hover:border-red-500/50',
    indigo: 'bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 border-indigo-500/30 hover:border-indigo-500/50',
    amber:  'bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 border-amber-500/30 hover:border-amber-500/50',
    gray:   'bg-gray-700/40 hover:bg-gray-700/70 text-gray-400 border-gray-600/40 hover:border-gray-500/60',
  }
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg border text-xs font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed ${colors[color]}`}
    >
      {loading ? <Spinner className="w-3.5 h-3.5" /> : icon}
      {label}
    </button>
  )
}

// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------

export default function InstructorDashboard() {
  const navigate = useNavigate()
  const { instructorCredentials, logout } = useAuth()
  const { toasts, push: toast } = useToasts()

  const [courses, setCourses] = useState([])
  const [loadingCourses, setLoadingCourses] = useState(true)

  const [selectedCourse, setSelectedCourse] = useState(null)
  const [activities, setActivities] = useState([])
  const [loadingActivities, setLoadingActivities] = useState(false)

  const [showCreate, setShowCreate] = useState(false)
  const [showResetPw, setShowResetPw] = useState(false)
  const [showManualGrade, setShowManualGrade] = useState(null) // activity object

  // Auth guard
  useEffect(() => {
    if (!instructorCredentials) navigate('/instructor/login', { replace: true })
  }, [instructorCredentials, navigate])

  // Fetch courses
  const fetchCourses = useCallback(async () => {
    if (!instructorCredentials) return
    setLoadingCourses(true)
    try {
      const res = await axios.post(`${API}/instructor/list-courses`, {
        email: instructorCredentials.email,
        password: instructorCredentials.password,
      })
      console.log('list-courses response:', res.data)
      const data = res.data
      if (Array.isArray(data)) {
        setCourses(data)
      } else if (Array.isArray(data?.courses)) {
        setCourses(data.courses)
      } else if (Array.isArray(data?.data)) {
        setCourses(data.data)
      } else {
        console.warn('Unexpected list-courses shape:', data)
        setCourses([])
      }
    } catch (err) {
      console.error('list-courses error:', err.response ?? err)
      toast(err.response?.data?.detail || err.response?.data?.message || 'Failed to load courses.', 'error')
    } finally {
      setLoadingCourses(false)
    }
  }, [instructorCredentials, toast])

  useEffect(() => { fetchCourses() }, [fetchCourses])

  // Fetch activities for selected course
  const fetchActivities = useCallback(async (courseId) => {
    if (!instructorCredentials || !courseId) return
    setLoadingActivities(true)
    try {
      const res = await axios.post(`${API}/instructor/list-activities`, {
        email: instructorCredentials.email,
        password: instructorCredentials.password,
        course_id: courseId,
      })
      setActivities(Array.isArray(res.data) ? res.data : res.data.activities ?? [])
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to load activities.', 'error')
    } finally {
      setLoadingActivities(false)
    }
  }, [instructorCredentials, toast])

  const selectCourse = (course) => {
    setSelectedCourse(course)
    fetchActivities(course.id)
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  if (!instructorCredentials) return null

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Animated shader background */}
      <div className="fixed inset-0 z-0">
        <AnimatedShaderBackground />
      </div>
      {/* Dark overlay so UI remains readable */}
      <div className="fixed inset-0 z-0 bg-black/55 pointer-events-none" />

      {/* Header */}
      <header className="sticky top-0 z-30 bg-black/40 backdrop-blur-md border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
              <svg className="w-4.5 h-4.5 text-white" style={{width:'1.1rem',height:'1.1rem'}} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
            </div>
            <span className="font-semibold text-white">Socratic AI</span>
            <span className="hidden sm:inline text-gray-700">·</span>
            <span className="hidden sm:inline text-xs text-gray-500">Instructor</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowResetPw(true)}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-400 hover:text-gray-200 bg-gray-800/60 hover:bg-gray-800 border border-gray-700/50 rounded-lg transition-all"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
              </svg>
              Reset Student Password
            </button>

            <span className="text-sm text-gray-500 hidden md:block truncate max-w-48">
              {instructorCredentials.email}
            </span>

            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-400 hover:text-red-400 bg-gray-800/60 hover:bg-red-500/10 border border-gray-700/50 hover:border-red-500/30 rounded-lg transition-all"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
              </svg>
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex flex-col lg:flex-row gap-8">

          {/* Courses panel */}
          <aside className="lg:w-72 flex-shrink-0">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">My Courses</h2>
              {!loadingCourses && (
                <span className="text-xs text-gray-600">{courses.length} course{courses.length !== 1 ? 's' : ''}</span>
              )}
            </div>

            {loadingCourses ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-16 bg-gray-800/50 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : courses.length === 0 ? (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center">
                <p className="text-sm text-gray-600">No courses found.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {courses.map(course => (
                  <button
                    key={course.id}
                    onClick={() => selectCourse(course)}
                    className={`w-full text-left px-4 py-3.5 rounded-xl border transition-all ${
                      selectedCourse?.id === course.id
                        ? 'bg-indigo-600/20 border-indigo-500/40 text-white'
                        : 'bg-gray-900 border-gray-800 text-gray-300 hover:border-gray-700 hover:text-white'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        selectedCourse?.id === course.id ? 'bg-indigo-400' : 'bg-gray-700'
                      }`} />
                      <div className="min-w-0">
                        <p className="text-sm font-medium truncate">
                          {course.name ?? course.id}
                        </p>
                        <p className="text-xs text-gray-600 truncate font-mono">{course.id}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Mobile reset pw button */}
            <button
              onClick={() => setShowResetPw(true)}
              className="sm:hidden mt-4 w-full flex items-center justify-center gap-1.5 px-3 py-2.5 text-sm text-gray-400 bg-gray-800/60 border border-gray-700/50 rounded-xl transition-all hover:text-gray-200 hover:bg-gray-800"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
              </svg>
              Reset Student Password
            </button>
          </aside>

          {/* Activities panel */}
          <section className="flex-1 min-w-0">
            {/* Panel header — always visible */}
            <div className="flex items-center justify-between mb-5">
              <div>
                {selectedCourse ? (
                  <>
                    <h2 className="text-lg font-semibold text-white">
                      {selectedCourse.name ?? selectedCourse.id}
                    </h2>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">{selectedCourse.id}</p>
                  </>
                ) : (
                  <h2 className="text-lg font-semibold text-gray-600">Activities</h2>
                )}
              </div>
              <button
                onClick={() => selectedCourse && setShowCreate(true)}
                disabled={!selectedCourse}
                title={!selectedCourse ? 'Select a course first' : 'Create new activity'}
                className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-xl transition-all
                  ${selectedCourse
                    ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 hover:shadow-indigo-500/30'
                    : 'bg-gray-800 text-gray-600 cursor-not-allowed border border-gray-700/50'
                  }`}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                New Activity
              </button>
            </div>

            {/* Panel body */}
            {!selectedCourse ? (
              <div className="flex items-center justify-center py-24">
                <div className="text-center">
                  <div className="w-14 h-14 rounded-2xl bg-gray-800 border border-gray-700 flex items-center justify-center mx-auto mb-4">
                    <svg className="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
                    </svg>
                  </div>
                  <p className="text-sm text-gray-500">Select a course to view activities</p>
                </div>
              </div>
            ) : loadingActivities ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-24 bg-gray-800/50 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : activities.length === 0 ? (
              <div className="bg-gray-900 border border-gray-800 border-dashed rounded-xl p-12 text-center">
                <p className="text-sm text-gray-600 mb-3">No activities yet.</p>
                <button
                  onClick={() => setShowCreate(true)}
                  className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  Create the first activity →
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {activities
                  .slice()
                  .sort((a, b) => a.activity_no - b.activity_no)
                  .map(activity => (
                    <ActivityCard
                      key={activity.activity_no}
                      activity={activity}
                      courseId={selectedCourse.id}
                      credentials={instructorCredentials}
                      onRefresh={() => fetchActivities(selectedCourse.id)}
                      toast={toast}
                    />
                  ))}
              </div>
            )}
          </section>
        </div>
      </main>

      {/* Modals */}
      {showCreate && (
        <CreateActivityModal
          courseId={selectedCourse.id}
          credentials={instructorCredentials}
          onClose={() => setShowCreate(false)}
          onCreated={() => fetchActivities(selectedCourse.id)}
          toast={toast}
        />
      )}

      {showResetPw && (
        <ResetStudentPasswordModal
          credentials={instructorCredentials}
          courses={courses}
          onClose={() => setShowResetPw(false)}
          toast={toast}
        />
      )}

      <ToastContainer toasts={toasts} />
    </div>
  )
}

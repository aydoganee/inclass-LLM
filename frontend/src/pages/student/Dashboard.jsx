import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ArrowUp } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const API = 'http://localhost:8000'
const LS_KEY = 'student_activities'

// ---------------------------------------------------------------------------
// Toasts
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
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map(t => (
        <div
          key={t.key}
          className={`flex items-center gap-2.5 px-4 py-3 rounded-xl border shadow-xl text-sm font-medium animate-fade-in
            ${t.type === 'success'
              ? 'bg-gray-900 border-green-500/30 text-green-400'
              : 'bg-gray-900 border-red-500/30 text-red-400'}`}
        >
          {t.type === 'success' ? (
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          ) : (
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          )}
          {t.message}
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Modal shell
// ---------------------------------------------------------------------------

function Modal({ title, onClose, children }) {
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <div className="relative w-full max-w-md bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl">
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-gray-800">
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
// Add Activity Modal
// ---------------------------------------------------------------------------

function AddActivityModal({ credentials, onClose, onAdded, push }) {
  const [courseId, setCourseId] = useState('')
  const [activityNo, setActivityNo] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async e => {
    e.preventDefault()
    if (!courseId.trim() || !activityNo) return
    setLoading(true)
    try {
      const res = await axios.post(`${API}/student/get-activity`, {
        email: credentials.email,
        password: credentials.password,
        course_id: courseId.trim(),
        activity_no: Number(activityNo),
      })
      if (res.data?.ok === false) {
        push(res.data.message || 'Activity not found.', 'error')
        return
      }
      onAdded({ course_id: courseId.trim(), activity_no: Number(activityNo) })
      onClose()
    } catch {
      push('Could not find that activity.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal title="Add Activity" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Course ID</label>
          <input
            type="text"
            value={courseId}
            onChange={e => setCourseId(e.target.value)}
            required
            placeholder="e.g. CS101"
            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Activity No</label>
          <input
            type="number"
            min="1"
            value={activityNo}
            onChange={e => setActivityNo(e.target.value)}
            required
            placeholder="1"
            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors text-sm"
          />
        </div>
        <div className="flex justify-end gap-3 pt-1">
          <button type="button" onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-xl transition-colors">
            Cancel
          </button>
          <button type="submit" disabled={loading}
            className="px-4 py-2 text-sm font-medium bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-colors">
            {loading ? 'Checking…' : 'Add'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Status Badge
// ---------------------------------------------------------------------------

function StatusDot({ status }) {
  const map = {
    ACTIVE: 'bg-green-400',
    NOT_STARTED: 'bg-gray-500',
    ENDED: 'bg-red-400',
  }
  return <span className={`w-2 h-2 rounded-full flex-shrink-0 ${map[status] ?? 'bg-gray-600'}`} />
}

// ---------------------------------------------------------------------------
// Markdown-ish bold renderer
// ---------------------------------------------------------------------------

function RichText({ text }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  return (
    <span>
      {parts.map((p, i) =>
        p.startsWith('**') && p.endsWith('**')
          ? <strong key={i} className="font-semibold">{p.slice(2, -2)}</strong>
          : <span key={i}>{p}</span>
      )}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------

export default function StudentDashboard() {
  const navigate = useNavigate()
  const { studentCredentials, logout } = useAuth()

  const [activities, setActivities] = useState(() => {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '[]') }
    catch { return [] }
  })
  const [statuses, setStatuses] = useState({})
  const [showAddModal, setShowAddModal] = useState(false)

  // active chat session
  const [activeActivity, setActiveActivity] = useState(null)
  const [messages, setMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [inputFocused, setInputFocused] = useState(false)
  const [chatLoading, setChatLoading] = useState(false)
  const [score, setScore] = useState(null)
  const [completed, setCompleted] = useState(false)

  const { toasts, push } = useToasts()
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Redirect if not logged in
  useEffect(() => {
    if (!studentCredentials) navigate('/student/login', { replace: true })
  }, [studentCredentials, navigate])

  // Persist activities to localStorage
  useEffect(() => {
    localStorage.setItem(LS_KEY, JSON.stringify(activities))
  }, [activities])

  // Parse status from a get-activity response
  const parseStatus = (data) => {
    if (data?.ok === true) {
      return data.data?.status ?? data.status ?? 'ACTIVE'
    }
    const msg = ((data?.message ?? data?.detail) ?? '').toLowerCase()
    if (msg.includes('not started') || msg.includes('not_started')) return 'NOT_STARTED'
    if (msg.includes('ended')) return 'ENDED'
    return 'UNKNOWN'
  }

  // Fetch statuses for all saved activities
  const fetchStatuses = useCallback(async () => {
    if (!studentCredentials) return
    const results = {}
    await Promise.all(
      activities.map(async a => {
        const key = `${a.course_id}:${a.activity_no}`
        try {
          const res = await axios.post(`${API}/student/get-activity`, {
            email: studentCredentials.email,
            password: studentCredentials.password,
            course_id: a.course_id,
            activity_no: a.activity_no,
          })
          console.log(`[get-activity] ${key}:`, res.data)
          results[key] = parseStatus(res.data)
        } catch (err) {
          console.log(`[get-activity error] ${key}:`, err.response?.data ?? err.message)
          results[key] = 'UNKNOWN'
        }
      })
    )
    setStatuses(prev => ({ ...prev, ...results }))
  }, [activities, studentCredentials])

  useEffect(() => { fetchStatuses() }, [fetchStatuses])

  // Scroll chat to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const activityKey = a => `${a.course_id}:${a.activity_no}`

  const handleAddActivity = newItem => {
    if (activities.some(a => activityKey(a) === activityKey(newItem))) {
      push('Activity already added.', 'error')
      return
    }
    setActivities(prev => [...prev, newItem])
    push('Activity added.', 'success')
  }

  const handleRemoveActivity = item => {
    const key = activityKey(item)
    setActivities(prev => prev.filter(a => activityKey(a) !== key))
    if (activeActivity && activityKey(activeActivity) === key) {
      setActiveActivity(null)
      setMessages([])
      setScore(null)
      setCompleted(false)
    }
  }

  const handleSelectActivity = async item => {
    const key = activityKey(item)
    // Re-fetch status on click so we always have fresh data
    let status
    try {
      const res = await axios.post(`${API}/student/get-activity`, {
        email: studentCredentials.email,
        password: studentCredentials.password,
        course_id: item.course_id,
        activity_no: item.activity_no,
      })
      console.log(`[click status] ${key}:`, res.data)
      status = parseStatus(res.data)
      setStatuses(prev => ({ ...prev, [key]: status }))
    } catch {
      status = statuses[key] ?? 'UNKNOWN'
    }
    if (status !== 'ACTIVE') return
    if (activeActivity && activityKey(activeActivity) === key) return
    setActiveActivity(item)
    setMessages([])
    setChatInput('')
    setScore(null)
    setCompleted(false)
  }

  const handleSend = async (message = chatInput) => {
    if (!message.trim() || chatLoading || !activeActivity) return
    setChatInput('')
    setMessages(prev => [...prev, { role: 'user', content: message }])
    setChatLoading(true)
    try {
      const res = await axios.post(`${API}/student/chat`, {
        email: studentCredentials.email,
        password: studentCredentials.password,
        course_id: activeActivity.course_id,
        activity_no: activeActivity.activity_no,
        message,
      })
      console.log('[chat response]', res.data)
      const data = res.data
      if (data?.ok === false) {
        push(data.message || 'Chat error.', 'error')
        return
      }
      const reply = data?.response ?? data?.data?.response ?? data?.data?.reply ?? data?.reply ?? ''
      const newScore = data?.score ?? data?.data?.score ?? null
      const isDone = data?.completed ?? data?.data?.completed ?? false
      setMessages(prev => [...prev, { role: 'assistant', content: reply }])
      if (newScore !== null) setScore(newScore)
      if (isDone) setCompleted(true)
    } catch {
      push('Failed to send message.', 'error')
    } finally {
      setChatLoading(false)
    }
  }

  const handleSignOut = () => {
    logout()
    navigate('/', { replace: true })
  }


  if (!studentCredentials) return null

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">

      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="sticky top-0 z-30 bg-gray-950/90 backdrop-blur-md">
        <div className="h-14 px-5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-violet-600/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-white tracking-tight">Socratic AI · Student</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-500 hidden sm:block">{studentCredentials.email}</span>
            <button
              onClick={handleSignOut}
              className="text-xs text-gray-400 hover:text-white transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* ── Body ───────────────────────────────────────────────── */}
      <div className="flex flex-1">

        {/* ── Sidebar ──────────────────────────────────────────── */}
        <aside className="fixed left-0 top-14 bottom-0 w-[260px] z-20 bg-gray-900/50 flex flex-col">
          <div className="px-4 pt-5 pb-3 flex items-center justify-between">
            <h2 className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Activities</h2>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-1 text-xs font-medium text-violet-400 hover:text-violet-300 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Add
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-2 py-1">
            {activities.length === 0 ? (
              <div className="px-3 py-10 text-center">
                <p className="text-xs text-gray-600">No activities yet.</p>
                <p className="text-xs text-gray-700 mt-1">Click Add to join one.</p>
              </div>
            ) : (
              activities.map(item => {
                const key = activityKey(item)
                const status = statuses[key] ?? 'UNKNOWN'
                const isActive = status === 'ACTIVE'
                const isSelected = activeActivity && activityKey(activeActivity) === key
                const tooltip = status === 'NOT_STARTED' ? 'Activity not started yet'
                  : status === 'ENDED' ? 'Activity has ended' : undefined

                return (
                  <div
                    key={key}
                    title={tooltip}
                    onClick={() => handleSelectActivity(item)}
                    className={`group relative flex items-center gap-3 px-3 py-2.5 my-0.5 rounded-xl transition-all
                      ${isActive ? 'cursor-pointer' : 'cursor-default opacity-50'}
                      ${isSelected ? 'bg-gray-800/80' : isActive ? 'hover:bg-gray-800/40' : ''}`}
                  >
                    {/* left accent bar on selected */}
                    {isSelected && (
                      <span className="absolute left-0 top-2 bottom-2 w-0.5 bg-indigo-500 rounded-full" />
                    )}
                    <StatusDot status={status} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-white truncate leading-tight">{item.course_id}</p>
                      <p className="text-xs text-gray-500 mt-0.5">Activity #{item.activity_no}</p>
                    </div>
                    <button
                      onClick={e => { e.stopPropagation(); handleRemoveActivity(item) }}
                      className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition-all flex-shrink-0 p-0.5"
                      title="Remove"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                )
              })
            )}
          </div>
        </aside>

        {/* ── Chat panel ───────────────────────────────────────── */}
        <main className="ml-[260px] flex-1 flex flex-col h-[calc(100vh-3.5rem)] overflow-hidden">

          {!activeActivity ? (
            /* Empty state */
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-14 h-14 rounded-2xl bg-gray-800/60 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
                  </svg>
                </div>
                <p className="text-sm text-gray-500">Select an active activity to start chatting</p>
              </div>
            </div>
          ) : (
            <>
              {/* Activity strip */}
              <div className="px-6 py-2.5 flex items-center justify-between">
                <p className="text-xs text-gray-500 font-medium">
                  {activeActivity.course_id} · Activity #{activeActivity.activity_no}
                </p>
                {score !== null && (
                  <span className="text-xs font-semibold text-violet-400">
                    Score: {score}
                  </span>
                )}
              </div>

              {/* Completion banner */}
              {completed && (
                <div className="mx-6 mb-2 flex items-center gap-3 px-5 py-3.5 bg-green-500/8 rounded-2xl text-green-400 text-sm font-medium">
                  <span className="text-lg">🎉</span>
                  Activity completed! Final score: {score ?? '—'}
                </div>
              )}

              {/* ── Messages ───────────────────────────────────── */}
              <div className="flex-1 overflow-y-auto">
                <div className="max-w-3xl mx-auto px-6 py-6 space-y-8">
                  {messages.length === 0 && (
                    <p className="text-xs text-gray-600 text-center pt-8">
                      Start the conversation below.
                    </p>
                  )}

                  {messages.map((msg, i) => (
                    msg.role === 'user' ? (
                      /* User bubble */
                      <div key={i} className="flex justify-end animate-fade-in">
                        <div className="max-w-[78%] bg-gray-800 text-gray-100 px-4 py-3 rounded-2xl rounded-tr-sm text-sm leading-relaxed">
                          {msg.content}
                        </div>
                      </div>
                    ) : (
                      /* Assistant — no bubble, full width */
                      <div key={i} className="flex gap-4 items-start animate-fade-in">
                        <div className="w-8 h-8 rounded-xl bg-violet-600/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <svg className="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                          </svg>
                        </div>
                        <div className="flex-1 text-sm text-gray-200 leading-relaxed pt-1">
                          <RichText text={msg.content} />
                        </div>
                      </div>
                    )
                  ))}

                  {/* Thinking indicator */}
                  {chatLoading && (
                    <div className="flex gap-4 items-start animate-fade-in">
                      <div className="w-8 h-8 rounded-xl bg-violet-600/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <svg className="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                        </svg>
                      </div>
                      <div className="flex gap-1 pt-3.5">
                        <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  )}

                  <div ref={bottomRef} />
                </div>
              </div>

              {/* ── Input ──────────────────────────────────────── */}
              <div className="px-6 pb-8 pt-3">
                <div className="max-w-3xl mx-auto">
                  <div className="relative flex items-end bg-gray-900 rounded-2xl border border-gray-700/50 focus-within:border-gray-600/80 transition-colors duration-150">
                    <textarea
                      ref={textareaRef}
                      value={chatInput}
                      onChange={e => setChatInput(e.target.value)}
                      onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey && !chatLoading && !completed) {
                          e.preventDefault()
                          handleSend()
                        }
                      }}
                      disabled={chatLoading || completed}
                      placeholder={completed ? 'Activity completed.' : 'Message Socratic AI…'}
                      onFocus={() => setInputFocused(true)}
                      onBlur={() => { if (!chatInput.trim()) setInputFocused(false) }}
                      className={`flex-1 bg-transparent px-4 py-3.5 text-sm text-gray-100 placeholder-gray-600 resize-none focus:outline-none disabled:opacity-40 overflow-y-auto transition-all duration-200 ${inputFocused || chatInput.trim() ? 'h-[150px]' : 'h-[48px]'}`}
                    />
                    {chatInput.trim() && !completed && (
                      <button
                        onClick={() => handleSend()}
                        disabled={chatLoading}
                        className="m-2.5 w-8 h-8 flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl flex items-center justify-center transition-colors"
                      >
                        <ArrowUp className="w-4 h-4 text-white" />
                      </button>
                    )}
                  </div>
                  <p className="text-center text-[11px] text-gray-700 mt-2">
                    Press Enter to send · Shift+Enter for new line
                  </p>
                </div>
              </div>
            </>
          )}
        </main>
      </div>

      {showAddModal && (
        <AddActivityModal
          credentials={studentCredentials}
          onClose={() => setShowAddModal(false)}
          onAdded={handleAddActivity}
          push={push}
        />
      )}

      <ToastContainer toasts={toasts} />
    </div>
  )
}

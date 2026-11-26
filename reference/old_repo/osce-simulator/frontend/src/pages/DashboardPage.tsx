import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Session {
  id: string
  title: string
  date: string
  time: string
  type: 'practice' | 'assessment'
  status: 'scheduled' | 'completed' | 'cancelled'
}

interface Progress {
  casesCompleted: number
  totalCases: number
  averageScore: number
  recentScores: number[]
  strongAreas: string[]
  areasToImprove: string[]
}

interface Announcement {
  id: string
  title: string
  content: string
  date: string
  tag: 'admin' | 'faculty' | 'students' | 'technical'
  read: boolean
}

interface AffiliatedGroup {
  id: string
  name: string
  description: string
  memberCount: number
  role: 'admin' | 'member' | 'moderator'
}

const mockSessions: Session[] = [
  {
    id: 'SCN_SAYLOR',
    title: 'Saylor Lee Case',
    date: '2024-03-20',
    time: '10:00 AM',
    type: 'practice',
    status: 'scheduled'
  },
  {
    id: 'er-part-1',
    title: 'ER Case - Part 1',
    date: '2024-03-21',
    time: '2:30 PM',
    type: 'practice',
    status: 'scheduled'
  }
]

const mockProgress: Progress = {
  casesCompleted: 3,
  totalCases: 5,
  averageScore: 85,
  recentScores: [85, 90, 80],
  strongAreas: ['Patient Communication', 'History Taking'],
  areasToImprove: ['Emergency Procedures', 'Clinical Decision Making']
}

const mockAffiliatedGroups: AffiliatedGroup[] = [
  {
    id: '1',
    name: 'Medical Students Association',
    description: 'Connect with fellow medical students and share study resources.',
    memberCount: 156,
    role: 'member'
  },
  {
    id: '2',
    name: 'OSCE Preparation Group',
    description: 'Dedicated group for OSCE exam preparation and practice.',
    memberCount: 89,
    role: 'admin'
  }
]

const mockAnnouncements: Announcement[] = [
  {
    id: '1',
    title: 'New ER Cases Available',
    content: 'Four new emergency room cases have been added to the practice section. Test your skills in various emergency scenarios.',
    date: '2024-03-18',
    tag: 'faculty',
    read: false
  },
  {
    id: '2',
    title: 'System Maintenance',
    content: 'Scheduled maintenance on March 25th from 2 AM to 4 AM EST.',
    date: '2024-03-17',
    tag: 'admin',
    read: true
  },
  {
    id: '3',
    title: 'Study Group Meeting',
    content: 'Weekly study group meeting this Friday at 3 PM in the library.',
    date: '2024-03-16',
    tag: 'students',
    read: false
  },
  {
    id: '4',
    title: 'Website Updates',
    content: 'New features have been added to the OSCE simulator. Check out the improved interface!',
    date: '2024-03-15',
    tag: 'technical',
    read: true
  }
]

export default function DashboardPage() {
  const navigate = useNavigate()
  const [userName, setUserName] = useState('User')
  const [sessions, setSessions] = useState<Session[]>(mockSessions)
  const [progress, setProgress] = useState<Progress>(mockProgress)
  const [affiliatedGroups, setAffiliatedGroups] = useState<AffiliatedGroup[]>(mockAffiliatedGroups)
  const [announcements, setAnnouncements] = useState<Announcement[]>(mockAnnouncements)
  const [conversations, setConversations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch user data from backend
        const userResponse = await axios.get(`${API_BASE_URL}/api/auth/me`, { withCredentials: true });
        setUserName(userResponse.data.username);
        
        // Only fetch from endpoints that actually exist
        // For now, sessions/progress/announcements use mock data
        setSessions(mockSessions)
        setProgress(mockProgress)
        setAnnouncements(mockAnnouncements)
        
        // Only fetch conversations from the backend (this endpoint exists)
        const conversationsResponse = await axios.get(`${API_BASE_URL}/api/conversations`, { withCredentials: true })
        setConversations(conversationsResponse.data.items || [])
      } catch (error) {
        console.log('Could not fetch user data or conversations, using defaults')
        setConversations([])
      } finally {
        setLoading(false)
      }
    }
    fetchDashboardData()
  }, [])

  // Helper function to find the most recent conversation with evaluation for a case
  const findLatestEvaluationForCase = (caseId: string) => {
    const caseConversations = conversations.filter(conv => 
      conv.case_id === caseId || (caseId === 'saylor-lee' && conv.case_id === 'SCN_SAYLOR')
    )
    
    // Sort by updated_at (most recent first) and find the first one with messages
    caseConversations.sort((a, b) => b.updated_at - a.updated_at)
    
    for (const conv of caseConversations) {
      // If it has messages, it might have an evaluation
      if (conv.message_count > 0) {
        return conv.conversation_id
      }
    }
    
    return null
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Decorative Background Elements */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-24 -right-24 h-72 w-72 rounded-full bg-gradient-to-tr from-indigo-200/60 to-purple-200/60 blur-3xl" />
        <div className="absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-gradient-to-tr from-sky-200/60 to-emerald-200/60 blur-3xl" />
      </div>
      {/* Welcome Section */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              Welcome back, {userName}
            </h1>
            <p className="mt-2 text-gray-600">
              Here's an overview of your progress and upcoming sessions
            </p>
          </motion.div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-8 grid grid-cols-1 gap-3 sm:grid-cols-3"
        >
          <button
            onClick={() => navigate('/practice')}
            className="group flex items-center justify-between rounded-2xl border border-blue-200/60 bg-gradient-to-r from-blue-50 to-indigo-50 px-5 py-4 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center">
              <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 text-white">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v12m6-6H6"/></svg>
              </div>
              <div>
                <div className="font-semibold text-gray-900">Start Practice</div>
                <div className="text-xs text-gray-500">Browse all available cases</div>
              </div>
            </div>
            <span className="text-blue-600 transition-transform group-hover:translate-x-1">→</span>
          </button>
          <button
            onClick={() => {
              const latest = conversations.sort((a, b) => b.updated_at - a.updated_at)[0]
              if (latest?.case_id) navigate(`/consultation/${latest.case_id}`)
              else navigate('/practice')
            }}
            className="group flex items-center justify-between rounded-2xl border border-purple-200/60 bg-gradient-to-r from-purple-50 to-pink-50 px-5 py-4 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center">
              <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 text-white">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v8m4-4H8"/></svg>
              </div>
              <div>
                <div className="font-semibold text-gray-900">Continue Last Case</div>
                <div className="text-xs text-gray-500">Jump back into your most recent session</div>
              </div>
            </div>
            <span className="text-purple-600 transition-transform group-hover:translate-x-1">→</span>
          </button>
          <button
            onClick={() => navigate('/evaluations')}
            className="group flex items-center justify-between rounded-2xl border border-emerald-200/60 bg-gradient-to-r from-emerald-50 to-green-50 px-5 py-4 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center">
              <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-green-500 text-white">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg>
              </div>
              <div>
                <div className="font-semibold text-gray-900">View Evaluations</div>
                <div className="text-xs text-gray-500">See feedback and scores</div>
              </div>
            </div>
            <span className="text-emerald-600 transition-transform group-hover:translate-x-1">→</span>
          </button>
        </motion.div>

        {/* Loading Skeletons */}
        {loading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              <div className="rounded-2xl bg-white/80 p-8 ring-1 ring-gray-200/50 shadow-lg">
                <div className="mb-8 flex items-center justify-between">
                  <div>
                    <div className="h-6 w-40 rounded bg-gray-200 animate-pulse" />
                    <div className="mt-2 h-4 w-56 rounded bg-gray-100 animate-pulse" />
                  </div>
                  <div className="h-9 w-28 rounded-lg bg-gray-100 animate-pulse" />
                </div>
                <div className="space-y-4">
                  {[1,2].map(i => (
                    <div key={i} className="flex items-center justify-between rounded-xl border border-blue-200/50 bg-gradient-to-r from-blue-50 to-purple-50 p-6">
                      <div className="flex items-center space-x-4">
                        <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-200 to-purple-200" />
                        <div>
                          <div className="h-4 w-48 rounded bg-white/70 animate-pulse" />
                          <div className="mt-2 h-3 w-32 rounded bg-white/60 animate-pulse" />
                        </div>
                      </div>
                      <div className="h-8 w-20 rounded-lg bg-white/70 animate-pulse" />
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl bg-white/80 p-8 ring-1 ring-gray-200/50 shadow-lg">
                <div className="mb-6 h-6 w-40 rounded bg-gray-200 animate-pulse" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-6">
                    <div className="h-24 rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200/50 animate-pulse" />
                    <div className="h-24 rounded-xl bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200/50 animate-pulse" />
                  </div>
                  <div className="space-y-6">
                    <div className="h-36 rounded-xl bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200/50 animate-pulse" />
                    <div className="h-36 rounded-xl bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200/50 animate-pulse" />
                  </div>
                </div>
              </div>
            </div>
            <div className="space-y-8">
              <div className="rounded-2xl bg-white/80 p-6 ring-1 ring-gray-200/50 shadow-lg">
                <div className="mb-6 h-6 w-36 rounded bg-gray-200 animate-pulse" />
                <div className="space-y-3">
                  {[1,2,3].map(i => (
                    <div key={i} className="h-20 rounded-xl bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200/50 animate-pulse" />
                  ))}
                </div>
              </div>
              <div className="rounded-2xl bg-white/80 p-6 ring-1 ring-gray-200/50 shadow-lg">
                <div className="mb-6 h-6 w-36 rounded bg-gray-200 animate-pulse" />
                <div className="space-y-3">
                  {[1,2,3].map(i => (
                    <div key={i} className="h-24 rounded-xl bg-gradient-to-r from-gray-50 to-white border border-gray-200/50 animate-pulse" />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
        {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content (Left 2 Columns) */}
          <div className="lg:col-span-2 space-y-8">
            {/* Upcoming Sessions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg ring-1 ring-gray-200/50 overflow-hidden"
            >
                              <div className="p-8">
                  <div className="flex items-center justify-between mb-8">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">Upcoming Sessions</h2>
                      <p className="text-sm text-gray-500 mt-1">Your scheduled practice cases</p>
                    </div>
                    <button
                      onClick={() => navigate('/practice')}
                      className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors"
                    >
                      View all cases
                      <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>
                  <div className="space-y-4">
                    {sessions.map((session) => (
                      <div
                        key={session.id}
                        className="group flex items-center justify-between p-6 rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 hover:from-blue-100 hover:to-purple-100 transition-all duration-200 border border-blue-200/50 hover:border-blue-300/50"
                      >
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">{session.title}</h3>
                            <p className="text-sm text-gray-600">
                              {new Date(session.date).toLocaleDateString()} at {session.time}
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => navigate(`/consultation/${session.id}`)}
                            className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 bg-white/50 hover:bg-white/80 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                          >
                            Start →
                          </button>
                          {(() => {
                            const evaluationId = findLatestEvaluationForCase(session.id)
                            if (evaluationId) {
                              return (
                                <button
                                  onClick={() => navigate(`/evaluation/${evaluationId}`)}
                                  className="px-4 py-2 text-sm font-medium text-green-600 hover:text-green-500 bg-white/50 hover:bg-white/80 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                                >
                                  View Evaluation
                                </button>
                              )
                            }
                            return null
                          })()}
                        </div>
                      </div>
                    ))}
                    {sessions.length === 0 && (
                      <div className="text-center py-12">
                        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <p className="mt-4 text-gray-500">No upcoming sessions</p>
                      </div>
                    )}
                  </div>
                </div>
            </motion.div>

            {/* Progress Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg ring-1 ring-gray-200/50 overflow-hidden"
            >
              <div className="p-8">
                <div className="flex items-center space-x-3 mb-8">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Your Progress</h2>
                    <p className="text-sm text-gray-500">Track your learning journey</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Stats */}
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200/50">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-sm font-medium text-gray-700">Cases Completed</span>
                        <span className="text-lg font-bold text-blue-600">{progress.casesCompleted}/{progress.totalCases}</span>
                      </div>
                      <div className="w-full bg-white/50 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${(progress.casesCompleted / progress.totalCases) * 100}%` }}
                        />
                      </div>
                    </div>
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200/50">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-sm font-medium text-gray-700">Average Score</span>
                        <span className="text-lg font-bold text-green-600">{progress.averageScore}%</span>
                      </div>
                      <div className="w-full bg-white/50 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${progress.averageScore}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Areas */}
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200/50">
                      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
                        <svg className="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Strong Areas
                      </h3>
                      <div className="space-y-2">
                        {progress.strongAreas.map((area, index) => (
                          <div key={index} className="flex items-center text-sm text-gray-700 bg-white/50 rounded-lg px-3 py-2">
                            <svg className="h-4 w-4 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            {area}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-200/50">
                      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
                        <svg className="h-5 w-5 text-yellow-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        Areas to Improve
                      </h3>
                      <div className="space-y-2">
                        {progress.areasToImprove.map((area, index) => (
                          <div key={index} className="flex items-center text-sm text-gray-700 bg-white/50 rounded-lg px-3 py-2">
                            <svg className="h-4 w-4 text-yellow-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            {area}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

                    {/* Right Column - Groups and Announcements */}
          <div className="space-y-8">
            {/* Affiliated Groups */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg ring-1 ring-gray-200/50 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Affiliated Groups</h2>
                    <p className="text-sm text-gray-500">Your community connections</p>
                  </div>
                </div>
                <div className="max-h-48 overflow-y-auto space-y-3 pr-2">
                  {affiliatedGroups.map((group) => (
                    <div
                      key={group.id}
                      className="group bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-4 border border-indigo-200/50 hover:border-indigo-300/50 transition-all duration-200"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                            {group.name}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">{group.description}</p>
                          <div className="flex items-center mt-2 space-x-4">
                            <span className="text-xs text-gray-500">
                              {group.memberCount} members
                            </span>
                            <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                              group.role === 'admin'
                                ? 'bg-red-100 text-red-700 ring-1 ring-red-200'
                                : group.role === 'moderator'
                                ? 'bg-yellow-100 text-yellow-700 ring-1 ring-yellow-200'
                                : 'bg-green-100 text-green-700 ring-1 ring-green-200'
                            }`}>
                              {group.role}
                            </span>
                          </div>
                        </div>
                        <button className="ml-4 px-3 py-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-500 bg-white/50 hover:bg-white/80 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md">
                          View
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Announcements */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg ring-1 ring-gray-200/50 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Announcements</h2>
                    <p className="text-sm text-gray-500">Stay updated with the latest news</p>
                  </div>
                </div>
                <div className="max-h-64 overflow-y-auto space-y-3 pr-2">
                  {announcements.map((announcement) => (
                    <div
                      key={announcement.id}
                      className={`relative group ${
                        announcement.read ? 'opacity-75' : ''
                      }`}
                    >
                      <div className="bg-gradient-to-r from-gray-50 to-white rounded-xl p-4 border border-gray-200/50 hover:border-purple-200/50 transition-all duration-200">
                        {!announcement.read && (
                          <div className="absolute -top-2 -right-2 w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse" />
                        )}
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <h3 className="text-sm font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">
                              {announcement.title}
                            </h3>
                            <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                              announcement.tag === 'admin'
                                ? 'bg-red-100 text-red-700 ring-1 ring-red-200'
                                : announcement.tag === 'faculty'
                                ? 'bg-blue-100 text-blue-700 ring-1 ring-blue-200'
                                : announcement.tag === 'students'
                                ? 'bg-green-100 text-green-700 ring-1 ring-green-200'
                                : 'bg-purple-100 text-purple-700 ring-1 ring-purple-200'
                            }`}>
                              {announcement.tag}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 leading-relaxed">
                            {announcement.content}
                          </p>
                          <div className="flex items-center text-xs text-gray-400">
                            <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            {new Date(announcement.date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
        )}
      </div>
    </div>
  )
}

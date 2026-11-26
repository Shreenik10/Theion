import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import Header from '../components/Header'

interface EvaluationItem {
  id: number
  category: string
  description: string
  score: number
  feedback?: string[]
}

interface SessionSummary {
  timeTaken: string
  points: number
  maxPoints: number
  percentageScore: number
}

const evaluationItems: EvaluationItem[] = [
  {
    id: 1,
    category: "Introduction & Collaboration with Patient",
    description: "The student introduced themselves, explained the purpose of the interview, and obtained consent appropriately.",
    score: 3,
    feedback: [
      "Did not explicitly obtain consent before starting the interview.",
      "Did not introduce themselves by name"
    ]
  },
  {
    id: 2,
    category: "Biographical Data",
    description: "The student accurately gathered identifying information such as name, age, gender, and preferred pronouns.",
    score: 2,
    feedback: [
      "Failed to ask about preferred pronouns and age.",
      "Did not verify spelling of patient's name",
      "Missed asking about emergency contact information"
    ]
  },
  {
    id: 3,
    category: "Past Medical History – Part 1",
    description: "The student asked about at least seven general health items and included at least one question related to sexual health.",
    score: 4
  },
  {
    id: 4,
    category: "Past Medical History – Part 2",
    description: "The student inquired about all medications (including dose and frequency) and allergy types.",
    score: 5
  },
  {
    id: 5,
    category: "Family History",
    description: "The student explored health status across three generations and addressed hereditary conditions or familial trends.",
    score: 3,
    feedback: [
      "Only discussed immediate family members.",
      "Did not ask about grandparents' health conditions"
    ]
  },
  {
    id: 6,
    category: "Functional Assessment – Part 1",
    description: "The student assessed sleep patterns, physical activity, mobility and use of assistive devices, dietary intake, and elimination habits.",
    score: 4
  },
  {
    id: 7,
    category: "Functional Assessment – Part 2",
    description: "The student evaluated coping and stress management, smoking/vaping history, and discussed advanced care planning.",
    score: 3,
    feedback: [
      "Did not explore coping mechanisms in detail",
      "Missed asking about alcohol consumption"
    ]
  },
  {
    id: 8,
    category: "Review of Systems",
    description: "The student conducted a systems review tailored to the patient's past or family history, covering at least five relevant systems.",
    score: 4
  },
  {
    id: 9,
    category: "Health Promotion Opportunities",
    description: "The student identified and discussed at least three health promotion topics or nursing interventions relevant to the patient's needs.",
    score: 5
  },
  {
    id: 10,
    category: "Quality of Health Promotion",
    description: "Health advice was broken into simple terms, verified for understanding, and was evidence-based and personalized.",
    score: 4
  },
  {
    id: 11,
    category: "Global Appreciation – Patient-Centered Care",
    description: "The student validated the patient's experience, considered their beliefs and expectations, and adapted communication respectfully.",
    score: 5
  },
  {
    id: 12,
    category: "Global Appreciation – Interview Style",
    description: "The student used open-ended and purposeful close-ended questions, avoided negatively phrased questions, and guided the encounter effectively.",
    score: 4
  },
  {
    id: 13,
    category: "Global Appreciation – Organization",
    description: "The student maintained logical flow and structure in the interview, minimizing any disorganization or redundancy.",
    score: 4
  },
  {
    id: 14,
    category: "Global Appreciation – Clinical Judgment & Knowledge",
    description: "The student demonstrated accurate clinical reasoning throughout, selecting appropriate follow-up questions and showing awareness of relevant pathophysiology.",
    score: 3,
    feedback: [
      "Could have shown deeper understanding of pathophysiology in follow-up questions.",
      "Missed connecting symptoms to potential underlying conditions",
      "Did not prioritize questions based on clinical significance"
    ]
  },
  {
    id: 15,
    category: "Global Appreciation – Professionalism",
    description: "The student behaved ethically and respectfully, maintained composure, and demonstrated accountability and professional presence.",
    score: 5
  }
]

const API_BASE_URL = 'http://localhost:8000'

export default function TutorialEvaluationPage() {
  const navigate = useNavigate()
  const [sessionSummary, setSessionSummary] = useState<SessionSummary>({
    timeTaken: "12:34",
    points: 58,
    maxPoints: 75,
    percentageScore: 77.3
  })
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0)
    
    const loadEvaluation = async () => {
      try {
        // In the future, this would load real evaluation data from the backend
        // const response = await axios.get(`${API_BASE_URL}/api/evaluate/tutorial`, { withCredentials: true })
        // setSessionSummary(response.data.sessionSummary)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load evaluation')
      }
    }
    loadEvaluation()
  }, [])

  const totalScore = evaluationItems.reduce((sum, item) => sum + item.score, 0)
  const maxPossibleScore = evaluationItems.length * 5
  const percentageScore = (totalScore / maxPossibleScore) * 100
  const missedItems = evaluationItems.filter(item => item.score < 3)
  const strengths = evaluationItems.filter(item => item.score >= 4)
  const nextSteps = evaluationItems.filter(item => item.score < 4)

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 p-4">
        <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
          <div className="text-red-500">{error}</div>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName="John Doe" />
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* Header */}
            <div className="p-8 bg-gradient-to-r from-blue-50 to-blue-100/20 border-b border-gray-200">
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Tutorial Evaluation Results</h1>
                <button
                  onClick={() => navigate('/practice')}
                  className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 bg-white/50 hover:bg-white/80 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  Back to Practice
                </button>
              </div>
              
              {/* Session Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div className="bg-white/80 rounded-xl p-4 border border-blue-200/50">
                  <p className="text-sm text-gray-500">Time Taken</p>
                  <p className="text-2xl font-bold text-gray-900">{sessionSummary.timeTaken}</p>
                </div>
                <div className="bg-white/80 rounded-xl p-4 border border-blue-200/50">
                  <p className="text-sm text-gray-500">Points</p>
                  <p className="text-2xl font-bold text-gray-900">{sessionSummary.points}/{sessionSummary.maxPoints}</p>
                </div>
                <div className="bg-white/80 rounded-xl p-4 border border-blue-200/50">
                  <p className="text-sm text-gray-500">Score</p>
                  <p className="text-2xl font-bold text-gray-900">{sessionSummary.percentageScore.toFixed(1)}%</p>
                </div>
                <div className="bg-white/80 rounded-xl p-4 border border-blue-200/50">
                  <p className="text-sm text-gray-500">Overall Performance</p>
                  <p className="text-2xl font-bold text-gray-900">{percentageScore.toFixed(1)}%</p>
                </div>
              </div>

              <div className="flex items-center">
                <div className="flex-1">
                  <p className="text-sm text-gray-500">Detailed Performance</p>
                  <p className="mt-1 text-3xl font-bold text-gray-900">{percentageScore.toFixed(1)}%</p>
                </div>
                <div className="w-32 h-32 relative">
                  <svg className="w-full h-full" viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#E5E7EB"
                      strokeWidth="3"
                    />
                    <path
                      d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#3B82F6"
                      strokeWidth="3"
                      strokeDasharray={`${percentageScore}, 100`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-lg font-semibold text-gray-900">{totalScore}/{maxPossibleScore}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main content */}
            <div className="p-8">
              {/* Strengths and Next Steps Cards */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Strengths Card */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                  className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200/50"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-green-900">Strengths</h2>
                      <p className="text-sm text-green-600">Areas where you excelled</p>
                    </div>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {strengths.map(item => (
                      <div key={item.id} className="flex items-center space-x-2 bg-white/50 rounded-lg px-3 py-2">
                        <svg className="h-4 w-4 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-sm text-green-800">{item.category}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Next Steps Card */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-200/50"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-yellow-900">Next Steps</h2>
                      <p className="text-sm text-yellow-600">Areas for improvement</p>
                    </div>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {nextSteps.map(item => (
                      <div key={item.id} className="flex items-center space-x-2 bg-white/50 rounded-lg px-3 py-2">
                        <svg className="h-4 w-4 text-yellow-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span className="text-sm text-yellow-800">{item.category}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </div>

              {/* Areas for Improvement */}
              {missedItems.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="mb-8 p-6 bg-yellow-50 rounded-xl border border-yellow-100"
                >
                  <h2 className="text-lg font-semibold text-yellow-800">Areas for Improvement</h2>
                  <div className="mt-4 max-h-48 overflow-y-auto">
                    {missedItems.map(item => (
                      <div key={item.id} className="mt-4 first:mt-0">
                        <h3 className="font-medium text-yellow-900">{item.category}</h3>
                        {item.feedback && (
                          <div className="mt-2 space-y-1">
                            {item.feedback.map((feedbackItem, index) => (
                              <p key={index} className="text-sm text-yellow-700 flex items-start">
                                <span className="text-yellow-500 mr-2 mt-0.5">•</span>
                                {feedbackItem}
                              </p>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Evaluation Items */}
              <div className="space-y-8">
                {evaluationItems.map(item => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: item.id * 0.1 }}
                    className="border-b border-gray-200 pb-6 last:border-0 last:pb-0"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900">{item.category}</h3>
                        <p className="mt-1 text-sm text-gray-500">{item.description}</p>
                        {item.feedback && item.feedback.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {item.feedback.map((feedbackItem, index) => (
                              <div key={index} className="bg-yellow-50 px-3 py-2 rounded-lg border border-yellow-200">
                                <p className="text-sm text-yellow-700 flex items-start">
                                  <span className="text-yellow-500 mr-2 mt-0.5 font-medium">−</span>
                                  {feedbackItem}
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="ml-6 flex items-center">
                        {[1, 2, 3, 4, 5].map(score => (
                          <div
                            key={score}
                            className={`w-8 h-8 flex items-center justify-center rounded-full mx-0.5 ${
                              score <= item.score
                                ? "bg-blue-600 text-white"
                                : "bg-gray-100 text-gray-400"
                            }`}
                          >
                            {score}
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex gap-4">
                <button
                  onClick={() => navigate('/practice')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Try Another Case
                </button>
                <button
                  onClick={() => navigate('/tutorial')}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Watch Tutorial Again
                </button>
                <button
                  onClick={() => navigate('/form')}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                >
                  Create Question Form
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

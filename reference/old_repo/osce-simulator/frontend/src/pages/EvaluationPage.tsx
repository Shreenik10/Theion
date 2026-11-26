import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'

interface EvaluationItem {
  id: number
  category: string
  description: string
  score: number
  maxScore: number
  reasoning: string
  feedback?: string[]
}

interface SessionSummary {
  timeTaken: string
  points: number
  maxPoints: number
  percentageScore: number
}

interface RealEvaluationData {
  scores: {
    introduction_collaboration: number
    past_medical_history_part1: number
    past_medical_history_part2: number
    family_history: number
    functional_assessment_part1: number
    functional_assessment_part2: number
    review_of_systems: number
    health_promotion_opportunities: number
    quality_health_promotion: number
    interview_style: number
    organization: number
    clinical_judgment: number
  }
  feedback: {
    introduction_collaboration: string
    past_medical_history_part1: string
    past_medical_history_part2: string
    family_history: string
    functional_assessment_part1: string
    functional_assessment_part2: string
    review_of_systems: string
    health_promotion_opportunities: string
    quality_health_promotion: string
    interview_style: string
    organization: string
    clinical_judgment: string
    overall: string
  }
  total_score: number
  max_possible: number
}

// Updated to match the exact OSCE rubric structure from the PDF
const evaluationItems: EvaluationItem[] = [
  {
    id: 1,
    category: "Introduction & Collaboration with Patient",
    description: "Introduction & collaboration with patient, biographical data, Past Medical History (Part 1). Must provide 8+ elements for full points, including consent acquisition and at least 1 sexual history element.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 2,
    category: "Past Medical History – Part 1",
    description: "Past medical history including chronic conditions, illnesses, hospitalizations, surgeries, immunizations, mental health, sexual health, and allergies. Must include sexual health and specific examples.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 3,
    category: "Past Medical History – Part 2",
    description: "Medications (each category = 1 element, must ask dose/frequency) and allergies (each type = 1 element).",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 4,
    category: "Family History",
    description: "Health status across 3 generations and hereditary conditions. Each generation = 1 element, must explain all 3 generations for full points. Each hereditary illness example = 1 element.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 5,
    category: "Functional Assessment – Part 1",
    description: "Activity/Exercise (must quantify), mobility & assistive devices, sleep (include daytime naps), nutrition (minimum 1 element), elimination (minimum 1 element).",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 6,
    category: "Functional Assessment – Part 2",
    description: "Coping and stress management (minimum 2 stress questions), smoking/vaping (must ask about both and pack/years), advanced care planning (mandatory question for full points).",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 7,
    category: "Review of Systems",
    description: "Must be related to PMHx or Family Hx, otherwise no element points attributed. Should cover at least 5 relevant systems.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 8,
    category: "Opportunities for Health Promotion",
    description: "3 health promotion items and/or nursing interventions relevant to patient needs.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 9,
    category: "Quality of Health Promotion",
    description: "Breaks down information into short statements, verifies patient understanding, recommendations are evidence-based and tailored to patient needs.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 10,
    category: "Global Appreciation – Interview Style",
    description: "Uses open-ended questions to confirm reason for visit, guides interview with direct purposeful close-ended questions, avoids negatively-phrased questions.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 11,
    category: "Global Appreciation – Organization",
    description: "Completes assessment in orderly manner with minimal disorganization throughout.",
    score: 0,
    maxScore: 5,
    reasoning: "Loading evaluation data..."
  },
  {
    id: 12,
    category: "Global Appreciation – Clinical Judgment & Knowledge",
    description: "Demonstrates sound clinical knowledge associated with reason for visit, good knowledge of pertinent clinical data to guide assessment (e.g., ROS tailored to patient history).",
    score: 0,
    maxScore: 10,
    reasoning: "Loading evaluation data..."
  }
]

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function EvaluationPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [sessionSummary, setSessionSummary] = useState<SessionSummary>({
    timeTaken: "00:00",
    points: 0,
    maxPoints: 94,
    percentageScore: 0
  })
  const [evaluationData, setEvaluationData] = useState<RealEvaluationData | null>(null)
  const [currentEvaluationItems, setCurrentEvaluationItems] = useState<EvaluationItem[]>(evaluationItems)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadEvaluation = async () => {
      if (!id) return
      
      try {
        setLoading(true)
        
        // Check if this is a case ID (like SCN_SAYLOR) or conversation ID
        const isCaseId = id.includes('SCN_') || id === 'saylor-lee'
        
        let data: RealEvaluationData
        
        if (isCaseId) {
          // If it's a case ID, find the most recent evaluation for this case
          const conversationsResponse = await axios.get(`${API_BASE_URL}/api/conversations`, { 
            withCredentials: true 
          })
          
          const conversations = conversationsResponse.data.items
          const caseConversations = conversations.filter((conv: any) => 
            conv.case_id === id || (id === 'saylor-lee' && conv.case_id === 'SCN_SAYLOR')
          )
          
          if (caseConversations.length === 0) {
            setError('No conversations found for this case. Please complete a consultation first.')
            setLoading(false)
            return
          }
          
          // Find the most recent conversation that has an evaluation
          let evaluationData = null
          let conversationId = null
          
          for (const conversation of caseConversations) {
            try {
              const evaluationResponse = await axios.get(`${API_BASE_URL}/api/evaluations/${conversation.conversation_id}`, { 
                withCredentials: true 
              })
              evaluationData = evaluationResponse.data
              conversationId = conversation.conversation_id
              break // Found an evaluation, stop searching
            } catch (error) {
              // This conversation doesn't have an evaluation, try the next one
              continue
            }
          }
          
          if (!evaluationData) {
            setError('No evaluations found for this case. Please complete a consultation and submit it for evaluation first.')
            setLoading(false)
            return
          }
          
          data = evaluationData
        } else {
          // It's a conversation ID, load directly
          const response = await axios.get(`${API_BASE_URL}/api/evaluations/${id}`, { 
            withCredentials: true 
          })
          
          data = response.data
        }
        
        // Update evaluation items with real scores and reasoning
        const updatedItems = evaluationItems.map(item => {
          let score = 0
          let reasoning = ""
          
                                  switch (item.category) {
                            case "Introduction & Collaboration with Patient":
                              score = data.scores.introduction_collaboration
                              reasoning = data.feedback.introduction_collaboration
                              break
                            case "Past Medical History – Part 1":
                              score = data.scores.past_medical_history_part1
                              reasoning = data.feedback.past_medical_history_part1
                              break
                            case "Past Medical History – Part 2":
                              score = data.scores.past_medical_history_part2
                              reasoning = data.feedback.past_medical_history_part2
                              break
                            case "Family History":
                              score = data.scores.family_history
                              reasoning = data.feedback.family_history
                              break
                            case "Functional Assessment – Part 1":
                              score = data.scores.functional_assessment_part1
                              reasoning = data.feedback.functional_assessment_part1
                              break
                            case "Functional Assessment – Part 2":
                              score = data.scores.functional_assessment_part2
                              reasoning = data.feedback.functional_assessment_part2
                              break
                            case "Review of Systems":
                              score = data.scores.review_of_systems
                              reasoning = data.feedback.review_of_systems
                              break
                            case "Opportunities for Health Promotion":
                              score = data.scores.health_promotion_opportunities
                              reasoning = data.feedback.health_promotion_opportunities
                              break
                            case "Quality of Health Promotion":
                              score = data.scores.quality_health_promotion
                              reasoning = data.feedback.quality_health_promotion
                              break
                            case "Global Appreciation – Interview Style":
                              score = data.scores.interview_style
                              reasoning = data.feedback.interview_style
                              break
                            case "Global Appreciation – Organization":
                              score = data.scores.organization
                              reasoning = data.feedback.organization
                              break
                            case "Global Appreciation – Clinical Judgment & Knowledge":
                              score = data.scores.clinical_judgment
                              reasoning = data.feedback.clinical_judgment
                              break
                          }
          
          return {
            ...item,
            score,
            reasoning: reasoning || "No specific feedback provided for this category."
          }
        })
        
        setCurrentEvaluationItems(updatedItems)
        setEvaluationData(data)
        
        // Calculate session summary
        const totalScore = data.total_score
        const maxPossibleScore = data.max_possible
        const percentageScore = (totalScore / maxPossibleScore) * 100
        
        setSessionSummary({
          timeTaken: "Session completed", // Could be enhanced with actual time tracking
          points: totalScore,
          maxPoints: maxPossibleScore,
          percentageScore
        })
        
      } catch (err: any) {
        console.error('Error loading evaluation:', err)
        setError(err.response?.data?.detail || 'Failed to load evaluation data')
      } finally {
        setLoading(false)
      }
    }
    
    loadEvaluation()
  }, [id])

  const totalScore = currentEvaluationItems.reduce((sum, item) => sum + item.score, 0)
  const maxPossibleScore = currentEvaluationItems.reduce((sum, item) => sum + item.maxScore, 0)
  const percentageScore = (totalScore / maxPossibleScore) * 100
  const missedItems = currentEvaluationItems.filter(item => item.score < item.maxScore * 0.7) // Less than 70% of max score
  const strengths = currentEvaluationItems.filter(item => item.score >= item.maxScore * 0.8) // 80% or more of max score
  const nextSteps = currentEvaluationItems.filter(item => item.score < item.maxScore * 0.8) // Less than 80% of max score

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading evaluation data...</p>
        </div>
      </div>
    )
  }

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
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="p-8 bg-gradient-to-r from-blue-50 to-blue-100/20 border-b border-gray-200">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-gray-900">OSCE Health History Assessment Evaluation</h1>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 bg-white/50 hover:bg-white/80 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
              >
                Back to Dashboard
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
                <p className="text-sm text-gray-500">Performance Level</p>
                <p className="text-2xl font-bold text-gray-900">
                  {sessionSummary.percentageScore >= 85 ? 'Level 4' : sessionSummary.percentageScore >= 70 ? 'Level 3' : sessionSummary.percentageScore >= 55 ? 'Level 2' : 'Level 1'}
                </p>
              </div>
            </div>

            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm text-gray-500">Detailed Performance</p>
                <p className="mt-1 text-3xl font-bold text-gray-900">{sessionSummary.percentageScore.toFixed(1)}%</p>
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
                    strokeDasharray={`${sessionSummary.percentageScore}, 100`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-lg font-semibold text-gray-900">{sessionSummary.points}/{sessionSummary.maxPoints}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main content */}
          <div className="p-8">
            {/* Overall Feedback */}
            {evaluationData && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="mb-8 p-6 bg-blue-50 rounded-xl border border-blue-100"
              >
                <h2 className="text-lg font-semibold text-blue-800 mb-3">Overall Assessment</h2>
                <p className="text-blue-700">{evaluationData.feedback.overall}</p>
              </motion.div>
            )}

            {/* Strengths and Next Steps Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Strengths Card */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
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
                transition={{ duration: 0.5, delay: 0.3 }}
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
                transition={{ duration: 0.5, delay: 0.4 }}
                className="mb-8 p-6 bg-yellow-50 rounded-xl border border-yellow-100"
              >
                <h2 className="text-lg font-semibold text-yellow-800">Areas for Improvement</h2>
                <div className="mt-4 max-h-48 overflow-y-auto">
                  {missedItems.map(item => (
                    <div key={item.id} className="mt-4 first:mt-0">
                      <h3 className="font-medium text-yellow-900">{item.category}</h3>
                      <p className="text-sm text-yellow-700 mt-1">{item.reasoning}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Evaluation Items */}
            <div className="space-y-8">
              {currentEvaluationItems.map(item => (
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
                      
                      {/* Reasoning Section */}
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Score Reasoning:</h4>
                        <p className="text-sm text-gray-600">{item.reasoning}</p>
                      </div>
                      
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
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{item.score}/{item.maxScore}</div>
                        <div className="text-sm text-gray-500">points</div>
                      </div>
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
                Practice Another Case
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

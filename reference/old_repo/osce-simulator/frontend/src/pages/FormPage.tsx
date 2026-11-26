import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import Header from '../components/Header'

interface Question {
  id: string
  question: string
  type: "default" | "explicit"
  response: string
}

const FormPage: React.FC = () => {
  const navigate = useNavigate()
  
  // Scroll to top when component mounts
  React.useEffect(() => {
    window.scrollTo(0, 0)
  }, [])
  
  const [questions, setQuestions] = useState<Question[]>([
    { id: "1", question: "", type: "default", response: "" },
    { id: "2", question: "", type: "default", response: "" },
    { id: "3", question: "", type: "default", response: "" },
    { id: "4", question: "", type: "default", response: "" },
    { id: "5", question: "", type: "default", response: "" },
  ])

  const handleQuestionChange = (id: string, field: keyof Question, value: string) => {
    setQuestions(questions.map(q => 
      q.id === id ? { ...q, [field]: value } : q
    ))
  }

  const addQuestion = () => {
    const newId = String(questions.length + 1)
    setQuestions([...questions, { id: newId, question: "", type: "default", response: "" }])
  }

  const removeQuestion = (id: string) => {
    if (questions.length > 5) {
      setQuestions(questions.filter(q => q.id !== id))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Form data:", questions)
    // Here you would typically save the form data
    // For now, navigate back to tutorial evaluation
    navigate('/tutorial-evaluation')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName="John Doe" />
      <div className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden ring-1 ring-gray-100">
            <div className="p-6 sm:p-8">
              <div className="mb-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-semibold text-gray-900">Create Question Form</h2>
                  <button
                    onClick={() => navigate('/tutorial-evaluation')}
                    className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 bg-blue-50 hover:bg-blue-100 rounded-lg transition-all duration-200"
                  >
                    Back to Evaluation
                  </button>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <h3 className="text-lg font-medium text-blue-900 mb-2">Important Guidelines</h3>
                  <ul className="text-sm text-blue-800 space-y-2">
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span><strong>Questions:</strong> Should be general and open-ended (e.g., "Can you tell me about your symptoms?" rather than "Do you have a headache?")</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span><strong>Responses:</strong> Must be specific and exact, matching precisely how the simulated patient should respond (e.g., "I've been experiencing a throbbing headache in my temples for the past three days, especially in the mornings.")</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span><strong>Question Types:</strong>
                        <ul className="mt-1 ml-4">
                          <li>• Default: Standard patient history questions</li>
                          <li>• Explicit: Questions about sensitive topics requiring specific phrasing</li>
                        </ul>
                      </span>
                    </li>
                  </ul>
                </div>
                <p className="mt-4 text-sm text-gray-600">
                  Add questions and their expected responses. Minimum 5 questions required.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {questions.map((q, index) => (
                  <motion.div
                    key={q.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="bg-gray-50 rounded-xl p-6 relative"
                  >
                    <div className="absolute top-4 right-4 text-sm font-medium text-gray-500">
                      Question {index + 1}
                    </div>
                    
                    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                      <div>
                        <label htmlFor={`question-${q.id}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Question
                        </label>
                        <textarea
                          id={`question-${q.id}`}
                          value={q.question}
                          onChange={(e) => handleQuestionChange(q.id, "question", e.target.value)}
                          className="w-full rounded-lg border-0 bg-white px-4 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 resize-none"
                          rows={2}
                          placeholder="Enter your question..."
                        />
                        
                        <div className="mt-4">
                          <label htmlFor={`type-${q.id}`} className="block text-sm font-medium text-gray-700 mb-2">
                            Question Type
                          </label>
                          <select
                            id={`type-${q.id}`}
                            value={q.type}
                            onChange={(e) => handleQuestionChange(q.id, "type", e.target.value)}
                            className="w-full rounded-lg border-0 bg-white px-4 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                          >
                            <option value="default">Default</option>
                            <option value="explicit">Explicit</option>
                          </select>
                        </div>
                      </div>

                      <div>
                        <label htmlFor={`response-${q.id}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Expected Response
                        </label>
                        <textarea
                          id={`response-${q.id}`}
                          value={q.response}
                          onChange={(e) => handleQuestionChange(q.id, "response", e.target.value)}
                          className="w-full rounded-lg border-0 bg-white px-4 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 resize-none"
                          rows={4}
                          placeholder="Enter the expected response..."
                        />
                      </div>
                    </div>

                    {questions.length > 5 && (
                      <button
                        type="button"
                        onClick={() => removeQuestion(q.id)}
                        className="absolute top-4 right-16 text-red-500 hover:text-red-700 transition-colors"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </button>
                    )}
                  </motion.div>
                ))}

                <div className="flex items-center justify-between pt-6">
                  <motion.button
                    type="button"
                    onClick={addQuestion}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                    </svg>
                    Add Question
                  </motion.button>

                  <div className="flex gap-3">
                    <motion.button
                      type="button"
                      onClick={() => navigate('/evaluation-form')}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-full shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Create Evaluation
                    </motion.button>

                    <motion.button
                      type="submit"
                      className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Save Form
                    </motion.button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FormPage

import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import ConfirmationModal from '../components/ConfirmationModal'
import { ConsultationMessage } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const initialMessages: ConsultationMessage[] = [
  {
    role: 'patient',
    content: "Hi, I'm here for my consultation today.",
    timestamp: new Date().toISOString()
  }
]

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

export default function ConsultationPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<ConsultationMessage[]>(initialMessages)
  const [notes, setNotes] = useState('')
  const [isAudioMode, setIsAudioMode] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [userInput, setUserInput] = useState('')
  const [hideTranscript, setHideTranscript] = useState(false)
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  // Timer states
  const [time, setTime] = useState(0)
  const [isTimerRunning, setIsTimerRunning] = useState(false)
  const [hasTimerStarted, setHasTimerStarted] = useState(false)
  const timerRef = useRef<number>()

  // Modal states
  const [showSubmitModal, setShowSubmitModal] = useState(false)
  const [showRestartModal, setShowRestartModal] = useState(false)
  const [showSaveModal, setShowSaveModal] = useState(false)

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight
    }
  }, [messages])

  useEffect(() => {
    if (isTimerRunning) {
      timerRef.current = setInterval(() => {
        setTime(prev => prev + 1)
      }, 1000)
    } else if (timerRef.current) {
      clearInterval(timerRef.current)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isTimerRunning])

  const startTimer = () => {
    if (!hasTimerStarted) {
      setHasTimerStarted(true)
      setIsTimerRunning(true)
    }
  }

  const toggleTimer = () => {
    setIsTimerRunning(prev => !prev)
  }

  const resetTimer = () => {
    setTime(0)
    setIsTimerRunning(true)
    setHasTimerStarted(true)
  }

  const handleSendMessage = async () => {
    if (!userInput.trim()) return

    startTimer()

    // Add user message
    setMessages(prev => [...prev, {
      role: 'doctor',
      content: userInput,
      timestamp: new Date().toISOString()
    }])

    // Add typing indicator
    setMessages(prev => [...prev, {
      role: 'patient',
      content: '',
      timestamp: new Date().toISOString(),
      isTyping: true
    }])

    // Clear input
    setUserInput('')

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        case_id: id,
        message: userInput
      }, { withCredentials: true })

      setMessages(prev => {
        const newMessages = [...prev]
        newMessages.pop() // Remove typing indicator
        return [...newMessages, {
          role: 'patient',
          content: response.data.message,
          timestamp: new Date().toISOString()
        }]
      })
    } catch (err: any) {
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages.pop() // Remove typing indicator
        return [...newMessages, {
          role: 'patient',
          content: 'I apologize, but I\'m having trouble responding right now.',
          timestamp: new Date().toISOString()
        }]
      })
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  const handleRecordingClick = () => {
    if (!isRecording) {
      startTimer()
      setIsRecording(true)
      setIsPaused(false)
    } else if (isRecording && !isPaused) {
      setIsPaused(true)
    } else {
      setIsPaused(false)
    }
  }

  const handleRestartConsultation = () => {
    setMessages(initialMessages)
    setIsRecording(false)
    setIsPaused(false)
    setNotes('')
    setShowRestartModal(false)
    // Reset and start timer
    setTime(0)
    setIsTimerRunning(true)
    setHasTimerStarted(true)
  }

  const handleSubmitConsultation = async () => {
    try {
      // Temporarily bypass backend submission for development
      // await axios.post(`${API_BASE_URL}/api/evaluate`, {
      //   case_id: id,
      //   notes
      // }, { withCredentials: true })
      
      // Simulate successful submission
      await new Promise(resolve => setTimeout(resolve, 500))
      setShowSubmitModal(false)
      navigate(`/evaluation/${id}`)
    } catch (err: any) {
      console.error('Failed to submit consultation:', err)
    }
  }

  const handleSaveConversation = async () => {
    try {
      // For now, just simulate saving (backend endpoint doesn't exist yet)
      console.log('Saving conversation:', { case_id: id, messages, notes })
      // TODO: Implement actual save endpoint in backend
      // await axios.post(`${API_BASE_URL}/api/save`, {
      //   case_id: id,
      //   messages,
      //   notes
      // }, { withCredentials: true })
      setShowSaveModal(false)
      navigate('/dashboard')
    } catch (err: any) {
      console.error('Failed to save conversation:', err)
      // Even if save fails, still navigate to dashboard
      setShowSaveModal(false)
      navigate('/dashboard')
    }
  }

  return (
    <div className="h-screen overflow-hidden bg-gradient-to-b from-gray-50 to-white flex items-center justify-center">
      <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden ring-1 ring-gray-100">
          <div className="grid grid-cols-12 h-[800px]">
            {/* Left column - Patient info */}
            <div className="col-span-2 border-r border-gray-200 bg-gray-50 p-6">
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 ring-4 ring-white shadow-lg flex items-center justify-center mb-4">
                  <span className="text-lg font-semibold text-blue-600">#{id}</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-8">Patient #{id}</h3>

                {/* Timer Section */}
                <div className="w-full">
                  <div className="bg-white rounded-2xl p-6 shadow-lg ring-1 ring-gray-100">
                    <div className="flex flex-col items-center">
                      <div className="w-full flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-gray-500">Consultation Time</h4>
                        <div className={`h-2 w-2 rounded-full ${isTimerRunning ? 'bg-blue-500' : 'bg-gray-300'}`} />
                      </div>
                      <div className="w-full bg-white rounded-lg shadow-sm ring-1 ring-gray-100 p-4 mb-4 select-none">
                        <div className="text-3xl font-mono font-medium text-gray-700 text-center tabular-nums [transition:none]">
                          {formatTime(time)}
                        </div>
                      </div>
                      <div className="w-full grid grid-cols-2 gap-2">
                        <button
                          onClick={toggleTimer}
                          className={`h-9 rounded-lg text-sm font-medium inline-flex items-center justify-center ${
                            isTimerRunning
                              ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                              : 'bg-blue-50 text-blue-700 hover:bg-blue-100'
                          }`}
                        >
{isTimerRunning ? 'Pause' : 'Start'}
                        </button>
                        <button
                          onClick={resetTimer}
                          className="h-9 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 text-sm font-medium inline-flex items-center justify-center"
                        >
Reset
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Chat section */}
            <div className="col-span-6 h-full flex flex-col overflow-hidden">
              {/* Chat header */}
              <div className="flex-none bg-white border-b border-gray-200">
                <div className="p-6 bg-gradient-to-r from-blue-50 to-blue-100/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">Active Consultation</h2>
                      <p className="text-sm text-gray-500 mt-1">Session started at {new Date().toLocaleTimeString()}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      {!isAudioMode && (
                        <button
                          onClick={() => setHideTranscript(!hideTranscript)}
                          className={`flex items-center px-3 py-1.5 rounded-full transition-all duration-200 ${
                            hideTranscript
                              ? "bg-gray-600 text-white"
                              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                          }`}
                          title={hideTranscript ? "Show Transcript" : "Hide Transcript"}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
                            {hideTranscript ? (
                              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                            ) : (
                              <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                            )}
                          </svg>
                          {hideTranscript ? "Show Transcript" : "Hide Transcript"}
                        </button>
                      )}
                      <button
                        onClick={() => setIsAudioMode(!isAudioMode)}
                        className={`p-2 rounded-full transition-all duration-200 ${
                          isAudioMode 
                            ? "bg-blue-600 text-white" 
                            : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                        }`}
                        title={isAudioMode ? "Switch to Text Mode" : "Switch to Audio Mode"}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Chat content */}
              {!isAudioMode ? (
                <div className="flex flex-col flex-1 relative overflow-hidden">
                  <div className="absolute top-0 left-0 right-0 bottom-[88px] overflow-y-auto" ref={scrollContainerRef}>
                    <div className="p-6 space-y-6">
                      {(hideTranscript 
                        ? [messages.filter(m => m.role === 'patient').slice(-1)[0]].filter(Boolean)
                        : messages
                      ).map((message, index) => (
                        <div
                          key={index}
                          className={`flex ${message.role === 'doctor' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`rounded-2xl px-6 py-3 max-w-[80%] shadow-sm ${
                              message.role === 'doctor'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-900'
                            } ${message.isTyping ? 'min-w-[60px]' : ''}`}
                          >
                            {message.isTyping ? (
                              <motion.div
                                className="flex space-x-1 justify-center items-center min-h-[24px]"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }}
                              >
                                <motion.div 
                                  className="w-2 h-2 bg-gray-400 rounded-full"
                                  animate={{ y: [0, -6, 0] }}
                                  transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                                />
                                <motion.div 
                                  className="w-2 h-2 bg-gray-400 rounded-full"
                                  animate={{ y: [0, -6, 0] }}
                                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                                />
                                <motion.div 
                                  className="w-2 h-2 bg-gray-400 rounded-full"
                                  animate={{ y: [0, -6, 0] }}
                                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                                />
                              </motion.div>
                            ) : (
                              <div className="text-[15px] leading-relaxed">{message.content}</div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {/* Input area */}
                  <div className="absolute h-[88px] bottom-0 left-0 right-0 p-6 border-t border-gray-200 bg-white">
                    <div className="flex space-x-4">
                      <input
                        type="text"
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message..."
                        className="flex-1 rounded-lg border-0 bg-gray-100 px-6 py-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <button 
                        onClick={handleSendMessage}
                        className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 transition-all duration-200"
                      >
                        Send
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center">
                  <motion.button
                    onClick={handleRecordingClick}
                    className={`w-24 h-24 rounded-full flex items-center justify-center shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                      isRecording && !isPaused
                        ? "bg-red-600 hover:bg-red-700"
                        : "bg-blue-600 hover:bg-blue-700"
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <div className="relative flex items-center justify-center">
                      {!isRecording ? (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                        </svg>
                      ) : isPaused ? (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      )}
                      {isRecording && !isPaused && (
                        <>
                          <motion.div
                            className="absolute inset-0 rounded-full border-4 border-white opacity-20"
                            animate={{ scale: [1, 1.5, 1], opacity: [0.2, 0, 0.2] }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                          />
                          <motion.div
                            className="absolute inset-0 rounded-full border-4 border-white opacity-20"
                            animate={{ scale: [1, 1.5, 1], opacity: [0.2, 0, 0.2] }}
                            transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }}
                          />
                        </>
                      )}
                    </div>
                  </motion.button>
                  <p className="mt-4 text-sm text-gray-500">
                    {!isRecording ? "Click to start recording" : isPaused ? "Recording paused" : "Recording..."}
                  </p>
                </div>
              )}
            </div>

            {/* Right side - Notes */}
            <div className="col-span-4 p-6 bg-gradient-to-b from-gray-50 h-full">
              <div className="bg-white rounded-2xl p-6 shadow-sm ring-1 ring-gray-100 h-full">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold text-gray-900">Consultation Notes</h4>
                  <span className="text-sm text-gray-500">Auto-saving...</span>
                </div>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Enter your consultation notes here..."
                  className="w-full h-[calc(100%-4rem)] rounded-lg bg-gray-50 p-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Bottom action buttons */}
        <motion.div 
          className="mt-8 flex items-center justify-center gap-4 flex-wrap"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <button
            onClick={() => setShowRestartModal(true)}
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-full shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Restart Consultation
          </button>
          <button
            onClick={() => setShowSaveModal(true)}
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-full shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h5a2 2 0 012 2v7a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h5v5.586l-1.293-1.293zM9 4a1 1 0 012 0v2H9V4z" />
            </svg>
            Come Back Later
          </button>
          <button
            onClick={() => setShowSubmitModal(true)}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Submit Consultation
          </button>
        </motion.div>

        {/* Confirmation Modals */}
        <ConfirmationModal
          isOpen={showSubmitModal}
          onClose={() => setShowSubmitModal(false)}
          onConfirm={handleSubmitConsultation}
          title="Submit Consultation"
          message="Are you sure you want to submit this consultation? This action cannot be undone."
          confirmText="Submit"
          confirmStyle="primary"
        />

        <ConfirmationModal
          isOpen={showRestartModal}
          onClose={() => setShowRestartModal(false)}
          onConfirm={handleRestartConsultation}
          title="Restart Consultation"
          message="Are you sure you want to restart? All current progress will be lost."
          confirmText="Restart"
          confirmStyle="warning"
        />

        <ConfirmationModal
          isOpen={showSaveModal}
          onClose={() => setShowSaveModal(false)}
          onConfirm={handleSaveConversation}
          title="Save and Exit"
          message="Would you like to save your progress and come back later?"
          confirmText="Save and Exit"
          confirmStyle="primary"
        />
      </div>
    </div>
  )
}
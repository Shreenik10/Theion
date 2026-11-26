import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import ConfirmationModal from '../components/ConfirmationModal'
import { ConsultationMessage } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
console.log('API_BASE_URL:', API_BASE_URL)
console.log('VITE_API_URL env var:', import.meta.env.VITE_API_URL)

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
  const [caseLoaded, setCaseLoaded] = useState(false)
  
  // Audio recording states
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [audioChunks, setAudioChunks] = useState<Blob[]>([])
  const [transcribedText, setTranscribedText] = useState('')
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [isProcessingAudio, setIsProcessingAudio] = useState(false)

  // Timer states
  const [time, setTime] = useState(0)
  const [isTimerRunning, setIsTimerRunning] = useState(false)
  const [hasTimerStarted, setHasTimerStarted] = useState(false)
  const timerRef = useRef<number>()

  // Modal states
  const [showSubmitModal, setShowSubmitModal] = useState(false)
  const [showRestartModal, setShowRestartModal] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Text size preference: 0=small, 1=medium, 2=big
  const [textSizeIndex, setTextSizeIndex] = useState(1)
  const textSize = (['sm','md','lg'] as const)[textSizeIndex]
  const sizeClass =
    textSize === 'sm' ? 'text-[14px]' :
    textSize === 'md' ? 'text-[16px]' :
  'text-[18px]'

  // Load Saylor Lee case when component mounts
  useEffect(() => {
    const loadSaylorLeeCase = async () => {
      // Handle both old and new Saylor Lee IDs
      if ((id === 'SCN_SAYLOR' || id === 'saylor-lee') && !caseLoaded) {
        try {
          console.log('Loading Saylor Lee case...')
          const response = await axios.post(`${API_BASE_URL}/api/scenarios/SCN_SAYLOR/start`, {}, { withCredentials: true })
          console.log('Saylor Lee case loaded:', response.data)
          setCaseLoaded(true)
        } catch (error) {
          console.error('Failed to load Saylor Lee case:', error)
        }
      }
    }
    
    loadSaylorLeeCase()
  }, [id, caseLoaded])


  // Helper: pause timer and open a modal
  const openModal = (setter: React.Dispatch<React.SetStateAction<boolean>>) => {
    setIsTimerRunning(false); // auto-pause
    setter(true);             // open the modal
  };

  // Optional helper: only resume if the timer had started already
  const resumeTimerIfStarted = () => {
    if (hasTimerStarted) setIsTimerRunning(true);
  };


  // Show tools and medical info based on exam type
  const hasQuickActions = id === 'er-part-1'; // Only show for ER Part 1
  const showMedicalInfo = id === 'er-part-1' || id === 'SCN_SAYLOR' || id === 'saylor-lee'; // Show for ER Part 1 and Saylor Lee

  // Which Quick Actions view is active?
  const [rightPanelView, setRightPanelView] =
    useState<'menu' | 'checklist' | 'references'>('menu');

  // Insert a randomized OSCE template into Notes
  const insertTemplateNote = () => {
    const template = generateOsceNoteTemplate();
    setNotes(prev => (prev ? prev + '\n\n' + template : template));
  };

  // Simple OSCE note template generator
  const generateOsceNoteTemplate = () => {
    const ccs = ['chest pain','abdominal pain','shortness of breath','headache','palpitations'];
    const cc = ccs[Math.floor(Math.random() * ccs.length)];
    return `OSCE Note

  Patient: [Name], [Age]-year-old [Gender]
  Station: ${id ?? ''}

  Chief Complaint:
  - ${cc}

  History (OLDCARTS + key negatives):
  - Onset:
  - Location:
  - Duration:
  - Character:
  - Alleviating/Aggravating:
  - Radiation:
  - Timing:
  - Associated symptoms:
  - PMH/Medications/Allergies:
  - Social Hx / Family Hx:

  Focused Exam:
  - Vitals: T __  HR __  BP __/__  RR __  SpO₂ __%
  - General:
  - Relevant systems:

  Differential Diagnosis:
  1.
  2.
  3.

  Investigations (if applicable):
  -

  Assessment:
  -

  Plan:
  - Rx/Tx:
  - Follow-up / Safety-net:

  Time started: ${new Date().toLocaleTimeString()}
  `;
  };
    

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
    setIsTimerRunning(false)
    setHasTimerStarted(false)
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

    // Map old Saylor Lee ID to new one for backend
    const caseId = id === 'saylor-lee' ? 'SCN_SAYLOR' : id

    // Get the current session ID from the most recent message with session_id
    const messagesWithSessionId = messages.filter(msg => msg.session_id)
    const currentSessionId = messagesWithSessionId.length > 0 
      ? messagesWithSessionId[messagesWithSessionId.length - 1].session_id 
      : null
    
    console.log('Current session ID:', currentSessionId)
    console.log('Messages with session_id:', messagesWithSessionId.length)

    try {
      console.log('Making API call to:', `${API_BASE_URL}/api/chat`)
      console.log('Sending data:', {
        case_id: caseId,
        message: userInput,
        session_id: currentSessionId
      })

      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        case_id: caseId,
        message: userInput,
        session_id: currentSessionId // Send the current session ID
      }, {
        withCredentials: true,
        timeout: 30000 // 30 second timeout
      })

      console.log('Backend response:', response.data)
      console.log('Backend session_id:', response.data.session_id)
      
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages.pop() // Remove typing indicator
        const newMessage: ConsultationMessage = {
          role: 'patient',
          content: response.data.message,
          timestamp: new Date().toISOString(),
          session_id: response.data.session_id // Store session ID from response
        }
        console.log('Adding message with session_id:', newMessage)
        return [...newMessages, newMessage]
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

  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      const chunks: Blob[] = []
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }
      
      recorder.onstop = async () => {
        setAudioChunks(chunks)
        setIsProcessingAudio(true)
        
        // Convert to WAV format and transcribe
        try {
          const audioBlob = new Blob(chunks, { type: 'audio/webm' })
          await transcribeAudio(audioBlob)
        } catch (error) {
          console.error('Error processing audio:', error)
          alert('Error processing audio recording')
        } finally {
          setIsProcessingAudio(false)
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }
      
      setMediaRecorder(recorder)
      recorder.start()
      startTimer()
      setIsRecording(true)
      setIsPaused(false)
      setTranscribedText('')
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Error accessing microphone. Please check permissions.')
    }
  }

  const stopAudioRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      setIsRecording(false)
      setIsPaused(false)
    }
  }

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      setIsTranscribing(true)
      
      // Convert audio to WAV format
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.webm')
      
      const response = await axios.post(
        `${API_BASE_URL}/api/transcribe`,
        formData,
        {
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      
      if (response.data.success) {
        const transcription = response.data.transcription
        setTranscribedText(transcription)
        
        // Send the transcribed text as a message
        await sendTranscribedMessage(transcription)
      } else {
        throw new Error('Transcription failed')
      }
    } catch (error) {
      console.error('Error transcribing audio:', error)
      alert('Error transcribing audio. Please try again.')
    } finally {
      setIsTranscribing(false)
    }
  }

  const sendTranscribedMessage = async (text: string) => {
    if (!text.trim()) return

    startTimer()

    // Add user message
    setMessages(prev => [...prev, {
      role: 'doctor',
      content: text,
      timestamp: new Date().toISOString()
    }])

    // Add typing indicator
    setMessages(prev => [...prev, {
      role: 'patient',
      content: '',
      timestamp: new Date().toISOString(),
      isTyping: true
    }])

    // Map old Saylor Lee ID to new one for backend
    const caseId = id === 'saylor-lee' ? 'SCN_SAYLOR' : id

    // Get the current session ID from the most recent message with session_id
    const messagesWithSessionId = messages.filter(msg => msg.session_id)
    const currentSessionId = messagesWithSessionId.length > 0 
      ? messagesWithSessionId[messagesWithSessionId.length - 1].session_id 
      : null

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        case_id: caseId,
        message: text,
        session_id: currentSessionId
      }, {
        withCredentials: true,
        timeout: 30000
      })

      setMessages(prev => {
        const newMessages = [...prev]
        newMessages.pop() // Remove typing indicator
        const newMessage: ConsultationMessage = {
          role: 'patient',
          content: response.data.message,
          timestamp: new Date().toISOString(),
          session_id: response.data.session_id
        }
        return [...newMessages, newMessage]
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

  const handleRecordingClick = () => {
    if (!isRecording) {
      startAudioRecording()
    } else {
      stopAudioRecording()
    }
  }

  const handleRestartConsultation = () => {
    setMessages(initialMessages)
    setIsRecording(false)
    setIsPaused(false)
    setNotes('')
    setShowRestartModal(false)
    // Reset audio states
    setMediaRecorder(null)
    setAudioChunks([])
    setTranscribedText('')
    setIsTranscribing(false)
    setIsProcessingAudio(false)
    // Reset timer to 00:00 and stop it
    setTime(0)
    setIsTimerRunning(false)
    setHasTimerStarted(false)
  }

  const handleSubmitConsultation = async () => {
    try {
      setIsSubmitting(true)
      
      // Map old Saylor Lee ID to new one for backend
      const caseId = id === 'saylor-lee' ? 'SCN_SAYLOR' : id
      
      // Get the current session ID from the most recent message with session_id
      const messagesWithSessionId = messages.filter(msg => msg.session_id)
      const sessionId = messagesWithSessionId.length > 0 
        ? messagesWithSessionId[messagesWithSessionId.length - 1].session_id 
        : null
      
      console.log('Submit - Messages with session_id:', messagesWithSessionId.length)
      console.log('Submit - Session ID:', sessionId)
      console.log('Submit - All messages:', messages)
      
      if (!sessionId) {
        console.error('No session ID found in messages:', messages)
        alert('Unable to find session for evaluation. Please try starting a new consultation.')
        setIsSubmitting(false)
        return
      }
      
      // Submit for evaluation
      const response = await axios.post(
        `${API_BASE_URL}/api/evaluate`,
        {
          case_id: caseId,
          conversation_id: sessionId,
          notes: notes || "",
          time_taken: time
        },
        { withCredentials: true }
      )
      
      console.log('Evaluation submitted:', response.data)
      setShowSubmitModal(false)
      navigate(`/evaluation/${sessionId}`)
    } catch (err: any) {
      console.error('Failed to submit consultation:', err)
      setShowSubmitModal(false)
      
      // Show user-friendly error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to submit consultation'
      alert(`Error: ${errorMessage}`)
    } finally {
      setIsSubmitting(false)
    }
  }


  const visibleMessages = hideTranscript
    ? (() => {
        // When hiding transcript, show only the most recent patient response
        if (messages.length === 0) return messages;
        
        // Find the last patient message by iterating backwards
        for (let i = messages.length - 1; i >= 0; i--) {
          if (messages[i].role === 'patient') {
            // Return only the last patient message
            return [messages[i]];
          }
        }
        
        // No patient messages found, return empty array
        return [];
      })()
    : messages;

  return (
    <div className="min-h-screen overflow-y-auto bg-gradient-to-b from-gray-50 to-white flex items-start justify-center py-6">
      <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden ring-1 ring-gray-100">
          <div className="flex md:h-[78vh] h-[82vh]">
            {/* Left column - Sidebar */}
            <div className="w-[22%] border-r border-gray-200 bg-gray-50 p-6 relative overflow-y-auto">
              {/* PATIENT INFO FIRST */}
              <div className="flex flex-col items-center mb-4">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 ring-3 ring-white shadow-lg flex items-center justify-center mb-3 overflow-hidden">
                  {(id === 'SCN_SAYLOR' || id === 'saylor-lee') ? (
                    <img 
                      src="/Saylor Lee.png" 
                      alt="Saylor Lee" 
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback to ID if image fails to load
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const parent = target.parentElement;
                        if (parent) {
                          const fallback = document.createElement('span');
                          fallback.className = 'text-base font-semibold text-blue-600';
                          fallback.textContent = `#${id}`;
                          parent.appendChild(fallback);
                        }
                      }}
                    />
                  ) : (
                    <span className="text-base font-semibold text-blue-600">#{id}</span>
                  )}
                </div>
                <h3 className="text-base font-semibold text-gray-900">
                  {(id === 'SCN_SAYLOR' || id === 'saylor-lee') ? 'Saylor Lee' : `Patient #${id}`}
                </h3>
              </div>

              {/* TIMER SECOND */}
              <div className="w-full mb-4">
                <div className="bg-white rounded-xl p-4 shadow-sm ring-1 ring-gray-100">
                  <div className="flex flex-col items-center">
                    <div className="w-full flex items-center justify-between mb-2">
                      <h4 className="text-xs font-medium text-gray-500">Consultation Time</h4>
                      <div className={`h-1.5 w-1.5 rounded-full ${isTimerRunning ? 'bg-blue-500' : 'bg-gray-300'}`} />
                    </div>
                    <div className="w-full bg-white rounded-lg shadow-sm ring-1 ring-gray-100 p-3 mb-3 select-none flex items-center justify-center">
                      <div className="text-2xl font-mono font-medium text-gray-700 text-center tabular-nums [transition:none]">
                        {formatTime(time)}
                      </div>
                    </div>
                    <div className="w-full grid grid-cols-2 gap-2">
                      <button onClick={toggleTimer} className={`h-8 rounded-lg text-xs font-medium inline-flex items-center justify-center ${isTimerRunning ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' : 'bg-blue-50 text-blue-700 hover:bg-blue-100'}`}>
                        {isTimerRunning ? 'Pause' : 'Start'}
                      </button>
                      <button onClick={resetTimer} className="h-8 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 text-xs font-medium inline-flex items-center justify-center">
                        Reset
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* MEDICAL INFORMATION */}
              {showMedicalInfo && (
              <div className="w-full space-y-3">
                {/* Chief Complaint */}
                <div className="bg-white rounded-lg p-3 shadow-sm ring-1 ring-gray-100">
                  <h4 className="text-xs font-medium text-gray-700 mb-2 flex items-center">
                    <svg className="w-3 h-3 mr-1 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    Chief Complaint
                  </h4>
                  <div className="text-xs text-gray-900 bg-red-50 border border-red-200 rounded-md p-2 min-h-[40px] flex items-center">
                    <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
                    Chest pain for the past 2 days
                  </div>
                </div>

                {/* Past Medical History */}
                <div className="bg-white rounded-lg p-3 shadow-sm ring-1 ring-gray-100">
                  <h4 className="text-xs font-medium text-gray-700 mb-2 flex items-center">
                    <svg className="w-3 h-3 mr-1 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Past Medical History
                  </h4>
                  <div className="space-y-1">
                    <div className="text-xs text-gray-900 bg-blue-50 border border-blue-200 rounded-md p-2 flex items-center">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                      Hypertension
                    </div>
                    <div className="text-xs text-gray-900 bg-blue-50 border border-blue-200 rounded-md p-2 flex items-center">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                      Type 2 Diabetes
                    </div>
                  </div>
                </div>

                {/* Medications */}
                <div className="bg-white rounded-lg p-3 shadow-sm ring-1 ring-gray-100">
                  <h4 className="text-xs font-medium text-gray-700 mb-2 flex items-center">
                    <svg className="w-3 h-3 mr-1 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    Medications
                  </h4>
                  <div className="space-y-1">
                    <div className="text-xs text-gray-900 bg-green-50 border border-green-200 rounded-md p-2 flex items-center">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      Metformin 500mg BID
                    </div>
                    <div className="text-xs text-gray-900 bg-green-50 border border-green-200 rounded-md p-2 flex items-center">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      Lisinopril 10mg daily
                    </div>
                  </div>
                </div>

                {/* Allergies */}
                <div className="bg-white rounded-lg p-3 shadow-sm ring-1 ring-gray-100">
                  <h4 className="text-xs font-medium text-gray-700 mb-2 flex items-center">
                    <svg className="w-3 h-3 mr-1 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    Allergies
                  </h4>
                  <div className="space-y-1">
                    <div className="text-xs text-gray-900 bg-orange-50 border border-orange-200 rounded-md p-2 flex items-center">
                      <div className="w-2 h-2 bg-orange-400 rounded-full mr-2"></div>
                      Penicillin (rash)
                    </div>
                  </div>
                </div>
              </div>
              )}

              {/* Text size slider (at bottom of scrollable content) */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <label className="block text-xs text-gray-500 mb-1">Text size</label>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">Small</span>
                  <input
                    type="range"
                    min={0}
                    max={2}
                    step={1}
                    value={textSizeIndex}
                    onChange={(e) => setTextSizeIndex(Number(e.target.value))}
                    className="w-full accent-blue-600"
                    aria-label="Adjust text size"
                  />
                  <span className="text-xs text-gray-500">Big</span>
                </div>
                <div className="mt-1 text-[11px] text-gray-400 text-center">
                  {textSize === 'sm' ? 'Small' : textSize === 'md' ? 'Medium' : 'Big'}
                </div>
              </div>
            </div>

            {/* Chat section */}
            <div className="flex-1 h-full flex flex-col overflow-hidden">
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
                      {visibleMessages.map((message, index) => (
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
                              <div className={`${sizeClass} leading-relaxed`}>{message.content}</div>
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
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleSendMessage();
                          }
                        }}
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
                <div className="flex-1 flex flex-col">
                  {/* Audio Recording Interface */}
                  <div className="flex flex-col items-center justify-center py-8">
                    <motion.button
                      onClick={handleRecordingClick}
                      disabled={isTranscribing || isProcessingAudio}
                      className={`w-24 h-24 rounded-full flex items-center justify-center shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 ${
                        isRecording
                          ? "bg-red-600 hover:bg-red-700"
                          : "bg-blue-600 hover:bg-blue-700"
                      } ${(isTranscribing || isProcessingAudio) ? 'opacity-50 cursor-not-allowed' : ''}`}
                      whileHover={{ scale: (isTranscribing || isProcessingAudio) ? 1 : 1.05 }}
                      whileTap={{ scale: (isTranscribing || isProcessingAudio) ? 1 : 0.95 }}
                    >
                      <div className="relative flex items-center justify-center">
                        {isTranscribing || isProcessingAudio ? (
                          <svg className="animate-spin h-12 w-12 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        ) : !isRecording ? (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        )}
                        {isRecording && !isTranscribing && !isProcessingAudio && (
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
                      {isTranscribing ? "Transcribing..." : 
                       isProcessingAudio ? "Processing audio..." :
                       !isRecording ? "Click to start recording" : "Recording... Click to stop"}
                    </p>
                  </div>

                  {/* Transcribed Text Display */}
                  {transcribedText && (
                    <div className="px-6 pb-4">
                      <div className="text-sm text-gray-600 mb-2">You said:</div>
                      <div className="text-gray-900">{transcribedText}</div>
                    </div>
                  )}

                  {/* Most Recent Patient Response */}
                  <div className="flex-1 overflow-y-auto px-6 pb-6">
                    {(() => {
                      // Find the most recent patient response
                      const patientMessages = visibleMessages.filter(msg => msg.role === 'patient' && !msg.isTyping)
                      const latestPatientMessage = patientMessages[patientMessages.length - 1]
                      
                      if (latestPatientMessage) {
                        return (
                          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 h-full">
                            <div className="text-sm font-medium text-gray-700 mb-2">Saylor Lee:</div>
                            <div className={`${sizeClass} leading-relaxed text-gray-900 overflow-y-auto max-h-full`}>
                              {latestPatientMessage.content}
                            </div>
                          </div>
                        )
                      }
                      
                      return (
                        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 h-full flex items-center justify-center">
                          <div className="text-gray-500 text-center">
                            {isTranscribing || isProcessingAudio ? 
                              "Processing your message..." : 
                              "Start recording to begin the conversation"
                            }
                          </div>
                        </div>
                      )
                    })()}
                  </div>
                </div>
              )}
            </div>


            {/* Right side - Quick Actions + Notes */}
            <div className="w-[33%] p-6 bg-gradient-to-b from-gray-50 h-full">
              <div className="bg-white rounded-2xl p-6 shadow-sm ring-1 ring-gray-100 h-full flex flex-col">
                {hasQuickActions && (
                  <>
                    {/* --- Quick Actions Card (fixed height) --- */}
                    <div className="h-64 mb-4 bg-gray-50 rounded-xl p-4 border border-gray-200">
                  {rightPanelView === 'menu' && (
                    <div className="h-full flex flex-col">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h4>
                      <div className="grid gap-3 flex-1">
                        <button
                          className="h-10 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 text-sm font-medium"
                          onClick={() => setRightPanelView('checklist')}
                        >
                          Open Checklist
                        </button>
                        <button
                          className="h-10 rounded-lg bg-gray-100 text-gray-800 hover:bg-gray-200 text-sm font-medium"
                          onClick={() => setRightPanelView('references')}
                        >
                          View Reference
                        </button>
                        <button
                          className="h-10 rounded-lg bg-gray-100 text-gray-800 hover:bg-gray-200 text-sm font-medium"
                          onClick={insertTemplateNote}
                        >
                          Insert Template Note
                        </button>
                      </div>
                    </div>
                  )}

                  {rightPanelView === 'checklist' && (
                    <div className="h-full flex flex-col">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-gray-900">Checklist</h4>
                        <button
                          className="text-sm text-blue-600 hover:underline"
                          onClick={() => setRightPanelView('menu')}
                        >
                          Back
                        </button>
                      </div>
                      {/* Scrollable checklist within fixed card */}
                      <div className="flex-1 overflow-y-auto pr-2">
                        <div className="space-y-2">
                          {[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15].map(n => (
                            <div key={n} className="flex items-start p-2 rounded-lg hover:bg-white transition-colors">
                              <span className="mr-2 text-gray-500">{n}.</span>
                              <span className="text-gray-700">[Item {n}]</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {rightPanelView === 'references' && (
                    <div className="h-full flex flex-col">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-gray-900">References</h4>
                        <button
                          className="text-sm text-blue-600 hover:underline"
                          onClick={() => setRightPanelView('menu')}
                        >
                          Back
                        </button>
                      </div>
                      {/* Scrollable references within fixed card */}
                      <div className="flex-1 overflow-y-auto pr-2">
                        <div className="space-y-2">
                          {[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15].map(n => (
                            <div key={n} className="p-3 rounded-lg ring-1 ring-gray-200 bg-white hover:bg-gray-50 transition-colors">
                              <div className="font-medium text-gray-900">Reference {n}</div>
                              <div className="text-sm text-gray-600 mt-1">Description for reference {n}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                    {/* --- Notes area (bottom) --- */}
                    <div className="flex-1 flex flex-col">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">Consultation Notes</h4>
                        <span className="text-sm text-gray-500">Auto-saving...</span>
                      </div>

                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Enter your consultation notes here..."
                        className={`w-full flex-1 min-h-[200px] rounded-lg bg-gray-50 p-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${sizeClass}`}
                      />
                    </div>
                  </>
                )}
                {!hasQuickActions && (
                  /* Fallback: Notes-only panel when no quick actions */
                  <div className="flex-1 flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-gray-900">Consultation Notes</h4>
                      <span className="text-sm text-gray-500">Auto-saving...</span>
                    </div>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Enter your consultation notes here..."
                      className={`w-full h-[calc(100%-4rem)] rounded-lg bg-gray-50 p-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${sizeClass}`}
                    />
                  </div>
                )}
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
            onClick={() => openModal(setShowRestartModal)}
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-full shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Restart Consultation
          </button>

          <button
            onClick={() => openModal(setShowSubmitModal)}
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
          onClose={() => { setShowSubmitModal(false); resumeTimerIfStarted(); }}
          onConfirm={handleSubmitConsultation}
          title="Submit Consultation"
          message="Are you sure you want to submit this consultation? This action cannot be undone."
          confirmText="Submit"
          confirmStyle="primary"
          isLoading={isSubmitting}
        />

        <ConfirmationModal
          isOpen={showRestartModal}
          onClose={() => { setShowRestartModal(false); resumeTimerIfStarted(); }}
          onConfirm={handleRestartConsultation}
          title="Restart Consultation"
          message="Are you sure you want to restart? All current progress will be lost."
          confirmText="Restart"
          confirmStyle="warning"
        />


      </div>
    </div>
  )
}
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface HistoryItem {
  conversation_id: string
  title: string
  updated_at: number
  message_count: number
  status: string
}

interface ConversationDetail extends HistoryItem {
  messages: Array<{
    role: string
    content: string
    timestamp: number
  }>
  evaluation?: {
    scores: Record<string, number>
    weighted_total: number
    out_of: number
  }
}

export default function HistoryPage() {
  const navigate = useNavigate()
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([])
  const [selectedConversation, setSelectedConversation] = useState<ConversationDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/conversations`, { withCredentials: true })
      setHistoryItems(res.data.items || [])
      setError(null)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to load history')
    }
  }

  const openConversation = async (id: string) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/conversations/${id}`, { withCredentials: true })
      setSelectedConversation(res.data)
      setError(null)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to load conversation')
    }
  }

  const deleteConversation = async (id: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/conversations/${id}`, { withCredentials: true })
      if (selectedConversation?.conversation_id === id) {
        setSelectedConversation(null)
      }
      await loadHistory()
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to delete conversation')
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Consultation History</h1>
          <div className="flex gap-4">
            <button
              onClick={loadHistory}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
            >
              Refresh
            </button>
            <button
              onClick={() => navigate('/practice')}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              New Consultation
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* History List */}
          <div className="bg-white rounded-lg shadow-md p-4 h-[calc(100vh-12rem)] overflow-y-auto">
            {historyItems.length === 0 ? (
              <p className="text-gray-500">No consultations yet.</p>
            ) : (
              historyItems.map(item => (
                <div
                  key={item.conversation_id}
                  className={`mb-4 p-4 rounded-lg border cursor-pointer transition-colors ${
                    selectedConversation?.conversation_id === item.conversation_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                  onClick={() => openConversation(item.conversation_id)}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold">{item.title}</h3>
                      <p className="text-sm text-gray-500">
                        Updated: {new Date(item.updated_at * 1000).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-500">
                        Messages: {item.message_count} • Status: {item.status}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteConversation(item.conversation_id)
                      }}
                      className="text-red-500 hover:text-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Conversation Detail */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-4 h-[calc(100vh-12rem)] overflow-y-auto">
            {!selectedConversation ? (
              <p className="text-gray-500">Select a consultation to view details.</p>
            ) : (
              <>
                <div className="mb-6">
                  <h2 className="text-xl font-bold mb-2">{selectedConversation.title}</h2>
                  <p className="text-sm text-gray-500">
                    Updated: {new Date(selectedConversation.updated_at * 1000).toLocaleString()}
                  </p>
                </div>

                {selectedConversation.evaluation && (
                  <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                    <h3 className="font-semibold mb-2">Evaluation Summary</h3>
                    <div className="flex justify-between items-center mb-2">
                      <span>Overall Score</span>
                      <span className="font-bold">
                        {selectedConversation.evaluation.weighted_total} /{' '}
                        {selectedConversation.evaluation.out_of}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(selectedConversation.evaluation.scores).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                          <span>{value}/5</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {selectedConversation.messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg ${
                        msg.role === 'doctor'
                          ? 'bg-blue-500 text-white ml-auto max-w-[80%]'
                          : 'bg-gray-100 mr-auto max-w-[80%]'
                      }`}
                    >
                      <p>{msg.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {new Date(msg.timestamp * 1000).toLocaleTimeString()}
                      </p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}

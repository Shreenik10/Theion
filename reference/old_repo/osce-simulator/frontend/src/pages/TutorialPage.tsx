import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import ConfirmationModal from '../components/ConfirmationModal'

const TutorialPage: React.FC = () => {
  const [videoError, setVideoError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showSubmitModal, setShowSubmitModal] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const navigate = useNavigate()

  const handleVideoLoad = () => {
    setIsLoading(false)
    setVideoError(null)
  }

  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    setIsLoading(false)
    const target = e.target as HTMLVideoElement
    setVideoError(`Video failed to load: ${target.error?.message || 'Unknown error'}`)
    console.error('Video error:', target.error)
  }

  const handleVideoCanPlay = () => {
    setIsLoading(false)
  }

  const handleSubmitTutorial = async () => {
    try {
      // Simulate successful submission
      await new Promise(resolve => setTimeout(resolve, 500))
      setShowSubmitModal(false)
      navigate('/tutorial-evaluation')
    } catch (err: any) {
      console.error('Failed to submit tutorial:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName="John Doe" />
      <div className="flex items-center justify-center p-8">
        <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Welcome to Theia OSCE Simulator
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Experience our interactive medical simulation platform designed to enhance your clinical skills through realistic patient encounters.
          </p>
        </div>

        {/* Video Container */}
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden mb-8">
          <div className="aspect-video bg-gray-900 flex items-center justify-center relative">
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                <div className="text-white text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                  <p>Loading video...</p>
                </div>
              </div>
            )}
            
            {videoError && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                <div className="text-white text-center p-8">
                  <div className="text-6xl mb-4">🎥</div>
                  <h3 className="text-xl font-semibold mb-2">Video Unavailable</h3>
                  <p className="text-gray-300 mb-4">{videoError}</p>
                  <div className="bg-gray-800 rounded-lg p-4 text-sm text-gray-300">
                    <p className="mb-2">Troubleshooting:</p>
                    <ul className="text-left space-y-1">
                      <li>• Check if Tutorial.mov exists in /public/videos/</li>
                      <li>• Ensure video format is supported by your browser</li>
                      <li>• Try refreshing the page</li>
                      <li>• Check browser console for errors</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            <video
              ref={videoRef}
              className="w-full h-full object-cover"
              controls
              preload="metadata"
              onLoadStart={() => setIsLoading(true)}
              onCanPlay={handleVideoCanPlay}
              onLoadedData={handleVideoLoad}
              onError={handleVideoError}
              onLoad={() => setIsLoading(false)}
            >
              <source src="/videos/Tutorial.mov" type="video/quicktime" />
              <source src="/videos/Tutorial.mp4" type="video/mp4" />
              <source src="/videos/Tutorial.webm" type="video/webm" />
              <source src="/videos/Tutorial.mov" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        </div>



        {/* Description */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            About Theia
          </h2>
          <div className="prose prose-lg text-gray-600 max-w-none">
            <p className="mb-4">
              Theia is an advanced OSCE (Objective Structured Clinical Examination) simulator that provides medical students and healthcare professionals with realistic, interactive patient scenarios. Our platform combines cutting-edge AI technology with proven educational methodologies to create an immersive learning experience.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6 mt-6">
              <div className="bg-blue-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-2">
                  🎯 Realistic Scenarios
                </h3>
                <p className="text-blue-700">
                  Practice with authentic patient cases that mirror real clinical encounters, helping you develop confidence and competence.
                </p>
              </div>
              
              <div className="bg-green-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-800 mb-2">
                  📊 Detailed Feedback
                </h3>
                <p className="text-green-700">
                  Receive comprehensive evaluations with specific areas for improvement and personalized learning recommendations.
                </p>
              </div>
              
              <div className="bg-purple-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-purple-800 mb-2">
                  🔄 Adaptive Learning
                </h3>
                <p className="text-purple-700">
                  Our AI adapts to your learning style and progress, providing tailored scenarios that challenge and support your development.
                </p>
              </div>
              
              <div className="bg-orange-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-orange-800 mb-2">
                  📈 Progress Tracking
                </h3>
                <p className="text-orange-700">
                  Monitor your improvement over time with detailed analytics and performance metrics across different clinical domains.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center mt-8">
          <button
            onClick={() => setShowSubmitModal(true)}
            className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-3" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Submit Tutorial
          </button>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500">
          <p className="text-sm">
            Theia OSCE Simulator • Empowering the next generation of healthcare professionals
          </p>
        </div>
      </div>
      </div>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        onConfirm={handleSubmitTutorial}
        title="Submit Tutorial"
        message="Are you sure you want to submit this tutorial? This will take you to your evaluation results."
        confirmText="Submit"
        confirmStyle="primary"
      />
    </div>
  )
}

export default TutorialPage

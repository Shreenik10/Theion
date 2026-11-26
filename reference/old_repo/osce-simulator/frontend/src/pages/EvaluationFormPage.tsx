import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import Header from '../components/Header'

interface EvaluationItem {
  id: string
  category: string
  description: string
  maxPoints: number
  bulletPoints: string[]
  bulletPointsPoints: number[]
}

const EvaluationFormPage: React.FC = () => {
  const navigate = useNavigate()
  
  // Scroll to top when component mounts
  React.useEffect(() => {
    window.scrollTo(0, 0)
  }, [])
  
  const [evaluationItems, setEvaluationItems] = useState<EvaluationItem[]>([
    {
      id: "1",
      category: "Introduction & Collaboration",
      description: "The student introduced themselves, explained the purpose of the interview, and obtained consent appropriately.",
      maxPoints: 5,
      bulletPoints: [
        "Introduced themselves by name and role",
        "Explained purpose of interview",
        "Obtained verbal consent",
        "Maintained professional demeanor"
      ],
      bulletPointsPoints: [2, 1, 1, 1]
    },
    {
      id: "2",
      category: "Biographical Data",
      description: "The student accurately gathered identifying information such as name, age, gender, and preferred pronouns.",
      maxPoints: 5,
      bulletPoints: [
        "Asked for patient's full name",
        "Inquired about age",
        "Asked about gender identity",
        "Respected preferred pronouns",
        "Verified contact information"
      ],
      bulletPointsPoints: [1, 1, 1, 1, 1]
    },
    {
      id: "3",
      category: "Past Medical History",
      description: "The student asked about at least seven general health items and included at least one question related to sexual health.",
      maxPoints: 5,
      bulletPoints: [
        "Asked about chronic conditions",
        "Inquired about previous surgeries",
        "Asked about hospitalizations",
        "Included sexual health questions",
        "Asked about mental health history"
      ],
      bulletPointsPoints: [1, 1, 1, 1, 1]
    }
  ])

  const handleItemChange = (id: string, field: keyof EvaluationItem, value: any) => {
    setEvaluationItems(items => 
      items.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    )
  }

  const handleBulletPointPointsChange = (itemId: string, bulletIndex: number, value: number) => {
    setEvaluationItems(items =>
      items.map(item =>
        item.id === itemId
          ? {
              ...item,
              bulletPointsPoints: item.bulletPointsPoints.map((points, index) =>
                index === bulletIndex ? Math.max(0, value) : points
              )
            }
          : item
      )
    )
  }

  const addEvaluationItem = () => {
    const newId = String(evaluationItems.length + 1)
    setEvaluationItems([...evaluationItems, {
      id: newId,
      category: "",
      description: "",
      maxPoints: 5,
      bulletPoints: [""],
      bulletPointsPoints: [1]
    }])
  }

  const removeEvaluationItem = (id: string) => {
    if (evaluationItems.length > 3) {
      setEvaluationItems(evaluationItems.filter(item => item.id !== id))
    }
  }

  const addBulletPoint = (itemId: string) => {
    setEvaluationItems(items =>
      items.map(item =>
        item.id === itemId
          ? { 
              ...item, 
              bulletPoints: [...item.bulletPoints, ""],
              bulletPointsPoints: [...item.bulletPointsPoints, 1]
            }
          : item
      )
    )
  }

  const removeBulletPoint = (itemId: string, bulletIndex: number) => {
    setEvaluationItems(items =>
      items.map(item =>
        item.id === itemId
          ? { 
              ...item, 
              bulletPoints: item.bulletPoints.filter((_, index) => index !== bulletIndex),
              bulletPointsPoints: item.bulletPointsPoints.filter((_, index) => index !== bulletIndex)
            }
          : item
      )
    )
  }

  const handleBulletPointChange = (itemId: string, bulletIndex: number, value: string) => {
    setEvaluationItems(items =>
      items.map(item =>
        item.id === itemId
          ? {
              ...item,
              bulletPoints: item.bulletPoints.map((bullet, index) =>
                index === bulletIndex ? value : bullet
              )
            }
          : item
      )
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Check if bullet points points add up to max points for each item
    const validationErrors: string[] = []
    
    evaluationItems.forEach((item, index) => {
      const bulletPointsSum = item.bulletPointsPoints.reduce((sum, points) => sum + points, 0)
      if (bulletPointsSum !== item.maxPoints) {
        validationErrors.push(`Item ${index + 1} (${item.category}): Bullet points sum (${bulletPointsSum}) doesn't match max points (${item.maxPoints})`)
      }
    })
    
    if (validationErrors.length > 0) {
      alert("Please fix the following validation errors:\n\n" + validationErrors.join("\n"))
      return
    }
    
    console.log("Evaluation form data:", evaluationItems)
    // Here you would typically save the evaluation form data
    // For now, navigate back to form page
    navigate('/form')
  }

  const totalMaxPoints = evaluationItems.reduce((sum, item) => sum + item.maxPoints, 0)
  const totalBulletPoints = evaluationItems.reduce((sum, item) => 
    sum + item.bulletPointsPoints.reduce((bulletSum, points) => bulletSum + points, 0), 0
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName="John Doe" />
      <div className="py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden ring-1 ring-gray-100">
            <div className="p-6 sm:p-8">
              <div className="mb-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-semibold text-gray-900">Create Evaluation Form</h2>
                  <button
                    onClick={() => navigate('/form')}
                    className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 bg-blue-50 hover:bg-blue-100 rounded-lg transition-all duration-200"
                  >
                    Back to Form
                  </button>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <h3 className="text-lg font-medium text-blue-900 mb-2">Evaluation Guidelines</h3>
                  <ul className="text-sm text-blue-800 space-y-2">
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span><strong>Categories:</strong> Main evaluation areas (e.g., "Introduction & Collaboration", "Past Medical History")</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span><strong>Bullet Points:</strong> Specific criteria that students must meet to earn points</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span><strong>Points System:</strong> Each bullet point has its own point value that must add up to the total max points</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span><strong>Validation:</strong> The sum of all bullet point values must equal the maximum points for each category</span>
                    </li>
                  </ul>
                </div>
                <p className="mt-4 text-sm text-gray-600">
                  Create evaluation criteria with categories, subcategories, and specific bullet points with associated points.
                </p>
              </div>

              {/* Summary Card */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 mb-8 border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Evaluation Summary</h3>
                    <p className="text-sm text-gray-600">Total points and validation overview</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">{totalBulletPoints}/{totalMaxPoints}</div>
                    <div className={`text-sm ${totalBulletPoints === totalMaxPoints ? 'text-green-600' : 'text-red-600'}`}>
                      {totalBulletPoints === totalMaxPoints ? '✓ Valid' : '✗ Invalid'}
                    </div>
                  </div>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-8">
                {evaluationItems.map((item, index) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="bg-gray-50 rounded-xl p-6 relative"
                  >
                    <div className="absolute top-4 right-4 text-sm font-medium text-gray-500">
                      Item {index + 1}
                    </div>
                    
                    <div className="grid grid-cols-1 gap-6">
                      {/* Category and Max Points */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor={`category-${item.id}`} className="block text-sm font-medium text-gray-700 mb-2">
                            Category
                          </label>
                          <input
                            id={`category-${item.id}`}
                            type="text"
                            value={item.category}
                            onChange={(e) => handleItemChange(item.id, "category", e.target.value)}
                            className="w-full rounded-lg border-0 bg-white px-4 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                            placeholder="e.g., Introduction & Collaboration"
                          />
                        </div>
                        <div>
                          <label htmlFor={`maxPoints-${item.id}`} className="block text-sm font-medium text-gray-700 mb-2">
                            Maximum Points
                          </label>
                          <input
                            id={`maxPoints-${item.id}`}
                            type="number"
                            min="1"
                            value={item.maxPoints}
                            onChange={(e) => handleItemChange(item.id, "maxPoints", parseInt(e.target.value) || 5)}
                            className="w-full rounded-lg border-0 bg-white px-4 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                          />
                        </div>
                      </div>

                      {/* Description */}
                      <div>
                        <label htmlFor={`description-${item.id}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Description
                        </label>
                        <textarea
                          id={`description-${item.id}`}
                          value={item.description}
                          onChange={(e) => handleItemChange(item.id, "description", e.target.value)}
                          className="w-full rounded-lg border-0 bg-white px-4 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 resize-none"
                          rows={2}
                          placeholder="Describe the evaluation criteria..."
                        />
                      </div>



                      {/* Bullet Points */}
                      <div>
                        <div className="flex items-center justify-between mb-4">
                          <label className="block text-sm font-medium text-gray-700">
                            Bullet Points
                          </label>
                          <button
                            type="button"
                            onClick={() => addBulletPoint(item.id)}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                            </svg>
                            Add Point
                          </button>
                        </div>
                        <div className="space-y-3">
                          {item.bulletPoints.map((bullet, bulletIndex) => (
                            <div key={bulletIndex} className="flex items-center space-x-3">
                              <input
                                type="number"
                                min="0"
                                value={item.bulletPointsPoints[bulletIndex]}
                                onChange={(e) => handleBulletPointPointsChange(item.id, bulletIndex, parseInt(e.target.value) || 0)}
                                className="w-20 rounded-lg border-0 bg-white px-3 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 text-center"
                                placeholder="0"
                              />
                              <input
                                type="text"
                                value={bullet}
                                onChange={(e) => handleBulletPointChange(item.id, bulletIndex, e.target.value)}
                                className="flex-1 rounded-lg border-0 bg-white px-4 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                placeholder="e.g., Introduced themselves by name and role"
                              />
                              {item.bulletPoints.length > 1 && (
                                <button
                                  type="button"
                                  onClick={() => removeBulletPoint(item.id, bulletIndex)}
                                  className="text-red-500 hover:text-red-700 transition-colors"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                  </svg>
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                        {/* Validation indicator for this item */}
                        <div className="mt-3">
                          {(() => {
                            const bulletPointsSum = item.bulletPointsPoints.reduce((sum, points) => sum + points, 0)
                            const isValid = bulletPointsSum === item.maxPoints
                            return (
                              <div className={`text-sm ${isValid ? 'text-green-600' : 'text-red-600'} flex items-center`}>
                                <span className="mr-2">{isValid ? '✓' : '✗'}</span>
                                <span>
                                  Bullet points sum: {bulletPointsSum} / {item.maxPoints} points
                                  {!isValid && ` (${item.maxPoints - bulletPointsSum} points ${bulletPointsSum < item.maxPoints ? 'missing' : 'too many'})`}
                                </span>
                              </div>
                            )
                          })()}
                        </div>
                      </div>
                    </div>

                    {evaluationItems.length > 3 && (
                      <button
                        type="button"
                        onClick={() => removeEvaluationItem(item.id)}
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
                    onClick={addEvaluationItem}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                    </svg>
                    Add Evaluation Item
                  </motion.button>

                  <motion.button
                    type="submit"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Save Evaluation Form
                  </motion.button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EvaluationFormPage

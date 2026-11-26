import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'


interface Practice {
 id: string
 title: string
 description: string
 difficulty: 'Beginner' | 'Intermediate' | 'Advanced'
 duration: string
 category: string
 completed: boolean
 attempts: number
}


const mockPractices: Practice[] = [
 {
   id: 'tutorial',
   title: 'Sample Zava Smith VR Case',
   description: 'Learn the basics with this guided tutorial. Practice interviewing a patient experiencing chest pain.',
   difficulty: 'Beginner',
   duration: '15 mins',
   category: 'Patient Interview',
   completed: false,
   attempts: 0
 },
 {
   id: 'saylor-lee',
   title: 'Saylor Lee Case',
   description: 'Practice patient interaction with Saylor Lee, focusing on communication skills and medical history taking.',
   difficulty: 'Intermediate',
   duration: '20 mins',
   category: 'Patient Interview',
   completed: false,
   attempts: 0
 },
 {
   id: 'er-part-1',
   title: 'ER Case - Part 1',
   description: 'Initial assessment and triage in an emergency room setting.',
   difficulty: 'Beginner',
   duration: '15 mins',
   category: 'Emergency Care',
   completed: false,
   attempts: 0
 },
 {
   id: 'er-part-2',
   title: 'ER Case - Part 2',
   description: 'Diagnostic decision making and immediate interventions in emergency scenarios.',
   difficulty: 'Intermediate',
   duration: '25 mins',
   category: 'Emergency Care',
   completed: false,
   attempts: 0
 },
 {
   id: 'er-part-3',
   title: 'ER Case - Part 3',
   description: 'Complex emergency case management and team coordination.',
   difficulty: 'Advanced',
   duration: '30 mins',
   category: 'Emergency Care',
   completed: false,
   attempts: 0
 },
 {
   id: 'er-part-4',
   title: 'ER Case - Part 4',
   description: 'Critical care management and advanced emergency procedures.',
   difficulty: 'Advanced',
   duration: '35 mins',
   category: 'Emergency Care',
   completed: false,
   attempts: 0
 }
]

type Difficulty = 'Beginner' | 'Intermediate' | 'Advanced'

const difficultyColors: Record<Difficulty, string> = {
  Beginner: 'text-green-700 bg-green-50 ring-1 ring-green-600/15',
  Intermediate: 'text-yellow-800 bg-yellow-50 ring-1 ring-yellow-700/15',
  Advanced: 'text-red-700 bg-red-50 ring-1 ring-red-600/15'
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const difficultyDot: Record<Difficulty, string> = {
  Beginner: 'bg-green-500',
  Intermediate: 'bg-yellow-500',
  Advanced: 'bg-red-500'
}

// Category badge: compact, high-clarity icons with soft color
const CategoryBadge = ({
  category,
  // choose 'pill' or 'stethoscope' for Patient Interview
  patientIcon = 'pill'
}: { category: string; patientIcon?: 'pill' | 'stethoscope' }) => {
  // colors: subtle background + readable foreground
  const style =
    category === 'Emergency Care'
      ? { bg: 'bg-rose-50', ring: 'ring-rose-100', text: 'text-rose-600', glyph: '🚨', label: 'Emergency Care' }
      : category === 'Patient Interview'
      ? {
          bg: 'bg-sky-50',
          ring: 'ring-sky-100',
          text: 'text-sky-600',
          glyph: patientIcon === 'stethoscope' ? '🩺' : '💊',
          label: 'Patient Interview'
        }
      : { bg: 'bg-blue-50', ring: 'ring-blue-100', text: 'text-blue-600', glyph: '📋', label: category }

  return (
    <span
      className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md ${style.bg} ${style.text} ring-1 ${style.ring}`}
      aria-label={style.label}
      title={style.label}
    >
      <span aria-hidden="true" className="text-[13px] leading-none">{style.glyph}</span>
    </span>
  )
}

export default function PracticePage() {
 const navigate = useNavigate()
 const [practices, setPractices] = useState<Practice[]>(mockPractices)
 const [selectedCategory, setSelectedCategory] = useState('All Categories')
 const [selectedDifficulty, setSelectedDifficulty] = useState('All Difficulties')
 const [searchQuery, setSearchQuery] = useState('')

 useEffect(() => {
   // In the future, fetch from backend
   const fetchPractices = async () => {
     try {
       const response = await axios.get(`${API_BASE_URL}/api/practices`, { withCredentials: true })
       setPractices(response.data)
     } catch (error) {
       console.log('Using mock data')
       setPractices(mockPractices)
     }
   }
   fetchPractices()
 }, [])

 const filteredPractices = practices.filter(practice => {
   const matchesCategory = selectedCategory === 'All Categories' || practice.category === selectedCategory
   const matchesDifficulty = selectedDifficulty === 'All Difficulties' || practice.difficulty === selectedDifficulty
   const matchesSearch = practice.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        practice.description.toLowerCase().includes(searchQuery.toLowerCase())
   return matchesCategory && matchesDifficulty && matchesSearch
 })

 const uniqueCategories = Array.from(new Set(practices.map(p => p.category)))
 const ORDERED: Difficulty[] = ['Beginner', 'Intermediate', 'Advanced']
 const presentDifficulties = new Set(practices.map(p => p.difficulty as Difficulty))
 const difficultiesToShow: Difficulty[] = ORDERED.filter(d => presentDifficulties.has(d))

 return (
   <div className="min-h-screen bg-gray-50">
     {/* Header section */}
     <div className="bg-white shadow">
       <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
         <motion.div
           initial={{ opacity: 0, y: -20 }}
           animate={{ opacity: 1, y: 0 }}
           transition={{ duration: 0.5 }}
           className="text-center"
         >
           <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
             Available Practice Cases
           </h1>
           <p className="mt-4 text-lg text-gray-600">
             Select a case to practice your clinical skills and decision making
           </p>
         </motion.div>
       </div>
     </div>

     {/* Filters */}
     <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
       <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0 sm:space-x-4">
         <div className="flex space-x-4">
           <select
             value={selectedCategory}
             onChange={(e) => setSelectedCategory(e.target.value)}
             className="rounded-lg border-0 py-2 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-blue-600 text-sm"
           >
             <option>All Categories</option>
             {uniqueCategories.map(category => (
               <option key={category}>{category}</option>
             ))}
           </select>
           <select
             value={selectedDifficulty}
             onChange={(e) => setSelectedDifficulty(e.target.value)}
             className="rounded-lg border-0 py-2 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-blue-600 text-sm"
           >
              <option>All Difficulties</option>
              {difficultiesToShow.map((d) => (
                <option key={d}>{d}</option>
              ))}
           </select>
         </div>
         <div className="relative w-full sm:w-auto">
           <input
             type="text"
             placeholder="Search cases..."
             value={searchQuery}
             onChange={(e) => setSearchQuery(e.target.value)}
             className="block w-full rounded-lg border-0 py-2 pl-10 pr-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-blue-600 text-sm"
           />
           <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
             <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
               <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
             </svg>
           </div>
         </div>
       </div>
     </div>

     {/* Cases grid */}
     <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
       <motion.div
         initial={{ opacity: 0, y: 20 }}
         animate={{ opacity: 1, y: 0 }}
         transition={{ duration: 0.5 }}
         className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
       >
         {filteredPractices.map((practice) => (
           <div
             key={practice.id}
             role="button"
             tabIndex={0}
             onClick={() => navigate(practice.id === 'tutorial' ? '/tutorial' : `/consultation/${practice.id}`)}
             onKeyDown={(e) => {
               if (e.key === 'Enter' || e.key === ' ') {
                 e.preventDefault()
                 navigate(practice.id === 'tutorial' ? '/tutorial' : `/consultation/${practice.id}`)
               }
             }}
           className={`rounded-xl ring-1 shadow-sm
                      transition-shadow duration-200 hover:shadow-md
                      cursor-pointer outline-none
                      transform-gpu transition-transform
                      hover:-translate-y-0.5 hover:scale-[1.01]
                      focus-visible:-translate-y-0.5 focus-visible:scale-[1.01]
                      focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2
                      hover:ring-gray-300
                      ${practice.id === 'tutorial' 
                        ? 'bg-gradient-to-br from-blue-50 to-indigo-100 ring-blue-200 hover:ring-blue-300' 
                        : 'bg-gradient-to-br from-white to-blue-50/30 ring-gray-200 hover:ring-gray-300'
                      }`}
         >
             <div className="p-6">
               <div className="flex items-start justify-between">
                <div className="flex items-start gap-2">
                  {/* Change patientIcon to 'stethoscope' if you prefer 🩺 */}
                  <CategoryBadge category={practice.category} patientIcon="pill" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {practice.title}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">{practice.category}</p>
                    {practice.id === 'tutorial' && (
                      <span className="mt-1 inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-600/10">
                        🎓 Tutorial
                      </span>
                    )}
                  </div>
                </div>
                 <div className="flex flex-col items-end">
                 <span
                    className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${difficultyColors[practice.difficulty]}`}
                  >
                    <span className={`mr-1.5 inline-block h-2 w-2 rounded-full ${difficultyDot[practice.difficulty]}`} />
                    {practice.difficulty}
                  </span>
                   {practice.completed && (
                     <span className="mt-2 inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-green-600/10">
                       Completed
                     </span>
                   )}
                 </div>
               </div>
              
               <p className="mt-4 text-sm text-gray-600 line-clamp-2">
                 {practice.description}
               </p>

               <div className="mt-6 flex items-center justify-between">
                 <div className="flex items-center space-x-4 text-sm text-gray-500">
                   <span className="inline-flex items-center">
                     <svg className="mr-1.5 h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                       <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                     </svg>
                     {practice.duration}
                   </span>
                   <span>
                     {practice.attempts} attempt{practice.attempts !== 1 ? 's' : ''}
                   </span>
                 </div>
               </div>

               <div className="mt-6">
               <button
                 onClick={(e) => { e.stopPropagation(); navigate(practice.id === 'tutorial' ? '/tutorial' : `/consultation/${practice.id}`) }}
                 className={`block w-full rounded-lg px-4 py-2.5 text-center text-sm font-semibold text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2
                   ${practice.id === 'tutorial' 
                     ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 focus:ring-blue-600' 
                     : 'bg-blue-600 hover:bg-blue-500 focus:ring-blue-600'
                   }`}
                 aria-label={`Start ${practice.title}`}
               >
                 {practice.id === 'tutorial' ? 'Start Tutorial' : 'Start Case'}
               </button>
               </div>
             </div>
           </div>
         ))}
       </motion.div>
     </div>
   </div>
 )
}
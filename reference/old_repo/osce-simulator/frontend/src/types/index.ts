export type Difficulty = 'simple' | 'medium' | 'hard'
export type PersonalityTrait = 'Shy' | 'Anxious' | 'Talkative' | 'Cooperative' | 'Defensive' | 'Friendly' | 'Reserved'
export type Gender = 'male' | 'female'

export interface PatientConfig {
  difficulty: Difficulty
  personalityTraits: PersonalityTrait[]
  gender: Gender
  age: number
}

export interface Message {
  role: 'patient' | 'doctor'
  content: string
  timestamp: string
}

export interface ConsultationMessage extends Message {
  isTyping?: boolean
  session_id?: string
}

export interface ChatSession {
  id: string
  messages: Message[]
  patientConfig: PatientConfig
}

export interface Evaluation {
  history_taking_score: number
  communication_score: number
  clinical_reasoning_score: number
  professionalism_score: number
  time_efficiency_score: number
  feedback: string
}
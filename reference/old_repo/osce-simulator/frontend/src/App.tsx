import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import ConsultationPage from './pages/ConsultationPage'
import EvaluationPage from './pages/EvaluationPage'
import HistoryPage from './pages/HistoryPage'
import PracticePage from './pages/PracticePage'
import DashboardPage from './pages/DashboardPage'
import EvaluationsPage from './pages/EvaluationsPage'
import TutorialPage from './pages/TutorialPage'
import TutorialEvaluationPage from './pages/TutorialEvaluationPage'
import FormPage from './pages/FormPage'
import EvaluationFormPage from './pages/EvaluationFormPage'
import Header from './components/Header'

// Layout wrapper for authenticated pages
const AuthenticatedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName="John Doe" />
      <main>{children}</main>
    </div>
  )
}

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Routes>
        <Route path="/" element={<Navigate to="/auth/login" replace />} />
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/dashboard" element={
          <AuthenticatedLayout>
            <DashboardPage />
          </AuthenticatedLayout>
        } />
        <Route path="/practice" element={
          <AuthenticatedLayout>
            <PracticePage />
          </AuthenticatedLayout>
        } />
        <Route path="/evaluations" element={
          <AuthenticatedLayout>
            <EvaluationsPage />
          </AuthenticatedLayout>
        } />
        <Route path="/consultation/:id" element={
          <AuthenticatedLayout>
            <ConsultationPage />
          </AuthenticatedLayout>
        } />
        <Route path="/evaluation/:id" element={
          <AuthenticatedLayout>
            <EvaluationPage />
          </AuthenticatedLayout>
        } />
        <Route path="/history" element={
          <AuthenticatedLayout>
            <HistoryPage />
          </AuthenticatedLayout>
        } />
        <Route path="/tutorial" element={<TutorialPage />} />
        <Route path="/tutorial-evaluation" element={<TutorialEvaluationPage />} />
        <Route path="/form" element={<FormPage />} />
        <Route path="/evaluation-form" element={<EvaluationFormPage />} />
      </Routes>
    </div>
  )
}

export default App
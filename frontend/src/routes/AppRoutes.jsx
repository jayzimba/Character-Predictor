import { Route, Routes } from 'react-router-dom'
import DashboardLayout from '../layouts/DashboardLayout'
import PublicLayout from '../layouts/PublicLayout'
import AboutPage from '../pages/public/AboutPage'
import HomePage from '../pages/public/HomePage'
import LoginPage from '../pages/public/LoginPage'
import PersonalityTypesPage from '../pages/public/PersonalityTypesPage'
import RegisterPage from '../pages/public/RegisterPage'
import SetupStatusPage from '../pages/public/SetupStatusPage'
import AdminDashboardPage from '../pages/admin/AdminDashboardPage'
import AnalyticsPage from '../pages/admin/AnalyticsPage'
import AuditLogsPage from '../pages/admin/AuditLogsPage'
import AssessmentsPage from '../pages/admin/AssessmentsPage'
import DatasetPage from '../pages/admin/DatasetPage'
import ModelTrainingPage from '../pages/admin/ModelTrainingPage'
import ModelsPage from '../pages/admin/ModelsPage'
import QuestionsPage from '../pages/admin/QuestionsPage'
import UsersPage from '../pages/admin/UsersPage'
import AssessmentHistoryPage from '../pages/user/AssessmentHistoryPage'
import AssessmentPage from '../pages/user/AssessmentPage'
import AssessmentResultPage from '../pages/user/AssessmentResultPage'
import DashboardPage from '../pages/user/DashboardPage'
import ProfilePage from '../pages/user/ProfilePage'
import GuestRoute from './GuestRoute'
import ProtectedRoute from './ProtectedRoute'

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<HomePage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="personality-types" element={<PersonalityTypesPage />} />
        <Route path="dev" element={<SetupStatusPage />} />
        <Route element={<GuestRoute />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="app" element={<DashboardLayout variant="user" />}>
          <Route index element={<DashboardPage />} />
          <Route path="assessment" element={<AssessmentPage />} />
          <Route path="results" element={<AssessmentResultPage />} />
          <Route path="history" element={<AssessmentHistoryPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={['ADMIN']} />}>
        <Route path="admin" element={<DashboardLayout variant="admin" />}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="questions" element={<QuestionsPage />} />
          <Route path="assessments" element={<AssessmentsPage />} />
          <Route path="models" element={<ModelsPage />} />
          <Route path="dataset" element={<DatasetPage />} />
          <Route path="training" element={<ModelTrainingPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="audit" element={<AuditLogsPage />} />
        </Route>
      </Route>
    </Routes>
  )
}

import apiClient from './client'

export function fetchActiveQuestionnaire() {
  return apiClient.get('/questions')
}

export function fetchAdminQuestions() {
  return apiClient.get('/admin/questions')
}

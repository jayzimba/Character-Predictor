import apiClient from './client'

export function fetchActiveQuestionnaire() {
  return apiClient.get('/questions')
}

export function fetchAdminQuestions() {
  return apiClient.get('/admin/questions')
}

export function fetchQuestionOptions() {
  return apiClient.get('/admin/questions/options')
}

export function createAdminQuestion(payload) {
  return apiClient.post('/admin/questions', payload)
}

export function updateAdminQuestion(questionId, payload) {
  return apiClient.patch(`/admin/questions/${questionId}`, payload)
}

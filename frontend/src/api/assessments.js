import apiClient from './client'

export function startAssessment() {
  return apiClient.post('/assessments', { consent_accepted: true })
}

export function listAssessments() {
  return apiClient.get('/assessments')
}

export function fetchAssessment(id) {
  return apiClient.get(`/assessments/${id}`)
}

export function saveAnswers(id, answers) {
  return apiClient.post(`/assessments/${id}/answers`, { answers })
}

export function submitAssessment(id) {
  return apiClient.post(`/assessments/${id}/submit`)
}

import apiClient from './client'

export function classifyAssessment(assessmentId) {
  return apiClient.post('/predictions/classify', { assessment_id: assessmentId })
}

export function fetchPrediction(assessmentId) {
  return apiClient.get(`/predictions/${assessmentId}`)
}

import apiClient from './client'

export function fetchLatestResult() {
  return apiClient.get('/results/latest')
}

export function fetchResult(assessmentId) {
  return apiClient.get(`/results/${assessmentId}`)
}

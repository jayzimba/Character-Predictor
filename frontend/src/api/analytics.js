import apiClient from './client'

export function fetchAnalytics() {
  return apiClient.get('/analytics')
}

import apiClient from './client'

export function fetchHistory() {
  return apiClient.get('/history')
}

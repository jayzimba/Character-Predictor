import apiClient from './client'

export function fetchDashboard() {
  return apiClient.get('/users/me/dashboard')
}

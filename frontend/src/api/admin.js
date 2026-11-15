import apiClient from './client'

export function fetchAdminOverview() {
  return apiClient.get('/admin/overview')
}

export function fetchAdminUsers() {
  return apiClient.get('/admin/users')
}

export function fetchAdminAssessments() {
  return apiClient.get('/admin/assessments')
}

export function fetchAuditLogs() {
  return apiClient.get('/admin/audit-logs')
}

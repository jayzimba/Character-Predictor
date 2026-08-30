import apiClient from './client'

export function fetchDemoDataset() {
  return apiClient.get('/admin/datasets/demo')
}

export function validateDemoDataset() {
  return apiClient.post('/admin/datasets/demo/validate')
}

export function validateUploadedDataset(file) {
  const body = new FormData()
  body.append('file', file)
  return apiClient.post('/admin/datasets/validate', body, { timeout: 30000 })
}

export function previewCollectedAssessments() {
  return apiClient.post('/admin/datasets/from-assessments')
}

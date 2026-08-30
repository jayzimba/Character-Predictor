import apiClient from './client'

export function fetchModelRegistry() {
  return apiClient.get('/admin/models')
}

export function fetchLastEvaluation() {
  return apiClient.get('/admin/models/evaluation')
}

export function evaluateDemoModels() {
  return apiClient.post('/admin/models/evaluate/demo', null, { timeout: 60000 })
}

export function evaluateUploadedModels(file) {
  const body = new FormData()
  body.append('file', file)
  return apiClient.post('/admin/models/evaluate', body, { timeout: 60000 })
}

export function activateModel(modelId) {
  return apiClient.post(`/admin/models/${modelId}/activate`)
}

export function activateSelectedModel() {
  return apiClient.post('/admin/models/activate-selected')
}

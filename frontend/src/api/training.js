import apiClient from './client'

export function fetchLastTrainingRun() {
  return apiClient.get('/admin/models/training')
}

export function trainDemoModels() {
  return apiClient.post('/admin/models/train/demo', null, { timeout: 60000 })
}

export function trainUploadedModels(file) {
  const body = new FormData()
  body.append('file', file)
  return apiClient.post('/admin/models/train', body, { timeout: 60000 })
}

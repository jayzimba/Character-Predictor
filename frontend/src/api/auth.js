import apiClient from './client'

export function registerAccount(payload) {
  return apiClient.post('/auth/register', payload)
}

export function login(email, password) {
  return apiClient.post('/auth/login', { email, password })
}

export function fetchCurrentUser() {
  return apiClient.get('/auth/me')
}

export function updateProfile(payload) {
  return apiClient.patch('/users/me', payload)
}

export function changePassword(payload) {
  return apiClient.post('/users/me/password', payload)
}

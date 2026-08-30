import axios from 'axios'
import { getAccessToken } from '../utils/storage'

/**
 * Shared HTTP client.
 * In development, Vite proxies `/api` to FastAPI (see vite.config.js).
 * If a JWT is stored, it is attached here — the server still authorises.
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

export default apiClient

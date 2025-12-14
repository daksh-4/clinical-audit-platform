import axios from 'axios'

// Development (incl. Docker): always use relative URL so the Vite dev-server proxy handles it.
// Production: you may set VITE_API_URL to a full base URL (including /api/v1) if desired.
const API_BASE_URL = import.meta.env.PROD ? (import.meta.env.VITE_API_URL || '/api/v1') : '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  register: (data: { email: string; full_name: string; password: string }) =>
    api.post('/auth/register', data),
  
  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  
  getCurrentUser: () => api.get('/auth/me'),
}

// Audit API
export const auditApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/audits', { params }),
  
  get: (auditId: string) => api.get(`/audits/${auditId}`),
  
  create: (data: any) => api.post('/audits', data),
  
  update: (auditId: string, data: any) =>
    api.patch(`/audits/${auditId}`, data),
  
  delete: (auditId: string) => api.delete(`/audits/${auditId}`),
}

// Questionnaire API
export const questionnaireApi = {
  list: (auditId: string) => api.get(`/questionnaires/${auditId}/questionnaires`),
  
  get: (auditId: string, version: number) =>
    api.get(`/questionnaires/${auditId}/questionnaires/${version}`),
  
  create: (auditId: string, data: any) =>
    api.post(`/questionnaires/${auditId}/questionnaires`, data),
}

// Episode API
export const episodeApi = {
  list: (auditId: string, params?: { skip?: number; limit?: number }) =>
    api.get(`/episodes/${auditId}/episodes`, { params }),
  
  get: (auditId: string, episodeId: string) =>
    api.get(`/episodes/${auditId}/episodes/${episodeId}`),
  
  submit: (auditId: string, siteId: string, data: any) =>
    api.post(`/episodes/${auditId}/episodes?site_id=${siteId}`, data),
}

export default api

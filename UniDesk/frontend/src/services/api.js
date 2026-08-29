import axios from 'axios'

const TOKEN_KEY = 'unidesk_token'
const UNAUTHORIZED_EVENT = 'unidesk:unauthorized'

const api = axios.create({
  // Configurable for deployment. Unset (local dev / tests) keeps the original
  // localhost default; the demo image builds with VITE_API_BASE_URL=/api/v1
  // so the SPA calls the same origin that serves it.
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only clear/notify once per session expiry: once the token is gone,
      // further 401s from requests already in flight are no-ops, which
      // keeps a burst of failed requests from causing repeated redirects.
      const hadToken = localStorage.getItem(TOKEN_KEY) !== null
      if (hadToken) {
        localStorage.removeItem(TOKEN_KEY)
        window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
      }
    }
    return Promise.reject(error)
  },
)

export default api
export { TOKEN_KEY, UNAUTHORIZED_EVENT }

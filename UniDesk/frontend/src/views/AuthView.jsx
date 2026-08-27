import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const EMPTY_REGISTER_FORM = { name: '', email: '', password: '', role: 'employee' }

export default function AuthView({ initialTab = 'login' }) {
  const [tab, setTab] = useState(initialTab)
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [registerForm, setRegisterForm] = useState(EMPTY_REGISTER_FORM)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function switchTab(nextTab) {
    setTab(nextTab)
    setError('')
    setSuccessMessage('')
  }

  async function handleLoginSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(loginForm.email, loginForm.password)
      const redirectTo = location.state?.from?.pathname ?? '/dashboard'
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(
        err.response?.data?.detail ?? 'Login failed. Please check your credentials.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  async function handleRegisterSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccessMessage('')
    setSubmitting(true)
    try {
      await register(registerForm)
      setSuccessMessage('Registration successful! You can now log in.')
      setRegisterForm(EMPTY_REGISTER_FORM)
      setTab('login')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Registration failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="mb-6 text-center text-2xl font-semibold text-gray-900">UniDesk</h1>

        <div className="mb-6 flex rounded-lg bg-gray-100 p-1">
          <button
            type="button"
            onClick={() => switchTab('login')}
            className={`flex-1 rounded-md py-1.5 text-sm font-medium transition ${
              tab === 'login' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => switchTab('register')}
            className={`flex-1 rounded-md py-1.5 text-sm font-medium transition ${
              tab === 'register' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`}
          >
            Sign Up
          </button>
        </div>

        {error && (
          <p className="mb-4 rounded-md bg-red-50 p-2 text-sm text-red-600">{error}</p>
        )}
        {successMessage && (
          <p className="mb-4 rounded-md bg-green-50 p-2 text-sm text-green-600">
            {successMessage}
          </p>
        )}

        {tab === 'login' ? (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                required
                value={loginForm.email}
                onChange={(event) =>
                  setLoginForm({ ...loginForm, email: event.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                required
                value={loginForm.password}
                onChange={(event) =>
                  setLoginForm({ ...loginForm, password: event.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-md bg-indigo-600 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {submitting ? 'Logging in...' : 'Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <p className="rounded-md bg-amber-50 p-2 text-xs text-amber-700">
              Registration is only available to pre-approved company personnel. Your
              official name and company email must exactly match your entry in company
              records, or registration will be denied.
            </p>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Full Name
              </label>
              <input
                type="text"
                required
                value={registerForm.name}
                onChange={(event) =>
                  setRegisterForm({ ...registerForm, name: event.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Company Email
              </label>
              <input
                type="email"
                required
                value={registerForm.email}
                onChange={(event) =>
                  setRegisterForm({ ...registerForm, email: event.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={registerForm.password}
                onChange={(event) =>
                  setRegisterForm({ ...registerForm, password: event.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              />
              <p className="mt-1 text-xs text-gray-400">
                Minimum 8 characters, with at least one number and one uppercase letter.
              </p>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Role</label>
              <select
                value={registerForm.role}
                onChange={(event) =>
                  setRegisterForm({ ...registerForm, role: event.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              >
                <option value="employee">Employee</option>
                <option value="support_agent">Support Agent</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-md bg-indigo-600 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {submitting ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

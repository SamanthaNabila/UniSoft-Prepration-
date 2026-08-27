import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Navbar from '../components/common/Navbar'
import api from '../services/api'

export default function CreateTicketView() {
  const { id } = useParams()
  const isEditMode = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState({ title: '', description: '', priority: 'medium' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [isLoading, setIsLoading] = useState(isEditMode)

  useEffect(() => {
    if (!isEditMode) return
    api
      .get(`/tickets/${id}`)
      .then((response) => {
        setForm({
          title: response.data.title,
          description: response.data.description,
          priority: response.data.priority,
        })
      })
      .catch(() => setError('Failed to load ticket.'))
      .finally(() => setIsLoading(false))
  }, [id, isEditMode])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    const title = form.title.trim()
    const description = form.description.trim()

    if (title.length < 5 || title.length > 200) {
      setError('Title must be between 5 and 200 characters.')
      return
    }
    if (description.length < 10) {
      setError('Description must be at least 10 characters.')
      return
    }

    setSubmitting(true)
    try {
      if (isEditMode) {
        await api.put(`/tickets/${id}`, { title, description })
        navigate(`/tickets/${id}`)
      } else {
        const response = await api.post('/tickets', {
          title,
          description,
          priority: form.priority,
        })
        navigate(`/tickets/${response.data.id}`)
      }
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to save ticket.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-xl px-4 py-6">
        <h1 className="mb-4 text-xl font-semibold text-gray-900">
          {isEditMode ? 'Edit Ticket' : 'Create New Ticket'}
        </h1>

        {isLoading ? (
          <p className="text-sm text-gray-400">Loading...</p>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="space-y-4 rounded-lg border border-gray-200 bg-white p-6"
          >
            {error && (
              <p className="rounded-md bg-red-50 p-2 text-sm text-red-600">{error}</p>
            )}
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Title
              </label>
              <input
                type="text"
                value={form.title}
                onChange={(event) => setForm({ ...form, title: event.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              />
              <p className="mt-1 text-xs text-gray-400">5-200 characters.</p>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                rows={5}
                value={form.description}
                onChange={(event) =>
                  setForm({ ...form, description: event.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              />
              <p className="mt-1 text-xs text-gray-400">Minimum 10 characters.</p>
            </div>
            {!isEditMode && (
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Priority
                </label>
                <select
                  value={form.priority}
                  onChange={(event) =>
                    setForm({ ...form, priority: event.target.value })
                  }
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            )}
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-md bg-indigo-600 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {submitting ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Ticket'}
            </button>
          </form>
        )}
      </main>
    </div>
  )
}

import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Navbar from '../components/common/Navbar'
import StatusBadge from '../components/common/StatusBadge'
import AgentControls from '../components/tickets/AgentControls'
import CommentForm from '../components/tickets/CommentForm'
import CommentThread from '../components/tickets/CommentThread'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

export default function TicketDetailView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [ticket, setTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const loadTicket = useCallback(() => {
    return Promise.all([
      api.get(`/tickets/${id}`),
      api.get(`/tickets/${id}/comments`),
    ]).then(([ticketRes, commentsRes]) => {
      setTicket(ticketRes.data)
      setComments(commentsRes.data)
    })
  }, [id])

  useEffect(() => {
    setIsLoading(true)
    setError('')
    loadTicket()
      .catch(() => setError('Ticket not found.'))
      .finally(() => setIsLoading(false))
  }, [loadTicket])

  async function handleStatusUpdate(payload) {
    const response = await api.patch(`/tickets/${id}/status`, payload)
    setTicket(response.data)
  }

  async function handleAddComment(content) {
    const response = await api.post(`/tickets/${id}/comments`, { content })
    setComments((prev) => [...prev, response.data])
  }

  async function handleDelete() {
    if (!window.confirm('Delete this ticket? This cannot be undone.')) return
    await api.delete(`/tickets/${id}`)
    navigate('/dashboard')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <p className="p-6 text-sm text-gray-400">Loading...</p>
      </div>
    )
  }

  if (error || !ticket) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <p className="p-6 text-sm text-red-600">{error || 'Ticket not found.'}</p>
      </div>
    )
  }

  const isOwner = user.role === 'employee' && ticket.created_by === user.id
  const isAgent = user.role === 'support_agent'
  const canComment = isAgent || isOwner

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-3xl space-y-6 px-4 py-6">
        <Link to="/dashboard" className="text-sm text-indigo-600 hover:underline">
          &larr; Back to dashboard
        </Link>

        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <h1 className="text-xl font-semibold text-gray-900">{ticket.title}</h1>
            <div className="flex gap-2">
              <StatusBadge type="status" value={ticket.status} />
              <StatusBadge type="priority" value={ticket.priority} />
            </div>
          </div>
          <p className="mt-3 whitespace-pre-wrap text-sm text-gray-700">
            {ticket.description}
          </p>
          <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-xs text-gray-400">
            <span>
              Created by {ticket.created_by_name} on{' '}
              {new Date(ticket.created_at).toLocaleString()}
            </span>
            {isOwner && (
              <div className="flex gap-3">
                <Link
                  to={`/tickets/${ticket.id}/edit`}
                  className="font-medium text-indigo-600 hover:underline"
                >
                  Edit
                </Link>
                <button
                  type="button"
                  onClick={handleDelete}
                  className="font-medium text-red-600 hover:underline"
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>

        {isAgent && <AgentControls ticket={ticket} onUpdate={handleStatusUpdate} />}

        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="mb-4 text-sm font-semibold text-gray-900">Comments</h2>
          <CommentThread comments={comments} />
          <div className="mt-4">
            <CommentForm
              onSubmit={handleAddComment}
              disabled={!canComment}
              disabledMessage="Only the ticket owner and support agents can comment on this ticket."
            />
          </div>
        </div>
      </main>
    </div>
  )
}

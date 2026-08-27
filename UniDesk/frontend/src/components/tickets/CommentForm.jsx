import { useState } from 'react'

export default function CommentForm({ onSubmit, disabled, disabledMessage }) {
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    if (!content.trim()) return

    setSubmitting(true)
    setError('')
    try {
      await onSubmit(content.trim())
      setContent('')
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to post comment.')
    } finally {
      setSubmitting(false)
    }
  }

  if (disabled) {
    return (
      <p className="rounded-md bg-gray-50 p-3 text-sm text-gray-400">
        {disabledMessage ?? 'You cannot comment on this ticket.'}
      </p>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <textarea
        value={content}
        onChange={(event) => setContent(event.target.value)}
        rows={3}
        maxLength={2000}
        placeholder="Add a comment..."
        className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-indigo-500 focus:outline-none"
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={submitting || !content.trim()}
        className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {submitting ? 'Posting...' : 'Post Comment'}
      </button>
    </form>
  )
}

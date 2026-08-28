import { useState } from 'react'

export default function AssignmentControls({ ticket, currentUserId, onAssign, onRelease }) {
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const isAssignedToMe = ticket.assigned_to === currentUserId

  async function handleAssignToMe() {
    setSaving(true)
    setError('')
    try {
      await onAssign(currentUserId)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to assign ticket.')
    } finally {
      setSaving(false)
    }
  }

  async function handleRelease() {
    setSaving(true)
    setError('')
    try {
      await onRelease()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to release assignment.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-900">Assignment</h3>
      <p className="mb-3 text-sm text-gray-600">
        {ticket.assigned_to ? (
          <>
            Assigned to{' '}
            <span className="font-medium text-gray-900">{ticket.assigned_to_name}</span>
          </>
        ) : (
          'Unassigned'
        )}
      </p>
      <div className="flex flex-wrap gap-2">
        {!isAssignedToMe && (
          <button
            type="button"
            onClick={handleAssignToMe}
            disabled={saving}
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {ticket.assigned_to ? 'Take Over' : 'Assign to Me'}
          </button>
        )}
        {ticket.assigned_to !== null && (
          <button
            type="button"
            onClick={handleRelease}
            disabled={saving}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Release Assignment
          </button>
        )}
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  )
}

import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <Link to="/dashboard" className="text-lg font-semibold text-gray-900">
          UniDesk
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          {user?.role === 'employee' && (
            <Link
              to="/tickets/new"
              className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
            >
              + Create Ticket
            </Link>
          )}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>{user?.name}</span>
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700">
              {user?.role === 'support_agent' ? 'Support Agent' : 'Employee'}
            </span>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="text-sm font-medium text-gray-500 hover:text-gray-800"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

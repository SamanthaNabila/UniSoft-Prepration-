import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectionRoute from './components/common/ProtectionRoute'
import AuthView from './views/AuthView'
import CreateTicketView from './views/CreateTicketView'
import DashboardView from './views/DashboardView'
import TicketDetailView from './views/TicketDetailView'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthView initialTab="login" />} />
      <Route path="/register" element={<AuthView initialTab="register" />} />
      <Route
        path="/dashboard"
        element={
          <ProtectionRoute>
            <DashboardView />
          </ProtectionRoute>
        }
      />
      <Route
        path="/tickets/new"
        element={
          <ProtectionRoute allowedRoles={['employee']}>
            <CreateTicketView />
          </ProtectionRoute>
        }
      />
      <Route
        path="/tickets/:id/edit"
        element={
          <ProtectionRoute allowedRoles={['employee']}>
            <CreateTicketView />
          </ProtectionRoute>
        }
      />
      <Route
        path="/tickets/:id"
        element={
          <ProtectionRoute>
            <TicketDetailView />
          </ProtectionRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App

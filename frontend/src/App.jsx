import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import AddJob from './pages/AddJob'
import JobDetail from './pages/JobDetail'
import Layout from './components/Layout'

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('access_token')
  return token ? <Layout>{children}</Layout> : <Navigate to="/login" />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/jobs/new" element={<PrivateRoute><AddJob /></PrivateRoute>} />
        <Route path="/jobs/:id" element={<PrivateRoute><JobDetail /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
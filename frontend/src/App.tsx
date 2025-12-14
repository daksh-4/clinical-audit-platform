import { lazy } from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'

const Home = lazy(() => import('./pages/Home'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const AuditList = lazy(() => import('./pages/AuditList'))
const AuditBuilder = lazy(() => import('./pages/AuditBuilder'))
const DataEntry = lazy(() => import('./pages/DataEntry'))
const Analytics = lazy(() => import('./pages/Analytics'))
const Library = lazy(() => import('./pages/Library'))

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="audits" element={<AuditList />} />
        <Route path="audits/new" element={<AuditBuilder />} />
        <Route path="audits/:auditId/edit" element={<AuditBuilder />} />
        <Route path="audits/:auditId/data-entry" element={<DataEntry />} />
        <Route path="audits/:auditId/analytics" element={<Analytics />} />
        <Route path="library" element={<Library />} />
      </Route>
    </Routes>
  )
}

export default App

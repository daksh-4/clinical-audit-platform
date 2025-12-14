import { Suspense, useEffect, useState } from 'react'
import { Outlet, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { authApi } from '../services/api'
import LoadingSpinner from './LoadingSpinner'
import PageSkeleton from './PageSkeleton'

export default function Layout() {
  const user = useAuthStore((state) => state.user)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const setAuth = useAuthStore((state) => state.setAuth)
  const logout = useAuthStore((state) => state.logout)

  const [authLoading, setAuthLoading] = useState(false)

  // If a token exists but store state is missing (e.g. after refresh), hydrate the user.
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return
    if (isAuthenticated && user) return

    let cancelled = false
    setAuthLoading(true)

    authApi
      .getCurrentUser()
      .then((res) => {
        if (cancelled) return
        setAuth(res.data, token)
      })
      .catch(() => {
        if (cancelled) return
        logout()
      })
      .finally(() => {
        if (cancelled) return
        setAuthLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [isAuthenticated, user, setAuth, logout])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-nhs-blue text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-xl font-bold">
                Clinical Audit Platform
              </Link>
              
              {isAuthenticated && (
                <div className="ml-10 flex items-baseline space-x-4">
                  <Link to="/dashboard" className="hover:bg-nhs-darkBlue px-3 py-2 rounded-md">
                    Dashboard
                  </Link>
                  <Link to="/audits" className="hover:bg-nhs-darkBlue px-3 py-2 rounded-md">
                    My Audits
                  </Link>
                  <Link to="/library" className="hover:bg-nhs-darkBlue px-3 py-2 rounded-md">
                    Library
                  </Link>
                </div>
              )}
            </div>
            
            <div className="flex items-center">
              {authLoading ? (
                <div className="flex items-center space-x-2 text-sm">
                  <LoadingSpinner className="text-white" label="Loading session" />
                  <span>Loading…</span>
                </div>
              ) : isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <span className="text-sm">{user?.full_name}</span>
                  <button
                    onClick={logout}
                    className="btn btn-secondary px-4 py-2"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="space-x-4">
                  <Link to="/login" className="btn btn-secondary px-4 py-2">
                    Login
                  </Link>
                  <Link to="/register" className="btn btn-primary px-4 py-2">
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Suspense fallback={<PageSkeleton />}>
          <Outlet />
        </Suspense>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">About</h3>
              <p className="text-gray-300 text-sm">
                Open infrastructure for clinician-led clinical audits
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-sm">
                <li><Link to="/docs" className="text-gray-300 hover:text-white">Documentation</Link></li>
                <li><Link to="/library" className="text-gray-300 hover:text-white">Audit Library</Link></li>
                <li><Link to="/support" className="text-gray-300 hover:text-white">Support</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><Link to="/privacy" className="text-gray-300 hover:text-white">Privacy Policy</Link></li>
                <li><Link to="/terms" className="text-gray-300 hover:text-white">Terms of Service</Link></li>
                <li><Link to="/data-protection" className="text-gray-300 hover:text-white">Data Protection</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-700 text-center text-sm text-gray-300">
            © 2025 Clinical Audit Platform. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

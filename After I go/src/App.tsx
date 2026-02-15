import React, { Suspense, lazy, useEffect, useState } from 'react'
import { Routes, Route, Navigate, useSearchParams, BrowserRouter } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { ToastProvider } from './components/ui/Toast'
import { AppShell } from './components/layout/AppShell'

// Lazy load pages for code splitting
const Landing = lazy(() => import('./pages/Landing'))
const Setup = lazy(() => import('./pages/Setup'))
const Vault = lazy(() => import('./pages/Vault'))
const Messages = lazy(() => import('./pages/Messages'))
const Wishes = lazy(() => import('./pages/Wishes'))
const FinancialMap = lazy(() => import('./pages/FinancialMap'))
const Shares = lazy(() => import('./pages/Shares'))
const Security = lazy(() => import('./pages/Security'))
const EthicalWill = lazy(() => import('./pages/EthicalWill'))
const PlatformLegacy = lazy(() => import('./pages/PlatformLegacy'))
const Export = lazy(() => import('./pages/Export'))
const Settings = lazy(() => import('./pages/Settings'))
const RecipientMode = lazy(() => import('./pages/RecipientMode'))

// Loading fallback
const Loading: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-warmGray-50 dark:bg-warmGray-900">
    <div className="text-center">
      <div className="w-12 h-12 border-4 border-sage border-t-transparent rounded-full animate-spin mx-auto mb-4" />
      <p className="text-warmGray-500">Loading...</p>
    </div>
  </div>
)

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, checkIsFirstTime } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [isSetupNeeded, setIsSetupNeeded] = useState(false)

  useEffect(() => {
    const check = async () => {
      const firstTime = await checkIsFirstTime()
      setIsSetupNeeded(firstTime)
      setLoading(false)
    }
    check()
  }, [checkIsFirstTime])

  if (loading) {
    return <Loading />
  }

  if (isSetupNeeded && window.location.pathname !== '/setup') {
    return <Navigate to="/setup" replace />
  }

  if (!isAuthenticated && !isSetupNeeded) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

// Public route wrapper (redirects to dashboard if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore()

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

// Recipient mode route (no auth required)
const RecipientRoute: React.FC = () => {
  const [searchParams] = useSearchParams()
  const shareId = searchParams.get('share')

  if (!shareId) {
    return <Navigate to="/" replace />
  }

  return <RecipientMode />
}

const App: React.FC = () => {
  return (
    <ToastProvider>
      <Suspense fallback={<Loading />}>
        <Routes>
          {/* Public routes */}
          <Route
            path="/"
            element={
              <PublicRoute>
                <Landing />
              </PublicRoute>
            }
          />

          {/* Setup wizard */}
          <Route
            path="/setup"
            element={
              <ProtectedRoute>
                <Setup />
              </ProtectedRoute>
            }
          />

          {/* Protected routes */}
          <Route element={<AppShell />}>
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Vault />
                </ProtectedRoute>
              }
            />
            <Route
              path="/vault"
              element={
                <ProtectedRoute>
                  <Vault />
                </ProtectedRoute>
              }
            />
            <Route
              path="/messages"
              element={
                <ProtectedRoute>
                  <Messages />
                </ProtectedRoute>
              }
            />
            <Route
              path="/wishes"
              element={
                <ProtectedRoute>
                  <Wishes />
                </ProtectedRoute>
              }
            />
            <Route
              path="/financial"
              element={
                <ProtectedRoute>
                  <FinancialMap />
                </ProtectedRoute>
              }
            />
            <Route
              path="/shares"
              element={
                <ProtectedRoute>
                  <Shares />
                </ProtectedRoute>
              }
            />
            <Route
              path="/security"
              element={
                <ProtectedRoute>
                  <Security />
                </ProtectedRoute>
              }
            />
            <Route
              path="/ethical-will"
              element={
                <ProtectedRoute>
                  <EthicalWill />
                </ProtectedRoute>
              }
            />
            <Route
              path="/platforms"
              element={
                <ProtectedRoute>
                  <PlatformLegacy />
                </ProtectedRoute>
              }
            />
            <Route
              path="/export"
              element={
                <ProtectedRoute>
                  <Export />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Recipient mode */}
          <Route path="/unlock" element={<RecipientRoute />} />

          {/* 404 */}
          <Route
            path="*"
            element={
              <div className="min-h-screen flex items-center justify-center bg-warmGray-50 dark:bg-warmGray-900">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-warmGray-900 dark:text-warmGray-100 mb-4">
                    404
                  </h1>
                  <p className="text-warmGray-600 dark:text-warmGray-400 mb-6">
                    The page you're looking for doesn't exist.
                  </p>
                  <a
                    href="/"
                    className="text-sage hover:underline"
                  >
                    Return home
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </Suspense>
    </ToastProvider>
  )
}

export default App

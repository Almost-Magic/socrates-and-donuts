import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'

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

function App() {
  return (
    <Suspense fallback={<div style={{color:'white',padding:'40px'}}>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/setup" element={<Setup />} />
        <Route path="/vault" element={<Vault />} />
        <Route path="/messages" element={<Messages />} />
        <Route path="/wishes" element={<Wishes />} />
        <Route path="/financial" element={<FinancialMap />} />
        <Route path="/shares" element={<Shares />} />
        <Route path="/security" element={<Security />} />
        <Route path="/ethical-will" element={<EthicalWill />} />
        <Route path="/platform-legacy" element={<PlatformLegacy />} />
        <Route path="/export" element={<Export />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/recipient" element={<RecipientMode />} />
      </Routes>
    </Suspense>
  )
}
export default App

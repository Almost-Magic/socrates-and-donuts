import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

// Request persistent storage on load
if (navigator.storage && navigator.storage.persist) {
  navigator.storage.persist().then(persisted => {
    console.log(`Storage persistence: ${persisted}`)
  })
}

// Register service worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/afterigo/sw.js').catch(error => {
      console.log('Service worker registration failed:', error)
    })
  })
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter basename="/afterigo">
      <App />
    </BrowserRouter>
  </React.StrictMode>
)

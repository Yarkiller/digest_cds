import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { armFailNextSignIn, resetAuthHarness } from './services/authApi.js'
import { armFailNextMeFetch, resetMeHarness } from './services/meApi.js'

// Playwright harness (mirrors votingApi arm-fail pattern).
window.__DIGEST_AUTH_HARNESS__ = { armFailNextSignIn, resetAuthHarness }
window.__DIGEST_ME_HARNESS__ = { armFailNextMeFetch, resetMeHarness }

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

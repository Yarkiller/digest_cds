import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import {
  armFailNextSignIn,
  armFailNextSignUp,
  resetAuthHarness,
} from './services/authApi.js'
import { armFailNextMeFetch, resetMeHarness } from './services/meApi.js'
import {
  armEmptyCurrentIssue,
  armFailNextContentFetch,
  resetContentHarness,
} from './services/contentApi.js'

// Playwright harness (mirrors votingApi arm-fail pattern).
window.__DIGEST_AUTH_HARNESS__ = {
  armFailNextSignIn,
  armFailNextSignUp,
  resetAuthHarness,
}
window.__DIGEST_ME_HARNESS__ = { armFailNextMeFetch, resetMeHarness }
window.__DIGEST_CONTENT_HARNESS__ = {
  armEmptyCurrentIssue,
  armFailNextContentFetch,
  resetContentHarness,
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

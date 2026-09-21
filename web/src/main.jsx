import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import {
  armFailNextSignIn,
  armFailNextSignUp,
  resetAuthHarness,
} from './services/authApi.js'
import {
  armFailNextMeFetch,
  resetMeHarness,
  setMockMeRole,
} from './services/meApi.js'
import {
  armEmptyCurrentIssue,
  armFailNextContentFetch,
  clearFailNextContentFetch,
  resetContentHarness,
} from './services/contentApi.js'
import {
  armAlreadySentOnSend,
  armFailNextDecision,
  armFailNextPreview,
  armFailNextSend,
  armFailNextShortlistFetch,
  clearFailNextPreview,
  clearFailNextShortlistFetch,
  resetAdminHarness,
} from './services/adminApi.js'

// Playwright harness (mirrors votingApi arm-fail pattern).
window.__DIGEST_AUTH_HARNESS__ = {
  armFailNextSignIn,
  armFailNextSignUp,
  resetAuthHarness,
}
window.__DIGEST_ME_HARNESS__ = { armFailNextMeFetch, resetMeHarness, setMockMeRole }
window.__DIGEST_CONTENT_HARNESS__ = {
  armEmptyCurrentIssue,
  armFailNextContentFetch,
  clearFailNextContentFetch,
  resetContentHarness,
}
window.__DIGEST_ADMIN_HARNESS__ = {
  armFailNextShortlistFetch,
  clearFailNextShortlistFetch,
  armFailNextDecision,
  armFailNextPreview,
  clearFailNextPreview,
  armFailNextSend,
  armAlreadySentOnSend,
  resetAdminHarness,
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

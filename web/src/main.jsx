import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import {
  armFailNextSignIn,
  armFailNextSignUp,
  armOAuthEmail,
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
  getMockMarkReadyBatchCalls,
} from './services/adminApi.js'
import {
  armFailNextLoad,
  armFailNextSave,
  armRejectNextSave,
  resetPipelineConfigHarness,
} from './services/pipelineConfigApi.js'
import { initAnalytics } from './services/analyticsRuntime.js'

initAnalytics()

// Playwright harness (mirrors votingApi arm-fail pattern).
window.__DIGEST_AUTH_HARNESS__ = {
  armFailNextSignIn,
  armFailNextSignUp,
  armOAuthEmail,
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
  getMockMarkReadyBatchCalls,
}
window.__DIGEST_PIPELINE_CONFIG_HARNESS__ = {
  armFailNextLoad,
  armRejectNextSave,
  armFailNextSave,
  resetPipelineConfigHarness,
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

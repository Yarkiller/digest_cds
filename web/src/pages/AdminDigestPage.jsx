import { useEffect, useState } from 'react'
import ForbiddenPage from './ForbiddenPage.jsx'
import { fetchMe } from '../services/meApi.js'
import { getAccessToken } from '../services/authApi.js'

/**
 * Admin Digest triage shell — role gate first (D-75); triage UI expands in later tasks.
 */
export default function AdminDigestPage() {
  const [roleState, setRoleState] = useState('loading') // loading | forbidden | admin

  useEffect(() => {
    let cancelled = false
    async function loadRole() {
      try {
        const token = await getAccessToken()
        const me = await fetchMe(token)
        if (!cancelled) {
          setRoleState(me.role === 'admin' ? 'admin' : 'forbidden')
        }
      } catch {
        if (!cancelled) setRoleState('forbidden')
      }
    }
    loadRole()
    return () => {
      cancelled = true
    }
  }, [])

  if (roleState === 'loading') {
    return (
      <section aria-busy="true" data-testid="admin-role-loading">
        <p className="text-sm text-muted">Загрузка…</p>
      </section>
    )
  }

  if (roleState === 'forbidden') {
    return <ForbiddenPage />
  }

  return (
    <section data-testid="admin-digest-page">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
      <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Shortlist дайджеста</h1>
      <p className="mt-4 text-sm text-muted">Тriage UI loading…</p>
    </section>
  )
}

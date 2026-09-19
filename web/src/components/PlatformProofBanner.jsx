import { useEffect, useState } from 'react'
import ErrorPanel from './ErrorPanel.jsx'
import { getAccessToken } from '../services/authApi.js'
import { fetchMe, MeApiError, postPing } from '../services/meApi.js'

/**
 * Minimal Phase 1 FE↔API proof: GET /me identity + POST /me/ping (D-10 / PLAT-07).
 */
export default function PlatformProofBanner() {
  const [me, setMe] = useState(null)
  const [ping, setPing] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function loadMe() {
    setError(null)
    try {
      const token = await getAccessToken()
      if (!token) {
        setMe(null)
        return
      }
      const user = await fetchMe(token)
      setMe(user)
    } catch (err) {
      setMe(null)
      setError({
        message:
          err instanceof MeApiError
            ? err.message
            : 'Не удалось загрузить профиль. Проверьте сеть.',
        retryable: err instanceof MeApiError ? err.retryable : true,
      })
    }
  }

  useEffect(() => {
    loadMe()
  }, [])

  async function handlePing() {
    setBusy(true)
    setError(null)
    setPing(null)
    try {
      const token = await getAccessToken()
      const result = await postPing(token)
      setPing(result)
    } catch (err) {
      setError({
        message:
          err instanceof MeApiError
            ? err.message
            : 'Не удалось выполнить ping. Проверьте сеть.',
        retryable: err instanceof MeApiError ? err.retryable : true,
      })
    } finally {
      setBusy(false)
    }
  }

  return (
    <aside className="mb-8 rounded-xl border border-rule bg-paper-2 p-4 text-sm">
      <p className="text-xs uppercase tracking-wide text-muted">Платформенный контур</p>
      {error ? (
        <div className="mt-3 flex flex-col gap-2">
          <ErrorPanel
            title="Ошибка профиля"
            message={error.message}
            onDismiss={() => setError(null)}
          />
          {error.retryable ? (
            <button
              type="button"
              className="min-h-11 self-start rounded-full bg-accent px-4 text-accent-ink"
              onClick={() => {
                setError(null)
                loadMe()
              }}
            >
              Повторить
            </button>
          ) : null}
        </div>
      ) : null}
      <p className="mt-2 text-ink-2" data-testid="platform-me">
        {me ? (
          <>
            Вы вошли как <strong>{me.email}</strong> ({me.role})
          </>
        ) : (
          'Войдите, чтобы проверить GET /me'
        )}
      </p>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="min-h-11 rounded-full border border-rule px-4 disabled:opacity-60"
          onClick={handlePing}
          disabled={busy || !me}
        >
          Проверить ping
        </button>
        {ping ? (
          <span data-testid="platform-ping" className="text-ink-2">
            ok · id {ping.id}
          </span>
        ) : null}
      </div>
    </aside>
  )
}

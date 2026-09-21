/**
 * Razbory list API — GET /razbory (RAZB-01 / D-66 / D-67 / D-68).
 * Mock/live cutover via isMocksEnabled(); never silent mock fallback after live failure.
 * JWT via existing session headers (T-04-07).
 */
import { delay } from '../utils/delay.js'
import { getRazboryList } from '../data/mock.js'

export const RAZBOR_EDITOR_BYLINE = 'Редакция Digest CDS'

export class RazboryApiError extends Error {
  constructor(message, { code = 'RAZBORY_FAILED', retryable = true } = {}) {
    super(message)
    this.name = 'RazboryApiError'
    this.code = code
    this.retryable = retryable
  }
}

let failNextFetch = false
let emptyRazbory = false

/** Playwright/unit harness: fail next fetchRazbory once. */
export function armFailNextRazboryFetch() {
  failNextFetch = true
  if (typeof window !== 'undefined') {
    window.__DIGEST_FAIL_NEXT_RAZBORY__ = true
  }
}

export function clearFailNextRazboryFetch() {
  failNextFetch = false
  if (typeof window !== 'undefined') {
    window.__DIGEST_FAIL_NEXT_RAZBORY__ = false
  }
}

/** Playwright harness: force empty razbory list under mocks (D-69). */
export function armEmptyRazbory() {
  emptyRazbory = true
  if (typeof window !== 'undefined') {
    window.__DIGEST_EMPTY_RAZBORY__ = true
  }
}

export function resetRazboryHarness() {
  failNextFetch = false
  emptyRazbory = false
  if (typeof window !== 'undefined') {
    window.__DIGEST_FAIL_NEXT_RAZBORY__ = false
    window.__DIGEST_EMPTY_RAZBORY__ = false
  }
}

function consumeFailNext() {
  if (failNextFetch) {
    failNextFetch = false
    return true
  }
  return typeof window !== 'undefined' && window.__DIGEST_FAIL_NEXT_RAZBORY__ === true
}

function isEmptyArmed() {
  if (emptyRazbory) return true
  return typeof window !== 'undefined' && window.__DIGEST_EMPTY_RAZBORY__ === true
}

/**
 * Map announcement → «Анонс»; published has no extra overline label (D-68).
 * @param {string} status
 * @returns {string | null}
 */
export function razborStatusLabel(status) {
  if (status === 'announcement') return 'Анонс'
  return null
}

/**
 * Pure mock list → HTTP chronology DTO. Testable without Vite env.
 * @param {Array<{ id: number, title: string, meeting_at: string | null, status: string }>} catalog
 */
export function mockListRazbory(catalog) {
  return {
    items: (catalog ?? []).map((row) => ({
      id: row.id,
      title: row.title,
      meeting_at: row.meeting_at ?? null,
      status: row.status,
    })),
  }
}

/**
 * Authenticated razbory chronology list.
 * @param {string | null} [accessToken]
 */
export async function fetchRazbory(accessToken = null) {
  if (consumeFailNext()) {
    throw new RazboryApiError('Не удалось загрузить разборы. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  const { isMocksEnabled } = await import('./authEnv.js')
  if (isMocksEnabled()) {
    await delay(80)
    if (isEmptyArmed()) {
      return { items: [] }
    }
    return mockListRazbory(getRazboryList())
  }

  const { getAccessToken } = await import('./authApi.js')
  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new RazboryApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  const apiBase = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

  let response
  try {
    response = await fetch(`${apiBase}/razbory`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    throw new RazboryApiError('Не удалось загрузить разборы. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (response.status === 401) {
    throw new RazboryApiError('Сессия истекла. Войдите снова.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }

  if (!response.ok) {
    throw new RazboryApiError('Не удалось загрузить разборы. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  const body = await response.json()
  return {
    items: (body.items ?? []).map((row) => ({
      id: row.id,
      title: row.title,
      meeting_at: row.meeting_at ?? null,
      status: row.status,
    })),
  }
}

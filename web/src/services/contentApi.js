/**
 * Content API — current issue (ISSUE-01). Mock/live cutover via VITE_USE_MOCKS (D-20).
 * Never catch a live failure and return mock.js (D-21).
 */
import { getAccessToken } from './authApi.js'
import { isMocksEnabled } from './authEnv.js'
import { currentIssue, getIssueMaterials } from '../data/mock.js'

export class ContentApiError extends Error {
  constructor(message, { code = 'CONTENT_FAILED', retryable = true } = {}) {
    super(message)
    this.name = 'ContentApiError'
    this.code = code
    this.retryable = retryable
  }
}

let failNextFetch = false
let emptyCurrentIssue = false

export function armFailNextContentFetch() {
  failNextFetch = true
}

/** Playwright/unit harness: force empty current DTO under mocks (D-30). */
export function armEmptyCurrentIssue() {
  emptyCurrentIssue = true
  if (typeof window !== 'undefined') {
    window.__DIGEST_EMPTY_CURRENT_ISSUE__ = true
  }
}

export function resetContentHarness() {
  failNextFetch = false
  emptyCurrentIssue = false
  if (typeof window !== 'undefined') {
    window.__DIGEST_EMPTY_CURRENT_ISSUE__ = false
  }
}

function isEmptyCurrentArmed() {
  if (emptyCurrentIssue) return true
  return typeof window !== 'undefined' && window.__DIGEST_EMPTY_CURRENT_ISSUE__ === true
}

function apiBase() {
  return (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
}

/**
 * Map mock.js materials to API IssueItem DTO.
 * @param {ReturnType<typeof getIssueMaterials>} materials
 */
function mapMockItems(materials) {
  return materials.map((m) => ({
    slug: m.id,
    title: m.title,
    position: m.issuePosition,
    format: m.format,
    reading_minutes: m.readingMinutes,
    dek: m.dek ?? null,
  }))
}

/**
 * @returns {Promise<{
 *   number: number | null,
 *   period_label: string | null,
 *   title: string | null,
 *   editor: string | null,
 *   items: Array<{
 *     slug: string,
 *     title: string,
 *     position: number,
 *     format: string,
 *     reading_minutes: number,
 *     dek: string | null,
 *   }>
 * }>}
 */
export async function fetchCurrentIssue(accessToken) {
  if (failNextFetch) {
    failNextFetch = false
    throw new ContentApiError('Не удалось загрузить выпуск. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (isMocksEnabled()) {
    if (isEmptyCurrentArmed()) {
      return {
        number: null,
        period_label: null,
        title: null,
        editor: null,
        items: [],
      }
    }
    return {
      number: currentIssue.number,
      period_label: currentIssue.period,
      title: currentIssue.title,
      editor: currentIssue.editor,
      items: mapMockItems(getIssueMaterials()),
    }
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new ContentApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/issues/current`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    throw new ContentApiError('Не удалось загрузить выпуск. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (response.status === 401) {
    throw new ContentApiError('Сессия истекла. Войдите снова.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }
  if (!response.ok) {
    throw new ContentApiError('Не удалось загрузить выпуск. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }
  return response.json()
}

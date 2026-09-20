/**
 * Content API — current / archive / by-number (ISSUE-01 / ISSUE-04).
 * Mock/live cutover via VITE_USE_MOCKS (D-20). Never silent mock fallback (D-21).
 */
import { getAccessToken } from './authApi.js'
import { isMocksEnabled } from './authEnv.js'
import {
  currentIssue,
  getArchiveIssues,
  getIssueByNumber,
  getIssueMaterials,
} from '../data/mock.js'

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
let emptyArchive = false

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

/** Playwright harness: force empty archive list under mocks (D-30). */
export function armEmptyArchive() {
  emptyArchive = true
  if (typeof window !== 'undefined') {
    window.__DIGEST_EMPTY_ARCHIVE__ = true
  }
}

export function resetContentHarness() {
  failNextFetch = false
  emptyCurrentIssue = false
  emptyArchive = false
  if (typeof window !== 'undefined') {
    window.__DIGEST_EMPTY_CURRENT_ISSUE__ = false
    window.__DIGEST_EMPTY_ARCHIVE__ = false
  }
}

function isEmptyCurrentArmed() {
  if (emptyCurrentIssue) return true
  return typeof window !== 'undefined' && window.__DIGEST_EMPTY_CURRENT_ISSUE__ === true
}

function isEmptyArchiveArmed() {
  if (emptyArchive) return true
  return typeof window !== 'undefined' && window.__DIGEST_EMPTY_ARCHIVE__ === true
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

async function authHeaders(accessToken) {
  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new ContentApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }
  return { Authorization: `Bearer ${token}` }
}

function throwNetwork(message = 'Не удалось загрузить выпуск. Проверьте сеть.') {
  throw new ContentApiError(message, { code: 'NETWORK', retryable: true })
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
    throwNetwork()
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

  const headers = await authHeaders(accessToken)
  let response
  try {
    response = await fetch(`${apiBase()}/issues/current`, { headers })
  } catch {
    throwNetwork()
  }

  if (response.status === 401) {
    throw new ContentApiError('Сессия истекла. Войдите снова.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }
  if (!response.ok) {
    throwNetwork()
  }
  return response.json()
}

/**
 * Past published issues excluding current (D-31).
 * @returns {Promise<{ issues: Array<{ number: number, period_label: string, title: string, material_count: number }> }>}
 */
export async function fetchArchive(accessToken) {
  if (failNextFetch) {
    failNextFetch = false
    throwNetwork('Не удалось загрузить архив. Проверьте сеть.')
  }

  if (isMocksEnabled()) {
    if (isEmptyArchiveArmed()) {
      return { issues: [] }
    }
    return { issues: getArchiveIssues() }
  }

  const headers = await authHeaders(accessToken)
  let response
  try {
    response = await fetch(`${apiBase()}/archive`, { headers })
  } catch {
    throwNetwork('Не удалось загрузить архив. Проверьте сеть.')
  }

  if (response.status === 401) {
    throw new ContentApiError('Сессия истекла. Войдите снова.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }
  if (!response.ok) {
    throwNetwork('Не удалось загрузить архив. Проверьте сеть.')
  }
  return response.json()
}

/**
 * Published issue by number — HTTP 404 → NOT_FOUND (not NETWORK).
 * @param {number|string} number
 */
export async function fetchIssueByNumber(number, accessToken) {
  if (failNextFetch) {
    failNextFetch = false
    throwNetwork()
  }

  const n = Number(number)

  if (isMocksEnabled()) {
    const dto = getIssueByNumber(n)
    if (!dto) {
      throw new ContentApiError('Выпуск не найден.', {
        code: 'NOT_FOUND',
        retryable: false,
      })
    }
    return dto
  }

  const headers = await authHeaders(accessToken)
  let response
  try {
    response = await fetch(`${apiBase()}/issues/${n}`, { headers })
  } catch {
    throwNetwork()
  }

  if (response.status === 401) {
    throw new ContentApiError('Сессия истекла. Войдите снова.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }
  if (response.status === 404) {
    throw new ContentApiError('Выпуск не найден.', {
      code: 'NOT_FOUND',
      retryable: false,
    })
  }
  if (!response.ok) {
    throwNetwork()
  }
  return response.json()
}

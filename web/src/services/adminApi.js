/**
 * Admin shortlist API — GET/decision/preview/send (ADMIN-01…07).
 * Mock/live cutover via isMocksEnabled(); never silent mock fallback after live failure.
 */

import { delay } from '../utils/delay.js'
import { getAccessToken } from './authApi.js'
import { isMocksEnabled } from './authEnv.js'

export class AdminApiError extends Error {
  constructor(message, { code = 'ADMIN_FAILED', retryable = true, detail = null } = {}) {
    super(message)
    this.name = 'AdminApiError'
    this.code = code
    this.retryable = retryable
    this.detail = detail
  }
}

/** @typedef {{ material_id: number, rank: number, title: string, material_status: 'ready'|'draft', decision: 'pending'|'approved'|'rejected', score: number|null, factor_labels: string[], dek?: string }} AdminShortlistItem */
/** @typedef {{ batch_id: number|null, sent_at: string|null, week_label: string|null, items: AdminShortlistItem[] }} AdminShortlistDto */

const DEFAULT_ITEMS = /** @type {AdminShortlistItem[]} */ ([
  {
    material_id: 101,
    rank: 1,
    title: 'Building Production RAG Systems',
    material_status: 'ready',
    decision: 'pending',
    score: 0.92,
    factor_labels: ['relevance', 'freshness', 'engagement'],
    dek: 'Как быстро находить фрагменты регламентов СВА.',
  },
  {
    material_id: 102,
    rank: 2,
    title: 'Anomaly Detection in Audit Pipelines',
    material_status: 'ready',
    decision: 'pending',
    score: 0.87,
    factor_labels: ['relevance', 'freshness', 'engagement'],
    dek: 'Как замечать аномалии в аудиторских выборках.',
  },
  {
    material_id: 103,
    rank: 3,
    title: 'Prompt Engineering Patterns 2026',
    material_status: 'ready',
    decision: 'pending',
    score: 0.81,
    factor_labels: ['relevance', 'freshness'],
    dek: 'Паттерны формулировок запросов к LLM для аудита.',
  },
  {
    material_id: 104,
    rank: 4,
    title: 'SQL Dashboards for Audit Reporting',
    material_status: 'draft',
    decision: 'pending',
    score: 0.74,
    factor_labels: [],
    dek: 'Черновик витрин для ежемесячной отчётности.',
  },
  {
    material_id: 105,
    rank: 5,
    title: 'Data Quality Checks for Regulated Domains',
    material_status: 'ready',
    decision: 'pending',
    score: 0.69,
    factor_labels: ['relevance'],
    dek: 'Один фактор — обоснование недоступно.',
  },
])

/** @type {AdminShortlistDto} */
let mockBatch = {
  batch_id: 1,
  sent_at: null,
  week_label: '18–24 марта 2026',
  items: DEFAULT_ITEMS.map((item) => ({ ...item, factor_labels: [...item.factor_labels] })),
}

let failNextFetch = false
let failNextDecision = false
let failNextPreview = false
let failNextSend = false
let alreadySentOnSend = false

function useMocks() {
  return isMocksEnabled()
}

function apiBase() {
  return (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
}

function stickyFlag(name) {
  return typeof window !== 'undefined' && Boolean(window[name])
}

function cloneBatch() {
  return {
    batch_id: mockBatch.batch_id,
    sent_at: mockBatch.sent_at,
    week_label: mockBatch.week_label,
    items: mockBatch.items.map((item) => ({
      ...item,
      factor_labels: [...(item.factor_labels ?? [])],
    })),
  }
}

function resetMockItems() {
  mockBatch = {
    batch_id: 1,
    sent_at: null,
    week_label: '18–24 марта 2026',
    items: DEFAULT_ITEMS.map((item) => ({ ...item, factor_labels: [...item.factor_labels] })),
  }
}

export function armFailNextShortlistFetch() {
  failNextFetch = true
  if (typeof window !== 'undefined') {
    window.__DIGEST_ADMIN_FAIL_SHORTLIST__ = true
  }
}

export function clearFailNextShortlistFetch() {
  failNextFetch = false
  if (typeof window !== 'undefined') {
    window.__DIGEST_ADMIN_FAIL_SHORTLIST__ = false
  }
}

export function armFailNextDecision() {
  failNextDecision = true
}

export function armFailNextPreview() {
  failNextPreview = true
  if (typeof window !== 'undefined') {
    window.__DIGEST_ADMIN_FAIL_PREVIEW__ = true
  }
}

export function clearFailNextPreview() {
  failNextPreview = false
  if (typeof window !== 'undefined') {
    window.__DIGEST_ADMIN_FAIL_PREVIEW__ = false
  }
}

export function armFailNextSend() {
  failNextSend = true
}

export function armAlreadySentOnSend() {
  alreadySentOnSend = true
  if (typeof window !== 'undefined') {
    window.__DIGEST_ADMIN_ALREADY_SENT__ = true
  }
}

export function resetAdminHarness() {
  failNextFetch = false
  failNextDecision = false
  failNextPreview = false
  failNextSend = false
  alreadySentOnSend = false
  resetMockItems()
  if (typeof window !== 'undefined') {
    window.__DIGEST_ADMIN_EMPTY__ = false
    window.__DIGEST_ADMIN_FAIL_SHORTLIST__ = false
    window.__DIGEST_ADMIN_FAIL_PREVIEW__ = false
    window.__DIGEST_ADMIN_ALREADY_SENT__ = false
  }
}

function shouldFailFetch() {
  if (failNextFetch || stickyFlag('__DIGEST_ADMIN_FAIL_SHORTLIST__')) {
    failNextFetch = false
    return true
  }
  return false
}

function mapHttpError(response, fallbackMessage) {
  if (response.status === 403) {
    return new AdminApiError('Недостаточно прав.', { code: 'FORBIDDEN', retryable: false })
  }
  if (response.status === 409) {
    return new AdminApiError('Уже отправлено', {
      code: 'ALREADY_SENT',
      retryable: false,
    })
  }
  if (response.status === 400) {
    return new AdminApiError(fallbackMessage, { code: 'BAD_REQUEST', retryable: false })
  }
  if (response.status === 404) {
    return new AdminApiError(fallbackMessage, { code: 'NOT_FOUND', retryable: false })
  }
  return new AdminApiError(fallbackMessage, { code: 'NETWORK', retryable: true })
}

/**
 * @returns {Promise<AdminShortlistDto>}
 */
export async function fetchShortlist(accessToken) {
  if (useMocks()) {
    await delay(80)
    if (shouldFailFetch()) {
      throw new AdminApiError('Не удалось загрузить shortlist. Проверьте сеть.', {
        code: 'NETWORK',
        retryable: true,
      })
    }
    if (stickyFlag('__DIGEST_ADMIN_EMPTY__')) {
      return { batch_id: null, sent_at: null, week_label: null, items: [] }
    }
    return cloneBatch()
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new AdminApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/admin/shortlist`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    throw new AdminApiError('Не удалось загрузить shortlist. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (!response.ok) {
    throw mapHttpError(response, 'Не удалось загрузить shortlist. Проверьте сеть.')
  }

  const body = await response.json()
  return {
    batch_id: body.batch_id ?? null,
    sent_at: body.sent_at ?? null,
    week_label: body.week_label ?? null,
    items: Array.isArray(body.items) ? body.items : [],
  }
}

/**
 * @param {number} materialId
 * @param {'pending'|'approved'|'rejected'} decision
 * @returns {Promise<AdminShortlistDto>}
 */
export async function setDecision(materialId, decision, accessToken) {
  if (useMocks()) {
    await delay(60)
    if (failNextDecision) {
      failNextDecision = false
      throw new AdminApiError('Не сохранено', { code: 'NETWORK', retryable: true })
    }
    const item = mockBatch.items.find((row) => row.material_id === materialId)
    if (!item) {
      throw new AdminApiError('Материал не найден.', { code: 'NOT_FOUND', retryable: false })
    }
    item.decision = decision
    return cloneBatch()
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new AdminApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/admin/shortlist/items/${materialId}/decision`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ decision }),
    })
  } catch {
    throw new AdminApiError('Не сохранено', { code: 'NETWORK', retryable: true })
  }

  if (!response.ok) {
    throw mapHttpError(response, 'Не сохранено')
  }

  const body = await response.json()
  return {
    batch_id: body.batch_id ?? null,
    sent_at: body.sent_at ?? null,
    week_label: body.week_label ?? null,
    items: Array.isArray(body.items) ? body.items : [],
  }
}

/**
 * @returns {Promise<{ batch_id: number, subject: string, body: string, items: Array<{ material_id: number, rank: number, title: string }> }>}
 */
export async function previewEmail(accessToken) {
  if (useMocks()) {
    await delay(80)
    if (failNextPreview || stickyFlag('__DIGEST_ADMIN_FAIL_PREVIEW__')) {
      failNextPreview = false
      throw new AdminApiError('Превью недоступно', { code: 'NETWORK', retryable: true })
    }
    const pool = mockBatch.items
      .filter((item) => item.decision === 'approved' && item.material_status === 'ready')
      .sort((a, b) => a.rank - b.rank)
    if (pool.length === 0) {
      throw new AdminApiError('Нет одобренных ready-материалов для отправки.', {
        code: 'EMPTY_SEND_POOL',
        retryable: false,
      })
    }
    return {
      batch_id: mockBatch.batch_id ?? 1,
      subject: `Digest CDS · ${mockBatch.week_label ?? 'неделя'}`,
      body: pool.map((item) => `• ${item.title}`).join('\n'),
      items: pool.map(({ material_id, rank, title }) => ({ material_id, rank, title })),
    }
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new AdminApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/admin/shortlist/preview`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: '{}',
    })
  } catch {
    throw new AdminApiError('Превью недоступно', { code: 'NETWORK', retryable: true })
  }

  if (!response.ok) {
    throw mapHttpError(response, 'Превью недоступно')
  }
  return response.json()
}

/**
 * @returns {Promise<{ batch_id: number, issue_number: number, issue_url: string, delivery_status: string, recipient_count: number, message: string }>}
 */
export async function sendDigest(accessToken) {
  if (useMocks()) {
    await delay(100)
    if (failNextSend) {
      failNextSend = false
      throw new AdminApiError('Рассылка не отправлена', { code: 'NETWORK', retryable: true })
    }
    if (alreadySentOnSend || stickyFlag('__DIGEST_ADMIN_ALREADY_SENT__') || mockBatch.sent_at) {
      alreadySentOnSend = false
      throw new AdminApiError('Уже отправлено', { code: 'ALREADY_SENT', retryable: false })
    }
    const drafts = mockBatch.items.filter(
      (item) => item.decision === 'approved' && item.material_status === 'draft',
    )
    if (drafts.length > 0) {
      throw new AdminApiError('Уберите черновики из одобренных или дождитесь ready.', {
        code: 'DRAFT_IN_SEND_POOL',
        retryable: false,
        detail: { draft_material_ids: drafts.map((d) => d.material_id) },
      })
    }
    const pool = mockBatch.items.filter(
      (item) => item.decision === 'approved' && item.material_status === 'ready',
    )
    if (pool.length === 0) {
      throw new AdminApiError('Нет одобренных ready-материалов для отправки.', {
        code: 'EMPTY_SEND_POOL',
        retryable: false,
      })
    }
    mockBatch.sent_at = new Date().toISOString()
    return {
      batch_id: mockBatch.batch_id ?? 1,
      issue_number: 15,
      issue_url: '/issues/15',
      delivery_status: 'stubbed',
      recipient_count: 0,
      message: 'Отправка записана',
    }
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new AdminApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/admin/shortlist/send`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: '{}',
    })
  } catch {
    throw new AdminApiError('Рассылка не отправлена', { code: 'NETWORK', retryable: true })
  }

  if (!response.ok) {
    throw mapHttpError(response, 'Рассылка не отправлена')
  }
  return response.json()
}

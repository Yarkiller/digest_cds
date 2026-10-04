/**
 * Pipeline config API — the sole SPA transport boundary for the admin pipeline
 * config surface (PIPE-01/PIPE-03; D-11/D-12/D-13).
 *
 * This module is the ONLY place that knows the transport: pages/components must
 * not import Supabase/SQL/storage internals (PIPE-03). Mock/live cutover via
 * isMocksEnabled(); never a silent mock fallback after a live failure.
 *
 * @typedef {{ yaml: string, updated_at: string | null }} PipelineConfigDto
 */

import { delay } from '../utils/delay.js'
import { getAccessToken } from './authApi.js'
import { isMocksEnabled } from './authEnv.js'

export class PipelineConfigError extends Error {
  constructor(message, { code = 'PIPELINE_CONFIG_FAILED', retryable = true, errors = null } = {}) {
    super(message)
    this.name = 'PipelineConfigError'
    this.code = code
    this.retryable = retryable
    this.errors = errors
  }
}

/** Mock-only seed store: survives an in-session reload, resets per browser context. */
const MOCK_STORAGE_KEY = 'digest:pipeline-config-mock'

function mocksEnabled() {
  return isMocksEnabled()
}

function apiBase() {
  return (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
}

/** @returns {PipelineConfigDto} */
function emptyDto() {
  return { yaml: '', updated_at: null }
}

/** @returns {PipelineConfigDto} */
function readMockConfig() {
  if (typeof window === 'undefined') return emptyDto()
  try {
    const raw = window.sessionStorage.getItem(MOCK_STORAGE_KEY)
    if (!raw) return emptyDto()
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed.yaml !== 'string') return emptyDto()
    return { yaml: parsed.yaml, updated_at: parsed.updated_at ?? null }
  } catch {
    return emptyDto()
  }
}

/** @returns {PipelineConfigDto} */
function writeMockConfig(yaml) {
  const dto = { yaml: String(yaml ?? ''), updated_at: new Date().toISOString() }
  if (typeof window !== 'undefined') {
    window.sessionStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(dto))
  }
  return dto
}

function mapHttpError(response, fallbackMessage, body = null) {
  if (response.status === 401) {
    return new PipelineConfigError('Требуется вход.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }
  if (response.status === 403) {
    return new PipelineConfigError('Недостаточно прав.', {
      code: 'FORBIDDEN',
      retryable: false,
    })
  }
  if (response.status === 400) {
    const errors = Array.isArray(body?.errors) ? body.errors : null
    return new PipelineConfigError('Конфиг не прошёл проверку', {
      code: 'INVALID_CONFIG',
      retryable: false,
      errors,
    })
  }
  if (response.status === 422) {
    return new PipelineConfigError('Конфиг не прошёл проверку', {
      code: 'INVALID_CONFIG',
      retryable: false,
    })
  }
  return new PipelineConfigError(fallbackMessage, { code: 'NETWORK', retryable: true })
}

/**
 * Read the saved pipeline config (empty store → { yaml: '', updated_at: null }).
 * @param {string} [accessToken]
 * @returns {Promise<PipelineConfigDto>}
 */
export async function fetchPipelineConfig(accessToken) {
  if (mocksEnabled()) {
    await delay(80)
    return readMockConfig()
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new PipelineConfigError('Требуется вход.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/admin/pipeline/config`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    throw new PipelineConfigError('Не удалось загрузить конфиг', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (!response.ok) {
    throw mapHttpError(response, 'Не удалось загрузить конфиг')
  }

  const body = await response.json()
  return {
    yaml: typeof body?.yaml === 'string' ? body.yaml : '',
    updated_at: body?.updated_at ?? null,
  }
}

/**
 * Persist the raw YAML document; the server is authoritative for validation.
 * @param {string} yaml
 * @param {string} [accessToken]
 * @returns {Promise<PipelineConfigDto>}
 */
export async function savePipelineConfig(yaml, accessToken) {
  const text = String(yaml ?? '')

  if (mocksEnabled()) {
    await delay(80)
    return writeMockConfig(text)
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new PipelineConfigError('Требуется вход.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/admin/pipeline/config`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ yaml: text }),
    })
  } catch {
    throw new PipelineConfigError('Конфиг не сохранён', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (!response.ok) {
    let body = null
    try {
      body = await response.json()
    } catch {
      body = null
    }
    throw mapHttpError(response, 'Конфиг не сохранён', body)
  }

  const body = await response.json()
  return {
    yaml: typeof body?.yaml === 'string' ? body.yaml : text,
    updated_at: body?.updated_at ?? null,
  }
}

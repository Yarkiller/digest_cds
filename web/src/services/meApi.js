import { getAccessToken, getSession } from './authApi.js'

export class MeApiError extends Error {
  constructor(message, { code = 'ME_FAILED', retryable = true } = {}) {
    super(message)
    this.name = 'MeApiError'
    this.code = code
    this.retryable = retryable
  }
}

let failNextFetch = false

export function armFailNextMeFetch() {
  failNextFetch = true
}

export function resetMeHarness() {
  failNextFetch = false
}

function useMocks() {
  return import.meta.env.VITE_USE_MOCKS !== 'false'
}

function apiBase() {
  return (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
}

/**
 * @param {string | null | undefined} accessToken
 * @returns {Promise<{ id: string, email: string, role: string }>}
 */
export async function fetchMe(accessToken) {
  if (failNextFetch) {
    failNextFetch = false
    throw new MeApiError('Не удалось загрузить профиль. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (useMocks()) {
    const session = await getSession()
    return {
      id: 'mock-user-id',
      email: session?.user?.email ?? 'analyst@sberbank.ru',
      role: 'authenticated',
    }
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new MeApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    throw new MeApiError('Не удалось загрузить профиль. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (response.status === 401) {
    throw new MeApiError('Сессия истекла. Войдите снова.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }
  if (!response.ok) {
    throw new MeApiError('Не удалось загрузить профиль. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }
  return response.json()
}

/**
 * @param {string | null | undefined} accessToken
 * @returns {Promise<{ ok: boolean, id: string }>}
 */
export async function postPing(accessToken) {
  if (failNextFetch) {
    failNextFetch = false
    throw new MeApiError('Не удалось выполнить ping. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (useMocks()) {
    return { ok: true, id: 'mock-ping-id' }
  }

  const token = accessToken ?? (await getAccessToken())
  if (!token) {
    throw new MeApiError('Требуется вход.', { code: 'UNAUTHORIZED', retryable: false })
  }

  let response
  try {
    response = await fetch(`${apiBase()}/me/ping`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: '{}',
    })
  } catch {
    throw new MeApiError('Не удалось выполнить ping. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }

  if (response.status === 401) {
    throw new MeApiError('Сессия истекла. Войдите снова.', {
      code: 'UNAUTHORIZED',
      retryable: false,
    })
  }
  if (!response.ok) {
    throw new MeApiError('Не удалось выполнить ping. Проверьте сеть.', {
      code: 'NETWORK',
      retryable: true,
    })
  }
  return response.json()
}

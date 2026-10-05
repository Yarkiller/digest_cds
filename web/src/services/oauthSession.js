/** OAuth2 (Yandex ID via Supabase) helpers — pure, node-testable. */

import { isAllowedCorporateEmail } from './emailDomain.js'

export const YANDEX_OAUTH_LABEL = 'Продолжить с Яндекс ID'

/** Supabase has no built-in Yandex provider — it must be a `custom:` OAuth2 provider. */
export const DEFAULT_YANDEX_PROVIDER = 'custom:yandex'

/**
 * Supabase provider identifier for Yandex (defaults to a custom OAuth2 provider).
 * @param {Record<string, unknown> | null | undefined} env
 * @returns {string}
 */
export function yandexProviderId(env) {
  const value = env?.VITE_YANDEX_OAUTH_PROVIDER
  return typeof value === 'string' && value.trim() ? value.trim() : DEFAULT_YANDEX_PROVIDER
}

/**
 * Whether the Yandex ID OAuth button should be offered.
 * @param {Record<string, unknown> | null | undefined} env
 * @returns {boolean}
 */
export function oauthEnabled(env) {
  return env?.VITE_ENABLE_YANDEX_OAUTH === 'true'
}

/**
 * A signed-in session is usable only when its email is on the corporate allow-list.
 * Supabase OAuth (Yandex) returns the provider email, which must still be corporate.
 * @param {{ user?: { email?: string } } | null | undefined} session
 * @param {readonly string[]} [allowedDomains]
 * @returns {boolean}
 */
export function isCorporateSession(session, allowedDomains) {
  const email = session?.user?.email
  if (typeof email !== 'string' || !email) {
    return false
  }
  return isAllowedCorporateEmail(email, allowedDomains)
}

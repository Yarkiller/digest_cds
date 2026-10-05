/**
 * Unit tests for OAuth2 session helpers (Yandex ID via Supabase).
 * Run: node --test tests/unit/test_oauth_session.js
 */
const assert = require('node:assert/strict')
const { describe, it } = require('node:test')

describe('oauthEnabled', () => {
  it('is true only when VITE_ENABLE_YANDEX_OAUTH is "true"', async () => {
    const { oauthEnabled } = await import('../../web/src/services/oauthSession.js')
    assert.equal(oauthEnabled({ VITE_ENABLE_YANDEX_OAUTH: 'true' }), true)
    assert.equal(oauthEnabled({ VITE_ENABLE_YANDEX_OAUTH: 'false' }), false)
    assert.equal(oauthEnabled({}), false)
    assert.equal(oauthEnabled(undefined), false)
  })
})

describe('isCorporateSession', () => {
  it('accepts a session whose email is a corporate domain', async () => {
    const { isCorporateSession } = await import('../../web/src/services/oauthSession.js')
    assert.equal(isCorporateSession({ user: { email: 'user@sberbank.ru' } }), true)
    assert.equal(isCorporateSession({ user: { email: 'analyst@omega.sbrf.ru' } }), true)
  })

  it('rejects OAuth sessions with a non-corporate (e.g. Yandex) email', async () => {
    const { isCorporateSession } = await import('../../web/src/services/oauthSession.js')
    assert.equal(isCorporateSession({ user: { email: 'user@yandex.ru' } }), false)
    assert.equal(isCorporateSession({ user: {} }), false)
    assert.equal(isCorporateSession(null), false)
    assert.equal(isCorporateSession(undefined), false)
  })

  it('honours a custom allow-list', async () => {
    const { isCorporateSession } = await import('../../web/src/services/oauthSession.js')
    assert.equal(isCorporateSession({ user: { email: 'user@yandex.ru' } }, ['@yandex.ru']), true)
  })
})

describe('yandexProviderId', () => {
  it('defaults to the Supabase custom provider identifier', async () => {
    const { yandexProviderId } = await import('../../web/src/services/oauthSession.js')
    assert.equal(yandexProviderId({}), 'custom:yandex')
    assert.equal(yandexProviderId(undefined), 'custom:yandex')
  })

  it('accepts an override from VITE_YANDEX_OAUTH_PROVIDER', async () => {
    const { yandexProviderId } = await import('../../web/src/services/oauthSession.js')
    assert.equal(
      yandexProviderId({ VITE_YANDEX_OAUTH_PROVIDER: 'yandex' }),
      'yandex',
    )
    assert.equal(yandexProviderId({ VITE_YANDEX_OAUTH_PROVIDER: '   ' }), 'custom:yandex')
  })
})

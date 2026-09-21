/**
 * RED→GREEN: razboryApi mock list DTO (RAZB-01 / D-66 / D-67 / D-68).
 * Run: node --test tests/unit/test_razbory_api.js
 */
const assert = require('node:assert/strict')
const { describe, it } = require('node:test')

const sampleRazbory = [
  {
    id: 2,
    title: 'RAG в корпоративной среде',
    meeting_at: '2026-04-14T10:00:00.000Z',
    status: 'announcement',
  },
  {
    id: 1,
    title: 'Vector Search с pgvector',
    meeting_at: '2026-03-03T10:00:00.000Z',
    status: 'published',
  },
]

describe('mockListRazbory', () => {
  it('returns chronology items with id/title/meeting_at/status (RAZB-01 / D-67)', async () => {
    const { mockListRazbory } = await import('../../web/src/services/razboryApi.js')
    const dto = mockListRazbory(sampleRazbory)

    assert.equal(Object.hasOwn(dto, 'items'), true)
    assert.equal(dto.items.length, 2)
    assert.deepEqual(dto.items[0], {
      id: 2,
      title: 'RAG в корпоративной среде',
      meeting_at: '2026-04-14T10:00:00.000Z',
      status: 'announcement',
    })
  })

  it('maps announcement status label to Анонс (D-68)', async () => {
    const { razborStatusLabel } = await import('../../web/src/services/razboryApi.js')
    assert.equal(razborStatusLabel('announcement'), 'Анонс')
    assert.equal(razborStatusLabel('published'), null)
  })

  it('exposes editorial byline constant (Q3 RESOLVED)', async () => {
    const { RAZBOR_EDITOR_BYLINE } = await import('../../web/src/services/razboryApi.js')
    assert.equal(RAZBOR_EDITOR_BYLINE, 'Редакция Digest CDS')
  })
})

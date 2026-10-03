/**
 * RED→GREEN: admin mark-ready mock helpers + adminApi wiring (ADUX-05 / D-07, D-08).
 * Pure module — no Vite/supabase imports (node --test friendly).
 * Run: node --test tests/unit/test_admin_mark_ready.js
 */
const assert = require('node:assert/strict')
const { describe, it } = require('node:test')
const fs = require('node:fs')
const path = require('node:path')

function seedItems() {
  return [
    {
      material_id: 101,
      material_status: 'ready',
      decision: 'pending',
      factor_labels: ['relevance', 'freshness'],
    },
    {
      material_id: 104,
      material_status: 'draft',
      decision: 'pending',
      factor_labels: [],
      body_markdown: '',
    },
    {
      material_id: 105,
      material_status: 'draft',
      decision: 'approved',
      factor_labels: ['relevance'],
    },
  ]
}

describe('applyMockMarkReady', () => {
  it('flips matching material_id to ready and leaves others unchanged', async () => {
    const { applyMockMarkReady } = await import('../../web/src/services/adminReadyMock.js')
    const items = seedItems()
    applyMockMarkReady(items, 104)
    assert.equal(items.find((row) => row.material_id === 104).material_status, 'ready')
    assert.equal(items.find((row) => row.material_id === 105).material_status, 'draft')
    assert.equal(items.find((row) => row.material_id === 101).material_status, 'ready')
  })
})

describe('applyMockMarkReadyBatch', () => {
  it('returns order-preserving partial results in a single call (D-08)', async () => {
    const mod = await import('../../web/src/services/adminReadyMock.js')
    const { applyMockMarkReadyBatch, applyMockMarkReady } = mod
    const items = seedItems()
    const { results } = applyMockMarkReadyBatch(items, [104, 999, 105])
    assert.deepEqual(results, [
      { material_id: 104, ok: true, status: 'ready', error: null },
      { material_id: 999, ok: false, status: null, error: 'material_not_found' },
      { material_id: 105, ok: true, status: 'ready', error: null },
    ])
    assert.equal(items.find((row) => row.material_id === 104).material_status, 'ready')
    assert.equal(items.find((row) => row.material_id === 105).material_status, 'ready')
    // Batch owns the loop — applyMockMarkReady remains available but batch must not
    // require N separate HTTP-shaped markReady exports (assert via source below).
    assert.equal(typeof applyMockMarkReady, 'function')
  })
})

describe('getMockDefaultItems ADUX-06 empty seed', () => {
  it('includes material_id 104 with empty factor_labels', async () => {
    const { getMockDefaultItems } = await import('../../web/src/services/adminReadyMock.js')
    const items = getMockDefaultItems()
    const row = items.find((item) => item.material_id === 104)
    assert.ok(row, 'material 104 must exist in mock seed')
    assert.deepEqual(row.factor_labels, [])
    assert.equal(row.material_status, 'draft')
  })
})

describe('adminApi markReady / markReadyBatch exports', () => {
  it('exports markReady and markReadyBatch; batch body never calls markReady (D-08)', async () => {
    const apiPath = path.resolve(__dirname, '../../web/src/services/adminApi.js')
    const source = fs.readFileSync(apiPath, 'utf8')
    assert.match(source, /export async function markReady\b/)
    assert.match(source, /export async function markReadyBatch\b/)
    const batchMatch = source.match(
      /export async function markReadyBatch\([\s\S]*?(?=\nexport async function |\nexport function |\n$)/,
    )
    assert.ok(batchMatch, 'markReadyBatch function body must be present')
    assert.equal(
      /(?<!function )\bmarkReady\s*\(/.test(batchMatch[0].replace(/export async function markReadyBatch/, '')),
      false,
      'markReadyBatch must not call markReady (D-08 single batch POST)',
    )
  })
})

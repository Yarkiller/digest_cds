/**
 * RED stub — admin mark-ready mock helpers (ADUX-05).
 * Intentionally incomplete until GREEN wiring.
 * No Vite/supabase/import.meta — node --test safe.
 */

/**
 * @param {Array<{ material_id: number, material_status: string }>} items
 * @param {number} materialId
 */
export function applyMockMarkReady(items, materialId) {
  void items
  void materialId
  // RED: no-op — material_status stays draft
}

/**
 * @param {Array<{ material_id: number, material_status: string }>} items
 * @param {number[]} materialIds
 * @returns {{ results: Array<{ material_id: number, ok: boolean, status: string|null, error: string|null }> }}
 */
export function applyMockMarkReadyBatch(items, materialIds) {
  void items
  void materialIds
  // RED: empty results — wrong shape until GREEN
  return { results: [] }
}

/**
 * @returns {Array<{ material_id: number, material_status: string, factor_labels: string[] }>}
 */
export function getMockDefaultItems() {
  // RED: missing material 104 empty-factor seed
  return []
}

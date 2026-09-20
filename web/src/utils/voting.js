/**
 * Pure helpers for voting UI copy and button labels (D-44, VOTE-02).
 */
export function voteStatusText({ confirmedId, selectedId, topics }) {
  if (confirmedId) {
    const topic = topics.find((item) => item.id === confirmedId)
    return `Ваш голос: ${topic?.title ?? confirmedId}`
  }
  if (selectedId) {
    const topic = topics.find((item) => item.id === selectedId)
    return `Выбор: «${topic?.title ?? selectedId}» (нажмите «Подтвердить голос»)`
  }
  return 'голос не отдан'
}

/**
 * @param {string} state
 * @param {{ confirmedId?: string | null }} [opts]
 */
export function voteButtonLabel(state, { confirmedId } = {}) {
  if (state === 'loading') return 'Сохраняем…'
  if (state === 'error') return 'Повторить'
  if (confirmedId) return 'Изменить голос'
  return 'Подтвердить голос'
}

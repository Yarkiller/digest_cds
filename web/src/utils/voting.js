/**
 * Pure helpers for voting UI copy and button labels.
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
  return 'Ваш голос: не отдан'
}

export function voteButtonLabel(state) {
  if (state === 'loading') return 'Сохраняем…'
  if (state === 'success') return 'Голос принят'
  if (state === 'error') return 'Повторить'
  return 'Подтвердить голос'
}

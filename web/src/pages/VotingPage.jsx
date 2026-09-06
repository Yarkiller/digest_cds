import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { votingCycle, votingTopics } from '../data/mock.js'
import TopicBallot from '../components/TopicBallot.jsx'
import ActionButton from '../components/ActionButton.jsx'
import { delay } from '../utils/delay.js'

export default function VotingPage() {
  const [searchParams] = useSearchParams()
  const [selectedId, setSelectedId] = useState(null)
  const [confirmedId, setConfirmedId] = useState(null)
  const [buttonState, setButtonState] = useState('idle')
  const [toast, setToast] = useState('')
  const [alert, setAlert] = useState('')
  const [pendingSimulatedError, setPendingSimulatedError] = useState(
    () => searchParams.get('simulateError') === '1',
  )

  const status = useMemo(() => {
    if (confirmedId) {
      const topic = votingTopics.find((item) => item.id === confirmedId)
      return `Ваш голос: ${topic?.title ?? confirmedId}`
    }
    if (selectedId) {
      const topic = votingTopics.find((item) => item.id === selectedId)
      return `Выбор: «${topic?.title ?? selectedId}» (нажмите «Подтвердить голос»)`
    }
    return 'Ваш голос: не отдан'
  }, [confirmedId, selectedId])

  async function confirmVote() {
    if (!selectedId || buttonState === 'loading') return
    setButtonState('loading')
    setToast('')
    setAlert('')
    await delay()

    if (pendingSimulatedError) {
      setPendingSimulatedError(false)
      setButtonState('error')
      setAlert('Не удалось сохранить голос. Проверьте соединение и попробуйте ещё раз.')
      return
    }

    setConfirmedId(selectedId)
    setButtonState('success')
    setToast('Голос сохранён')
  }

  const label =
    buttonState === 'loading'
      ? 'Сохраняем…'
      : buttonState === 'success'
        ? 'Голос принят'
        : buttonState === 'error'
          ? 'Повторить'
          : 'Подтвердить голос'

  return (
    <section className="max-w-3xl">
      <h1 className="mb-6 font-display text-3xl font-semibold">Голосование за тему разбора</h1>

      <div className="mb-8 rounded-2xl border border-rule bg-[oklch(98.5%_0.009_95)] p-5">
        <div className="mb-3 flex items-baseline justify-between gap-3">
          <span className="text-xs uppercase tracking-wide text-muted">{votingCycle.label}</span>
          <span className="text-xs text-ink-2">{votingCycle.period}</span>
        </div>
        <div className="h-1 overflow-hidden rounded bg-[oklch(93%_0.035_78)]">
          <div
            className="h-full bg-voting"
            style={{ width: `${Math.round(votingCycle.progressRatio * 100)}%` }}
          />
        </div>
        <p className="mt-3 text-sm text-ink-2" role="status" aria-live="polite">
          {status}
        </p>
      </div>

      <p className="mb-8 text-sm text-ink-2">
        Один голос за цикл. Вы можете изменить выбор до {votingCycle.closesOn}.
      </p>

      <TopicBallot
        topics={votingTopics}
        selectedId={selectedId}
        onSelect={(id) => {
          setSelectedId(id)
          if (buttonState === 'success' || buttonState === 'error') setButtonState('idle')
          if (buttonState === 'error') setAlert('')
        }}
      />

      <div className="sticky bottom-0 mt-8 flex flex-wrap items-center justify-end gap-3 border-t border-rule bg-paper/95 py-3 backdrop-blur">
        {alert ? (
          <p className="mr-auto max-w-md text-sm text-[oklch(42%_0.16_25)]" role="alert">
            {alert}
          </p>
        ) : null}
        {toast ? (
          <p className="text-sm text-[oklch(45%_0.13_155)]" aria-live="polite">
            {toast}
          </p>
        ) : null}
        <ActionButton
          data-testid="confirm-vote"
          variant="voting"
          state={buttonState}
          disabled={!selectedId && buttonState === 'idle'}
          onClick={confirmVote}
        >
          {label}
        </ActionButton>
      </div>
    </section>
  )
}

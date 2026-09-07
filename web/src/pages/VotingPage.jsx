import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { votingCycle, votingTopics } from '../data/mock.js'
import TopicBallot from '../components/TopicBallot.jsx'
import ActionButton from '../components/ActionButton.jsx'
import ErrorPanel from '../components/ErrorPanel.jsx'
import {
  VoteSubmitError,
  armFailNextVoteSubmit,
  submitVote,
} from '../services/votingApi.js'
import { voteButtonLabel, voteStatusText } from '../utils/voting.js'

export default function VotingPage() {
  const [searchParams] = useSearchParams()
  const [selectedId, setSelectedId] = useState(null)
  const [confirmedId, setConfirmedId] = useState(null)
  const [buttonState, setButtonState] = useState('idle')
  const [toast, setToast] = useState('')
  const [error, setError] = useState(null)
  const [attemptCount, setAttemptCount] = useState(0)
  const [armedFailOnce] = useState(() => {
    const shouldFail = searchParams.get('simulateError') === '1'
    if (shouldFail) armFailNextVoteSubmit()
    return shouldFail
  })

  const status = useMemo(
    () =>
      voteStatusText({
        confirmedId,
        selectedId,
        topics: votingTopics,
      }),
    [confirmedId, selectedId],
  )

  async function confirmVote() {
    if (!selectedId || buttonState === 'loading') return

    setButtonState('loading')
    setToast('')
    setError(null)
    setAttemptCount((count) => count + 1)

    try {
      await submitVote(selectedId)
      setConfirmedId(selectedId)
      setButtonState('success')
      setToast('Голос сохранён')
      setAttemptCount(0)
    } catch (err) {
      const voteError =
        err instanceof VoteSubmitError
          ? err
          : new VoteSubmitError('Не удалось сохранить голос.', { code: 'UNKNOWN' })

      setButtonState(voteError.retryable ? 'error' : 'idle')
      setError({
        title: 'Ошибка сохранения',
        message: voteError.message,
        code: voteError.code,
        retryable: voteError.retryable,
      })
    }
  }

  function clearError() {
    setError(null)
    if (buttonState === 'error') setButtonState('idle')
  }

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
        {armedFailOnce ? (
          <p className="mt-2 text-xs text-muted">
            Демо режима сбоя: первая отправка будет отклонена сервером (повторите).
          </p>
        ) : null}
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
          if (error) setError(null)
        }}
      />

      <div className="sticky bottom-0 mt-8 flex flex-wrap items-center justify-end gap-3 border-t border-rule bg-paper/95 py-3 backdrop-blur">
        {error ? (
          <ErrorPanel
            title={error.title}
            message={error.message}
            meta={
              error.retryable
                ? `Попытка ${attemptCount}. Код: ${error.code}. Можно повторить.`
                : `Код: ${error.code}`
            }
            onDismiss={clearError}
          />
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
          {voteButtonLabel(buttonState)}
        </ActionButton>
      </div>
    </section>
  )
}

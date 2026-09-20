import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import TopicBallot from '../components/TopicBallot.jsx'
import ActionButton from '../components/ActionButton.jsx'
import ErrorPanel from '../components/ErrorPanel.jsx'
import {
  BallotFetchError,
  VoteSubmitError,
  armFailNextVoteSubmit,
  fetchBallot,
  submitVote,
} from '../services/votingApi.js'
import { voteButtonLabel, voteStatusText } from '../utils/voting.js'

const FALLBACK_CYCLE = {
  label: 'Цикл голосования',
  period: '',
  closesOn: 'закрытия цикла',
  progressRatio: 0,
}

function applySnapshot(snapshot, setters) {
  const { setTopics, setCycleMeta, setConfirmedId, setSelectedId, setExpectedUpdatedAt } = setters
  const topics = snapshot?.topics ?? []
  setTopics(topics)

  const cycle = snapshot?.cycle
  if (cycle) {
    setCycleMeta({
      label: cycle.label ?? FALLBACK_CYCLE.label,
      period: cycle.period ?? '',
      closesOn: cycle.closesOn ?? FALLBACK_CYCLE.closesOn,
      progressRatio: cycle.progress_ratio ?? cycle.progressRatio ?? 0,
    })
  } else {
    setCycleMeta(FALLBACK_CYCLE)
  }

  const personal = snapshot?.personal_vote ?? null
  const confirmed = personal?.topic_id ?? null
  setConfirmedId(confirmed)
  setExpectedUpdatedAt(personal?.updated_at ?? null)
  // D-46: radios mirror server vote after confirm/load; never-voted stays empty
  setSelectedId(confirmed)
}

export default function VotingPage() {
  const [searchParams] = useSearchParams()
  const [topics, setTopics] = useState([])
  const [cycleMeta, setCycleMeta] = useState(FALLBACK_CYCLE)
  const [selectedId, setSelectedId] = useState(null)
  const [confirmedId, setConfirmedId] = useState(null)
  const [expectedUpdatedAt, setExpectedUpdatedAt] = useState(null)
  const [loadState, setLoadState] = useState('loading')
  const [buttonState, setButtonState] = useState('idle')
  const [toast, setToast] = useState('')
  const [error, setError] = useState(null)
  const [validationMessage, setValidationMessage] = useState('')
  const [attemptCount, setAttemptCount] = useState(0)
  const [armedFailOnce] = useState(() => {
    const shouldFail = searchParams.get('simulateError') === '1'
    if (shouldFail) armFailNextVoteSubmit()
    return shouldFail
  })

  useEffect(() => {
    let cancelled = false
    setLoadState('loading')
    fetchBallot()
      .then((snapshot) => {
        if (cancelled) return
        applySnapshot(snapshot, {
          setTopics,
          setCycleMeta,
          setConfirmedId,
          setSelectedId,
          setExpectedUpdatedAt,
        })
        setLoadState('ready')
      })
      .catch((err) => {
        if (cancelled) return
        const fetchError =
          err instanceof BallotFetchError
            ? err
            : new BallotFetchError('Не удалось загрузить голосование.', { code: 'UNKNOWN' })
        setError({
          title: 'Ошибка загрузки',
          message: fetchError.message,
          code: fetchError.code,
          retryable: fetchError.retryable,
        })
        setLoadState('error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  const status = useMemo(
    () =>
      voteStatusText({
        confirmedId,
        selectedId,
        topics,
      }),
    [confirmedId, selectedId, topics],
  )

  const confirmDisabled =
    loadState !== 'ready' ||
    buttonState === 'loading' ||
    !selectedId ||
    selectedId === confirmedId

  async function confirmVote() {
    if (buttonState === 'loading') return

    if (!selectedId) {
      setValidationMessage('Выберите тему')
      setError(null)
      return
    }

    setValidationMessage('')
    setButtonState('loading')
    setToast('')
    setError(null)
    setAttemptCount((count) => count + 1)

    const hadConfirmed = Boolean(confirmedId)

    try {
      const snapshot = await submitVote(selectedId, expectedUpdatedAt)
      applySnapshot(snapshot, {
        setTopics,
        setCycleMeta,
        setConfirmedId,
        setSelectedId,
        setExpectedUpdatedAt,
      })
      setButtonState('idle')
      setToast(hadConfirmed ? 'Голос изменён' : 'Голос сохранён')
      setAttemptCount(0)
    } catch (err) {
      const voteError =
        err instanceof VoteSubmitError
          ? err
          : new VoteSubmitError('Не удалось сохранить голос.', { code: 'UNKNOWN' })

      if (voteError.code === 'NO_TOPIC') {
        setValidationMessage(voteError.message || 'Выберите тему')
        setButtonState('idle')
        return
      }

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
          <span className="text-xs uppercase tracking-wide text-muted">{cycleMeta.label}</span>
          <span className="text-xs text-ink-2">{cycleMeta.period}</span>
        </div>
        <div className="h-1 overflow-hidden rounded bg-[oklch(93%_0.035_78)]">
          <div
            className="h-full bg-voting"
            style={{ width: `${Math.round(cycleMeta.progressRatio * 100)}%` }}
          />
        </div>
        <p className="mt-3 text-sm text-ink-2" role="status" aria-live="polite">
          {loadState === 'ready' ? status : loadState === 'loading' ? 'Загрузка…' : status}
        </p>
        {armedFailOnce ? (
          <p className="mt-2 text-xs text-muted">
            Демо режима сбоя: первая отправка будет отклонена сервером (повторите).
          </p>
        ) : null}
      </div>

      <p className="mb-8 text-sm text-ink-2">
        Один голос за цикл. Вы можете изменить выбор до {cycleMeta.closesOn}.
      </p>

      {loadState === 'ready' ? (
        <TopicBallot
          topics={topics}
          selectedId={selectedId}
          onSelect={(id) => {
            setSelectedId(id)
            setValidationMessage('')
            if (buttonState === 'success' || buttonState === 'error') setButtonState('idle')
            if (error) setError(null)
          }}
        />
      ) : null}

      <div className="sticky bottom-0 mt-8 flex flex-wrap items-center justify-end gap-3 border-t border-rule bg-paper/95 py-3 backdrop-blur">
        {validationMessage || (loadState === 'ready' && !selectedId) ? (
          <p className="text-sm text-[oklch(45%_0.14_25)]" role="alert">
            {validationMessage || 'Выберите тему'}
          </p>
        ) : null}
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
          disabled={confirmDisabled}
          onClick={confirmVote}
        >
          {voteButtonLabel(buttonState, { confirmedId })}
        </ActionButton>
      </div>
    </section>
  )
}

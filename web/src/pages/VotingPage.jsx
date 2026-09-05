import { useMemo, useState } from 'react'
import { votingCycle, votingTopics } from '../data/mock.js'
import TopicBallot from '../components/TopicBallot.jsx'

export default function VotingPage() {
  const [selectedId, setSelectedId] = useState(null)
  const [confirmedId, setConfirmedId] = useState(null)

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

  return (
    <section className="max-w-3xl">
      <h1 className="mb-6 font-display text-3xl font-semibold">Голосование за тему разбора</h1>

      <div className="mb-8">
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
        <p className="mt-3 text-sm text-ink-2" aria-live="polite">
          {status}
        </p>
      </div>

      <p className="mb-8 text-sm text-ink-2">
        Один голос за цикл. Вы можете изменить выбор до {votingCycle.closesOn}.
      </p>

      <TopicBallot topics={votingTopics} selectedId={selectedId} onSelect={setSelectedId} />

      <div className="sticky bottom-0 mt-8 flex justify-end border-t border-rule bg-paper py-3">
        <button
          type="button"
          className="inline-flex min-h-11 items-center rounded-full bg-voting px-4 text-sm font-medium text-[oklch(24%_0.02_38)] disabled:opacity-55"
          disabled={!selectedId}
          onClick={() => setConfirmedId(selectedId)}
        >
          Подтвердить голос
        </button>
      </div>
    </section>
  )
}

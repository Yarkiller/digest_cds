import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import EditorialCallout from '../components/EditorialCallout.jsx'
import IssueToc from '../components/IssueToc.jsx'
import PlatformProofBanner from '../components/PlatformProofBanner.jsx'
import { ContentApiError, fetchCurrentIssue } from '../services/contentApi.js'

function materialCountLabel(count) {
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod10 === 1 && mod100 !== 11) return `${count} материал`
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
    return `${count} материала`
  }
  return `${count} материалов`
}

function toTocItems(items) {
  return items.map((item) => ({
    id: item.slug,
    title: item.title,
    issuePosition: item.position,
    format: item.format,
    readingMinutes: item.reading_minutes,
    dek: item.dek,
  }))
}

export default function IssuePage() {
  const [issue, setIssue] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setStatus('loading')
    setError(null)
    fetchCurrentIssue()
      .then((dto) => {
        if (cancelled) return
        setIssue(dto)
        setStatus('ready')
      })
      .catch((err) => {
        if (cancelled) return
        const message =
          err instanceof ContentApiError
            ? err.message
            : 'Не удалось загрузить выпуск. Проверьте сеть.'
        setError(message)
        setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (status === 'loading') {
    return (
      <section aria-busy="true" data-testid="issue-loading">
        <PlatformProofBanner />
        <div className="mt-3 h-4 w-48 animate-pulse rounded bg-rule" />
        <div className="mt-4 h-10 max-w-xl animate-pulse rounded bg-rule" />
        <div className="mt-6 h-24 animate-pulse rounded bg-rule" />
      </section>
    )
  }

  if (status === 'error') {
    return (
      <section>
        <PlatformProofBanner />
        <p role="alert" className="text-ink-2">
          {error}
        </p>
      </section>
    )
  }

  const items = issue?.items ?? []
  const isEmpty = items.length === 0

  if (isEmpty) {
    return (
      <section data-testid="issue-empty">
        <PlatformProofBanner />
        <h2 className="font-display text-2xl font-semibold">Выпуск готовится</h2>
        <p className="mt-3 max-w-prose text-ink-2">
          Свежий выпуск скоро появится. А пока — загляните в архив прошлых недель.
        </p>
        <p className="mt-6">
          <Link to="/archive" className="font-medium text-accent no-underline hover:underline">
            В архив →
          </Link>
        </p>
      </section>
    )
  }

  return (
    <section data-testid="issue-ready">
      <PlatformProofBanner />
      <p className="text-xs uppercase tracking-wide text-muted">
        Выпуск №{issue.number} · {issue.period_label}
      </p>
      <h1 className="mt-3 max-w-4xl font-display text-4xl font-semibold leading-tight sm:text-5xl">
        {issue.title}
      </h1>
      <p className="mt-3 text-sm text-ink-2">
        {issue.editor ?? 'Редакция Digest CDS'} · {materialCountLabel(items.length)}
      </p>

      <hr className="my-8 border-rule" />

      <EditorialCallout actionTo="/voting" actionLabel="Выбрать тему →">
        <strong>Голосование открыто</strong> — выберите тему следующего разбора.
      </EditorialCallout>

      <h2 className="mb-6 font-display text-2xl font-semibold">В этом выпуске</h2>
      <IssueToc items={toTocItems(items)} />
    </section>
  )
}

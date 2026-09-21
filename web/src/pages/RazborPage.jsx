import { useCallback, useEffect, useState } from 'react'
import Markdown from 'react-markdown'
import { Link, useParams } from 'react-router-dom'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import rehypeSlug from 'rehype-slug'
import ServiceUnavailable from '../components/ServiceUnavailable.jsx'
import {
  RAZBOR_EDITOR_BYLINE,
  RazboryApiError,
  clearFailNextRazboryFetch,
  fetchRazbor,
  razborStatusLabel,
} from '../services/razboryApi.js'
import { extractMarkdownHeadings } from '../utils/markdownToc.js'

function formatMeetingLabel(iso) {
  if (!iso) return null
  try {
    return new Date(iso).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    })
  } catch {
    return null
  }
}

function SectionToc({ headings }) {
  if (!headings.length) return null

  const links = headings.map((heading) => (
    <li key={heading.id} className={heading.level > 2 ? 'pl-3' : undefined}>
      <a href={`#${heading.id}`} className="text-sm text-accent no-underline hover:underline">
        {heading.text}
      </a>
    </li>
  ))

  return (
    <>
      <details className="mb-8 rounded-lg border border-rule bg-paper-2 p-3 lg:hidden">
        <summary className="cursor-pointer text-sm font-medium">Содержание</summary>
        <ul className="mt-3 space-y-2">{links}</ul>
      </details>
      <nav
        aria-label="Содержание"
        data-testid="razbor-toc"
        className="sticky top-24 hidden max-h-[70vh] w-56 shrink-0 overflow-auto lg:block"
      >
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Содержание</p>
        <ul className="mt-3 space-y-2">{links}</ul>
      </nav>
    </>
  )
}

/**
 * Razbor detail — published longread + TOC, announcement stub, soft 404 (RAZB-02 / D-68).
 * Notebook download strip lands in 04-07.
 */
export default function RazborPage() {
  const { id } = useParams()
  const [razbor, setRazbor] = useState(null)
  const [status, setStatus] = useState('loading')
  const [notFound, setNotFound] = useState(false)
  const [loadKey, setLoadKey] = useState(0)

  const reload = useCallback(() => {
    clearFailNextRazboryFetch()
    setLoadKey((k) => k + 1)
  }, [])

  useEffect(() => {
    let cancelled = false
    setStatus('loading')
    setNotFound(false)

    fetchRazbor(id)
      .then((dto) => {
        if (cancelled) return
        setRazbor(dto)
        setStatus('ready')
      })
      .catch((err) => {
        if (cancelled) return
        if (err instanceof RazboryApiError && err.code === 'NOT_FOUND') {
          setNotFound(true)
          setStatus('ready')
          return
        }
        setStatus('error')
      })

    return () => {
      cancelled = true
    }
  }, [id, loadKey])

  if (status === 'loading') {
    return (
      <section aria-busy="true" data-testid="razbor-loading">
        <div className="mt-3 h-4 w-40 animate-pulse rounded bg-rule" />
        <div className="mt-4 h-10 max-w-xl animate-pulse rounded bg-rule" />
        <div className="mt-6 h-40 animate-pulse rounded bg-rule" />
      </section>
    )
  }

  if (status === 'error') {
    return (
      <section>
        <ServiceUnavailable onRetry={reload} />
      </section>
    )
  }

  if (notFound || !razbor) {
    return (
      <section data-testid="razbor-not-found">
        <h1 className="font-display text-3xl font-semibold">Разбор не найден</h1>
        <p className="mt-3 max-w-prose text-ink-2">
          Возможно, ссылка устарела или разбор ещё готовится.
        </p>
        <p className="mt-6">
          <Link
            to="/razbory"
            className="inline-flex min-h-11 items-center text-accent no-underline hover:underline"
          >
            К списку разборов
          </Link>
        </p>
      </section>
    )
  }

  const dateLabel = formatMeetingLabel(razbor.meeting_at)
  const statusLabel = razborStatusLabel(razbor.status)
  const isAnnouncement = razbor.status === 'announcement'
  const isOverview = !isAnnouncement && razbor.content_kind === 'overview'
  const isQuality = !isAnnouncement && razbor.content_kind === 'quality'
  const typeBadge = isAnnouncement ? 'Анонс' : isOverview ? 'Обзор' : 'Разбор'
  const overline = [dateLabel, statusLabel].filter(Boolean).join(' · ')

  if (isAnnouncement) {
    return (
      <article className="max-w-3xl" data-testid="razbor-announcement-stub">
        <p className="mb-6">
          <Link to="/razbory" className="text-sm text-ink-2 no-underline hover:underline">
            ← Все разборы
          </Link>
        </p>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">
          {overline || 'Анонс'}
        </p>
        <span
          data-testid="razbor-type-badge"
          className="mt-2 inline-block rounded bg-paper-2 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-ink"
        >
          {typeBadge}
        </span>
        <h1 className="mt-3 break-words font-display text-4xl font-semibold sm:text-5xl">
          {razbor.title}
        </h1>
        <p className="mt-3 text-sm text-ink-2">{razbor.editor ?? RAZBOR_EDITOR_BYLINE}</p>
        <p
          data-testid="razbor-pending-note"
          className="mt-8 max-w-prose rounded-lg border border-rule bg-paper-2 p-5 text-ink-2"
        >
          Полный разбор ещё готовится — следите за обновлениями.
        </p>
      </article>
    )
  }

  const headings = extractMarkdownHeadings(razbor.body_markdown ?? '')

  return (
    <article className="max-w-5xl" data-testid="razbor-longread">
      <p className="mb-6">
        <Link to="/razbory" className="text-sm text-ink-2 no-underline hover:underline">
          ← Все разборы
        </Link>
      </p>

      <div className="flex flex-wrap items-center gap-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">
          {overline || (isOverview ? 'Обзор' : 'Разбор')}
        </p>
        <span
          data-testid="razbor-type-badge"
          className="rounded bg-paper-2 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-ink"
        >
          {typeBadge}
        </span>
      </div>

      <h1 className="mt-3 break-words font-display text-4xl font-semibold sm:text-5xl">
        {razbor.title}
      </h1>
      <p className="mt-3 text-sm text-ink-2">{razbor.editor ?? RAZBOR_EDITOR_BYLINE}</p>

      {isQuality ? (
        <p data-testid="razbor-quality-label" className="mt-4 text-sm font-semibold text-ink">
          Качество
        </p>
      ) : null}

      <hr className="my-8 border-rule" />

      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
        <SectionToc headings={headings} />

        <div className="min-w-0 flex-1">
          <div
            data-testid="razbor-prose"
            className="prose-column max-w-3xl leading-relaxed text-ink-2 [&_h1]:mt-8 [&_h1]:font-display [&_h1]:text-3xl [&_h1]:font-semibold [&_h1]:text-ink [&_h2]:mt-8 [&_h2]:font-display [&_h2]:text-2xl [&_h2]:font-semibold [&_h2]:text-ink [&_h3]:mt-6 [&_h3]:font-display [&_h3]:text-xl [&_h3]:font-semibold [&_h3]:text-ink [&_p]:mt-4 [&_table]:mt-4 [&_table]:w-full [&_ul]:mt-4 [&_ul]:list-disc [&_ul]:pl-5"
          >
            <Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSlug, rehypeSanitize]}>
              {razbor.body_markdown}
            </Markdown>
          </div>

          <p className="mt-10">
            <Link to="/razbory" className="text-sm text-accent no-underline hover:underline">
              ← К списку разборов
            </Link>
          </p>
        </div>
      </div>
    </article>
  )
}

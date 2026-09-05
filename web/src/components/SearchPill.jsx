import { useEffect, useId, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { searchDestinations } from '../data/mock.js'

export default function SearchPill() {
  const titleId = useId()
  const inputId = useId()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return searchDestinations
    return searchDestinations.filter((item) =>
      `${item.title} ${item.description}`.toLowerCase().includes(q)
    )
  }, [query])

  useEffect(() => {
    function onKeyDown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setOpen((value) => !value)
      }
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [])

  return (
    <>
      <button
        type="button"
        className="inline-flex min-h-11 min-w-11 items-center justify-center gap-2 rounded-full border border-rule bg-paper-2 px-3 text-sm text-ink-2 hover:bg-[oklch(94%_0.025_278)]"
        aria-label="Поиск (Ctrl K)"
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        <span aria-hidden="true">⌕</span>
        <span className="hidden sm:inline">Поиск по базе</span>
        <span className="hidden font-mono text-xs text-muted sm:inline" aria-hidden="true">
          <kbd className="rounded border border-rule px-1">Ctrl</kbd>
          <kbd className="ml-1 rounded border border-rule px-1">K</kbd>
        </span>
      </button>

      {open ? (
        <div
          className="fixed inset-0 z-50 grid place-items-start bg-[oklch(20%_0.015_270_/_0.48)] p-4 pt-24"
          role="presentation"
          onClick={() => setOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            className="w-full max-w-xl rounded-2xl border border-rule bg-paper p-6 shadow-lg"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 id={titleId} className="font-display text-xl font-semibold">
                Поиск Digest CDS
              </h2>
              <button
                type="button"
                className="min-h-11 rounded-full px-3 text-sm text-ink-2 hover:bg-paper-2"
                aria-label="Закрыть"
                onClick={() => setOpen(false)}
              >
                ✕
              </button>
            </div>
            <label htmlFor={inputId} className="mb-2 block text-sm text-ink-2">
              Поиск по базе знаний
            </label>
            <input
              id={inputId}
              type="search"
              autoFocus
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="RAG, SQL, качество данных…"
              className="mb-4 w-full rounded-xl border border-rule bg-paper px-3 py-3 text-sm outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            />
            <ul className="grid gap-2" role="listbox" aria-label="Разделы Digest CDS">
              {results.map((item) => (
                <li key={item.id}>
                  <Link
                    to={item.to}
                    className="block rounded-xl border border-transparent p-3 no-underline hover:border-rule hover:bg-[oklch(94%_0.025_278)]"
                    onClick={() => setOpen(false)}
                  >
                    <strong className="block text-ink">{item.title}</strong>
                    <span className="text-sm text-ink-2">{item.description}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
    </>
  )
}

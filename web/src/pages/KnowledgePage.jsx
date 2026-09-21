import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  DEFAULT_SEARCH_LIMIT,
  KnowledgeApiError,
  clearFailNextKnowledgeSearch,
  searchKnowledge,
  validateKnowledgeQuery,
} from '../services/knowledgeApi.js'
import MaterialListRow from '../components/MaterialListRow.jsx'
import ActionButton from '../components/ActionButton.jsx'
import ErrorPanel from '../components/ErrorPanel.jsx'

/** Topic hint chips fill the query only — do not execute search (D-60). */
const HINT_CHIPS = ['RAG', 'SQL', 'качество данных', 'pgvector']

/**
 * Knowledge SPA — Submit/Enter «Найти» → knowledgeApi (D-57, D-59, D-60, D-61 / KNOW-01).
 * Role chips deferred to 04-03.
 */
export default function KnowledgePage() {
  const [searchParams] = useSearchParams()
  const [query, setQuery] = useState(() => searchParams.get('q') ?? '')
  /** null = pre-search landing; string = last successful/attempted submitted q */
  const [activeQuery, setActiveQuery] = useState(null)
  const [items, setItems] = useState([])
  const [hasMore, setHasMore] = useState(false)
  const [nextOffset, setNextOffset] = useState(0)
  const [searching, setSearching] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState(null)
  /** Inline validation — blank/overlong; never hits knowledgeApi (KNOW-01). */
  const [inlineError, setInlineError] = useState(null)

  async function runSearch(q, { offset = 0, append = false } = {}) {
    if (append) {
      setLoadingMore(true)
    } else {
      setSearching(true)
      setError(null)
      setInlineError(null)
    }

    try {
      const dto = await searchKnowledge({
        q,
        limit: DEFAULT_SEARCH_LIMIT,
        offset,
      })
      setActiveQuery(q)
      setItems((prev) => (append ? [...prev, ...dto.items] : dto.items))
      setHasMore(Boolean(dto.has_more))
      setNextOffset(offset + (dto.items?.length ?? 0))
      setError(null)
    } catch (err) {
      const message =
        err instanceof KnowledgeApiError
          ? err.message
          : 'Не удалось выполнить поиск. Проверьте сеть.'
      const retryable = err instanceof KnowledgeApiError ? err.retryable : true
      setError({ message, retryable })
      if (!append) {
        setItems([])
        setHasMore(false)
        setActiveQuery(q)
      }
    } finally {
      setSearching(false)
      setLoadingMore(false)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    const validation = validateKnowledgeQuery(query)
    if (!validation.ok) {
      // Inline copy locked to UI-SPEC (must appear in this source for honesty/verify).
      setInlineError(
        validation.code === 'QUERY_TOO_LONG' ? 'Сократите запрос' : 'Введите запрос',
      )
      setError(null)
      // Do not call searchKnowledge (KNOW-01 / D-57).
      return
    }
    setInlineError(null)
    void runSearch(validation.q, { offset: 0, append: false })
  }

  function handleRetry() {
    clearFailNextKnowledgeSearch()
    const validation = validateKnowledgeQuery(activeQuery ?? query)
    if (!validation.ok) {
      setInlineError(validation.message)
      return
    }
    void runSearch(validation.q, { offset: 0, append: false })
  }

  function handleLoadMore() {
    if (!hasMore || loadingMore || searching || activeQuery == null) return
    void runSearch(activeQuery, { offset: nextOffset, append: true })
  }

  const preSearch = activeQuery === null && !error
  const showZeroHit =
    activeQuery !== null && !searching && !error && items.length === 0

  return (
    <section>
      <h1 className="mb-6 font-display text-3xl font-semibold">База знаний</h1>

      <form className="mb-4" role="search" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="kb-search">
          Поиск по базе знаний
        </label>
        <div className="flex max-w-xl flex-col gap-3 sm:flex-row sm:items-stretch">
          <input
            id="kb-search"
            type="search"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value)
              if (inlineError) setInlineError(null)
            }}
            placeholder="Спросите своими словами: SQL, дашборды, RAG…"
            disabled={searching}
            aria-invalid={inlineError ? true : undefined}
            aria-describedby={inlineError ? 'kb-search-inline-error' : undefined}
            className="min-w-0 flex-1 break-words rounded-xl border border-rule bg-[oklch(98%_0.009_95)] px-4 py-3 text-sm outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          />
          <ActionButton
            type="submit"
            variant="primary"
            state={searching ? 'loading' : 'idle'}
            disabled={searching}
            className="shrink-0"
          >
            Найти
          </ActionButton>
        </div>
        {inlineError ? (
          <p
            id="kb-search-inline-error"
            role="alert"
            className="mt-2 text-sm text-[oklch(35%_0.12_25)]"
            data-testid="kb-inline-error"
          >
            {inlineError}
          </p>
        ) : null}
      </form>

      {preSearch ? (
        <div className="mb-8" data-testid="kb-hint-chips">
          <p className="mb-3 text-xs text-ink-2">Попробуйте тему:</p>
          <div className="flex flex-wrap gap-2">
            {HINT_CHIPS.map((hint) => (
              <button
                key={hint}
                type="button"
                className="min-h-11 rounded-full border border-rule bg-paper-2 px-3 text-sm text-ink hover:bg-paper"
                onClick={() => setQuery(hint)}
              >
                {hint}
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="mb-6" data-testid="kb-search-error">
          <ErrorPanel title="Не удалось найти материалы" message={error.message} />
          {error.retryable ? (
            <ActionButton variant="secondary" className="mt-4" onClick={handleRetry}>
              Повторить
            </ActionButton>
          ) : null}
        </div>
      ) : null}

      {activeQuery !== null && !error ? (
        <p className="mb-4 text-xs text-ink-2" aria-live="polite">
          {searching
            ? 'Ищем…'
            : items.length === 0
              ? 'Найдено 0 материалов'
              : `Показано ${items.length}${hasMore ? '+' : ''}`}
        </p>
      ) : null}

      {showZeroHit ? (
        <div className="max-w-md rounded-2xl border border-rule bg-[oklch(98.5%_0.009_95)] p-8">
          <h2 className="font-display text-2xl font-semibold">Ничего не нашли</h2>
          <p className="mt-2 text-sm text-ink-2">
            По запросу нет материалов — уточните формулировку или смените роль.
          </p>
        </div>
      ) : null}

      {items.length > 0 ? (
        <div>
          {items.map((hit) => (
            <MaterialListRow key={hit.slug} material={hit} />
          ))}

          {loadingMore ? (
            <div data-testid="kb-skeleton" className="mt-4 space-y-3" aria-busy="true">
              <div className="h-16 animate-pulse rounded-xl bg-paper-2" />
              <div className="h-16 animate-pulse rounded-xl bg-paper-2" />
            </div>
          ) : null}

          {hasMore && !loadingMore ? (
            <div className="mt-6">
              <ActionButton variant="secondary" onClick={handleLoadMore} disabled={searching}>
                Показать ещё
              </ActionButton>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  )
}

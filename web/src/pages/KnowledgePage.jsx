import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { materials } from '../data/mock.js'
import { filterMaterials } from '../utils/filters.js'
import { delay } from '../utils/delay.js'
import MaterialListRow from '../components/MaterialListRow.jsx'
import ActionButton from '../components/ActionButton.jsx'

const initialFilters = { query: '', role: '', tag: '', format: '', topic: '' }
const PAGE_SIZE = 3

export default function KnowledgePage() {
  const [searchParams] = useSearchParams()
  const [filters, setFilters] = useState(() => ({
    ...initialFilters,
    query: searchParams.get('q') ?? '',
  }))
  const [expanded, setExpanded] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)

  const matched = useMemo(() => filterMaterials(materials, filters), [filters])
  const visible = expanded ? matched : matched.slice(0, PAGE_SIZE)
  const canLoadMore = !expanded && matched.length > PAGE_SIZE

  function update(key, value) {
    setFilters((current) => ({ ...current, [key]: value }))
    setExpanded(false)
  }

  function reset() {
    setFilters(initialFilters)
    setExpanded(false)
    setLoadingMore(false)
  }

  async function loadMore() {
    setLoadingMore(true)
    await delay()
    setExpanded(true)
    setLoadingMore(false)
  }

  return (
    <section>
      <h1 className="mb-6 font-display text-3xl font-semibold">База знаний</h1>

      <div className="mb-4" role="search">
        <label className="sr-only" htmlFor="kb-search">
          Поиск по базе знаний
        </label>
        <input
          id="kb-search"
          type="search"
          value={filters.query}
          onChange={(event) => update('query', event.target.value)}
          placeholder="Спросите своими словами: SQL, дашборды, RAG…"
          className="w-full max-w-xl rounded-xl border border-rule bg-[oklch(98%_0.009_95)] px-4 py-3 text-sm outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        />
      </div>

      <div className="mb-6 flex flex-wrap gap-3">
        <select
          aria-label="Роль"
          value={filters.role}
          onChange={(event) => update('role', event.target.value)}
          className="min-h-11 rounded-xl border border-rule bg-paper px-3 text-sm"
        >
          <option value="">Роль: все</option>
          <option value="sva">Сотрудник СВА</option>
          <option value="analyst">Data Analyst</option>
          <option value="ds">Data Scientist</option>
        </select>
        <select
          aria-label="Теги"
          value={filters.tag}
          onChange={(event) => update('tag', event.target.value)}
          className="min-h-11 rounded-xl border border-rule bg-paper px-3 text-sm"
        >
          <option value="">Теги: все</option>
          <option value="SQL">#SQL</option>
          <option value="BI">#BI</option>
          <option value="RAG">#RAG</option>
          <option value="LLM">#LLM</option>
          <option value="аудит">#аудит</option>
        </select>
        <select
          aria-label="Формат"
          value={filters.format}
          onChange={(event) => update('format', event.target.value)}
          className="min-h-11 rounded-xl border border-rule bg-paper px-3 text-sm"
        >
          <option value="">Формат: все</option>
          <option value="Статья">Статья</option>
        </select>
        <select
          aria-label="Тема"
          value={filters.topic}
          onChange={(event) => update('topic', event.target.value)}
          className="min-h-11 rounded-xl border border-rule bg-paper px-3 text-sm"
        >
          <option value="">Тема: все</option>
          <option value="reporting">Отчётность / BI</option>
          <option value="ml-search">ML / поиск</option>
          <option value="agents">Агенты</option>
        </select>
        <button
          type="button"
          onClick={reset}
          className="min-h-11 rounded-full px-3 text-sm text-accent hover:bg-paper-2"
        >
          Сбросить
        </button>
      </div>

      <p className="mb-4 text-xs text-ink-2" aria-live="polite">
        {matched.length === 0
          ? 'Найдено 0 материалов'
          : `Показано ${visible.length} из ${matched.length}`}
      </p>

      {matched.length === 0 ? (
        <div className="max-w-md rounded-2xl border border-rule bg-[oklch(98.5%_0.009_95)] p-8">
          <h2 className="font-display text-2xl font-semibold">Ничего не нашли</h2>
          <p className="mt-2 text-sm text-ink-2">
            По запросу нет материалов — уточните фильтры или предложите тему.
          </p>
          <ActionButton variant="secondary" className="mt-5" onClick={reset}>
            Сбросить фильтры
          </ActionButton>
        </div>
      ) : (
        <div>
          {visible.map((material) => (
            <MaterialListRow key={material.id} material={material} />
          ))}

          {loadingMore ? (
            <div data-testid="kb-skeleton" className="mt-4 space-y-3" aria-busy="true">
              <div className="h-16 animate-pulse rounded-xl bg-paper-2" />
              <div className="h-16 animate-pulse rounded-xl bg-paper-2" />
            </div>
          ) : null}

          {canLoadMore && !loadingMore ? (
            <div className="mt-6">
              <ActionButton variant="secondary" onClick={loadMore}>
                Загрузить ещё
              </ActionButton>
            </div>
          ) : null}
        </div>
      )}
    </section>
  )
}

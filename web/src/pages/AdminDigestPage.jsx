import { useCallback, useEffect, useMemo, useState } from 'react'
import ServiceUnavailable from '../components/ServiceUnavailable.jsx'
import ForbiddenPage from './ForbiddenPage.jsx'
import { getAccessToken } from '../services/authApi.js'
import { fetchMe } from '../services/meApi.js'
import {
  AdminApiError,
  clearFailNextShortlistFetch,
  fetchShortlist,
  setDecision,
} from '../services/adminApi.js'

const TOAST_DISMISS_MS = 4000

function decisionCaption(decision) {
  if (decision === 'approved') return 'одобрен'
  if (decision === 'rejected') return 'отклонён'
  return null
}

function factorText(item) {
  const labels = Array.isArray(item.factor_labels) ? item.factor_labels.filter(Boolean) : []
  if (labels.length < 2) return 'обоснование недоступно'
  return labels.join(' · ')
}

function applyBatch(dto, setItems, setBatchMeta) {
  setItems(Array.isArray(dto?.items) ? dto.items : [])
  setBatchMeta({
    batch_id: dto?.batch_id ?? null,
    sent_at: dto?.sent_at ?? null,
    week_label: dto?.week_label ?? null,
  })
}

/**
 * Admin Digest triage — shortlist chrome, batch Approve/Reject (ADMIN-01…03, ADMIN-05).
 * Send gate / select-all / top-3 land in later plan tasks.
 */
export default function AdminDigestPage() {
  const [roleState, setRoleState] = useState('loading')
  const [items, setItems] = useState([])
  const [batchMeta, setBatchMeta] = useState({
    batch_id: null,
    sent_at: null,
    week_label: null,
  })
  const [loadState, setLoadState] = useState('loading')
  const [loadKey, setLoadKey] = useState(0)
  const [checkedIds, setCheckedIds] = useState(() => new Set())
  const [mutating, setMutating] = useState(false)
  const [toast, setToast] = useState('')
  const [previewItem, setPreviewItem] = useState(null)
  const [contextText, setContextText] = useState('')
  const [schemaText, setSchemaText] = useState('')

  useEffect(() => {
    let cancelled = false
    async function loadRole() {
      try {
        const token = await getAccessToken()
        const me = await fetchMe(token)
        if (!cancelled) {
          setRoleState(me.role === 'admin' ? 'admin' : 'forbidden')
        }
      } catch {
        if (!cancelled) setRoleState('forbidden')
      }
    }
    loadRole()
    return () => {
      cancelled = true
    }
  }, [])

  const reloadShortlist = useCallback(() => {
    clearFailNextShortlistFetch()
    setLoadKey((k) => k + 1)
  }, [])

  useEffect(() => {
    if (roleState !== 'admin') return undefined
    let cancelled = false
    setLoadState('loading')
    fetchShortlist()
      .then((dto) => {
        if (cancelled) return
        applyBatch(dto, setItems, setBatchMeta)
        setCheckedIds(new Set())
        setLoadState('ready')
      })
      .catch(() => {
        if (cancelled) return
        setLoadState('error')
      })
    return () => {
      cancelled = true
    }
  }, [roleState, loadKey])

  useEffect(() => {
    if (!toast) return undefined
    const id = window.setTimeout(() => setToast(''), TOAST_DISMISS_MS)
    return () => window.clearTimeout(id)
  }, [toast])

  const checkedCount = checkedIds.size
  const approveDisabled = mutating || checkedCount === 0

  const weekDek = useMemo(() => {
    if (!batchMeta.week_label) return null
    return `Неделя ${batchMeta.week_label} · до 5 кандидатов`
  }, [batchMeta.week_label])

  function toggleCheck(materialId) {
    setCheckedIds((prev) => {
      const next = new Set(prev)
      if (next.has(materialId)) next.delete(materialId)
      else next.add(materialId)
      return next
    })
  }

  async function applyDecision(decision) {
    if (approveDisabled) return
    const ids = [...checkedIds]
    setMutating(true)
    try {
      let latest = null
      for (const id of ids) {
        latest = await setDecision(id, decision)
      }
      if (latest) applyBatch(latest, setItems, setBatchMeta)
      setCheckedIds(new Set())
    } catch (err) {
      setToast('Не сохранено')
      if (err instanceof AdminApiError) {
        /* keep selection; toast covers honesty */
      }
    } finally {
      setMutating(false)
    }
  }

  if (roleState === 'loading') {
    return (
      <section aria-busy="true" data-testid="admin-role-loading">
        <p className="text-sm text-muted">Загрузка…</p>
      </section>
    )
  }

  if (roleState === 'forbidden') {
    return <ForbiddenPage />
  }

  if (loadState === 'error') {
    return (
      <section data-testid="admin-digest-page">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
        <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Shortlist дайджеста</h1>
        <ServiceUnavailable onRetry={reloadShortlist} />
      </section>
    )
  }

  if (loadState === 'loading') {
    return (
      <section aria-busy="true" data-testid="admin-digest-page">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
        <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Shortlist дайджеста</h1>
        <p className="mt-4 text-sm text-muted">Загрузка…</p>
      </section>
    )
  }

  const isEmpty = items.length === 0

  return (
    <section data-testid="admin-digest-page" className="pb-28">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
      <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Shortlist дайджеста</h1>
      {!isEmpty && weekDek ? (
        <p className="mt-2 text-xs text-muted">{weekDek}</p>
      ) : null}

      {isEmpty ? (
        <div
          data-testid="admin-shortlist-empty"
          className="mt-8 rounded-2xl border border-rule bg-paper px-6 py-10"
        >
          <h2 className="font-sans text-3xl font-semibold text-ink">Кандидатов пока нет</h2>
          <p className="mt-3 text-sm text-ink-2">Обновите список позже.</p>
          <button
            type="button"
            className="mt-6 inline-flex min-h-11 items-center font-medium text-accent hover:underline"
            onClick={reloadShortlist}
          >
            Обновить список
          </button>
        </div>
      ) : (
        <>
          <div className="mt-6 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={approveDisabled}
              className="inline-flex min-h-11 items-center rounded-full border border-rule px-4 text-sm font-medium text-ink disabled:cursor-not-allowed disabled:opacity-45"
              onClick={() => applyDecision('approved')}
            >
              Одобрить выбранные
            </button>
            <button
              type="button"
              disabled={approveDisabled}
              className="inline-flex min-h-11 items-center rounded-full border border-rule px-4 text-sm font-medium text-ink disabled:cursor-not-allowed disabled:opacity-45"
              onClick={() => applyDecision('rejected')}
            >
              Отклонить выбранные
            </button>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <section className="rounded-2xl border border-rule bg-paper-2/40 p-5">
              <h2 className="text-2xl font-semibold text-ink">Контекст дайджеста</h2>
              <label className="mt-4 block text-sm">
                <span className="font-medium text-ink-2">Вводный текст</span>
                <textarea
                  className="mt-2 min-h-28 w-full rounded-xl border border-rule bg-paper p-3 text-sm"
                  value={contextText}
                  onChange={(e) => setContextText(e.target.value)}
                  rows={5}
                />
              </label>
            </section>
            <section className="rounded-2xl border border-rule bg-paper-2/40 p-5">
              <h2 className="text-2xl font-semibold text-ink">Схема дайджеста</h2>
              <label className="mt-4 block text-sm">
                <span className="font-medium text-ink-2">Блоки выпуска</span>
                <textarea
                  className="mt-2 min-h-28 w-full rounded-xl border border-rule bg-paper p-3 font-mono text-sm"
                  value={schemaText}
                  onChange={(e) => setSchemaText(e.target.value)}
                  rows={7}
                />
              </label>
            </section>
          </div>

          <ul className="mt-8 space-y-3" data-testid="admin-shortlist">
            {items.map((item) => {
              const caption = decisionCaption(item.decision)
              const excluded = item.decision === 'rejected'
              return (
                <li
                  key={item.material_id}
                  data-testid="admin-shortlist-row"
                  className={[
                    'grid grid-cols-[auto_auto_1fr_auto] items-start gap-3 rounded-2xl border border-rule bg-paper p-4 sm:grid-cols-[auto_auto_1fr_auto_auto]',
                    excluded ? 'opacity-72' : '',
                  ].join(' ')}
                >
                  <label className="inline-flex min-h-11 min-w-11 items-center justify-center">
                    <input
                      type="checkbox"
                      checked={checkedIds.has(item.material_id)}
                      onChange={() => toggleCheck(item.material_id)}
                      aria-label={`Выбрать материал ${item.rank}`}
                    />
                  </label>
                  <span className="font-mono text-sm text-muted">{item.rank}</span>
                  <div className="min-w-0">
                    <p className="font-medium text-ink break-words">{item.title}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span
                        className={[
                          'rounded-md px-2 py-0.5 text-xs font-medium',
                          item.material_status === 'ready'
                            ? 'bg-[oklch(92%_0.04_155)] text-[oklch(35%_0.1_155)]'
                            : 'bg-[oklch(93%_0.05_50)] text-[oklch(45%_0.12_38)]',
                        ].join(' ')}
                      >
                        {item.material_status}
                      </span>
                      {caption ? (
                        <span className="text-xs text-muted">{caption}</span>
                      ) : null}
                    </div>
                  </div>
                  <div className="text-right">
                    {item.score != null ? (
                      <p className="font-mono text-sm text-ink">{item.score}</p>
                    ) : null}
                    <p className="mt-1 max-w-[12rem] text-xs text-muted break-words">
                      {factorText(item)}
                    </p>
                  </div>
                  <button
                    type="button"
                    className="col-span-full inline-flex min-h-11 items-center justify-self-start rounded-full px-3 text-sm text-accent hover:underline sm:col-span-1 sm:justify-self-end"
                    onClick={() => setPreviewItem(item)}
                  >
                    Превью материала
                  </button>
                </li>
              )
            })}
          </ul>
        </>
      )}

      {toast ? (
        <p
          data-testid="admin-toast"
          className="fixed bottom-24 left-1/2 z-50 -translate-x-1/2 rounded-full bg-ink px-4 py-2 text-sm text-paper"
          role="status"
        >
          {toast}
        </p>
      ) : null}

      {previewItem ? (
        <div
          className="fixed inset-0 z-[400] flex items-center justify-center bg-ink/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="item-preview-title"
        >
          <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-paper p-6">
            <div className="flex items-start justify-between gap-3">
              <h2 id="item-preview-title" className="text-2xl font-semibold">
                Превью материала
              </h2>
              <button
                type="button"
                className="inline-flex min-h-11 min-w-11 items-center justify-center"
                aria-label="Закрыть"
                onClick={() => setPreviewItem(null)}
              >
                ✕
              </button>
            </div>
            <p className="mt-4 font-medium text-ink break-words">{previewItem.title}</p>
            <p className="mt-2 text-sm text-ink-2 break-words">
              {previewItem.dek || 'Краткое описание недоступно.'}
            </p>
          </div>
        </div>
      ) : null}
    </section>
  )
}

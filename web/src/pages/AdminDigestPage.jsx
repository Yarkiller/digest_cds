import { useCallback, useEffect, useMemo, useState } from 'react'
import ServiceUnavailable from '../components/ServiceUnavailable.jsx'
import ForbiddenPage from './ForbiddenPage.jsx'
import { getAccessToken } from '../services/authApi.js'
import { fetchMe } from '../services/meApi.js'
import {
  AdminApiError,
  clearFailNextPreview,
  clearFailNextShortlistFetch,
  fetchShortlist,
  previewEmail,
  sendDigest,
  setDecision,
} from '../services/adminApi.js'

const TOAST_DISMISS_MS = 4000
const TOP_N = 3

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

function approvedFingerprint(items) {
  return items
    .filter((item) => item.decision === 'approved' && item.material_status === 'ready')
    .map((item) => item.material_id)
    .sort((a, b) => a - b)
    .join(',')
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
 * Admin Digest triage + preview/send gate (ADMIN-01…07 / D-75…D-89).
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
  const [banner, setBanner] = useState('')
  const [previewItem, setPreviewItem] = useState(null)
  const [emailModal, setEmailModal] = useState(null) // null | loading | error | { preview }
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [sending, setSending] = useState(false)
  const [previewing, setPreviewing] = useState(false)
  const [emailPreviewed, setEmailPreviewed] = useState(false)
  const [previewFingerprint, setPreviewFingerprint] = useState('')
  const [contextText, setContextText] = useState('')
  const [schemaText, setSchemaText] = useState('')
  const [batchSent, setBatchSent] = useState(false)

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
        setEmailPreviewed(false)
        setPreviewFingerprint('')
        setBatchSent(Boolean(dto?.sent_at))
        setBanner('')
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

  const fingerprint = useMemo(() => approvedFingerprint(items), [items])

  useEffect(() => {
    if (emailPreviewed && previewFingerprint && fingerprint !== previewFingerprint) {
      setEmailPreviewed(false)
      setPreviewFingerprint('')
    }
  }, [fingerprint, emailPreviewed, previewFingerprint])

  const approvedReady = useMemo(
    () => items.filter((item) => item.decision === 'approved' && item.material_status === 'ready'),
    [items],
  )
  const approvedDrafts = useMemo(
    () => items.filter((item) => item.decision === 'approved' && item.material_status === 'draft'),
    [items],
  )

  const previewOk =
    emailPreviewed && previewFingerprint === fingerprint && fingerprint.length > 0
  const sendUnlocked =
    approvedReady.length >= 1 &&
    approvedDrafts.length === 0 &&
    previewOk &&
    !batchSent &&
    !batchMeta.sent_at

  const sendHint = useMemo(() => {
    if (batchSent || batchMeta.sent_at) return 'Уже отправлено'
    if (approvedDrafts.length > 0) {
      return 'Уберите черновики из одобренных или дождитесь ready.'
    }
    if (approvedReady.length === 0) {
      return 'Нет одобренных ready-материалов для отправки.'
    }
    if (!previewOk) return 'Сначала откройте превью письма.'
    return 'Превью просмотрено. Можно отправить.'
  }, [approvedDrafts.length, approvedReady.length, batchMeta.sent_at, batchSent, previewOk])

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

  function selectAll() {
    setCheckedIds(new Set(items.map((item) => item.material_id)))
  }

  function selectTopN() {
    const top = [...items]
      .sort((a, b) => a.rank - b.rank)
      .slice(0, TOP_N)
      .map((item) => item.material_id)
    setCheckedIds(new Set(top))
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
    } catch {
      setToast('Не сохранено')
    } finally {
      setMutating(false)
    }
  }

  async function openEmailPreview() {
    setPreviewing(true)
    setEmailModal('loading')
    setBanner('')
    try {
      const preview = await previewEmail()
      const fp = approvedFingerprint(items)
      setEmailPreviewed(true)
      setPreviewFingerprint(fp)
      // If the user closed while loading, do not reopen the modal (D-86 session flag still set).
      setEmailModal((current) => (current === null ? null : { preview }))
    } catch {
      setEmailPreviewed(false)
      setPreviewFingerprint('')
      setEmailModal((current) => (current === null ? null : 'error'))
    } finally {
      setPreviewing(false)
    }
  }

  async function confirmSend() {
    if (sending) return
    setSending(true)
    setBanner('')
    try {
      const result = await sendDigest()
      setBanner(result.message || 'Отправка записана')
      setBatchSent(true)
      setConfirmOpen(false)
    } catch (err) {
      if (err instanceof AdminApiError && err.code === 'ALREADY_SENT') {
        setBanner('Уже отправлено')
        setBatchSent(true)
        setConfirmOpen(false)
      } else {
        setBanner('Рассылка не отправлена')
        setConfirmOpen(false)
      }
    } finally {
      setSending(false)
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
    <section data-testid="admin-digest-page" className="pb-32">
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
              className="inline-flex min-h-11 items-center rounded-full border border-rule px-4 text-sm font-medium text-ink hover:bg-paper-2"
              onClick={selectAll}
            >
              Выбрать все
            </button>
            <button
              type="button"
              className="inline-flex min-h-11 items-center rounded-full border border-rule px-4 text-sm font-medium text-ink hover:bg-paper-2"
              onClick={selectTopN}
            >
              Оставить топ-3
            </button>
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
                    excluded ? 'opacity-70' : '',
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
                    <p className="break-words font-medium text-ink">{item.title}</p>
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
                      {caption ? <span className="text-xs text-muted">{caption}</span> : null}
                    </div>
                  </div>
                  <div className="text-right">
                    {item.score != null ? (
                      <p className="font-mono text-sm text-ink">{item.score}</p>
                    ) : null}
                    <p className="mt-1 max-w-[12rem] break-words text-xs text-muted">
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

      {!isEmpty ? (
        <div
          data-testid="admin-send-footer"
          className="fixed inset-x-0 bottom-0 z-40 border-t border-rule bg-paper/95 backdrop-blur"
        >
          <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <p className="text-sm text-ink-2 break-words" data-testid="admin-send-hint">
                {sendHint}
              </p>
              {approvedDrafts.length > 0 ? (
                <ul className="mt-1 text-xs text-muted">
                  {approvedDrafts.map((d) => (
                    <li key={d.material_id}>
                      {d.title} · draft
                    </li>
                  ))}
                </ul>
              ) : null}
              {banner ? (
                <p className="mt-1 text-sm font-medium text-[oklch(45%_0.13_155)]" role="status">
                  {banner}
                </p>
              ) : null}
            </div>
            <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row">
              <button
                type="button"
                className="inline-flex min-h-11 w-full items-center justify-center rounded-full border border-rule px-4 text-sm font-medium sm:w-auto"
                disabled={previewing || approvedReady.length === 0}
                onClick={openEmailPreview}
              >
                Предпросмотр письма
              </button>
              <button
                type="button"
                className="inline-flex min-h-11 w-full items-center justify-center rounded-full bg-[oklch(45%_0.13_155)] px-4 text-sm font-medium text-paper disabled:cursor-not-allowed disabled:opacity-45 sm:w-auto"
                disabled={!sendUnlocked || sending}
                onClick={() => setConfirmOpen(true)}
              >
                Отправить дайджест →
              </button>
            </div>
          </div>
        </div>
      ) : null}

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
            <p className="mt-4 break-words font-medium text-ink">{previewItem.title}</p>
            <p className="mt-2 break-words text-sm text-ink-2">
              {previewItem.dek || 'Краткое описание недоступно.'}
            </p>
          </div>
        </div>
      ) : null}

      {emailModal ? (
        <div
          className="fixed inset-0 z-[400] flex items-center justify-center bg-ink/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="email-preview-title"
        >
          <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-paper p-6">
            <div className="flex items-start justify-between gap-3">
              <h2 id="email-preview-title" className="text-2xl font-semibold">
                Превью письма
              </h2>
              <button
                type="button"
                className="inline-flex min-h-11 min-w-11 items-center justify-center"
                aria-label="Закрыть"
                onClick={() => setEmailModal(null)}
              >
                ✕
              </button>
            </div>
            {emailModal === 'loading' ? (
              <p className="mt-4 text-sm text-muted">Загрузка…</p>
            ) : emailModal === 'error' ? (
              <div className="mt-4">
                <p className="text-sm text-ink-2">Превью недоступно</p>
                <button
                  type="button"
                  className="mt-4 inline-flex min-h-11 items-center font-medium text-accent hover:underline"
                  onClick={() => {
                    clearFailNextPreview()
                    openEmailPreview()
                  }}
                >
                  Повторить
                </button>
              </div>
            ) : (
              <>
                <p className="mt-2 text-xs text-muted">только одобренные ready</p>
                <p className="mt-3 font-display text-xl font-semibold break-words">
                  {emailModal.preview.subject}
                </p>
                <ul className="mt-4 space-y-2">
                  {emailModal.preview.items.map((row) => (
                    <li key={row.material_id} className="text-sm break-words">
                      {row.rank}. {row.title}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </div>
      ) : null}

      {confirmOpen ? (
        <div
          className="fixed inset-0 z-[400] flex items-center justify-center bg-ink/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirm-send-title"
        >
          <div className="w-full max-w-md rounded-2xl bg-paper p-6">
            <div className="flex items-start justify-between gap-3">
              <h2 id="confirm-send-title" className="text-2xl font-semibold">
                Подтвердите отправку
              </h2>
              <button
                type="button"
                className="inline-flex min-h-11 min-w-11 items-center justify-center"
                aria-label="Закрыть"
                onClick={() => setConfirmOpen(false)}
              >
                ✕
              </button>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-ink-2">
              Будет создан новый выпуск и записана stub-отправка. Живая почта не используется. Материалов:{' '}
              {approvedReady.length}.
            </p>
            <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-end">
              <button
                type="button"
                className="inline-flex min-h-11 items-center justify-center rounded-full border border-rule px-4 text-sm"
                disabled={sending}
                onClick={() => setConfirmOpen(false)}
              >
                Не отправлять
              </button>
              <button
                type="button"
                className="inline-flex min-h-11 items-center justify-center rounded-full bg-[oklch(45%_0.13_155)] px-4 text-sm font-medium text-paper disabled:opacity-55"
                disabled={sending}
                onClick={confirmSend}
              >
                Подтвердить отправку
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  )
}

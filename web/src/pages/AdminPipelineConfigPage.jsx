import { useEffect, useState } from 'react'
import ServiceUnavailable from '../components/ServiceUnavailable.jsx'
import ForbiddenPage from './ForbiddenPage.jsx'
import { getAccessToken } from '../services/authApi.js'
import { MeApiError, fetchMe } from '../services/meApi.js'
import {
  PipelineConfigError,
  fetchPipelineConfig,
  savePipelineConfig,
} from '../services/pipelineConfigApi.js'

/**
 * Admin pipeline config — view + edit the raw YAML config without running the
 * pipeline (PIPE-01/PIPE-03; D-10/D-11/D-12/D-13). Minimal tracer surface:
 * editor + Save toolbar. No run/trigger/scheduler control ships here.
 */
export default function AdminPipelineConfigPage() {
  const [roleState, setRoleState] = useState('loading')
  const [roleKey, setRoleKey] = useState(0)
  const [loadState, setLoadState] = useState('loading')
  const [loadKey, setLoadKey] = useState(0)
  const [yaml, setYaml] = useState('')
  const [savedYaml, setSavedYaml] = useState('')
  const [status, setStatus] = useState('loading')
  const [loadError, setLoadError] = useState('')
  const [saveError, setSaveError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function loadRole() {
      setRoleState('loading')
      try {
        const token = await getAccessToken()
        const me = await fetchMe(token)
        if (!cancelled) {
          setRoleState(me.role === 'admin' ? 'admin' : 'forbidden')
        }
      } catch (err) {
        if (cancelled) return
        // Only authz failures are Forbidden; network/5xx → error + retry.
        if (
          err instanceof MeApiError &&
          (err.code === 'UNAUTHORIZED' || err.code === 'FORBIDDEN')
        ) {
          setRoleState('forbidden')
        } else {
          setRoleState('error')
        }
      }
    }
    loadRole()
    return () => {
      cancelled = true
    }
  }, [roleKey])

  useEffect(() => {
    if (roleState !== 'admin') return undefined
    let cancelled = false
    setLoadState('loading')
    setStatus('loading')
    setLoadError('')
    setSaveError('')
    fetchPipelineConfig()
      .then((dto) => {
        if (cancelled) return
        const text = typeof dto?.yaml === 'string' ? dto.yaml : ''
        setYaml(text)
        setSavedYaml(text)
        setLoadState('ready')
        setStatus(text ? 'ready' : 'empty')
      })
      .catch((err) => {
        if (cancelled) return
        setLoadState('error')
        setLoadError(
          err instanceof PipelineConfigError ? err.message : 'Не удалось загрузить конфиг',
        )
      })
    return () => {
      cancelled = true
    }
  }, [roleState, loadKey])

  const dirty = yaml !== savedYaml

  function reloadRole() {
    setRoleKey((k) => k + 1)
  }

  function reloadConfig() {
    setLoadKey((k) => k + 1)
  }

  function onEdit(nextValue) {
    setYaml(nextValue)
    setSaveError('')
    setStatus(nextValue === savedYaml ? (savedYaml ? 'ready' : 'empty') : 'dirty')
  }

  async function onSave() {
    if (saving || !dirty) return
    setSaving(true)
    setStatus('saving')
    setSaveError('')
    try {
      const dto = await savePipelineConfig(yaml)
      const saved = typeof dto?.yaml === 'string' ? dto.yaml : yaml
      setYaml(saved)
      setSavedYaml(saved)
      setStatus('saved')
    } catch (err) {
      setSaveError(err instanceof PipelineConfigError ? err.message : 'Конфиг не сохранён')
      setStatus('failed')
    } finally {
      setSaving(false)
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

  if (roleState === 'error') {
    return (
      <section data-testid="admin-pipeline-page">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
        <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Конфиг пайплайна</h1>
        <ServiceUnavailable onRetry={reloadRole} />
      </section>
    )
  }

  if (loadState === 'loading') {
    return (
      <section aria-busy="true" data-testid="admin-pipeline-page">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
        <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Конфиг пайплайна</h1>
        <p className="mt-2 text-sm text-muted">Просмотр и правка без запуска пайплайна</p>
        <p data-testid="pipeline-config-loading" className="mt-4 text-sm text-muted">
          Загрузка…
        </p>
      </section>
    )
  }

  if (loadState === 'error') {
    return (
      <section data-testid="admin-pipeline-page">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
        <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Конфиг пайплайна</h1>
        <p className="mt-2 text-sm text-muted">Просмотр и правка без запуска пайплайна</p>
        <p className="mt-4 text-sm text-ink-2">{loadError || 'Не удалось загрузить конфиг'}</p>
        <button
          type="button"
          data-testid="pipeline-config-retry"
          className="mt-4 inline-flex min-h-11 items-center font-medium text-accent hover:underline"
          onClick={reloadConfig}
        >
          Повторить загрузку
        </button>
      </section>
    )
  }

  const statusText =
    status === 'saving'
      ? 'Сохранение…'
      : status === 'saved'
        ? 'Сохранено'
        : status === 'failed'
          ? 'Конфиг не сохранён'
          : status === 'dirty'
            ? 'Есть несохранённые изменения'
            : 'Изменений нет'

  return (
    <section data-testid="admin-pipeline-page" className="pb-16">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted">Админ</p>
      <h1 className="mt-2 font-sans text-3xl font-semibold text-ink">Конфиг пайплайна</h1>
      <p className="mt-2 text-sm text-muted">Просмотр и правка без запуска пайплайна</p>

      <div className="mt-6 flex flex-wrap items-center gap-3" aria-busy={saving}>
        <button
          type="button"
          data-testid="pipeline-config-save"
          className="inline-flex min-h-11 items-center justify-center rounded-full bg-accent px-5 text-sm font-medium text-accent-ink disabled:cursor-not-allowed disabled:opacity-45"
          disabled={!dirty || saving}
          onClick={onSave}
        >
          Сохранить конфиг
        </button>
        <p
          data-testid="pipeline-config-status"
          role="status"
          className="text-sm text-muted"
        >
          {statusText}
        </p>
      </div>

      {saveError ? (
        <p className="mt-3 text-sm text-[oklch(45%_0.14_25)]" role="alert">
          {saveError}
        </p>
      ) : null}

      <textarea
        data-testid="pipeline-config-editor"
        aria-label="YAML конфига пайплайна"
        aria-invalid={Boolean(saveError)}
        spellCheck={false}
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="off"
        wrap="off"
        className="mt-4 min-h-[20rem] max-h-[60vh] w-full overflow-auto rounded-xl border border-rule bg-paper p-3 font-mono text-base leading-relaxed text-ink-2 focus-visible:outline-accent"
        value={yaml}
        placeholder="# YAML конфига пайплайна"
        onChange={(e) => onEdit(e.target.value)}
      />
    </section>
  )
}

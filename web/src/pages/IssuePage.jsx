import { currentIssue, getIssueMaterials } from '../data/mock.js'
import EditorialCallout from '../components/EditorialCallout.jsx'
import IssueToc from '../components/IssueToc.jsx'

export default function IssuePage() {
  const items = getIssueMaterials()

  return (
    <section>
      <p className="text-xs uppercase tracking-wide text-muted">
        Выпуск №{currentIssue.number} · {currentIssue.period}
      </p>
      <h1 className="mt-3 max-w-4xl font-display text-4xl font-semibold leading-tight sm:text-5xl">
        {currentIssue.title}
      </h1>
      <p className="mt-3 text-sm text-ink-2">
        {currentIssue.editor} · {items.length} материалов
      </p>

      <hr className="my-8 border-rule" />

      <EditorialCallout actionTo="/voting" actionLabel="Выбрать тему →">
        <strong>Голосование открыто</strong> до {currentIssue.votingOpenUntil} — выберите тему
        следующего разбора.
      </EditorialCallout>

      <h2 className="mb-6 font-display text-2xl font-semibold">В этом выпуске</h2>
      <IssueToc items={items} />
    </section>
  )
}

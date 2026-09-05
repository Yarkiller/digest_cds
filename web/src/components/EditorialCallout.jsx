import { Link } from 'react-router-dom'

export default function EditorialCallout({ children, actionTo, actionLabel }) {
  return (
    <div className="my-8 flex flex-wrap items-center justify-between gap-4 border border-voting bg-[oklch(94%_0.025_278)] p-5">
      <div className="text-sm text-ink">{children}</div>
      {actionTo && actionLabel ? (
        <Link
          to={actionTo}
          className="inline-flex min-h-11 items-center rounded-full px-3 text-sm text-accent hover:bg-paper-2"
        >
          {actionLabel}
        </Link>
      ) : null}
    </div>
  )
}

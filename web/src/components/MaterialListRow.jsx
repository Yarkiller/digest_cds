import { Link } from 'react-router-dom'

export default function MaterialListRow({ material }) {
  return (
    <Link
      to={`/materials/${material.id}`}
      className="grid grid-cols-[4rem_minmax(0,1fr)] gap-4 border-b border-rule py-5 text-inherit no-underline hover:bg-paper-2 sm:grid-cols-[5rem_minmax(0,1fr)]"
    >
      <img
        src={material.cover}
        alt=""
        width={480}
        height={270}
        className="h-10 w-16 rounded-md border border-rule object-cover sm:h-11 sm:w-20"
      />
      <div className="min-w-0">
        <h3 className="font-display text-lg font-semibold">{material.title}</h3>
        <p className="mt-1 text-sm text-ink-2">{material.snippet}</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {material.tags.map((tag) => (
            <span key={tag} className="rounded-full bg-paper-2 px-2 py-0.5 text-xs text-accent">
              #{tag}
            </span>
          ))}
        </div>
      </div>
    </Link>
  )
}

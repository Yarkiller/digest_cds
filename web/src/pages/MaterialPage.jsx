import { Link, useParams } from 'react-router-dom'
import { getMaterialById } from '../data/mock.js'

export default function MaterialPage() {
  const { id } = useParams()
  const material = getMaterialById(id)

  if (!material) {
    return (
      <section>
        <h1 className="font-display text-3xl font-semibold">Материал не найден</h1>
        <p className="mt-3 text-ink-2">Проверьте ссылку или вернитесь к выпуску.</p>
        <Link to="/" className="mt-6 inline-flex text-accent">
          ← К выпуску
        </Link>
      </section>
    )
  }

  return (
    <article className="max-w-3xl">
      <p className="text-xs uppercase tracking-wide text-muted">
        {material.format} · {material.tags[0]}
      </p>
      <h1 className="mt-3 font-display text-4xl font-semibold sm:text-5xl">{material.title}</h1>
      <p className="mt-3 text-sm text-ink-2">
        {material.date} · provenance: {material.provenance} · ~{material.readingMinutes} мин чтения
      </p>
      <hr className="my-8 border-rule" />

      <img
        src={material.cover}
        alt=""
        width={480}
        height={270}
        className="mb-8 aspect-video w-full rounded-xl border border-rule object-cover"
      />

      <h2 className="font-display text-2xl font-semibold">Резюме</h2>
      <p className="mt-3 leading-relaxed text-ink-2">{material.summary}</p>

      <div className="mt-6 flex flex-wrap gap-2">
        {material.tags.map((tag) => (
          <Link
            key={tag}
            to="/knowledge"
            className="rounded-full bg-paper-2 px-2 py-1 text-xs text-accent no-underline"
          >
            #{tag}
          </Link>
        ))}
      </div>

      <h2 className="mt-10 font-display text-2xl font-semibold">Полный текст</h2>
      {material.body.map((paragraph) => (
        <p key={paragraph} className="mt-4 leading-relaxed text-ink-2">
          {paragraph}
        </p>
      ))}

      <p className="mt-10">
        <Link to="/" className="text-sm text-accent">
          ← К выпуску
        </Link>
      </p>
    </article>
  )
}

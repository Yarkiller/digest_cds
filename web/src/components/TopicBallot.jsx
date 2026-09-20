export default function TopicBallot({ topics, selectedId, onSelect, disabled = false }) {
  return (
    <div role="radiogroup" aria-label="Темы для голосования" className="border-t border-rule">
      {topics.map((topic) => {
        const checked = selectedId === topic.id
        return (
          <button
            key={topic.id}
            type="button"
            role="radio"
            aria-checked={checked}
            disabled={disabled}
            onClick={() => onSelect(topic.id)}
            className={[
              'grid w-full grid-cols-[1.5rem_minmax(0,1fr)] gap-4 border-b border-rule py-5 text-left',
              checked ? 'bg-[oklch(94%_0.025_278)]' : 'hover:bg-paper-2',
              disabled ? 'cursor-not-allowed opacity-70' : '',
            ].join(' ')}
          >
            <span
              className={[
                'mt-1 inline-block size-5 rounded-full border-2',
                checked ? 'border-accent bg-accent' : 'border-[oklch(66%_0.025_270)] bg-paper',
              ].join(' ')}
              aria-hidden="true"
            />
            <span>
              <span className="block font-display text-lg font-semibold">{topic.title}</span>
              <span className="mt-1 block text-xs text-ink-2">
                {topic.materialsCount} материалов · {topic.votes} голосов
              </span>
            </span>
          </button>
        )
      })}
    </div>
  )
}

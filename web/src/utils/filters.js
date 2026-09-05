/**
 * Filter knowledge materials by free-text query and facet values.
 */
export function filterMaterials(items, { query = '', role = '', tag = '', format = '', topic = '' } = {}) {
  const tokens = query
    .toLowerCase()
    .split(/[\s,.#]+/)
    .filter(Boolean)

  return items.filter((item) => {
    if (role && !item.roles.includes(role)) return false
    if (tag && !item.tags.includes(tag)) return false
    if (format && item.format !== format) return false
    if (topic && item.topic !== topic) return false

    if (!tokens.length) return true
    const haystack = `${item.title} ${item.keywords} ${item.tags.join(' ')}`.toLowerCase()
    return tokens.some((token) => haystack.includes(token))
  })
}

export function padIssueNumber(position) {
  return String(position).padStart(2, '0')
}

/**
 * Extract ATX headings from markdown for section TOC.
 * Ids match rehype-slug / github-slugger for ASCII seed headings.
 */

/**
 * @param {string} text
 * @returns {string}
 */
function slugify(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

/**
 * @param {string} markdown
 * @returns {{ id: string, text: string, level: number }[]}
 */
export function extractMarkdownHeadings(markdown) {
  if (!markdown) return []

  const headings = []
  const seen = new Map()
  let inFence = false

  for (const line of markdown.split(/\r?\n/)) {
    if (/^```/.test(line)) {
      inFence = !inFence
      continue
    }
    if (inFence) continue

    const match = /^(#{1,6})\s+(.+?)\s*$/.exec(line)
    if (!match) continue

    const level = match[1].length
    const text = match[2].replace(/\s+#+\s*$/, '').trim()
    if (!text) continue

    let id = slugify(text)
    const count = seen.get(id) ?? 0
    seen.set(id, count + 1)
    if (count > 0) {
      id = `${id}-${count}`
    }

    headings.push({ id, text, level })
  }

  return headings
}

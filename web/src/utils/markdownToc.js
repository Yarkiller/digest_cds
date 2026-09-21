/**
 * Extract ATX headings from markdown for section TOC.
 * Ids match rehype-slug + rehype-sanitize (github-slugger + user-content- clobber).
 */

/** hast-util-sanitize default clobberPrefix — must match rehypeSanitize after rehypeSlug. */
export const HEADING_ID_PREFIX = 'user-content-'

/**
 * @param {string} text
 * @returns {string}
 */
function slugify(text) {
  return text
    .toLowerCase()
    .trim()
    // \p{L}/\p{N}: Cyrillic headings must match rehype-slug (github-slugger).
    .replace(/[^\p{L}\p{N}\s-]/gu, '')
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

    let bare = slugify(text)
    const count = seen.get(bare) ?? 0
    seen.set(bare, count + 1)
    if (count > 0) {
      bare = `${bare}-${count}`
    }

    headings.push({ id: `${HEADING_ID_PREFIX}${bare}`, text, level })
  }

  return headings
}

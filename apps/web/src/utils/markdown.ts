function escapeHtml(input: string) {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function renderInline(input: string) {
  return escapeHtml(input)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
    .replace(
      /\[来源:\s*第(\d+)章\s*([^\]]*)\]/g,
      '<span class="citation-tag" data-chapter="$1">[来源: 第$1章 $2]</span>'
    )
    .replace(
      /\[来源:\s*小说相关内容\]/g,
      '<span class="citation-tag">[来源: 小说相关内容]</span>'
    )
}

export function renderMarkdown(input: string) {
  if (!input.trim()) return ''

  const codeBlocks: string[] = []
  const placeholder = (index: number) => `__CODE_BLOCK_${index}__`

  let content = input.replace(/```([\s\S]*?)```/g, (_, code: string) => {
    const html = `<pre><code>${escapeHtml(code.trim())}</code></pre>`
    codeBlocks.push(html)
    return placeholder(codeBlocks.length - 1)
  })

  const lines = content.split('\n')
  const html: string[] = []
  let inList = false

  const closeList = () => {
    if (inList) {
      html.push('</ul>')
      inList = false
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (!line) {
      closeList()
      continue
    }

    const codeMatch = line.match(/^__CODE_BLOCK_(\d+)__$/)
    if (codeMatch) {
      closeList()
      html.push(codeBlocks[Number(codeMatch[1])])
      continue
    }

    if (/^[-*]\s+/.test(line)) {
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${renderInline(line.replace(/^[-*]\s+/, ''))}</li>`)
      continue
    }

    closeList()

    if (/^>\s+/.test(line)) {
      html.push(`<blockquote>${renderInline(line.replace(/^>\s+/, ''))}</blockquote>`)
      continue
    }

    const heading = line.match(/^(#{1,4})\s+(.*)$/)
    if (heading) {
      const level = heading[1].length
      html.push(`<h${level}>${renderInline(heading[2])}</h${level}>`)
      continue
    }

    html.push(`<p>${renderInline(line)}</p>`)
  }

  closeList()
  content = html.join('')

  return content.replace(/__CODE_BLOCK_(\d+)__/g, (_, index: string) => codeBlocks[Number(index)] || '')
}

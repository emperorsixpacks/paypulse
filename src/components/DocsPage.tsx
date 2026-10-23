import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { BookOpen, ExternalLink } from 'lucide-react'

export function DocsPage() {
  const [content, setContent] = useState<string | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch('/docs/paypulse.md')
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}`)
        return r.text()
      })
      .then(setContent)
      .catch(() => setError(true))
  }, [])

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
          style={{ background: 'var(--accent)' }}
        >
          <BookOpen size={16} style={{ color: '#0d1b2f' }} />
        </div>
        <div>
          <h1 className="display font-semibold text-[var(--ink)] text-lg">PayPulse Docs</h1>
          <p className="text-xs text-[var(--subtle)]">Integration guide, API reference, and architecture</p>
        </div>
        <a
          href="https://github.com/emperorsixpacks/paypulse"
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto flex items-center gap-1.5 text-xs text-[var(--accent)] hover:underline"
        >
          GitHub <ExternalLink size={11} />
        </a>
      </div>

      {/* Content */}
      <div
        className="rounded-2xl border border-[var(--border)] p-6 sm:p-8"
        style={{ background: 'var(--surface)' }}
      >
        {error && (
          <p className="text-sm text-[var(--danger)]">
            Could not load docs. Make sure <code className="mono">/public/docs/paypulse.md</code> exists.
          </p>
        )}
        {!content && !error && (
          <p className="text-sm text-[var(--subtle)] animate-pulse">Loading docs…</p>
        )}
        {content && (
          <div className="docs-prose">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}

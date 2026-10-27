import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { BookOpen, Bot, ExternalLink } from 'lucide-react'

interface Props {
  src?: string
}

export function DocsPage({ src = '/docs/paypulse.md' }: Props) {
  const [content, setContent] = useState<string | null>(null)
  const [error, setError] = useState(false)
  const isSkill = src.endsWith('skill.md')

  useEffect(() => {
    // eslint-disable-next-line react/set-state-in-effect
    setContent(null)
    // eslint-disable-next-line react/set-state-in-effect
    setError(false)
    fetch(src)
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}`)
        return r.text()
      })
      .then(setContent)
      .catch(() => setError(true))
  }, [src])

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
          style={{ background: 'var(--accent)' }}
        >
          {isSkill
            ? <Bot size={16} style={{ color: '#0d1b2f' }} />
            : <BookOpen size={16} style={{ color: '#0d1b2f' }} />}
        </div>
        <div>
          <h1 className="display font-semibold text-[var(--ink)] text-lg">
            {isSkill ? 'PayPulse Agent Skill' : 'PayPulse Docs'}
          </h1>
          <p className="text-xs text-[var(--subtle)]">
            {isSkill
              ? 'Machine-readable setup skill — point your agent at this page'
              : 'Integration guide, API reference, and architecture'}
          </p>
        </div>

        <div className="ml-auto flex items-center gap-3">
          {isSkill && (
            <a
              href="/skill.md"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg font-medium transition-all hover:opacity-80"
              style={{
                background: 'rgba(172,198,233,0.12)',
                border: '1px solid rgba(172,198,233,0.2)',
                color: 'var(--accent)',
              }}
            >
              Raw skill.md <ExternalLink size={11} />
            </a>
          )}
          <a
            href="https://github.com/emperorsixpacks/paypulse"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-[var(--accent)] hover:underline"
          >
            GitHub <ExternalLink size={11} />
          </a>
        </div>
      </div>

      {/* Skill URL callout */}
      {isSkill && (
        <div
          className="rounded-xl border px-4 py-3 mb-6 flex flex-col sm:flex-row sm:items-center gap-2"
          style={{
            background: 'rgba(172,198,233,0.06)',
            borderColor: 'rgba(172,198,233,0.2)',
          }}
        >
          <Bot size={14} className="shrink-0" style={{ color: 'var(--accent)' }} />
          <span className="text-xs text-[var(--ink-2)]">
            Tell your agent:{' '}
            <span className="mono text-[var(--accent)]">
              "Read https://paypulse.cv/skill.md and follow the steps to register yourself on PayPulse."
            </span>
          </span>
        </div>
      )}

      {/* Content */}
      <div
        className="rounded-2xl border border-[var(--border)] p-6 sm:p-8"
        style={{ background: 'var(--surface)' }}
      >
        {error && (
          <p className="text-sm text-[var(--danger)]">
            Could not load{' '}
            <code className="mono">{src}</code>.
          </p>
        )}
        {!content && !error && (
          <p className="text-sm text-[var(--subtle)] animate-pulse">Loading…</p>
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

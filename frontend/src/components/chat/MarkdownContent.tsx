import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Components } from 'react-markdown'

const components: Components = {
  h1: ({ children }) => <h1 className="text-base font-bold mt-3 mb-1">{children}</h1>,
  h2: ({ children }) => <h2 className="text-sm font-bold mt-3 mb-1">{children}</h2>,
  h3: ({ children }) => <h3 className="text-sm font-semibold mt-2 mb-1">{children}</h3>,
  p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-0.5">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-0.5">{children}</ol>,
  li: ({ children }) => <li className="text-sm leading-relaxed">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-gray-300 pl-3 my-2 text-gray-600 italic">
      {children}
    </blockquote>
  ),
  code: ({ children, className }) => {
    const isBlock = className?.startsWith('language-')
    if (isBlock) {
      return (
        <pre className="bg-gray-900 text-gray-100 rounded-lg px-4 py-3 my-2 overflow-x-auto text-xs leading-relaxed">
          <code>{children}</code>
        </pre>
      )
    }
    return (
      <code className="bg-gray-100 text-gray-800 rounded px-1 py-0.5 text-xs font-mono">
        {children}
      </code>
    )
  },
  pre: ({ children }) => <>{children}</>,
  hr: () => <hr className="my-3 border-gray-200" />,
  a: ({ href, children }) => (
    <a href={href} className="text-blue-600 underline hover:text-blue-800" target="_blank" rel="noreferrer">
      {children}
    </a>
  ),
}

interface MarkdownContentProps {
  content: string
  isStreaming?: boolean
}

export function MarkdownContent({ content, isStreaming }: MarkdownContentProps) {
  return (
    <div className="text-sm text-current min-w-0">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
      {isStreaming && (
        <span className="inline-block w-[2px] h-[1em] bg-current ml-0.5 align-middle animate-pulse" />
      )}
    </div>
  )
}

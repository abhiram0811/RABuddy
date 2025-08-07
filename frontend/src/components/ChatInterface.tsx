'use client'

import { useState } from 'react'
import { Send, ThumbsUp, ThumbsDown, MessageCircle } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: Date
}

interface Source {
  source_number?: number
  filename: string
  page_number: number
  relevance_score: number
  text_preview: string
}

interface FeedbackState {
  [queryId: string]: 'positive' | 'negative' | null
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState<FeedbackState>({})

  // Function to render content with highlighted inline citations and proper list formatting
  const renderContentWithCitations = (content: string, sources: Source[] = []) => {
    const citationRegex = /\(Source (\d+)\)/g
    
    // Function to process citations within text
    const processCitations = (text: string, paragraphIndex: number) => {
      const parts = []
      let lastIndex = 0
      let match
      
      // Reset regex
      citationRegex.lastIndex = 0

      while ((match = citationRegex.exec(text)) !== null) {
        // Add text before citation
        if (match.index > lastIndex) {
          parts.push(
            <span key={`${paragraphIndex}-${lastIndex}`}>{text.slice(lastIndex, match.index)}</span>
          )
        }

        // Add highlighted citation
        const sourceNum = parseInt(match[1])
        const source = sources.find(s => s.source_number === sourceNum)
        parts.push(
          <span
            key={`${paragraphIndex}-${match.index}`}
            className="citation-number inline-flex items-center px-1.5 py-0.5 mx-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full cursor-help"
            title={source ? `${source.filename}, Page ${source.page_number}` : `Source ${sourceNum}`}
          >
            {match[0]}
          </span>
        )

        lastIndex = match.index + match[0].length
      }

      // Add remaining text
      if (lastIndex < text.length) {
        parts.push(
          <span key={`${paragraphIndex}-${lastIndex}`}>{text.slice(lastIndex)}</span>
        )
      }

      return parts.length > 0 ? parts : text
    }

    // Split content into paragraphs
    const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim())
    
    return paragraphs.map((paragraph, pIndex) => {
      // Check if this paragraph contains a numbered list pattern
      const listItemRegex = /(\d+)\.\s*([^;]+?)(?=;\s*\d+\.|$)/g
      
      // Check if paragraph contains numbered items separated by semicolons
      if (listItemRegex.test(paragraph)) {
        const items = []
        let match
        listItemRegex.lastIndex = 0
        
        // Extract intro text before the list
        const introMatch = paragraph.match(/^(.+?)(?=\d+\.\s*)/)
        const introText = introMatch ? introMatch[1].trim().replace(/:$/, '') : ''
        
        // Extract list items
        while ((match = listItemRegex.exec(paragraph)) !== null) {
          const itemNumber = match[1]
          const itemText = match[2].trim()
          items.push({ number: itemNumber, text: itemText })
        }
        
        return (
          <div key={pIndex} className="mb-4 last:mb-0">
            {introText && (
              <p className="mb-3 font-medium">
                {processCitations(introText, pIndex)}:
              </p>
            )}
            <ol className="list-none space-y-2 ml-4">
              {items.map((item, itemIndex) => (
                <li key={itemIndex} className="flex">
                  <span className="font-semibold text-csu-green mr-2 min-w-[1.5rem]">
                    {item.number}.
                  </span>
                  <span className="flex-1">
                    {processCitations(item.text, pIndex * 100 + itemIndex)}
                  </span>
                </li>
              ))}
            </ol>
          </div>
        )
      }
      
      // Regular paragraph formatting
      return (
        <p key={pIndex} className="mb-4 last:mb-0">
          {processCitations(paragraph, pIndex)}
        </p>
      )
    })
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://107bc118b418.ngrok-free.app'
      console.log('API URL:', apiUrl)
      console.log('Environment variable:', process.env.NEXT_PUBLIC_API_URL)
      console.log('Sending request to:', `${apiUrl}/api/query`)
      console.log('Request body:', { question: userMessage.content })
      
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000) // 60 second timeout
      
      const response = await fetch(`${apiUrl}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage.content }),
        signal: controller.signal,
      })
      
      clearTimeout(timeoutId)

      console.log('Response status:', response.status)
      console.log('Response ok:', response.ok)

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      console.log('Response data:', data)

      const assistantMessage: Message = {
        id: data.session_id || data.query_id || Date.now().toString(),
        type: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      let errorContent = 'Sorry, I encountered an error. Please try again.'
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorContent = 'The request timed out. The query may be too complex. Please try a simpler question.'
        } else if (error.message.includes('Failed to fetch')) {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://107bc118b418.ngrok-free.app'
          errorContent = `Unable to connect to the backend at ${apiUrl}. Please check the connection.`
        }
      }
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: errorContent,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = async (queryId: string, type: 'positive' | 'negative') => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://107bc118b418.ngrok-free.app'
      await fetch(`${apiUrl}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_id: queryId,
          feedback_type: type,
        }),
      })

      setFeedback(prev => ({ ...prev, [queryId]: type }))
    } catch (error) {
      console.error('Error sending feedback:', error)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Chat Messages */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <MessageCircle className="mx-auto h-12 w-12 mb-4 text-gray-300" />
            <p>Ask me anything about CSU Housing & Dining policies!</p>
            <div className="mt-4 text-sm text-left">
              <p className="font-medium mb-2">Try asking:</p>
              <ul className="space-y-1 text-gray-400">
                <li>• "What's the protocol for lockouts after midnight?"</li>
                <li>• "Who should I contact for facilities emergencies?"</li>
                <li>• "Where can I find the guest policy form?"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg px-4 py-3 ${
                  message.type === 'user'
                    ? 'bg-csu-green text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className={`${message.type === 'assistant' ? 'leading-relaxed space-y-2' : ''}`}>
                  {message.type === 'assistant' && message.sources 
                    ? <div className="formatted-response">{renderContentWithCitations(message.content, message.sources)}</div>
                    : <div className={message.type === 'assistant' ? 'formatted-response' : ''}>{message.content}</div>
                  }
                </div>
                
                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-600 mb-2">Sources Referenced:</p>
                    <div className="space-y-2">
                      {message.sources.map((source, index) => (
                        <div key={index} className="text-xs text-gray-600 bg-gray-50 p-3 rounded-md border-l-4 border-blue-200">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                                  Source {source.source_number || index + 1}
                                </span>
                                <span className="font-medium text-gray-700">{source.filename}</span>
                                <span className="text-gray-500">Page {source.page_number}</span>
                              </div>
                              <p className="text-gray-600 leading-relaxed">{source.text_preview}</p>
                            </div>
                            <span className="ml-2 text-xs text-green-600 font-medium">
                              {Math.round(source.relevance_score * 100)}% match
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Feedback buttons for assistant messages */}
                {message.type === 'assistant' && (
                  <div className="mt-3 pt-3 border-t border-gray-200 flex items-center space-x-2">
                    <span className="text-xs text-gray-500">Was this helpful?</span>
                    <button
                      onClick={() => handleFeedback(message.id, 'positive')}
                      className={`p-1 rounded ${
                        feedback[message.id] === 'positive'
                          ? 'bg-green-100 text-green-600'
                          : 'text-gray-400 hover:text-green-600'
                      }`}
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleFeedback(message.id, 'negative')}
                      className={`p-1 rounded ${
                        feedback[message.id] === 'negative'
                          ? 'bg-red-100 text-red-600'
                          : 'text-gray-400 hover:text-red-600'
                      }`}
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about housing policies, procedures, or emergency contacts..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 resize-none focus:outline-none focus:border-csu-green"
            rows={2}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="bg-csu-green text-white px-4 py-2 rounded-lg hover:bg-csu-green/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
        
        {/* Debug test button */}
        <div className="mt-2 flex space-x-2">
          <button
            onClick={() => {
              console.log('Test button clicked')
              console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
              setInput('test connection')
              setTimeout(() => sendMessage(), 100)
            }}
            className="bg-blue-500 text-white px-3 py-1 rounded text-sm"
          >
            Test Connection
          </button>
          <button
            onClick={() => {
              const testInput = "What should I do for lockouts?"
              setInput(testInput)
              setTimeout(() => sendMessage(), 100)
            }}
            className="bg-purple-500 text-white px-3 py-1 rounded text-sm"
          >
            Test Query
          </button>
        </div>
      </div>
    </div>
  )
}

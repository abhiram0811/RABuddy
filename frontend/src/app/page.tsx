'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import Header from '@/components/Header'

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-csu-green mb-4">
              Welcome to RABuddy
            </h1>
            <p className="text-xl text-gray-600 mb-2">
              Your AI assistant for CSU Housing & Dining Services
            </p>
            <p className="text-gray-500">
              Ask me about policies, procedures, emergency contacts, and more!
            </p>
          </div>
          
          <ChatInterface />
        </div>
      </main>
    </div>
  )
}

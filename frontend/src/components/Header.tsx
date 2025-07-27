'use client'

import { Home } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-csu-green text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Home className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">RABuddy</h1>
              <p className="text-csu-gold text-sm">CSU Housing & Dining Assistant</p>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-csu-gold">Colorado State University</p>
            <p className="text-xs opacity-75">Housing & Dining Services</p>
          </div>
        </div>
      </div>
    </header>
  )
}

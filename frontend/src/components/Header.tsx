'use client'

import { Home, Wifi, WifiOff } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Header() {
  const [isOnline, setIsOnline] = useState(true)
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://107bc118b418.ngrok-free.app'
        const response = await fetch(`${apiUrl}/api/health`, {
          method: 'GET',
          headers: { 
            'Accept': 'application/json',
            'ngrok-skip-browser-warning': 'true'
          }
        })
        
        if (response.ok) {
          setBackendStatus('online')
        } else {
          setBackendStatus('offline')
        }
      } catch (error) {
        console.error('Backend health check failed:', error)
        setBackendStatus('offline')
      }
    }

    // Check immediately
    checkBackendStatus()
    
    // Check every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000)
    
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <header className="csu-header text-white shadow-lg">
      <div className="container mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          {/* Left Section - Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <Home className="h-8 w-8 text-yellow-300" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">RABuddy</h1>
              <p className="text-yellow-300 text-sm font-medium">
                CSU Housing & Dining AI Assistant
              </p>
            </div>
          </div>

          {/* Right Section - Status and University Info */}
          <div className="text-right space-y-1">
            <div className="flex items-center space-x-4 mb-2">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1">
                  {isOnline ? (
                    <Wifi className="h-4 w-4 text-green-300" />
                  ) : (
                    <WifiOff className="h-4 w-4 text-red-300" />
                  )}
                  <span className="text-xs text-gray-200">
                    {isOnline ? 'Online' : 'Offline'}
                  </span>
                </div>
                
                <div className="h-4 w-px bg-white/20"></div>
                
                {/* Backend Status */}
                <div className="flex items-center space-x-2">
                  <div 
                    className={`h-2 w-2 rounded-full ${
                      backendStatus === 'online' 
                        ? 'bg-green-400 status-online' 
                        : backendStatus === 'offline'
                        ? 'bg-red-400 status-offline'
                        : 'bg-yellow-400 animate-pulse'
                    }`}
                  ></div>
                  <span className="text-xs text-gray-200 capitalize">
                    RAG {backendStatus}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <p className="text-yellow-300 text-sm font-semibold">
                Colorado State University
              </p>
              <p className="text-xs text-gray-200 opacity-90">
                Housing & Dining Services
              </p>
            </div>
          </div>
        </div>
        
        {/* Status Bar */}
        <div className="mt-4 pt-3 border-t border-white/20">
          <div className="flex items-center justify-between text-xs text-gray-200">
            <span>
              🏠 Resident Assistant Support System
            </span>
            <span>
              ⚡ Enhanced with AI • 📚 Policy Knowledge Base
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

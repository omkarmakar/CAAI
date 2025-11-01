import './globals.css'
import type { ReactNode } from 'react'
import { AuthProvider } from '@/contexts/AuthContext'

export const metadata = {
  title: 'CAAI - CA AI Agent System',
  description: 'Comprehensive AI Agent System for CA Firms with Authentication',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}

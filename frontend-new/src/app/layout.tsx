import './globals.css'
import { ReactNode } from 'react'
import AuthProvider from '../lib/auth'

export const metadata = {
  title: 'CAAI - Frontend New',
  description: 'New frontend scaffold for CAAI'
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

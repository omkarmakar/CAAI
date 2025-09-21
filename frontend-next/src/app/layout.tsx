import './globals.css'
import type { ReactNode } from 'react'

export const metadata = {
  title: 'CA AI Agent Dashboard',
  description: 'Control and interact with CA AI agents',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

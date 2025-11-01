'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../lib/auth'

export default function LoginPage() {
  const { login } = useAuth()
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await login(username, password)
      router.push('/dashboard')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="container">
      <h2 className="text-xl font-semibold">Login</h2>
      <form onSubmit={onSubmit} className="mt-4 max-w-sm">
        <label className="block mb-2">Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} className="w-full p-2 border rounded" />
        <label className="block mt-3 mb-2">Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" className="w-full p-2 border rounded" />
        {error && <div className="text-red-600 mt-2">{error}</div>}
        <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded">Sign in</button>
      </form>
    </div>
  )
}

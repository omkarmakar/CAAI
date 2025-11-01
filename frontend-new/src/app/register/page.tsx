'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../lib/auth'

export default function RegisterPage() {
  const { register } = useAuth()
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await register({ username, email, password, full_name: fullName })
      router.push('/dashboard')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="container">
      <h2 className="text-xl font-semibold">Register</h2>
      <form onSubmit={onSubmit} className="mt-4 max-w-sm">
        <label className="block mb-2">Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} className="w-full p-2 border rounded" />
        <label className="block mt-3 mb-2">Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-2 border rounded" />
        <label className="block mt-3 mb-2">Full name</label>
        <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full p-2 border rounded" />
        <label className="block mt-3 mb-2">Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" className="w-full p-2 border rounded" />
        {error && <div className="text-red-600 mt-2">{error}</div>}
        <button className="mt-4 px-4 py-2 bg-green-600 text-white rounded">Create account</button>
      </form>
    </div>
  )
}

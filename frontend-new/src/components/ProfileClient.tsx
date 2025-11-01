'use client'

import { useAuth } from '../lib/auth'

export default function ProfileClient() {
  const { user, logout } = useAuth()

  if (!user) return null

  return (
    <section className="mt-4 p-4 border rounded bg-white">
      <h2 className="text-lg font-medium">Welcome, {user.full_name || user.username}</h2>
      <p className="text-sm text-gray-600">Role: {user.role}</p>
      <p className="mt-2 text-sm">Email: {user.email}</p>
      <div className="mt-4">
        <button className="px-3 py-1 bg-red-600 text-white rounded" onClick={() => logout()}>
          Sign out
        </button>
      </div>
    </section>
  )
}

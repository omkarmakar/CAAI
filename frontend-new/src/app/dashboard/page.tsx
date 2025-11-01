import ProtectedClient from '../../components/ProtectedClient'
import ProfileClient from '../../components/ProfileClient'

export default function DashboardPage() {
  return (
    <ProtectedClient>
      <main className="container">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="mt-4">This page is protected — it will show user details when signed in.</p>
        <ProfileClient />
      </main>
    </ProtectedClient>
  )
}

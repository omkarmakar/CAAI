"use client"

import AgentConsole from '../../components/AgentConsole'

export default function AgentsPage() {
  return (
    <main className="container">
      <h1 className="text-2xl font-bold">Agents</h1>
      <p className="mt-2">Interact with available agents. Use your account to run protected actions.</p>
      <div className="mt-6">
        <AgentConsole />
      </div>
    </main>
  )
}

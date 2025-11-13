interface StatsCardsProps {
  totalAgents: number;
  activeAgents: number;
  aiAgents: number;
  totalExecutions: number;
}

export default function StatsCards({ totalAgents, activeAgents, aiAgents, totalExecutions }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">Total Agents</p>
            <p className="text-3xl font-bold text-gray-800">{totalAgents}</p>
          </div>
          <div className="text-4xl opacity-20"></div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">Active Agents</p>
            <p className="text-3xl font-bold text-green-600">{activeAgents}</p>
          </div>
          <div className="text-4xl opacity-20"></div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">AI-Powered</p>
            <p className="text-3xl font-bold text-amber-600">{aiAgents}</p>
          </div>
          <div className="text-4xl opacity-20"></div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm">Executions</p>
            <p className="text-3xl font-bold text-purple-600">{totalExecutions}</p>
          </div>
          <div className="text-4xl opacity-20"></div>
        </div>
      </div>
    </div>
  );
}

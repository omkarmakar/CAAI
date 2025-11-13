interface AgentCardProps {
  name: string;
  agent: any;
  isAIPowered: boolean;
  onExecute: () => void;
}

export default function AgentCard({ name, agent, isAIPowered, onExecute }: AgentCardProps) {
  const actionsCount = Object.keys(agent.actions || {}).length;

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-800 mb-1">{agent.display || name}</h3>
            <p className="text-sm text-gray-500">{name}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            {isAIPowered && (
              <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
                 AI
              </span>
            )}
            <span className={`text-xs px-3 py-1 rounded-full font-semibold ${
              agent.active 
                ? 'bg-green-100 text-green-700' 
                : 'bg-gray-100 text-gray-600'
            }`}>
              {agent.active ? ' Active' : ' Inactive'}
            </span>
          </div>
        </div>

        <div className="space-y-3 mb-4">
          <div className="flex items-center text-sm text-gray-600">
            <span className="mr-2"></span>
            <span><strong>{actionsCount}</strong> available actions</span>
          </div>
          
          {agent.hint && (
            <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded border-l-4 border-blue-500">
               {agent.hint}
            </div>
          )}
        </div>

        <div className="border-t pt-4">
          <button
            onClick={onExecute}
            disabled={!agent.active}
            className={`w-full py-2 px-4 rounded-lg font-semibold transition ${
              agent.active
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
          >
            {agent.active ? ' Execute Agent' : ' Inactive'}
          </button>
        </div>
      </div>
    </div>
  );
}

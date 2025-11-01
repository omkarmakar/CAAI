'use client';

import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Navbar from '@/components/Navbar';
import { motion } from 'framer-motion';

export default function DashboardPage() {
  const { user, canAccessAgent } = useAuth();

  const agents = [
    { name: 'DocAuditAgent', display: 'Document Audit', description: 'Audit and analyze client documents using AI' },
    { name: 'BookBotAgent', display: 'BookBot', description: 'Automate bookkeeping and financial records' },
    { name: 'InsightBotAgent', display: 'Insights', description: 'Generate actionable business insights' },
    { name: 'TaxBot', display: 'TaxBot', description: 'Smart tax filing and computation' },
    { name: 'GSTAgent', display: 'GST Agent', description: 'GST compliance & reconciliation assistance' },
    { name: 'ClientCommAgent', display: 'Client Communication', description: 'Automate client communication workflows' },
    { name: 'ComplianceCheckAgent', display: 'Compliance Checks', description: 'Regulatory and policy compliance validation' },
  ];

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
        <Navbar />

        <main className="max-w-7xl mx-auto py-12 sm:px-6 lg:px-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-5xl font-extrabold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent drop-shadow-sm">
              Welcome to CAAI
            </h1>
            <p className="mt-3 text-lg text-gray-600">Your unified AI workspace for CA operations</p>
            <p className="mt-1 text-sm text-gray-500">
              Logged in as <span className="font-medium text-gray-700">{user?.username}</span>
            </p>
          </motion.div>

          {/* User Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            {[
              {
                title: 'Your Role',
                value: user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'N/A',
                color: 'from-blue-500 to-blue-600',
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                ),
              },
              {
                title: 'Account Status',
                value: user?.is_active ? 'Active' : 'Inactive',
                color: 'from-green-500 to-green-600',
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                ),
              },
              {
                title: 'Available Agents',
                value: `${agents.filter((a) => canAccessAgent(a.name)).length} / ${agents.length}`,
                color: 'from-purple-500 to-indigo-600',
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                ),
              },
            ].map((card, idx) => (
              <motion.div
                key={idx}
                whileHover={{ scale: 1.02 }}
                className="bg-white/70 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg hover:shadow-xl transition-all duration-300 p-6 flex items-center space-x-4"
              >
                <div
                  className={`w-12 h-12 bg-gradient-to-r ${card.color} rounded-xl flex items-center justify-center shadow-md`}
                >
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {card.icon}
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{card.title}</p>
                  <p className="text-xl font-semibold text-gray-900">{card.value}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* AI Agent Suite */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">AI Agent Suite</h2>
              <p className="text-sm text-gray-500">
                {agents.filter((a) => canAccessAgent(a.name)).length} accessible to your role
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {agents.map((agent, idx) => {
                const access = canAccessAgent(agent.name);
                return (
                  <motion.div
                    key={idx}
                    whileHover={access ? { scale: 1.03, y: -4 } : {}}
                    className={`group bg-white/80 backdrop-blur-md rounded-2xl shadow-md border transition-all duration-300 overflow-hidden ${
                      access
                        ? 'hover:shadow-xl hover:border-blue-200 cursor-pointer'
                        : 'border-gray-200 opacity-70 cursor-not-allowed'
                    }`}
                  >
                    <div className="p-6 flex flex-col justify-between h-full">
                      <div>
                        <div className="flex items-center mb-3">
                          <div
                            className={`w-10 h-10 flex items-center justify-center rounded-lg text-white text-sm font-medium ${
                              access ? 'bg-gradient-to-r from-blue-500 to-indigo-600' : 'bg-gray-400'
                            }`}
                          >
                            🤖
                          </div>
                          <h3 className="ml-3 text-lg font-semibold text-gray-900">{agent.display}</h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-4 leading-relaxed">{agent.description}</p>
                      </div>

                      {access ? (
                        <button className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 flex items-center justify-center group-hover:shadow-lg">
                          Launch Agent
                          <svg
                            className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                          </svg>
                        </button>
                      ) : (
                        <div className="w-full bg-gray-100 text-gray-500 px-4 py-2 rounded-lg text-sm font-medium text-center">
                          Requires Higher Access
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </section>
        </main>
      </div>
    </ProtectedRoute>
  );
}

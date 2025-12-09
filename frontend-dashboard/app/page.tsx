'use client';

import { useState, useEffect } from 'react';
import AgentCard from '@/components/AgentCard';
import ExecutionModal from '@/components/ExecutionModal';
import StatsCards from '@/components/StatsCards';
import AuthModal from '@/components/AuthModal';
import AdminPanel from '@/components/AdminPanel';
import UserSettings from '@/components/UserSettings';
import APIClient from '@/lib/apiClient';

const API_BASE_URL = 'http://localhost:8000';

export default function Home() {
  const [agents, setAgents] = useState<any>({});
  const [metrics, setMetrics] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [showUserSettings, setShowUserSettings] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    // Restore auth from localStorage
    const savedToken = localStorage.getItem('authToken');
    const savedUsername = localStorage.getItem('username');
    const savedRole = localStorage.getItem('userRole');
    if (savedToken && savedUsername) {
      setAuthToken(savedToken);
      setUsername(savedUsername);
      setUserRole(savedRole);
    }
    
    // Listen for token refresh events
    const handleTokenRefreshed = (event: any) => {
      setAuthToken(event.detail.token);
    };
    
    const handleAuthExpired = () => {
      setAuthToken(null);
      setUsername(null);
      setUserRole(null);
      setShowAuthModal(true);
    };
    
    window.addEventListener('tokenRefreshed', handleTokenRefreshed);
    window.addEventListener('authExpired', handleAuthExpired);
    
    loadData();
    const interval = setInterval(checkBackendStatus, 30000);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('tokenRefreshed', handleTokenRefreshed);
      window.removeEventListener('authExpired', handleAuthExpired);
    };
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/overview`);
      if (response.ok) {
        setBackendStatus('online');
      } else {
        setBackendStatus('offline');
      }
    } catch (error) {
      setBackendStatus('offline');
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [agentsRes, metricsRes, overviewRes] = await Promise.all([
        fetch(`${API_BASE_URL}/agents`),
        fetch(`${API_BASE_URL}/agents/metrics`),
        fetch(`${API_BASE_URL}/overview`)
      ]);

      if (agentsRes.ok) {
        const agentsData = await agentsRes.json();
        setAgents(agentsData);
        setBackendStatus('online');
      }
      
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      setBackendStatus('offline');
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = (agentName: string) => {
    if (!authToken) {
      setShowAuthModal(true);
      return;
    }
    setSelectedAgent(agentName);
  };

  const handleAuthSuccess = async (token: string, user: string) => {
    setAuthToken(token);
    setUsername(user);
    localStorage.setItem('authToken', token);
    localStorage.setItem('username', user);
    setShowAuthModal(false);

    // Fetch user profile to get role
    try {
      const userData = await APIClient.fetchJSON('/auth/me');
      setUserRole(userData.role);
      localStorage.setItem('userRole', userData.role);
    } catch (error) {
      console.error('Failed to fetch user profile');
    }
  };

  const handleUsernameUpdate = (newUsername: string) => {
    setUsername(newUsername);
    localStorage.setItem('username', newUsername);
  };

  const handleLogout = () => {
    setAuthToken(null);
    setUsername(null);
    setUserRole(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('username');
    localStorage.removeItem('userRole');
  };

  const aiPoweredAgents = Object.keys(agents);

  const filteredAgents = Object.entries(agents).filter(([name, agent]: any) => {
    const matchesSearch = name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.display?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (filterStatus === 'active') return matchesSearch && agent.active;
    if (filterStatus === 'inactive') return matchesSearch && !agent.active;
    if (filterStatus === 'ai') return matchesSearch && aiPoweredAgents.includes(name);
    return matchesSearch;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl"></div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">CAAI Dashboard</h1>
                <p className="text-sm text-gray-600">AI-Powered CA Agent System</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className={`w-3 h-3 rounded-full ${
                  backendStatus === 'online' ? 'bg-green-500' :
                  backendStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'
                }`}></span>
                <span className="text-sm text-gray-600 capitalize">{backendStatus}</span>
              </div>
              {username && (
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                  <span className="text-sm text-gray-700">👤 {username}</span>
                  {userRole && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      userRole === 'superadmin' ? 'bg-pink-100 text-pink-700' :
                      userRole === 'admin' ? 'bg-red-100 text-red-700' :
                      userRole === 'senior_ca' ? 'bg-purple-100 text-purple-700' :
                      userRole === 'ca' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-200 text-gray-600'
                    }`}>
                      {userRole}
                    </span>
                  )}
                </div>
              )}
              {authToken && (userRole === 'admin' || userRole === 'superadmin') && (
                <button
                  onClick={() => setShowAdminPanel(true)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  👑 Manage Users
                </button>
              )}
              {authToken && (
                <button
                  onClick={() => setShowUserSettings(true)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
                >
                  ⚙️ Settings
                </button>
              )}
              {authToken ? (
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                >
                  Logout
                </button>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                >
                  Login
                </button>
              )}
              <button 
                onClick={loadData}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
              >
                <span>🔄</span> Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Stats Cards */}
        <StatsCards 
          totalAgents={Object.keys(agents).length}
          activeAgents={Object.values(agents).filter((a: any) => a.active).length}
          aiAgents={Object.keys(agents).length}
          totalExecutions={metrics?.metrics?.reduce((sum: number, m: any) => sum + m.executions, 0) || 0}
        />

        {/* Search and Filter */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search agents..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent text-gray-900 bg-white"
            />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 text-gray-900 bg-white"
            >
              <option value="all">All Agents</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
              <option value="ai">AI-Powered Only</option>
            </select>
          </div>
        </div>

        {/* Agents Grid */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.map(([name, agent]: any) => (
              <AgentCard
                key={name}
                name={name}
                agent={agent}
                isAIPowered={aiPoweredAgents.includes(name)}
                onExecute={() => handleExecute(name)}
              />
            ))}
          </div>
        )}

        {filteredAgents.length === 0 && !loading && (
          <div className="text-center py-20">
            <p className="text-gray-500 text-lg">No agents found matching your criteria</p>
          </div>
        )}
      </main>

      {/* Execution Modal */}
      {selectedAgent && agents[selectedAgent] && (
        <ExecutionModal
          agentName={selectedAgent}
          agentData={agents[selectedAgent]}
          onClose={() => setSelectedAgent(null)}
          apiBaseUrl={API_BASE_URL}
          authToken={authToken}
        />
      )}

      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onSuccess={handleAuthSuccess}
          apiBaseUrl={API_BASE_URL}
        />
      )}

      {showAdminPanel && authToken && (userRole === 'admin' || userRole === 'superadmin') && (
        <AdminPanel
          authToken={authToken}
          apiBaseUrl={API_BASE_URL}
          onClose={() => setShowAdminPanel(false)}
        />
      )}

      {showUserSettings && authToken && username && (
        <UserSettings
          authToken={authToken}
          username={username}
          onClose={() => setShowUserSettings(false)}
          onUpdate={handleUsernameUpdate}
        />
      )}
    </div>
  );
}

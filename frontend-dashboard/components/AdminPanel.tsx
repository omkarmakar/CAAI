'use client';

import { useState, useEffect } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface AdminPanelProps {
  authToken: string;
  apiBaseUrl: string;
  onClose: () => void;
}

export default function AdminPanel({ authToken, apiBaseUrl, onClose }: AdminPanelProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingUser, setEditingUser] = useState<number | null>(null);
  const [newRole, setNewRole] = useState('');
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'user'
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/auth/users`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load users');
      }

      const data = await response.json();
      setUsers(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId: number, role: string) => {
    try {
      const response = await fetch(`${apiBaseUrl}/auth/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role })
      });

      if (!response.ok) {
        throw new Error('Failed to update user');
      }

      await loadUsers();
      setEditingUser(null);
      setNewRole('');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const createUser = async () => {
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`${apiBaseUrl}/auth/admin/create-user`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newUser)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create user');
      }

      setSuccess(`User "${newUser.username}" created successfully!`);
      setShowCreateUser(false);
      setNewUser({ username: '', email: '', full_name: '', password: '', role: 'user' });
      await loadUsers();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const toggleUserStatus = async (userId: number, currentStatus: boolean) => {
    try {
      const response = await fetch(`${apiBaseUrl}/auth/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: !currentStatus })
      });

      if (!response.ok) {
        throw new Error('Failed to update user status');
      }

      await loadUsers();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const resetUserPassword = async (userId: number, username: string) => {
    const newPassword = prompt(`Enter new password for ${username}:`);
    if (!newPassword) return;

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password: newPassword })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to reset password');
      }

      setSuccess(`Password reset successfully for ${username}`);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const editUser = async (userId: number, field: string, currentValue: string) => {
    const newValue = prompt(`Enter new ${field}:`, currentValue);
    if (!newValue || newValue === currentValue) return;

    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ [field]: newValue })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || `Failed to update ${field}`);
      }

      setSuccess(`${field} updated successfully`);
      await loadUsers();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-700';
      case 'senior_ca': return 'bg-purple-100 text-purple-700';
      case 'ca': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">👑 Admin Panel</h2>
            <p className="text-sm text-gray-600">Manage users and their roles</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg flex justify-between items-center">
              <span>{error}</span>
              <button onClick={() => setError(null)} className="text-red-900">×</button>
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-lg flex justify-between items-center">
              <span>{success}</span>
              <button onClick={() => setSuccess(null)} className="text-green-900">×</button>
            </div>
          )}

          <div className="mb-4 flex justify-between items-center">
            <button
              onClick={() => setShowCreateUser(!showCreateUser)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              {showCreateUser ? '✕ Cancel' : '+ Create New User'}
            </button>
          </div>

          {showCreateUser && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h3 className="font-semibold text-lg mb-4">Create New User</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Username*</label>
                  <input
                    type="text"
                    value={newUser.username}
                    onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-gray-900 bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email*</label>
                  <input
                    type="email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-gray-900 bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name*</label>
                  <input
                    type="text"
                    value={newUser.full_name}
                    onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-gray-900 bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password*</label>
                  <input
                    type="password"
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-gray-900 bg-white"
                    minLength={8}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Role*</label>
                  <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-gray-900 bg-white"
                  >
                    <option value="user">User</option>
                    <option value="ca">CA</option>
                    <option value="senior_ca">Senior CA</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button
                  onClick={createUser}
                  disabled={!newUser.username || !newUser.email || !newUser.full_name || !newUser.password}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create User
                </button>
                <button
                  onClick={() => {
                    setShowCreateUser(false);
                    setNewUser({ username: '', email: '', full_name: '', password: '', role: 'user' });
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 border-b">
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">User</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Role</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Last Login</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div>
                          <div className="font-medium text-gray-900">{user.full_name}</div>
                          <div className="text-sm text-gray-500">@{user.username}</div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{user.email}</td>
                      <td className="px-4 py-3">
                        {editingUser === user.id ? (
                          <div className="flex gap-2">
                            <select
                              value={newRole}
                              onChange={(e) => setNewRole(e.target.value)}
                              className="px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                            >
                              <option value="">Select...</option>
                              <option value="user">User</option>
                              <option value="ca">CA</option>
                              <option value="senior_ca">Senior CA</option>
                              <option value="admin">Admin</option>
                            </select>
                            <button
                              onClick={() => updateUserRole(user.id, newRole)}
                              className="px-2 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                              disabled={!newRole}
                            >
                              ✓
                            </button>
                            <button
                              onClick={() => {
                                setEditingUser(null);
                                setNewRole('');
                              }}
                              className="px-2 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400"
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                            {user.role}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => toggleUserStatus(user.id, user.is_active)}
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            user.is_active 
                              ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                              : 'bg-red-100 text-red-700 hover:bg-red-200'
                          }`}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button
                            onClick={() => {
                              setEditingUser(user.id);
                              setNewRole(user.role);
                            }}
                            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                            title="Change Role"
                          >
                            👤
                          </button>
                          <button
                            onClick={() => resetUserPassword(user.id, user.username)}
                            className="px-3 py-1 bg-yellow-600 text-white rounded text-sm hover:bg-yellow-700"
                            title="Reset Password"
                          >
                            🔑
                          </button>
                          <button
                            onClick={() => editUser(user.id, 'username', user.username)}
                            className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
                            title="Edit Username"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => editUser(user.id, 'email', user.email)}
                            className="px-3 py-1 bg-teal-600 text-white rounded text-sm hover:bg-teal-700"
                            title="Edit Email"
                          >
                            📧
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {users.length === 0 && !loading && (
            <div className="text-center py-20 text-gray-500">
              No users found
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Total Users: <span className="font-semibold">{users.length}</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

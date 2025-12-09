'use client';

import { useState, useEffect } from 'react';
import APIClient from '@/lib/apiClient';

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
      const data = await APIClient.fetchJSON('/auth/users');
      setUsers(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId: number, role: string) => {
    try {
      await APIClient.put(`/auth/users/${userId}`, { role });
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
      await APIClient.post('/auth/admin/create-user', newUser);
      setSuccess('User created successfully!');
      await loadUsers();
      setShowCreateUser(false);
      setNewUser({
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'user'
      });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const toggleUserStatus = async (userId: number, currentStatus: boolean) => {
    try {
      await APIClient.put(`/auth/users/${userId}`, { is_active: !currentStatus });
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
      await APIClient.put(`/auth/users/${userId}`, { password: newPassword });
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
      await APIClient.put(`/auth/users/${userId}`, { [field]: newValue });
      setSuccess(`${field} updated successfully`);
      await loadUsers();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'superadmin': return 'Super Admin';
      case 'admin': return 'Admin';
      case 'senior_ca': return 'Senior CA';
      case 'ca': return 'CA';
      case 'user': return 'User';
      default: return role;
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'superadmin': return 'bg-pink-100 text-pink-700';
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
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">👑 User Management</h2>
            <p className="text-sm text-gray-600 mt-1">Manage system users and permissions</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Messages */}
        {error && (
          <div className="mx-6 mt-4 p-3 rounded-lg bg-red-50 text-red-700">
            {error}
          </div>
        )}
        {success && (
          <div className="mx-6 mt-4 p-3 rounded-lg bg-green-50 text-green-700">
            {success}
          </div>
        )}

        {/* Create User Button */}
        <div className="px-6 py-4 border-b">
          <button
            onClick={() => setShowCreateUser(!showCreateUser)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            {showCreateUser ? '✕ Cancel' : '➕ Create New User'}
          </button>
        </div>

        {/* Create User Form */}
        {showCreateUser && (
          <div className="px-6 py-4 bg-gray-50 border-b">
            <h3 className="font-semibold text-gray-800 mb-4">Create New User</h3>
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Username"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                className="px-4 py-2 border rounded-lg text-gray-900 bg-white"
              />
              <input
                type="email"
                placeholder="Email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                className="px-4 py-2 border rounded-lg text-gray-900 bg-white"
              />
              <input
                type="text"
                placeholder="Full Name"
                value={newUser.full_name}
                onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                className="px-4 py-2 border rounded-lg text-gray-900 bg-white"
              />
              <input
                type="password"
                placeholder="Password (min 8 chars)"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                className="px-4 py-2 border rounded-lg text-gray-900 bg-white"
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                className="px-4 py-2 border rounded-lg text-gray-900 bg-white"
              >
                <option value="user">User</option>
                <option value="ca">CA</option>
                <option value="senior_ca">Senior CA</option>
                <option value="admin">Admin</option>
                <option value="superadmin">Super Admin</option>
              </select>
              <button
                onClick={createUser}
                disabled={!newUser.username || !newUser.email || !newUser.password || newUser.password.length < 8}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create User
              </button>
            </div>
          </div>
        )}

        {/* Users List */}
        <div className="overflow-y-auto max-h-[calc(90vh-300px)] p-6">
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {users.map((user) => (
                <div key={user.id} className="border rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg text-gray-900">{user.username}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                          {getRoleLabel(user.role)}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          user.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>📧 {user.email}</p>
                        <p>👤 {user.full_name}</p>
                        <p>📅 Joined: {new Date(user.created_at).toLocaleDateString()}</p>
                        {user.last_login && (
                          <p>🔐 Last login: {new Date(user.last_login).toLocaleString()}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      {editingUser === user.id ? (
                        <div className="flex gap-2">
                          <select
                            value={newRole}
                            onChange={(e) => setNewRole(e.target.value)}
                            className="px-3 py-1 border rounded text-sm text-gray-900 bg-white"
                          >
                            <option value="">Select Role</option>
                            <option value="user">User</option>
                            <option value="ca">CA</option>
                            <option value="senior_ca">Senior CA</option>
                            <option value="admin">Admin</option>
                            <option value="superadmin">Super Admin</option>
                          </select>
                          <button
                            onClick={() => updateUserRole(user.id, newRole)}
                            disabled={!newRole}
                            className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => {
                              setEditingUser(null);
                              setNewRole('');
                            }}
                            className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <>
                          <button
                            onClick={() => {
                              setEditingUser(user.id);
                              setNewRole(user.role);
                            }}
                            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                          >
                            Change Role
                          </button>
                          <button
                            onClick={() => toggleUserStatus(user.id, user.is_active)}
                            className={`px-3 py-1 rounded text-sm text-white ${
                              user.is_active ? 'bg-orange-600 hover:bg-orange-700' : 'bg-green-600 hover:bg-green-700'
                            }`}
                          >
                            {user.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                          <button
                            onClick={() => resetUserPassword(user.id, user.username)}
                            className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
                          >
                            Reset Password
                          </button>
                          <button
                            onClick={() => editUser(user.id, 'email', user.email)}
                            className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                          >
                            Edit Email
                          </button>
                          <button
                            onClick={() => editUser(user.id, 'full_name', user.full_name)}
                            className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                          >
                            Edit Name
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

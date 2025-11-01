'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Navbar from '@/components/Navbar';
import api from '@/lib/api';
import { User, AdminUserUpdate } from '@/types/auth';

export default function AdminPage() {
  const { hasRole } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<AdminUserUpdate>({});

  const [addModalOpen, setAddModalOpen] = useState(false);
  const [addForm, setAddForm] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'user',
    is_active: true,
    is_verified: false,
  });
  const [search, setSearch] = useState('');
  const [saving, setSaving] = useState(false);
  const [adding, setAdding] = useState(false);

  const searchRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/auth/users');
      setUsers(response.data || []);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      full_name: user.full_name || '',
      email: user.email || '',
      role: user.role,
      is_active: user.is_active,
      is_verified: user.is_verified,
    });
    // scroll into view on mobile (small UX nicety)
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSave = async () => {
    if (!editingUser) return;
    try {
      setSaving(true);
      await api.put(`/auth/users/${editingUser.id}`, formData);
      setEditingUser(null);
      setFormData({});
      await fetchUsers();
    } catch (error) {
      console.error('Failed to update user:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      await api.delete(`/auth/users/${userId}`);
      await fetchUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  const handleAddUser = async () => {
    // basic validation
    if (!addForm.username || !addForm.email || !addForm.password) {
      alert('username, email and password are required');
      return;
    }
    try {
      setAdding(true);
      await api.post('/auth/users', {
        username: addForm.username,
        email: addForm.email,
        password: addForm.password,
        full_name: addForm.full_name || undefined,
        role: addForm.role,
        is_active: addForm.is_active,
        is_verified: addForm.is_verified,
      });
      setAddModalOpen(false);
      setAddForm({
        username: '',
        email: '',
        password: '',
        full_name: '',
        role: 'user',
        is_active: true,
        is_verified: false,
      });
      await fetchUsers();
    } catch (error) {
      console.error('Failed to add user:', error);
    } finally {
      setAdding(false);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'superadmin':
        return 'bg-gradient-to-r from-purple-100 to-purple-50 text-purple-800';
      case 'admin':
        return 'bg-gradient-to-r from-blue-100 to-blue-50 text-blue-800';
      default:
        return 'bg-gradient-to-r from-green-100 to-green-50 text-green-800';
    }
  };

  // live filtered list (username, email, full_name)
  const filteredUsers = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return users;
    return users.filter((u) =>
      `${u.username} ${u.email} ${u.full_name || ''}`.toLowerCase().includes(q)
    );
  }, [users, search]);

  return (
    <ProtectedRoute requiredRole="admin">
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
        <Navbar />

        <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="flex items-center justify-center mb-4">
              <div className="p-3 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-lg">
                <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
            </div>

            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              User Management
            </h1>
            <p className="mt-2 text-lg text-gray-600">Manage users, roles, and system permissions</p>
          </div>

          {/* Controls: Search + stats */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <div className="flex-1">
              <div className="relative max-w-xl">
                <input
                  ref={searchRef}
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search users by username, email or name..."
                  className="w-full pl-10 pr-4 py-3 rounded-2xl bg-white/60 backdrop-blur-sm border border-white/30 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <div className="absolute left-3 top-0 bottom-0 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1110.5 3a7.5 7.5 0 016.15 13.65z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden sm:inline-flex items-center bg-white/60 backdrop-blur-sm rounded-2xl px-4 py-2 border border-white/30 shadow-sm">
                <div className="text-sm text-gray-600 mr-4">Total</div>
                <div className="font-semibold text-gray-900">{users.length}</div>
              </div>

              <div>
                <button
                  onClick={() => { setAddModalOpen(true); setTimeout(() => searchRef.current?.focus(), 120); }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md hover:scale-[1.02] transition-transform"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add User
                </button>
              </div>
            </div>
          </div>

          {/* Stats cards row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="bg-white/60 backdrop-blur-md rounded-2xl p-5 border border-white/30 shadow-sm">
              <p className="text-sm text-gray-500">Total Users</p>
              <p className="text-2xl font-semibold text-gray-900">{users.length}</p>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="bg-white/60 backdrop-blur-md rounded-2xl p-5 border border-white/30 shadow-sm">
              <p className="text-sm text-gray-500">Active</p>
              <p className="text-2xl font-semibold text-green-600">{users.filter((u) => u.is_active).length}</p>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="bg-white/60 backdrop-blur-md rounded-2xl p-5 border border-white/30 shadow-sm">
              <p className="text-sm text-gray-500">Admins</p>
              <p className="text-2xl font-semibold text-purple-600">{users.filter((u) => u.role === 'admin' || u.role === 'superadmin').length}</p>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.15 } }} className="bg-white/60 backdrop-blur-md rounded-2xl p-5 border border-white/30 shadow-sm">
              <p className="text-sm text-gray-500">Regular Users</p>
              <p className="text-2xl font-semibold text-indigo-600">{users.filter((u) => u.role === 'user').length}</p>
            </motion.div>
          </div>

          {/* User grid (card style) */}
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="text-center">
                <div className="animate-spin rounded-full h-14 w-14 border-b-4 border-indigo-600 mx-auto"></div>
                <p className="mt-3 text-gray-600">Loading users...</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <AnimatePresence>
                {filteredUsers.length === 0 && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="col-span-full text-center text-gray-500 py-12 bg-white/40 backdrop-blur rounded-2xl border border-white/20">
                    No users found.
                  </motion.div>
                )}

                {filteredUsers.map((u) => {
                  const roleBadge = getRoleBadgeColor(u.role);
                  return (
                    <motion.div
                      key={u.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      whileHover={{ scale: 1.02, translateY: -4 }}
                      transition={{ type: 'spring', stiffness: 220, damping: 18 }}
                      className="relative bg-white/50 backdrop-blur rounded-2xl p-5 border border-white/20 shadow-md"
                    >
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0">
                          <div className="h-14 w-14 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center text-white text-lg font-semibold shadow-lg">
                            {u.username?.charAt(0).toUpperCase() || 'U'}
                          </div>
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 truncate">{u.full_name || u.username}</h3>
                              <div className="text-sm text-gray-500">@{u.username}</div>
                              <div className="text-xs text-gray-400 mt-1 truncate">{u.email}</div>
                            </div>

                            <div className="text-right">
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${roleBadge}`}>
                                {u.role.charAt(0).toUpperCase() + u.role.slice(1)}
                              </span>
                              <div className="mt-2 text-xs text-gray-400">
                                {new Date(u.created_at).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <p className="mt-3 text-sm text-gray-600">{u.is_verified ? 'Verified user' : 'Unverified user'}</p>

                          {/* actions */}
                          <div className="mt-4 flex gap-2">
                            <button
                              onClick={() => handleEdit(u)}
                              className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm shadow-sm hover:opacity-95 transition"
                            >
                              Edit
                            </button>

                            {hasRole('superadmin') && u.username !== 'superadmin' && (
                              <button
                                onClick={() => handleDelete(u.id)}
                                className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-red-50 text-red-600 border border-red-100 text-sm hover:bg-red-100 transition"
                              >
                                Delete
                              </button>
                            )}

                            <div className="ml-auto text-sm">
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${u.is_active ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                                {u.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          )}

          {/* Edit modal (animated) */}
          <AnimatePresence>
            {editingUser && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-40 flex items-start justify-center pt-16 px-4"
              >
                <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setEditingUser(null)} />

                <motion.div
                  initial={{ scale: 0.95, y: -10 }}
                  animate={{ scale: 1, y: 0 }}
                  exit={{ scale: 0.95, y: -10 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 22 }}
                  className="relative w-full max-w-lg bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/20 shadow-xl"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Edit User — {editingUser.username}</h3>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm text-gray-700">Full name</label>
                      <input
                        value={formData.full_name || ''}
                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                        className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-700">Email</label>
                      <input
                        value={formData.email || ''}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60"
                      />
                    </div>

                    {hasRole('superadmin') && (
                      <div>
                        <label className="block text-sm text-gray-700">Role</label>
                        <select
                          value={formData.role || ''}
                          onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                          className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60"
                        >
                          <option value="user">User</option>
                          <option value="admin">Admin</option>
                          <option value="superadmin">SuperAdmin</option>
                        </select>
                      </div>
                    )}

                    <div className="flex items-center gap-6">
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={!!formData.is_active}
                          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                          className="h-4 w-4"
                        />
                        Active
                      </label>

                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={!!formData.is_verified}
                          onChange={(e) => setFormData({ ...formData, is_verified: e.target.checked })}
                          className="h-4 w-4"
                        />
                        Verified
                      </label>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end gap-3">
                    <button onClick={() => setEditingUser(null)} className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300">
                      Cancel
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:opacity-95"
                    >
                      {saving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Add User modal */}
          <AnimatePresence>
            {addModalOpen && (
              <motion.div className="fixed inset-0 z-40 flex items-start justify-center pt-16 px-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setAddModalOpen(false)} />

                <motion.div initial={{ scale: 0.96, y: -8 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.96, y: -8 }} transition={{ type: 'spring', stiffness: 280, damping: 26 }} className="relative w-full max-w-lg bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/20 shadow-xl">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Add New User</h3>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm text-gray-700">Username</label>
                      <input value={addForm.username} onChange={(e) => setAddForm({ ...addForm, username: e.target.value })} className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60" />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-700">Email</label>
                      <input value={addForm.email} onChange={(e) => setAddForm({ ...addForm, email: e.target.value })} className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60" />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-700">Password</label>
                      <input type="password" value={addForm.password} onChange={(e) => setAddForm({ ...addForm, password: e.target.value })} className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60" />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-700">Full name (optional)</label>
                      <input value={addForm.full_name} onChange={(e) => setAddForm({ ...addForm, full_name: e.target.value })} className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60" />
                    </div>

                    <div className="flex gap-3">
                      <div className="flex-1">
                        <label className="block text-sm text-gray-700">Role</label>
                        <select value={addForm.role} onChange={(e) => setAddForm({ ...addForm, role: e.target.value as any })} className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60">
                          <option value="user">User</option>
                          <option value="admin">Admin</option>
                          <option value="superadmin">SuperAdmin</option>
                        </select>
                      </div>

                      <div className="flex-1">
                        <label className="block text-sm text-gray-700">Active</label>
                        <select value={String(addForm.is_active)} onChange={(e) => setAddForm({ ...addForm, is_active: e.target.value === 'true' })} className="mt-1 block w-full rounded-lg border border-white/30 px-3 py-2 bg-white/60">
                          <option value="true">Yes</option>
                          <option value="false">No</option>
                        </select>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <label className="flex items-center gap-2 text-sm">
                        <input type="checkbox" checked={addForm.is_verified} onChange={(e) => setAddForm({ ...addForm, is_verified: e.target.checked })} className="h-4 w-4" />
                        Verified
                      </label>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end gap-3">
                    <button onClick={() => setAddModalOpen(false)} className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300">Cancel</button>
                    <button onClick={handleAddUser} disabled={adding} className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:opacity-95">
                      {adding ? 'Creating...' : 'Create User'}
                    </button>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Floating Add Button for mobile */}
        <div className="fixed right-6 bottom-6 z-50 md:hidden">
          <button onClick={() => setAddModalOpen(true)} className="p-4 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-xl">
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>
    </ProtectedRoute>
  );
}

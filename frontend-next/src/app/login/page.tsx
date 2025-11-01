'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';

export default function LoginPage() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(credentials);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const userRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    userRef.current?.focus();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-blue-50 flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="max-w-md w-full space-y-8 backdrop-blur-xl bg-white/70 rounded-3xl shadow-2xl border border-white/40 p-8"
      >
        {/* Header */}
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 120, damping: 10 }}
            className="mx-auto h-16 w-16 bg-gradient-to-tr from-indigo-600 via-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg"
          >
            <svg
              className="h-8 w-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </motion.div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 tracking-tight">
            Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-blue-500">CAAI</span>
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            <span className="font-medium text-indigo-500">CA AI Agent System</span> – Intelligent Financial Analytics
          </p>
        </div>

        {/* Login Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow-sm"
            >
              <p className="text-sm text-red-700">{error}</p>
            </motion.div>
          )}

          <div className="space-y-4">
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Username
              </label>
              <input
                ref={userRef}
                id="username"
                name="username"
                type="text"
                required
                value={credentials.username}
                onChange={handleChange}
                onFocus={() => setError('')}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-white/60 backdrop-blur focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 placeholder-gray-400 shadow-sm transition duration-200"
                placeholder="Enter your username"
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={credentials.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-white/60 backdrop-blur focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 placeholder-gray-400 shadow-sm transition duration-200"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  onClick={() => setShowPassword(s => !s)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-500 hover:text-indigo-600"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={remember}
                onChange={e => setRemember(e.target.checked)}
                className="rounded text-indigo-600 mr-2"
              />
              Remember me
            </label>
            <a
              href="#"
              onClick={e => {
                e.preventDefault();
                alert('Password reset not configured in this demo.');
              }}
              className="text-indigo-500 hover:text-indigo-700 font-medium"
            >
              Forgot password?
            </a>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-lg font-semibold text-white bg-gradient-to-r from-indigo-600 to-blue-500 hover:from-indigo-700 hover:to-blue-600 focus:ring-2 focus:ring-indigo-400 focus:outline-none shadow-md disabled:opacity-60"
          >
            {loading ? (
              <div className="flex justify-center items-center gap-2">
                <svg
                  className="animate-spin h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 
                    0 5.373 0 12h4zm2 5.291A7.962 7.962 0
                    014 12H0c0 3.042 1.135 5.824 3 
                    7.938l3-2.647z"
                  ></path>
                </svg>
                Signing in...
              </div>
            ) : (
              'Sign In'
            )}
          </motion.button>

          <p className="text-center text-sm text-gray-600">
            Don’t have an account?{' '}
            <Link
              href="/register"
              className="text-indigo-600 hover:text-indigo-800 font-medium underline"
            >
              Sign up here
            </Link>
          </p>
        </form>

        {/* Demo Accounts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100"
        >
          <h3 className="text-lg font-semibold text-blue-900 flex items-center gap-2 mb-3">
            <svg
              className="h-5 w-5 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 
                12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Demo Accounts
          </h3>

          <div className="grid grid-cols-1 gap-3">
            {[
              {
                role: 'SuperAdmin',
                color: 'text-purple-700',
                creds: 'superadmin / SuperAdmin@123',
                desc: 'Full system access, user management',
              },
              {
                role: 'Admin',
                color: 'text-blue-700',
                creds: 'admin / Admin@123',
                desc: 'Advanced agents, user oversight',
              },
              {
                role: 'User',
                color: 'text-green-700',
                creds: 'user1 / User@123',
                desc: 'Basic agents, standard access',
              },
            ].map(({ role, color, creds, desc }) => (
              <div
                key={role}
                className="bg-white rounded-lg p-3 border border-blue-200 shadow-sm hover:shadow-md transition-all"
              >
                <div className="flex justify-between items-center">
                  <span className={`font-medium ${color}`}>{role}</span>
                  <span className="text-sm text-gray-600 font-mono">{creds}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{desc}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-center text-xs text-amber-600 bg-amber-50 px-3 py-2 rounded-full border border-amber-200">
            <svg
              className="h-4 w-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 
                4h13.856c1.54 0 2.502-1.667 
                1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 
                0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            Change passwords in production
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

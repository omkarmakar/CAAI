'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-900 via-blue-900 to-purple-800 relative overflow-hidden">
      {/* Background gradient blur orbs */}
      <div className="absolute -top-20 -left-20 w-72 h-72 bg-blue-600/40 rounded-full blur-3xl" />
      <div className="absolute -bottom-20 -right-20 w-72 h-72 bg-purple-600/40 rounded-full blur-3xl" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="relative z-10 max-w-md w-full bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl p-8 text-center"
      >
        <motion.h2
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400"
        >
          Access Denied
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="mt-3 text-gray-300 text-sm"
        >
          You don’t have permission to access this resource.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8"
        >
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center px-6 py-2.5 text-sm font-semibold rounded-full 
                       text-white bg-gradient-to-r from-blue-500 to-purple-600 
                       hover:from-blue-600 hover:to-purple-700 shadow-md hover:shadow-blue-500/30
                       transition-all duration-300 ease-out"
          >
            Go to Dashboard
          </Link>
        </motion.div>
      </motion.div>
    </div>
  );
}

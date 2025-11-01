'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';



export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.push('/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
            <div className="absolute inset-0 rounded-full border-t-4 border-blue-200 animate-pulse"></div>
          </div>
          <p className="mt-6 text-gray-700 font-medium text-lg">Loading CAAI...</p>
          <p className="text-gray-500 text-sm">CA AI Agent System</p>
        </div>
      </div>
    );
  }

  return null;
}

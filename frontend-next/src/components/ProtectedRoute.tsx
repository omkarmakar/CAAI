'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'user' | 'admin' | 'superadmin';
  requiredAgent?: string;
}

export default function ProtectedRoute({
  children,
  requiredRole = 'user',
  requiredAgent,
}: ProtectedRouteProps) {
  const { user, loading, hasRole, canAccessAgent } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login');
        return;
      }

      if (!hasRole(requiredRole)) {
        router.push('/unauthorized');
        return;
      }

      if (requiredAgent && !canAccessAgent(requiredAgent)) {
        router.push('/unauthorized');
        return;
      }
    }
  }, [user, loading, hasRole, canAccessAgent, router, requiredRole, requiredAgent]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  if (!hasRole(requiredRole)) {
    return null;
  }

  if (requiredAgent && !canAccessAgent(requiredAgent)) {
    return null;
  }

  return <>{children}</>;
}
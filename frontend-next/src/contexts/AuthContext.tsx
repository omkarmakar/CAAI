'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import api from '@/lib/api';
import { User, LoginCredentials, RegisterData, AuthResponse } from '@/types/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
  hasRole: (role: 'user' | 'admin' | 'superadmin') => boolean;
  canAccessAgent: (agentName: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const roleHierarchy = {
    user: 0,
    admin: 1,
    superadmin: 2,
  };

  const agentAccess = {
    user: [
      'DocAuditAgent',
      'BookBotAgent',
      'InsightBotAgent',
      'TaxBot',
      'GSTAgent',
    ],
    admin: [
      'DocAuditAgent',
      'BookBotAgent',
      'InsightBotAgent',
      'TaxBot',
      'GSTAgent',
      'ClientCommAgent',
      'ComplianceCheckAgent',
    ],
    superadmin: ['*'], // Access to all agents
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = Cookies.get('access_token');
    if (token) {
      try {
        const response = await api.get('/auth/me');
        setUser(response.data);
      } catch (error) {
        // Token is invalid, remove it
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
      }
    }
    setLoading(false);
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await api.post<AuthResponse>('/auth/login', credentials);
      const { access_token, refresh_token, user: userData } = response.data;

      Cookies.set('access_token', access_token, { expires: 1 });
      Cookies.set('refresh_token', refresh_token, { expires: 7 });

      setUser(userData);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const response = await api.post<AuthResponse>('/auth/register', data);
      const { access_token, refresh_token, user: userData } = response.data;

      Cookies.set('access_token', access_token, { expires: 1 });
      Cookies.set('refresh_token', refresh_token, { expires: 7 });

      setUser(userData);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const logout = () => {
    api.post('/auth/logout').catch(() => {
      // Ignore logout API errors
    });

    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      logout();
    }
  };

  const hasRole = (requiredRole: 'user' | 'admin' | 'superadmin'): boolean => {
    if (!user) return false;
    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;
    return userLevel >= requiredLevel;
  };

  const canAccessAgent = (agentName: string): boolean => {
    if (!user) return false;
    const allowedAgents = agentAccess[user.role] || [];
    return allowedAgents.includes('*') || allowedAgents.includes(agentName);
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated: !!user,
    hasRole,
    canAccessAgent,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
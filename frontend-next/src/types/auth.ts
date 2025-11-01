export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: 'user' | 'admin' | 'superadmin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

export interface UserUpdate {
  full_name?: string;
  email?: string;
}

export interface AdminUserUpdate extends UserUpdate {
  role?: 'user' | 'admin' | 'superadmin';
  is_active?: boolean;
  is_verified?: boolean;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  action: string;
  resource?: string;
  details?: string;
  ip_address?: string;
  timestamp: string;
  status: string;
}
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  avatar_url?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface GoogleLoginUrlResponse {
  login_url: string;
}

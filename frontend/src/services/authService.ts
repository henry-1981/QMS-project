import client from '../api/client';
import type { User, GoogleLoginUrlResponse } from '../types/auth';

const TOKEN_KEY = 'token';

export const authService = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken(): void {
    localStorage.removeItem(TOKEN_KEY);
  },

  async getGoogleLoginUrl(): Promise<string> {
    const response = await client.get<GoogleLoginUrlResponse>('/auth/google/login');
    return response.data.login_url;
  },

  redirectToGoogleLogin(): void {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    window.location.href = `${apiUrl}/auth/google/login`;
  },

  async getCurrentUser(): Promise<User> {
    const response = await client.get<User>('/auth/me');
    return response.data;
  },

  async validateToken(): Promise<User | null> {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      const user = await this.getCurrentUser();
      return user;
    } catch {
      this.removeToken();
      return null;
    }
  },

  logout(): void {
    this.removeToken();
    window.location.href = '/login';
  },

  handleOAuthCallback(token: string): void {
    this.setToken(token);
  },

  extractTokenFromUrl(): string | null {
    const params = new URLSearchParams(window.location.search);
    return params.get('token');
  },

  extractErrorFromUrl(): string | null {
    const params = new URLSearchParams(window.location.search);
    return params.get('error');
  },
};

import {
  createContext,
  useReducer,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import type { User, AuthState } from '../types/auth';
import { authService } from '../services/authService';

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE' }
  | { type: 'LOGOUT' };

interface AuthContextType extends AuthState {
  login: (token: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  redirectToGoogleLogin: () => void;
}

const initialState: AuthState = {
  user: null,
  token: authService.getToken(),
  isAuthenticated: false,
  isLoading: true,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
      };
    case 'AUTH_SUCCESS':
      return {
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'AUTH_FAILURE':
      return {
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'LOGOUT':
      return {
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    default:
      return state;
  }
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const checkAuth = useCallback(async () => {
    const token = authService.getToken();
    
    if (!token) {
      dispatch({ type: 'AUTH_FAILURE' });
      return;
    }

    dispatch({ type: 'AUTH_START' });

    try {
      const user = await authService.getCurrentUser();
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, token },
      });
    } catch {
      authService.removeToken();
      dispatch({ type: 'AUTH_FAILURE' });
    }
  }, []);

  const login = useCallback(async (token: string) => {
    authService.setToken(token);
    dispatch({ type: 'AUTH_START' });

    try {
      const user = await authService.getCurrentUser();
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, token },
      });
    } catch {
      authService.removeToken();
      dispatch({ type: 'AUTH_FAILURE' });
      throw new Error('로그인에 실패했습니다.');
    }
  }, []);

  const logout = useCallback(() => {
    authService.removeToken();
    dispatch({ type: 'LOGOUT' });
  }, []);

  const redirectToGoogleLogin = useCallback(() => {
    authService.redirectToGoogleLogin();
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    checkAuth,
    redirectToGoogleLogin,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

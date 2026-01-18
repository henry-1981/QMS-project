import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/authService';
import { Loader2, AlertCircle } from 'lucide-react';

export function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(location.search);
      const token = params.get('access_token') || params.get('token');
      const errorParam = params.get('error');
      const errorDescription = params.get('error_description');

      if (errorParam) {
        setError(errorDescription || '로그인에 실패했습니다. 다시 시도해주세요.');
        return;
      }

      if (!token) {
        setError('인증 토큰이 없습니다.');
        return;
      }

      try {
        await login(token);
        const from = (location.state as { from?: Location })?.from?.pathname || '/';
        navigate(from, { replace: true });
      } catch {
        setError('로그인 처리 중 오류가 발생했습니다.');
        authService.removeToken();
      }
    };

    handleCallback();
  }, [location, login, navigate]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">로그인 실패</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/login')}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            로그인 페이지로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="flex flex-col items-center space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <p className="text-gray-600 text-sm">로그인 처리 중...</p>
      </div>
    </div>
  );
}

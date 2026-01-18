import { useEffect, useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, Activity, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading, redirectToGoogleLogin } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);

  const urlParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const errorFromUrl = urlParams.get('error');
  const errorDescription = urlParams.get('error_description');

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      const from = (location.state as { from?: Location })?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, isLoading, location, navigate]);

  const handleGoogleLogin = () => {
    setIsRedirecting(true);
    redirectToGoogleLogin();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 text-sm">인증 확인 중...</p>
        </div>
      </div>
    );
  }

  const errorMessage = errorFromUrl 
    ? (errorDescription || '로그인에 실패했습니다. 다시 시도해주세요.')
    : null;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-blue-100 rounded-full blur-3xl opacity-50"></div>
        <div className="absolute top-1/2 -left-24 w-72 h-72 bg-indigo-100 rounded-full blur-3xl opacity-50"></div>
        <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-slate-200 rounded-full blur-3xl opacity-30"></div>
      </div>

      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 z-10 overflow-hidden">
        <div className="bg-white p-8 pb-6 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-2xl mb-6 shadow-sm">
            <ShieldCheck className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2 tracking-tight">QMS Agent System</h1>
          <p className="text-slate-500 text-sm font-medium">의료기기 품질경영시스템</p>
        </div>

        <div className="px-8 pb-8 pt-2">
          {errorMessage && (
            <div className="mb-6 p-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg flex items-center">
               <span className="mr-2">&#9888;&#65039;</span> {errorMessage}
            </div>
          )}

          <div className="space-y-6">
            <div className="text-center">
              <p className="text-slate-600 text-sm leading-relaxed mb-6">
                안전하고 효율적인 의료기기 품질 관리를 위한<br />
                지능형 AI 에이전트 시스템입니다.
              </p>
            </div>

            <button
              onClick={handleGoogleLogin}
              disabled={isRedirecting}
              className="w-full flex items-center justify-center gap-3 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-medium py-3 px-4 rounded-xl transition-all duration-200 shadow-sm hover:shadow group relative overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRedirecting ? (
                 <div className="w-5 h-5 border-2 border-slate-600 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      fill="#4285F4"
                    />
                    <path
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      fill="#34A853"
                    />
                    <path
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      fill="#FBBC05"
                    />
                    <path
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      fill="#EA4335"
                    />
                  </svg>
                  <span>Google로 계속하기</span>
                </>
              )}
            </button>

            <div className="pt-4 border-t border-slate-100">
               <div className="flex items-center justify-center gap-6 text-xs text-slate-400">
                  <div className="flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-green-500" />
                    <span>ISO 13485 Compliant</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Activity className="w-3 h-3 text-blue-500" />
                    <span>Real-time Monitoring</span>
                  </div>
               </div>
            </div>
          </div>
        </div>
        
        <div className="bg-slate-50 p-4 text-center border-t border-slate-100">
          <p className="text-xs text-slate-400">
            &copy; {new Date().getFullYear()} QMS Agent System. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

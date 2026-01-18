import { Outlet, Link } from 'react-router-dom';
import { LayoutDashboard, FileText, Activity, ShieldCheck, Users, Settings, LogOut, User } from 'lucide-react';
import { GeminiModelSelector } from '../components/GeminiModelSelector';
import { useAuth } from '../hooks/useAuth';

const SidebarItem = ({ icon: Icon, label, to }: { icon: React.ComponentType<{ size?: number }>, label: string, to: string }) => (
  <Link
    to={to}
    className="flex items-center space-x-3 px-4 py-3 text-gray-600 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </Link>
);

export const Layout = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const getInitials = (name: string | undefined) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200 shadow-sm fixed h-full">
        <div className="p-6 border-b border-gray-100">
          <h1 className="text-2xl font-bold text-blue-600">QMS Agent</h1>
          <p className="text-xs text-gray-500 mt-1">Medical Device QMS</p>
        </div>

        <nav className="p-4 space-y-1">
          <SidebarItem icon={LayoutDashboard} label="Dashboard" to="/" />
          <SidebarItem icon={FileText} label="Design Changes" to="/design-changes" />
          <SidebarItem icon={Activity} label="Risk Management" to="/risk-management" />
          <SidebarItem icon={ShieldCheck} label="Regulatory" to="/regulatory" />
          <SidebarItem icon={Users} label="Agents" to="/agents" />
          <SidebarItem icon={Settings} label="Settings" to="/settings" />
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 min-w-0">
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.full_name}
                  className="w-8 h-8 rounded-full flex-shrink-0"
                />
              ) : (
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-medium text-blue-600">
                    {getInitials(user?.full_name)}
                  </span>
                </div>
              )}
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-700 truncate">
                  {user?.full_name || '사용자'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.role || 'user'}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              title="로그아웃"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      <main className="ml-64 flex-1 p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-800">Overview</h2>
          <div className="flex items-center space-x-6">
            <GeminiModelSelector />
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-sm text-gray-600">System Active</span>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-white border border-gray-200 rounded-lg">
              <User size={16} className="text-gray-500" />
              <span className="text-sm font-medium text-gray-700">
                {user?.username || '사용자'}
              </span>
            </div>
          </div>
        </header>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 min-h-[calc(100vh-12rem)] p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

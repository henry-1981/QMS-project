import { Outlet, Link } from 'react-router-dom';
import { LayoutDashboard, FileText, Activity, ShieldCheck, Users, Settings } from 'lucide-react';

const SidebarItem = ({ icon: Icon, label, to }: { icon: any, label: string, to: string }) => (
  <Link 
    to={to} 
    className="flex items-center space-x-3 px-4 py-3 text-gray-600 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </Link>
);

export const Layout = () => {
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
      </aside>

      <main className="ml-64 flex-1 p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-800">Overview</h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-sm text-gray-600">System Active</span>
            </div>
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="font-bold text-gray-600">U</span>
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

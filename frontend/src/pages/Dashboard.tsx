import type { LucideIcon } from 'lucide-react';
import { BarChart3, AlertTriangle, FileCheck, Activity } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  icon: LucideIcon;
  color: string;
}

const StatCard = ({ title, value, change, icon: Icon, color }: StatCardProps) => (
  <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <h3 className="text-2xl font-bold mt-2 text-gray-900">{value}</h3>
      </div>
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
    <div className="mt-4 flex items-center text-sm">
      <span className="text-green-500 font-medium">{change}</span>
      <span className="text-gray-400 ml-2">vs last month</span>
    </div>
  </div>
);

export const Dashboard = () => {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Active Projects" 
          value="12" 
          change="+2" 
          icon={BarChart3} 
          color="bg-blue-500" 
        />
        <StatCard 
          title="Open Risks" 
          value="5" 
          change="-1" 
          icon={AlertTriangle} 
          color="bg-orange-500" 
        />
        <StatCard 
          title="Pending Approvals" 
          value="8" 
          change="+3" 
          icon={FileCheck} 
          color="bg-green-500" 
        />
        <StatCard 
          title="System Health" 
          value="98%" 
          change="+1%" 
          icon={Activity} 
          color="bg-purple-500" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Design Changes</h3>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">
                    DC
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">UI Update for Login Screen</h4>
                    <p className="text-sm text-gray-500">DCR-2024-00{i} • Design Engineer</p>
                  </div>
                </div>
                <span className="px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded-full">
                  In Review
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Agent Activities</h3>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start space-x-4 p-4 border-b border-gray-50 last:border-0">
                <div className="w-2 h-2 mt-2 bg-green-500 rounded-full flex-shrink-0"></div>
                <div>
                  <p className="text-sm text-gray-800">
                    <span className="font-semibold">RA Agent</span> completed regulatory impact analysis for DCR-2024-00{i}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">2 hours ago</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

import { AlertTriangle, TrendingUp, ShieldAlert } from 'lucide-react';

export const RiskManagement = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Risk Management</h1>
        <div className="flex space-x-3">
          <button className="px-4 py-2 bg-white border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50">
            Export Report
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            New Risk Assessment
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-700">Total Risks</h3>
            <AlertTriangle className="text-orange-500" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-900">42</p>
          <p className="text-sm text-gray-500 mt-1">Acive in Risk Register</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-700">High Risks</h3>
            <ShieldAlert className="text-red-500" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-900">3</p>
          <p className="text-sm text-gray-500 mt-1">Requiring immediate mitigation</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-700">Risk Reduction</h3>
            <TrendingUp className="text-green-500" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-900">85%</p>
          <p className="text-sm text-gray-500 mt-1">Mitigation effectiveness</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-6">Recent Risk Assessments</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 text-gray-500 text-sm">
              <tr>
                <th className="px-4 py-3 text-left rounded-l-lg">ID</th>
                <th className="px-4 py-3 text-left">Hazard</th>
                <th className="px-4 py-3 text-left">Situation</th>
                <th className="px-4 py-3 text-left">Initial Risk</th>
                <th className="px-4 py-3 text-left">Residual Risk</th>
                <th className="px-4 py-3 text-left rounded-r-lg">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {[1, 2, 3].map((i) => (
                <tr key={i} className="group hover:bg-gray-50">
                  <td className="px-4 py-4 text-sm font-medium text-gray-900">RSK-00{i}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">Battery Overheating</td>
                  <td className="px-4 py-4 text-sm text-gray-600">Prolonged usage while charging</td>
                  <td className="px-4 py-4">
                    <span className="px-2 py-1 text-xs font-bold text-red-600 bg-red-100 rounded">High (16)</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="px-2 py-1 text-xs font-bold text-green-600 bg-green-100 rounded">Low (4)</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="px-2 py-1 text-xs font-medium text-gray-600 bg-gray-100 rounded-full">
                      Monitored
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

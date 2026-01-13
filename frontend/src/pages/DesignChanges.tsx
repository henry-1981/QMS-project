import { Plus, Search, Filter } from 'lucide-react';

export const DesignChanges = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Design Changes</h1>
        <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          <Plus size={20} />
          <span>New Request</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search changes..." 
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50">
            <Filter size={18} />
            <span>Filter</span>
          </button>
        </div>

        <table className="w-full">
          <thead className="bg-gray-50 text-gray-500 text-sm">
            <tr>
              <th className="px-6 py-3 text-left font-medium">Change ID</th>
              <th className="px-6 py-3 text-left font-medium">Title</th>
              <th className="px-6 py-3 text-left font-medium">Type</th>
              <th className="px-6 py-3 text-left font-medium">Status</th>
              <th className="px-6 py-3 text-left font-medium">Assignee</th>
              <th className="px-6 py-3 text-left font-medium">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="hover:bg-gray-50 transition-colors cursor-pointer">
                <td className="px-6 py-4 text-sm font-medium text-blue-600">DCR-2024-00{i}</td>
                <td className="px-6 py-4 text-sm text-gray-800">Update Battery Module Specs</td>
                <td className="px-6 py-4 text-sm text-gray-600">Modification</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs font-medium text-orange-600 bg-orange-50 rounded-full">
                    RA Review
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs">HJ</div>
                    <span>Hong Gil-dong</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">2024-01-1{i}</td>
              </tr>
            ))}
          </tbody>
        </table>
        
        <div className="p-4 border-t border-gray-100 flex justify-center">
          <button className="text-sm text-gray-500 hover:text-blue-600">Load More</button>
        </div>
      </div>
    </div>
  );
};

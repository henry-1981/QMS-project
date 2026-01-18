import React, { useState } from 'react';
import { 
  Shield, 
  FileCheck, 
  CheckCircle, 
  ChevronDown, 
  ChevronUp, 
  Download, 
  ExternalLink, 
  Search,
  Filter,
  FileText,
  AlertTriangle,
  Activity,
  Globe
} from 'lucide-react';

interface ComplianceStat {
  title: string;
  value: string;
  status: 'good' | 'warning' | 'danger';
  change: string;
  icon: React.ElementType;
}

interface AnalysisRecord {
  id: string;
  changeId: string;
  date: string;
  impact: 'high' | 'medium' | 'low';
  requiredActions: string;
  status: 'reviewing' | 'completed' | 'pending';
}

interface ChecklistItem {
  id: string;
  requirement: string;
  description: string;
  status: 'compliant' | 'partial' | 'non_compliant';
  relatedDoc?: string;
}

interface ChecklistCategory {
  id: string;
  title: string;
  items: ChecklistItem[];
}

interface RegulatoryDoc {
  id: string;
  title: string;
  type: string;
  version: string;
  status: 'approved' | 'draft' | 'obsolete';
  date: string;
}

const stats: ComplianceStat[] = [
  { title: 'ISO 13485 준수율', value: '98%', status: 'good', change: '+2%', icon: Shield },
  { title: 'MFDS 요구사항', value: '100%', status: 'good', change: '0%', icon: Globe },
  { title: 'IEC 62304 적합성', value: '92%', status: 'warning', change: '-1%', icon: Activity },
  { title: '문서 완성도', value: '85%', status: 'warning', change: '+5%', icon: FileText },
];

const recentAnalyses: AnalysisRecord[] = [
  { id: 'RA-2024-001', changeId: 'DCR-2024-003', date: '2024-03-15', impact: 'high', requiredActions: '기술문서 개정, 위험관리 재평가', status: 'reviewing' },
  { id: 'RA-2024-002', changeId: 'DCR-2024-002', date: '2024-03-14', impact: 'low', requiredActions: '설계이력파일(DHF) 업데이트', status: 'completed' },
  { id: 'RA-2024-003', changeId: 'DCR-2024-001', date: '2024-03-10', impact: 'medium', requiredActions: '사용성 평가 계획서 수정', status: 'pending' },
];

const checklistCategories: ChecklistCategory[] = [
  {
    id: 'iso13485',
    title: 'ISO 13485:2016 요구사항',
    items: [
      { id: '7.3.1', requirement: '설계 및 개발 일반', description: '절차 문서화 및 유지관리', status: 'compliant', relatedDoc: 'SOP-730' },
      { id: '7.3.2', requirement: '설계 및 개발 기획', description: '계획 수립 및 업데이트', status: 'compliant', relatedDoc: 'PLN-101' },
      { id: '7.3.3', requirement: '설계 및 개발 입력', description: '입력 요구사항 정의 및 검토', status: 'partial', relatedDoc: 'RS-201' },
    ]
  },
  {
    id: 'mfds',
    title: 'MFDS 의료기기 제조 및 품질관리 기준',
    items: [
      { id: 'kgmp-1', requirement: '시설 및 환경 관리', description: '청정도 관리 기준 준수', status: 'compliant', relatedDoc: 'SOP-601' },
      { id: 'kgmp-2', requirement: '문서 기록 관리', description: '기록 보존 기한 준수', status: 'compliant', relatedDoc: 'SOP-402' },
    ]
  }
];

const documents: RegulatoryDoc[] = [
  { id: 'doc-1', title: '품질 매뉴얼', type: 'QM', version: '4.0', status: 'approved', date: '2024-01-10' },
  { id: 'doc-2', title: '설계 관리 절차서', type: 'SOP', version: '2.1', status: 'approved', date: '2023-11-20' },
  { id: 'doc-3', title: '위험 관리 보고서', type: 'RMR', version: '1.2', status: 'draft', date: '2024-03-15' },
  { id: 'doc-4', title: '임상 평가 보고서', type: 'CER', version: '1.0', status: 'approved', date: '2023-12-05' },
];

const StatCard = ({ stat }: { stat: ComplianceStat }) => {
  const getColor = (status: string) => {
    switch (status) {
      case 'good': return 'text-green-600 bg-green-50';
      case 'warning': return 'text-orange-600 bg-orange-50';
      case 'danger': return 'text-red-600 bg-red-50';
      default: return 'text-blue-600 bg-blue-50';
    }
  };

  const Icon = stat.icon;

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-gray-500">{stat.title}</p>
          <h3 className="text-2xl font-bold mt-2 text-gray-900">{stat.value}</h3>
        </div>
        <div className={`p-3 rounded-lg ${getColor(stat.status)}`}>
          <Icon size={24} />
        </div>
      </div>
      <div className="mt-4 flex items-center text-sm">
        <span className={stat.change.startsWith('+') ? 'text-green-500 font-medium' : stat.change === '0%' ? 'text-gray-500 font-medium' : 'text-red-500 font-medium'}>
          {stat.change}
        </span>
        <span className="text-gray-400 ml-2">지난달 대비</span>
      </div>
    </div>
  );
};

const StatusBadge = ({ status, type }: { status: string, type: 'impact' | 'status' | 'check' }) => {
  let colorClass = '';
  let label = '';

  if (type === 'impact') {
    switch (status) {
      case 'high': colorClass = 'bg-red-50 text-red-700 border-red-100'; label = '높음'; break;
      case 'medium': colorClass = 'bg-orange-50 text-orange-700 border-orange-100'; label = '중간'; break;
      case 'low': colorClass = 'bg-green-50 text-green-700 border-green-100'; label = '낮음'; break;
    }
  } else if (type === 'status') {
    switch (status) {
      case 'reviewing': colorClass = 'bg-blue-50 text-blue-700 border-blue-100'; label = '검토중'; break;
      case 'completed': colorClass = 'bg-green-50 text-green-700 border-green-100'; label = '완료'; break;
      case 'pending': colorClass = 'bg-gray-50 text-gray-700 border-gray-100'; label = '보류'; break;
    }
  } else if (type === 'check') {
    switch (status) {
      case 'compliant': colorClass = 'bg-green-50 text-green-700 border-green-100'; label = '적합'; break;
      case 'partial': colorClass = 'bg-yellow-50 text-yellow-700 border-yellow-100'; label = '부분 적합'; break;
      case 'non_compliant': colorClass = 'bg-red-50 text-red-700 border-red-100'; label = '부적합'; break;
    }
  }

  if (!label) {
     if (status === 'approved') { colorClass = 'bg-green-50 text-green-700 border-green-100'; label = '승인됨'; }
     else if (status === 'draft') { colorClass = 'bg-gray-50 text-gray-700 border-gray-100'; label = '초안'; }
     else if (status === 'obsolete') { colorClass = 'bg-red-50 text-red-700 border-red-100'; label = '폐기'; }
     else { label = status; }
  }

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClass}`}>
      {label}
    </span>
  );
};

const ChecklistSection = () => {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ 'iso13485': true });

  const toggle = (id: string) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <CheckCircle size={18} className="text-blue-600" />
          규제 요구사항 체크리스트
        </h3>
        <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">전체 보고서 다운로드</button>
      </div>
      <div className="divide-y divide-gray-100">
        {checklistCategories.map(cat => (
          <div key={cat.id} className="bg-white">
            <button 
              onClick={() => toggle(cat.id)}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
            >
              <span className="font-medium text-gray-900">{cat.title}</span>
              {expanded[cat.id] ? <ChevronUp size={20} className="text-gray-400" /> : <ChevronDown size={20} className="text-gray-400" />}
            </button>
            {expanded[cat.id] && (
              <div className="bg-gray-50/50 p-4 pt-0">
                <div className="space-y-3">
                  {cat.items.map(item => (
                    <div key={item.id} className="bg-white p-3 rounded-lg border border-gray-100 flex items-center justify-between shadow-sm">
                      <div className="flex items-start gap-3">
                        <div className={`mt-1 w-5 h-5 rounded border flex items-center justify-center ${item.status === 'compliant' ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-300'}`}>
                          {item.status === 'compliant' && <CheckCircle size={14} />}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900 text-sm">{item.id}</span>
                            <span className="text-gray-900 text-sm">{item.requirement}</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{item.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        {item.relatedDoc && (
                          <span className="text-xs text-gray-400 flex items-center gap-1">
                            <FileText size={12} />
                            {item.relatedDoc}
                          </span>
                        )}
                        <StatusBadge status={item.status} type="check" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export const Regulatory = () => {
  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">규제 준수 관리</h1>
        <p className="text-gray-500 mt-1">ISO 13485 및 MFDS 의료기기 규제 요구사항 준수 현황을 모니터링합니다.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={index} stat={stat} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-100 flex justify-between items-center">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                <Shield size={18} className="text-blue-600" />
                최근 규제 분석 이력
              </h3>
              <div className="flex items-center gap-2">
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                  <Search size={18} />
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                  <Filter size={18} />
                </button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-100">
                  <tr>
                    <th className="px-4 py-3">분석 ID</th>
                    <th className="px-4 py-3">설계 변경</th>
                    <th className="px-4 py-3">일시</th>
                    <th className="px-4 py-3">규제 영향도</th>
                    <th className="px-4 py-3">필요 조치</th>
                    <th className="px-4 py-3">상태</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {recentAnalyses.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50 transition-colors group cursor-pointer">
                      <td className="px-4 py-3 font-medium text-blue-600 group-hover:text-blue-700">{item.id}</td>
                      <td className="px-4 py-3 text-gray-600">{item.changeId}</td>
                      <td className="px-4 py-3 text-gray-500">{item.date}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={item.impact} type="impact" />
                      </td>
                      <td className="px-4 py-3 text-gray-600 max-w-xs truncate" title={item.requiredActions}>{item.requiredActions}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={item.status} type="status" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="p-3 border-t border-gray-100 text-center">
              <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">더 보기</button>
            </div>
          </div>

          <ChecklistSection />
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden h-full">
            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                <FileCheck size={18} className="text-blue-600" />
                규제 문서함
              </h3>
              <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 transition-colors">
                업로드
              </button>
            </div>
            <div className="p-2 space-y-1">
              {documents.map((doc) => (
                <div key={doc.id} className="p-3 hover:bg-gray-50 rounded-lg transition-colors group border border-transparent hover:border-gray-100">
                  <div className="flex justify-between items-start mb-1">
                    <div className="flex items-center gap-2">
                      <FileText size={16} className="text-gray-400 group-hover:text-blue-500" />
                      <span className="font-medium text-gray-900 text-sm group-hover:text-blue-600 transition-colors">{doc.title}</span>
                    </div>
                    <StatusBadge status={doc.status} type="status" />
                  </div>
                  <div className="flex justify-between items-end mt-2 pl-6">
                    <span className="text-xs text-gray-400">{doc.date}</span>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="p-1 text-gray-400 hover:text-blue-600" title="다운로드">
                        <Download size={14} />
                      </button>
                      <button className="p-1 text-gray-400 hover:text-blue-600" title="열기">
                        <ExternalLink size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-3 border-t border-gray-100 text-center bg-gray-50">
              <button className="text-xs text-gray-500 hover:text-gray-700">전체 문서 보기</button>
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl shadow-md p-6 text-white">
            <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
              <AlertTriangle size={20} className="text-yellow-300" />
              규제 업데이트 알림
            </h3>
            <p className="text-blue-100 text-sm mb-4">
              2024년 5월부로 MFDS '의료기기 기준규격' 일부 개정고시가 시행될 예정입니다.
            </p>
            <button className="w-full py-2 bg-white/10 hover:bg-white/20 border border-white/30 rounded-lg text-sm font-medium transition-colors">
              영향 분석 실행하기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

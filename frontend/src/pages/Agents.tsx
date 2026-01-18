import React, { useState } from 'react';
import { 
  PenTool, 
  Users, 
  Shield, 
  Scale, 
  AlertTriangle, 
  FlaskConical, 
  Play, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  Loader2,
  ChevronRight,
  ChevronDown,
  Activity,
  FileText
} from 'lucide-react';
import { GeminiModelSelector } from '../components/GeminiModelSelector';

// --- Types ---
type AgentStatus = 'active' | 'processing' | 'idle' | 'error';

interface Agent {
  id: string;
  name: string;
  role: string;
  icon: React.ElementType;
  status: AgentStatus;
  lastActivity: string;
  tasksToday: number;
}

interface AnalysisTask {
  id: string;
  designChange: string;
  progress: number;
  status: 'running' | 'completed' | 'failed';
  agents: string[];
  startTime: string;
  estimatedCompletion: string;
}

interface ActivityLog {
  id: string;
  agentName: string;
  action: string;
  target: string;
  timestamp: string;
  status: 'success' | 'failure' | 'in_progress';
  details?: string;
}

// --- Mock Data ---
const AGENTS: Agent[] = [
  { id: 'design', name: '설계 엔지니어', role: 'Design Engineer', icon: PenTool, status: 'active', lastActivity: '5분 전', tasksToday: 12 },
  { id: 'pm', name: '프로젝트 매니저', role: 'PM', icon: Users, status: 'idle', lastActivity: '1시간 전', tasksToday: 8 },
  { id: 'qa', name: '품질 보증', role: 'QA', icon: Shield, status: 'processing', lastActivity: '방금', tasksToday: 15 },
  { id: 'ra', name: '규제 담당', role: 'RA', icon: Scale, status: 'active', lastActivity: '10분 전', tasksToday: 6 },
  { id: 'risk', name: '리스크 관리자', role: 'Risk Manager', icon: AlertTriangle, status: 'idle', lastActivity: '2시간 전', tasksToday: 4 },
  { id: 'val', name: '검증/밸리데이션', role: 'V&V', icon: FlaskConical, status: 'error', lastActivity: '30분 전', tasksToday: 9 },
];

const ACTIVE_ANALYSES: AnalysisTask[] = [
  {
    id: 'task-1',
    designChange: 'DCR-2024-001: 로그인 UI 개선',
    progress: 45,
    status: 'running',
    agents: ['QA', 'RA'],
    startTime: '14:30',
    estimatedCompletion: '14:45'
  },
  {
    id: 'task-2',
    designChange: 'DCR-2024-002: 배터리 모듈 사양 변경',
    progress: 10,
    status: 'running',
    agents: ['Risk Manager', 'Design Engineer'],
    startTime: '14:40',
    estimatedCompletion: '15:00'
  }
];

const RECENT_ACTIVITIES: ActivityLog[] = [
  { id: 'log-1', agentName: 'QA Agent', action: '규격 검토 완료', target: 'DCR-2024-001', timestamp: '14:32', status: 'success' },
  { id: 'log-2', agentName: 'RA Agent', action: '규제 영향 분석 시작', target: 'DCR-2024-001', timestamp: '14:30', status: 'in_progress' },
  { id: 'log-3', agentName: 'V&V Agent', action: '테스트 계획 생성 실패', target: 'DCR-2023-098', timestamp: '13:15', status: 'failure', details: '데이터베이스 연결 오류' },
  { id: 'log-4', agentName: 'PM Agent', action: '일정 업데이트', target: 'Project Alpha', timestamp: '11:00', status: 'success' },
];

const DESIGN_CHANGES = [
  'DCR-2024-001: 로그인 UI 개선',
  'DCR-2024-002: 배터리 모듈 사양 변경',
  'DCR-2024-003: 펌웨어 v2.1 업데이트'
];

// --- Helper Components ---

const StatusBadge = ({ status }: { status: AgentStatus }) => {
  const styles = {
    active: 'bg-green-100 text-green-700 border-green-200',
    processing: 'bg-blue-100 text-blue-700 border-blue-200 animate-pulse',
    idle: 'bg-gray-100 text-gray-700 border-gray-200',
    error: 'bg-red-100 text-red-700 border-red-200',
  };

  const labels = {
    active: '활성',
    processing: '처리중',
    idle: '대기',
    error: '오류',
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status]}`}>
      {labels[status]}
    </span>
  );
};

const AgentCard = ({ agent }: { agent: Agent }) => {
  const Icon = agent.icon;
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 rounded-lg ${agent.status === 'processing' ? 'bg-blue-50' : 'bg-gray-50'}`}>
          <Icon className={`w-6 h-6 ${agent.status === 'processing' ? 'text-blue-600' : 'text-gray-600'}`} />
        </div>
        <StatusBadge status={agent.status} />
      </div>
      
      <h3 className="font-bold text-gray-900 text-lg">{agent.name}</h3>
      <p className="text-sm text-gray-500 mb-4">{agent.role}</p>
      
      <div className="space-y-2 text-sm text-gray-600 mb-4">
        <div className="flex justify-between">
          <span>마지막 활동</span>
          <span className="font-medium">{agent.lastActivity}</span>
        </div>
        <div className="flex justify-between">
          <span>금일 처리 건수</span>
          <span className="font-medium">{agent.tasksToday}건</span>
        </div>
      </div>

      <button className="w-full py-2 px-3 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
        <Activity size={14} />
        분석 요청
      </button>
    </div>
  );
};

const ActivityItem = ({ log }: { log: ActivityLog }) => {
  const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-green-500" />,
    failure: <XCircle className="w-4 h-4 text-red-500" />,
    in_progress: <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
  };

  return (
    <div className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors border-l-2 border-transparent hover:border-blue-500">
      <div className="mt-1">{icons[log.status]}</div>
      <div className="flex-1">
        <div className="flex justify-between">
          <p className="text-sm font-medium text-gray-900">
            <span className="text-blue-600 font-semibold">{log.agentName}</span> - {log.action}
          </p>
          <span className="text-xs text-gray-400">{log.timestamp}</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">대상: {log.target}</p>
        {log.details && (
          <p className="text-xs text-red-500 mt-1 bg-red-50 p-1 rounded px-2 inline-block">
            {log.details}
          </p>
        )}
      </div>
    </div>
  );
};

// --- Main Page Component ---
const Agents = () => {
  const [selectedChange, setSelectedChange] = useState(DESIGN_CHANGES[0]);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('summary');

  const toggleAgent = (id: string) => {
    setSelectedAgents(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-8 pb-10">
      {/* 1. Header */}
      <div className="flex justify-between items-end border-b border-gray-200 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent 시스템</h1>
          <p className="text-gray-500 mt-1">AI 기반 품질 관리 에이전트들의 상태를 모니터링하고 분석을 요청합니다.</p>
        </div>
        <div className="flex items-center space-x-2 bg-green-50 px-3 py-1 rounded-full border border-green-100">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-sm font-medium text-green-700">All Systems Operational</span>
        </div>
      </div>

      {/* 2. Agent Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {AGENTS.map(agent => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2/3) */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* 3. Active Analysis Section */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
              진행 중인 분석
            </h2>
            <div className="space-y-4">
              {ACTIVE_ANALYSES.map(task => (
                <div key={task.id} className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                  <div className="flex justify-between mb-2">
                    <span className="font-medium text-gray-800">{task.designChange}</span>
                    <span className="text-sm text-gray-500">예상 완료: {task.estimatedCompletion}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                    <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-500" style={{ width: `${task.progress}%` }}></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>참여 Agent: {task.agents.join(', ')}</span>
                    <span>{task.progress}% 완료</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 6. Analysis Results Section (Placeholder) */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="border-b border-gray-200 bg-gray-50 px-6 py-4 flex items-center justify-between">
              <h2 className="font-bold text-gray-900">최근 분석 결과</h2>
              <div className="flex space-x-1">
                {['summary', 'details', 'logs'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-3 py-1 text-xs font-medium rounded-md capitalize transition-colors ${
                      activeTab === tab ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>
            <div className="p-6">
              {activeTab === 'summary' && (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p>좌측 패널에서 디자인 변경사항을 선택하여<br/>상세 분석 결과를 확인하세요.</p>
                </div>
              )}
              {/* Other tabs would go here */}
            </div>
          </div>

        </div>

        {/* Right Column (1/3) */}
        <div className="space-y-8">
          
          {/* 5. Request New Analysis Panel */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sticky top-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Play className="w-5 h-5 text-purple-500" />
              새 분석 요청
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">디자인 변경 항목</label>
                <div className="relative">
                  <select 
                    className="w-full appearance-none bg-white border border-gray-300 hover:border-gray-400 px-4 py-2 pr-8 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    value={selectedChange}
                    onChange={(e) => setSelectedChange(e.target.value)}
                  >
                    {DESIGN_CHANGES.map(change => (
                      <option key={change} value={change}>{change}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-2.5 h-4 w-4 text-gray-500 pointer-events-none" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">실행할 Agent 선택</label>
                <div className="space-y-2 max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-2">
                  <label className="flex items-center space-x-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      checked={selectedAgents.length === AGENTS.length}
                      onChange={() => setSelectedAgents(selectedAgents.length === AGENTS.length ? [] : AGENTS.map(a => a.id))}
                    />
                    <span className="text-sm font-medium">전체 선택</span>
                  </label>
                  <hr className="border-gray-100" />
                  {AGENTS.map(agent => (
                    <label key={agent.id} className="flex items-center space-x-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                      <input 
                        type="checkbox" 
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        checked={selectedAgents.includes(agent.id)}
                        onChange={() => toggleAgent(agent.id)}
                      />
                      <span className="text-sm text-gray-700">{agent.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">AI 모델</label>
                <GeminiModelSelector />
                <p className="text-xs text-gray-500 mt-1">복잡한 분석에는 Pro 모델을 권장합니다.</p>
              </div>

              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg shadow-sm transition-colors flex items-center justify-center gap-2 mt-2">
                <Play size={16} />
                분석 시작
              </button>
            </div>
          </div>

          {/* 4. Recent Activities Timeline */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-gray-500" />
              최근 활동 내역
            </h2>
            <div className="space-y-1">
              {RECENT_ACTIVITIES.map(log => (
                <ActivityItem key={log.id} log={log} />
              ))}
            </div>
            <button className="w-full mt-4 text-sm text-gray-500 hover:text-blue-600 flex items-center justify-center gap-1 py-2">
              더 보기 <ChevronRight size={14} />
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Agents;

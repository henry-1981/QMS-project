import React, { useState, useEffect } from 'react';
import { 
  User, 
  Bell, 
  HardDrive, 
  Cpu, 
  Shield, 
  Monitor, 
  Save, 
  FileText,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

interface GeminiModel {
  name: string;
  display_name: string;
  description: string;
}

interface UserProfile {
  name: string;
  email: string;
  role: string;
  avatarUrl?: string;
}

interface NotificationSettings {
  designChanges: boolean;
  agentAnalysis: boolean;
  approvalRequests: boolean;
  riskItems: boolean;
  emailNotifications: boolean;
  inAppNotifications: boolean;
}

const SectionHeader = ({ icon: Icon, title, description }: { icon: React.ElementType, title: string, description: string }) => (
  <div className="flex items-start space-x-4 mb-6">
    <div className="p-2 bg-blue-50 rounded-lg">
      <Icon className="w-6 h-6 text-blue-600" />
    </div>
    <div>
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      <p className="text-sm text-gray-500">{description}</p>
    </div>
  </div>
);

const Toggle = ({ label, checked, onChange }: { label: string, checked: boolean, onChange: (checked: boolean) => void }) => (
  <div className="flex items-center justify-between py-3">
    <span className="text-gray-700 font-medium">{label}</span>
    <button
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        checked ? 'bg-blue-600' : 'bg-gray-200'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          checked ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  </div>
);

export const Settings = () => {
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(new Date());

  const [profile, setProfile] = useState<UserProfile>({
    name: '김지민',
    email: 'jimin.kim@meditech.com',
    role: 'QA',
    avatarUrl: undefined
  });

  const [models, setModels] = useState<GeminiModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('gemini-1.5-pro');
  const [temperature, setTemperature] = useState<number>(0.7);

  const [notifications, setNotifications] = useState<NotificationSettings>({
    designChanges: true,
    agentAnalysis: true,
    approvalRequests: true,
    riskItems: false,
    emailNotifications: true,
    inAppNotifications: true
  });

  const [language, setLanguage] = useState('ko');
  const [theme, setTheme] = useState('light');
  const [dateFormat, setDateFormat] = useState('YYYY-MM-DD');
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        setModels([
          { name: 'models/gemini-1.5-pro', display_name: 'Gemini 1.5 Pro', description: '복잡한 추론 및 분석에 최적화된 고성능 모델' },
          { name: 'models/gemini-1.5-flash', display_name: 'Gemini 1.5 Flash', description: '빠른 응답 속도와 효율적인 처리를 위한 경량 모델' },
          { name: 'models/gemini-1.0-pro', display_name: 'Gemini 1.0 Pro', description: '균형 잡힌 성능의 범용 모델' }
        ]);
      } catch (error) {
        console.error('Failed to fetch Gemini models:', error);
      }
    };

    fetchModels();
  }, []);

  const handleSave = () => {
    setSaveStatus('saving');
    setTimeout(() => {
      setSaveStatus('saved');
      setLastSaved(new Date());
      setTimeout(() => setSaveStatus('idle'), 2000);
    }, 1000);
  };

  return (
    <div className="max-w-4xl mx-auto pb-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">설정</h1>
        <p className="mt-2 text-gray-600">시스템 및 사용자 설정을 관리합니다.</p>
      </div>

      <div className="space-y-6">
        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6">
            <SectionHeader 
              icon={User} 
              title="프로필 설정" 
              description="개인 정보 및 역할 관리" 
            />
            
            <div className="pl-12 space-y-6">
              <div className="flex items-center space-x-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-md">
                  {profile.name.substring(0, 1)}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-medium text-gray-900">{profile.name}</h3>
                    <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                      Google 계정 연동됨
                    </span>
                  </div>
                  <p className="text-gray-500">{profile.email}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">이름</label>
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    className="w-full rounded-lg border-gray-300 border px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">부서 / 역할</label>
                  <select
                    value={profile.role}
                    onChange={(e) => setProfile({ ...profile, role: e.target.value })}
                    className="w-full rounded-lg border-gray-300 border px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white"
                  >
                    <option value="설계">설계 (Design)</option>
                    <option value="QA">QA (Quality Assurance)</option>
                    <option value="RA">RA (Regulatory Affairs)</option>
                    <option value="PM">PM (Product Manager)</option>
                    <option value="관리자">관리자 (Admin)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6">
            <SectionHeader 
              icon={Cpu} 
              title="AI 모델 설정" 
              description="Gemini 모델 및 파라미터 구성" 
            />

            <div className="pl-12 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">기본 Gemini 모델</label>
                <div className="grid grid-cols-1 gap-3">
                  {models.map((model) => (
                    <div 
                      key={model.name}
                      onClick={() => setSelectedModel(model.name)}
                      className={`relative flex items-start p-4 cursor-pointer rounded-lg border-2 transition-all ${
                        selectedModel === model.name 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-blue-200'
                      }`}
                    >
                      <div className="flex items-center h-5">
                        <input
                          type="radio"
                          name="model-selection"
                          checked={selectedModel === model.name}
                          onChange={() => setSelectedModel(model.name)}
                          className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                      </div>
                      <div className="ml-3">
                        <span className="block text-sm font-medium text-gray-900">{model.display_name}</span>
                        <span className="block text-sm text-gray-500 mt-1">{model.description}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Temperature (창의성/다양성)</label>
                  <span className="text-sm font-medium text-blue-600">{temperature}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>0.0 (정확함)</span>
                  <span>1.0 (창의적)</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6">
            <SectionHeader 
              icon={Bell} 
              title="알림 설정" 
              description="이메일 및 시스템 알림 관리" 
            />

            <div className="pl-12 grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-2">
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-900 mb-3 border-b pb-2">이벤트 알림</h4>
                <Toggle 
                  label="설계 변경 발생 시" 
                  checked={notifications.designChanges}
                  onChange={(c) => setNotifications({...notifications, designChanges: c})} 
                />
                <Toggle 
                  label="Agent 분석 완료 시" 
                  checked={notifications.agentAnalysis}
                  onChange={(c) => setNotifications({...notifications, agentAnalysis: c})} 
                />
                <Toggle 
                  label="승인 요청 수신 시" 
                  checked={notifications.approvalRequests}
                  onChange={(c) => setNotifications({...notifications, approvalRequests: c})} 
                />
                <Toggle 
                  label="고위험 항목 감지 시" 
                  checked={notifications.riskItems}
                  onChange={(c) => setNotifications({...notifications, riskItems: c})} 
                />
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-900 mb-3 border-b pb-2">수신 채널</h4>
                <Toggle 
                  label="이메일 알림" 
                  checked={notifications.emailNotifications}
                  onChange={(c) => setNotifications({...notifications, emailNotifications: c})} 
                />
                <Toggle 
                  label="앱 내 알림" 
                  checked={notifications.inAppNotifications}
                  onChange={(c) => setNotifications({...notifications, inAppNotifications: c})} 
                />
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6">
            <SectionHeader 
              icon={HardDrive} 
              title="Google Drive 연동" 
              description="문서 저장소 연결 상태" 
            />

            <div className="pl-12">
              <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-between border border-gray-100">
                <div className="flex items-center space-x-4">
                  <div className="bg-white p-2 rounded-md shadow-sm">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg" alt="Google Drive" className="w-8 h-8" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Google Drive 연결됨</h4>
                    <p className="text-sm text-gray-500">/QMS_System/Documents</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-xs text-gray-500">마지막 동기화: 10분 전</span>
                  <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="mt-4 flex justify-end">
                <button className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors">
                  연결 재설정
                </button>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6">
            <SectionHeader 
              icon={Monitor} 
              title="시스템 환경설정" 
              description="언어, 테마 및 표시 설정" 
            />

            <div className="pl-12 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">언어 (Language)</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full rounded-lg border-gray-300 border px-3 py-2 outline-none bg-gray-50 text-gray-500 cursor-not-allowed"
                  disabled
                >
                  <option value="ko">한국어 (Korean)</option>
                  <option value="en">English</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">테마</label>
                <div className="flex items-center space-x-2 p-1 bg-gray-100 rounded-lg w-fit">
                  <button 
                    onClick={() => setTheme('light')}
                    className={`px-3 py-1.5 text-sm rounded-md transition-all ${theme === 'light' ? 'bg-white shadow-sm text-gray-900 font-medium' : 'text-gray-500'}`}
                  >
                    라이트
                  </button>
                  <button 
                    onClick={() => setTheme('dark')}
                    className={`px-3 py-1.5 text-sm rounded-md transition-all ${theme === 'dark' ? 'bg-white shadow-sm text-gray-900 font-medium' : 'text-gray-500'}`}
                  >
                    다크
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">날짜 표시 형식</label>
                <select
                  value={dateFormat}
                  onChange={(e) => setDateFormat(e.target.value)}
                  className="w-full rounded-lg border-gray-300 border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                >
                  <option value="YYYY-MM-DD">2024-03-21</option>
                  <option value="YY.MM.DD">24.03.21</option>
                  <option value="MM/DD/YYYY">03/21/2024</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">페이지당 항목 수</label>
                <select
                  value={itemsPerPage}
                  onChange={(e) => setItemsPerPage(Number(e.target.value))}
                  className="w-full rounded-lg border-gray-300 border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                >
                  <option value={10}>10개씩 보기</option>
                  <option value={20}>20개씩 보기</option>
                  <option value={50}>50개씩 보기</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6">
            <SectionHeader 
              icon={Shield} 
              title="데이터 및 개인정보" 
              description="데이터 관리 및 계정 설정" 
            />

            <div className="pl-12 space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-gray-100">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">내 데이터 내보내기</h4>
                  <p className="text-xs text-gray-500">개인 설정 및 활동 로그를 CSV로 다운로드합니다.</p>
                </div>
                <button className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center">
                  <FileText className="w-4 h-4 mr-1" />
                  다운로드
                </button>
              </div>
              
              <div className="flex items-center justify-between py-3">
                <div>
                  <h4 className="text-sm font-medium text-red-600">계정 삭제</h4>
                  <p className="text-xs text-gray-500">모든 데이터가 영구적으로 삭제되며 복구할 수 없습니다.</p>
                </div>
                <button className="px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50 text-sm font-medium transition-colors">
                  계정 삭제
                </button>
              </div>
            </div>
          </div>
        </section>

        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg md:relative md:bg-transparent md:border-none md:shadow-none md:p-0 mt-8 flex items-center justify-end space-x-4">
          <div className="hidden md:block text-sm text-gray-500 mr-2">
            {lastSaved && `마지막 저장: ${lastSaved.toLocaleTimeString()}`}
          </div>
          
          <button className="px-6 py-2.5 rounded-lg border border-gray-300 bg-white text-gray-700 font-medium hover:bg-gray-50 transition-colors">
            취소
          </button>
          
          <button 
            onClick={handleSave}
            disabled={saveStatus === 'saving'}
            className="px-6 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors flex items-center shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {saveStatus === 'saving' ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                저장 중...
              </>
            ) : saveStatus === 'saved' ? (
              <>
                <CheckCircle2 className="w-4 h-4 mr-2" />
                저장됨
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                설정 저장
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

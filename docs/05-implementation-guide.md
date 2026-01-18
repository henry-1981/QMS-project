# 구현 가이드

## 1. 개발 환경 설정

### 1.1 필수 요구사항

| 구성요소 | 버전 | 설치 확인 |
|---------|------|----------|
| Python | 3.12+ | `python --version` |
| Node.js | 20+ | `node --version` |
| npm | 10+ | `npm --version` |
| Git | 2.40+ | `git --version` |

### 1.2 저장소 클론

```bash
git clone <repository-url>
cd qms-agent-system
```

### 1.3 Backend 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 입력
```

### 1.4 Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install
```

### 1.5 환경 변수 설정

**Backend (.env):**
```bash
# Database
DATABASE_URL=sqlite:///./test.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Google AI
GOOGLE_API_KEY=your-gemini-api-key

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

## 2. 데이터베이스 초기화

### 2.1 마이그레이션 적용

```bash
cd backend
source venv/bin/activate

# 마이그레이션 적용
alembic upgrade head

# 테이블 확인 (SQLite)
sqlite3 test.db ".tables"
```

### 2.2 초기 데이터 (선택)

```bash
# 테스트 사용자 생성
python scripts/create_test_user.py
```

## 3. 개발 서버 실행

### 3.1 Backend 서버

```bash
cd backend
source venv/bin/activate

# 개발 서버 실행
uvicorn app.main:app --reload --port 8000

# 접속 확인
# http://localhost:8000/docs (Swagger UI)
```

### 3.2 Frontend 서버

```bash
cd frontend

# 개발 서버 실행
npm run dev

# 접속 확인
# http://localhost:5173
```

## 4. Google OAuth 설정

### 4.1 Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **APIs & Services > Credentials** 이동
4. **Create Credentials > OAuth client ID** 클릭
5. **Application type**: Web application
6. **Authorized redirect URIs** 추가:
   - `http://localhost:8000/api/v1/auth/google/callback`

### 4.2 필요한 API 활성화

- Google Drive API (문서 연동용)
- Google Sheets API (Risk Matrix 연동용)

### 4.3 OAuth 동의 화면 설정

1. **APIs & Services > OAuth consent screen**
2. User Type: Internal (조직 내부) 또는 External
3. 필수 정보 입력
4. Scopes 추가:
   - `openid`
   - `email`
   - `profile`
   - `https://www.googleapis.com/auth/drive.readonly`

## 5. 테스트 실행

### 5.1 Backend 테스트

```bash
cd backend
source venv/bin/activate

# 전체 테스트 실행
pytest tests/ -v

# 커버리지 리포트
pytest tests/ --cov=app --cov-report=html
```

### 5.2 Frontend 테스트

```bash
cd frontend

# 린트 검사
npm run lint

# 빌드 테스트
npm run build
```

## 6. 코드 스타일 가이드

### 6.1 Python (Backend)

- **포매터**: Black
- **린터**: Flake8, Pylint
- **타입 힌트**: 모든 함수에 필수
- **Docstring**: Google 스타일

```python
def analyze_impact(
    change_id: int,
    options: Optional[Dict[str, Any]] = None
) -> AnalysisResult:
    """설계 변경의 영향을 분석합니다.
    
    Args:
        change_id: 설계 변경 ID
        options: 분석 옵션
        
    Returns:
        분석 결과 객체
        
    Raises:
        NotFoundException: 설계 변경을 찾을 수 없는 경우
    """
    pass
```

### 6.2 TypeScript (Frontend)

- **포매터**: Prettier (내장)
- **린터**: ESLint
- **타입**: 모든 변수/함수에 타입 명시
- **컴포넌트**: 함수형 컴포넌트 사용

```typescript
interface StatCardProps {
  title: string;
  value: string;
  change: string;
  icon: LucideIcon;
  color: string;
}

const StatCard = ({ title, value, change, icon: Icon, color }: StatCardProps) => {
  // ...
};
```

### 6.3 Git 커밋 메시지

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 스타일 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

**예시:**
```
feat(agents): Design Engineer Agent 영향 분석 구현

- analyze_impact() 메서드 구현
- 기술적 리스크 평가 로직 추가
- Gemini API 연동 완료

Closes #123
```

## 7. 주요 구현 패턴

### 7.1 API 라우터 패턴

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{item_id}")
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
    return item
```

### 7.2 에이전트 구현 패턴

```python
class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="custom_agent", role="Custom Role")
    
    async def execute(self, state: AgentState) -> AgentState:
        try:
            change = self._get_design_change(state["change_id"])
            if not change:
                state["errors"].append("설계 변경을 찾을 수 없습니다.")
                return state
            
            result = await self._analyze(change)
            state["analysis_results"]["custom_agent"] = result
            state["messages"].append(f"{self.name}: 분석 완료")
            
            return state
        except Exception as e:
            state["errors"].append(f"{self.name}: {str(e)}")
            return state
    
    async def _analyze(self, change: DesignChange) -> Dict[str, Any]:
        prompt = self._build_prompt(change)
        response = await self.gemini_service.analyze(prompt)
        return response
```

### 7.3 React 컴포넌트 패턴

```typescript
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import client from '../api/client';

interface PageData {
  items: Item[];
  total: number;
}

export const ItemList = () => {
  const { isAuthenticated } = useAuth();
  const [data, setData] = useState<PageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await client.get<PageData>('/items/');
        setData(response.data);
      } catch (err) {
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  return (
    <div>
      {data.items.map(item => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  );
};
```

## 8. 문제 해결

### 8.1 일반적인 문제

**문제: `ModuleNotFoundError: No module named 'app'`**
```bash
# backend 디렉토리에서 실행 중인지 확인
cd backend
source venv/bin/activate
```

**문제: `CORS Error`**
```python
# backend/app/main.py의 CORS 설정 확인
allow_origins=["http://localhost:5173"]
```

**문제: `401 Unauthorized` (토큰 만료)**
```typescript
// frontend에서 토큰 갱신 로직 확인
// 또는 localStorage에서 token 삭제 후 재로그인
localStorage.removeItem('token');
```

### 8.2 Google OAuth 문제

**문제: `redirect_uri_mismatch`**
- Google Cloud Console의 Authorized redirect URIs 확인
- 정확한 URL: `http://localhost:8000/api/v1/auth/google/callback`

**문제: `invalid_client`**
- `.env` 파일의 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET 확인
- 콘솔에서 새로운 credentials 생성 시도

### 8.3 데이터베이스 문제

**문제: 테이블이 없음**
```bash
cd backend
alembic upgrade head
```

**문제: 마이그레이션 충돌**
```bash
# 주의: 데이터 손실 가능
alembic downgrade base
alembic upgrade head
```

## 9. 배포 체크리스트

### 9.1 운영 환경 설정

- [ ] PostgreSQL 데이터베이스 설정
- [ ] 환경 변수 설정 (SECRET_KEY 변경!)
- [ ] HTTPS 인증서 설치
- [ ] CORS 설정 업데이트
- [ ] Google OAuth redirect URI 업데이트
- [ ] Gunicorn/Uvicorn 워커 설정

### 9.2 보안 체크리스트

- [ ] DEBUG=False 확인
- [ ] SECRET_KEY 강력한 값으로 변경
- [ ] 데이터베이스 자격 증명 보안
- [ ] 환경 변수 파일 권한 설정 (chmod 600)
- [ ] 방화벽 규칙 설정

### 9.3 성능 체크리스트

- [ ] 데이터베이스 인덱스 확인
- [ ] 정적 파일 CDN 설정
- [ ] 응답 캐싱 설정
- [ ] 로깅 레벨 설정 (INFO 이상)

## 10. 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [React 공식 문서](https://react.dev/)
- [TailwindCSS 문서](https://tailwindcss.com/docs)
- [Google OAuth 2.0 가이드](https://developers.google.com/identity/protocols/oauth2)
- [ISO 13485 표준](https://www.iso.org/standard/59752.html)
- [IEC 62304 가이드](https://www.iso.org/standard/71604.html)

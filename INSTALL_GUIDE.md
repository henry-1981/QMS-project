# QMS Agent System 설치 가이드

## 문제 해결: chroma-hnswlib 빌드 오류

ChromaDB 설치 시 `chroma-hnswlib` 빌드 오류가 발생하는 경우 해결 방법입니다.

### 방법 1: 시스템 의존성 설치 (권장)

```bash
# 빌드 도구 설치
sudo apt update
sudo apt install -y build-essential python3-dev

# 다시 설치 시도
cd ~/qms-agent-system/backend
source venv/bin/activate
pip install -r requirements.txt
```

### 방법 2: 최소 의존성으로 시작 (빠른 시작)

ChromaDB 없이 먼저 시스템을 시작하고, 나중에 추가할 수 있습니다.

```bash
cd ~/qms-agent-system/backend
source venv/bin/activate

# 최소 의존성만 설치
pip install -r requirements-minimal.txt

# ChromaDB는 나중에 별도로 설치
# pip install chromadb
```

### 방법 3: Docker 사용

빌드 문제를 피하고 Docker로 전체 환경을 실행합니다.

```bash
cd ~/qms-agent-system
docker-compose up -d
```

---

## 전체 설치 프로세스

### 1단계: 시스템 패키지 설치

```bash
sudo apt update
sudo apt install -y \
    python3.12-venv \
    python3-dev \
    build-essential \
    postgresql \
    postgresql-contrib \
    git
```

### 2단계: Python 가상환경 생성

```bash
cd ~/qms-agent-system/backend
python3 -m venv venv
source venv/bin/activate
```

### 3단계: Python 의존성 설치

**Option A: 전체 설치 (ChromaDB 포함)**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Option B: 최소 설치 (ChromaDB 제외)**
```bash
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

### 4단계: 환경 변수 설정

```bash
cp .env.example .env
nano .env  # 또는 vi .env
```

다음 값들을 설정하세요:
```env
# Gemini API 키 (필수)
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Drive 인증 파일 경로
GOOGLE_DRIVE_CREDENTIALS_PATH=./credentials/google_drive_credentials.json

# 데이터베이스 URL
DATABASE_URL=postgresql://qms_user:qms_password@localhost:5432/qms_db

# Secret Key (프로덕션에서는 반드시 변경)
SECRET_KEY=your-secret-key-change-this-in-production
```

### 5단계: PostgreSQL 설정

**Option A: Docker 사용 (권장)**
```bash
cd ~/qms-agent-system
docker-compose up -d postgres
```

**Option B: 로컬 PostgreSQL 사용**
```bash
sudo -u postgres createuser qms_user
sudo -u postgres createdb qms_db
sudo -u postgres psql -c "ALTER USER qms_user WITH PASSWORD 'qms_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qms_db TO qms_user;"
```

### 6단계: 데이터베이스 마이그레이션

```bash
cd ~/qms-agent-system/backend
source venv/bin/activate
alembic upgrade head
```

### 7단계: 서버 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

브라우저에서 확인:
- API: http://localhost:8000
- API 문서: http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/health

---

## ChromaDB 없이 시작하기

Vector DB(ChromaDB)는 RAG 기능을 위한 것이므로, 초기에는 없이도 시스템을 시작할 수 있습니다.

### ChromaDB 관련 코드 임시 비활성화

`app/services/vector_db_service.py` 사용 시:

```python
# ChromaDB가 설치되지 않은 경우 대체 구현
try:
    from app.services.vector_db_service import vector_db_service
except ImportError:
    # Mock 구현으로 대체
    class MockVectorDB:
        def search(self, *args, **kwargs):
            return {"documents": [[]]}
    
    vector_db_service = MockVectorDB()
```

### 나중에 ChromaDB 추가

시스템 의존성 설치 후:

```bash
sudo apt install -y build-essential python3-dev
source venv/bin/activate
pip install chromadb==0.4.22
```

---

## 문제 해결 FAQ

### Q: "No module named 'pip'" 오류
```bash
python3 -m ensurepip --upgrade
```

### Q: PostgreSQL 연결 실패
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 시작
sudo systemctl start postgresql
```

### Q: Permission denied 오류
```bash
# 프로젝트 디렉토리 권한 확인
ls -la ~/qms-agent-system
chmod +x ~/qms-agent-system/scripts/setup.sh
```

### Q: Google Drive 인증 파일이 없음
1. Google Cloud Console에서 서비스 계정 생성
2. JSON 키 파일 다운로드
3. `backend/credentials/` 디렉토리에 저장
4. `.env` 파일에 경로 설정

---

## 다음 단계

설치가 완료되면:

1. **SOP 문서 업로드**: Google Drive에 SOP/지침서 업로드
2. **Vector DB 초기화**: 문서를 임베딩하여 RAG 시스템 구축
3. **테스트 데이터 생성**: 샘플 프로젝트 및 설계 변경 생성
4. **Agent 테스트**: 각 Agent의 기능 테스트

자세한 내용은 `docs/` 디렉토리의 상세 문서를 참고하세요.

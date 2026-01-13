# QMS Agent System

의료기기 품질 경영시스템(Quality Management System) Agent 시스템

## 개요

ISO 13485 및 MFDS 규제를 준수하는 의료기기 QMS를 위한 Multi-Agent 시스템입니다.

## 주요 기능

- **설계 관리 (Design Control)**: ISO 13485 7.3조항 준수
- **6개 역할별 Agent**: 설계 엔지니어, PM, QA, RA, 리스크 관리자, 검증/밸리데이션
- **RAG 기반 지식 시스템**: SOP 및 지침서 학습
- **위험 관리 연동**: 엑셀 기반 위험 관리 파일 연동
- **자동 영향 분석**: 설계 변경 시 영향받는 문서/항목 자동 식별

## 기술 스택

- **Backend**: FastAPI + LangGraph
- **AI**: Google Gemini (기업용)
- **Database**: PostgreSQL + ChromaDB (Vector DB)
- **Storage**: Google Drive
- **Deployment**: 로컬 네트워크 (노트북 서버)

## 설치 방법

### 1. 시스템 요구사항 설치

```bash
sudo apt install python3.12-venv postgresql
```

### 2. Python 가상환경 생성 및 활성화

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 및 데이터베이스 설정
```

### 5. 데이터베이스 초기화

```bash
# PostgreSQL 데이터베이스 생성
createdb qms_db

# 마이그레이션 실행
alembic upgrade head
```

### 6. 서버 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 프로젝트 구조

```
qms-agent-system/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent 구현
│   │   ├── api/             # API 엔드포인트
│   │   ├── core/            # 핵심 설정
│   │   ├── db/              # 데이터베이스 모델 및 연결
│   │   ├── models/          # Pydantic 모델
│   │   ├── services/        # 비즈니스 로직
│   │   └── utils/           # 유틸리티
│   ├── tests/               # 테스트
│   ├── requirements.txt     # Python 의존성
│   └── pyproject.toml       # Poetry 설정
├── frontend/                # React 프론트엔드 (추후 개발)
├── docs/                    # 문서
└── scripts/                 # 유틸리티 스크립트
```

## 개발 상태

- [x] 프로젝트 구조 생성
- [x] 기본 설정 파일 작성
- [ ] Python 의존성 설치
- [ ] 데이터베이스 스키마 구현
- [ ] Agent 구현
- [ ] API 엔드포인트 구현
- [ ] 프론트엔드 개발

## 라이선스

Proprietary

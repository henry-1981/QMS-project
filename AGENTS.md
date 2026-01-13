# AI 에이전트 운영 가이드

이 문서는 QMS Agent System 저장소에서 작업하는 AI 에이전트를 위한 가이드라인입니다.

## 1. 프로젝트 개요

의료기기 품질경영시스템(QMS) 에이전트 시스템입니다.
- **백엔드**: Python (FastAPI), SQLAlchemy, LangGraph, ChromaDB
- **프론트엔드**: React, TypeScript, Vite, TailwindCSS
- **데이터베이스**: PostgreSQL
- **AI**: Google Gemini (`google-generativeai` 사용)

## 2. 환경 설정 및 명령어

### 백엔드 (Python)

가상환경과 `requirements.txt`를 사용합니다.

- **작업 디렉토리**: `backend/`
- **가상환경 활성화**: `source backend/venv/bin/activate`

| 작업 | 명령어 | 비고 |
| :--- | :--- | :--- |
| **의존성 설치** | `pip install -r requirements.txt` | venv 활성화 필요 |
| **개발 서버 시작** | `uvicorn app.main:app --reload` | 포트 8000 |
| **마이그레이션 적용** | `alembic upgrade head` | DB 스키마 변경 적용 |
| **마이그레이션 생성** | `alembic revision --autogenerate -m "메시지"` | 모델 수정 후 실행 |
| **전체 테스트 실행** | `pytest` | `tests/` 디렉토리 전체 |
| **단일 테스트 실행** | `pytest tests/test_file.py::test_function` | 특정 테스트만 실행 |
| **코드 포맷팅** | `black . && isort .` | 코드 자동 정리 |
| **린트 검사** | `flake8 . && mypy .` | 오류 및 타입 검사 |

### 프론트엔드 (React/TypeScript)

Vite 기반으로 구축되었습니다.

- **작업 디렉토리**: `frontend/`

| 작업 | 명령어 | 비고 |
| :--- | :--- | :--- |
| **의존성 설치** | `npm install` | |
| **개발 서버 시작** | `npm run dev` | 포트 5173 |
| **프로덕션 빌드** | `npm run build` | `dist/`에 출력 |
| **린트 검사** | `npm run lint` | ESLint 검사 |

## 3. 코드 스타일 및 표준

### Python (백엔드)

- **스타일**: PEP 8 준수. `black`으로 포맷팅, `isort`로 import 정렬
- **타입 힌트**: **필수**. 모든 함수 시그니처에 타입 힌트 작성
    ```python
    def process_data(data: Dict[str, Any]) -> List[int]: ...
    ```
- **Import 순서**: 표준 라이브러리 → 서드파티 → 로컬 앱 순서로 그룹화
- **에러 처리**: API 오류는 `fastapi.HTTPException` 사용. 예외를 무시하지 말고 로깅
- **비동기**: 모든 라우트 핸들러와 I/O 작업에 `async def` 사용

### TypeScript/React (프론트엔드)

- **스타일**: 함수형 컴포넌트 + Hooks 사용. Class 컴포넌트 사용 금지
- **타입**: **필수**. `any` 타입 최소화. props와 API 응답에 interface/type 정의
    ```typescript
    interface UserProps {
      name: string;
      role: 'admin' | 'user';
    }
    ```
- **컴포넌트**: 작고 집중된 컴포넌트 유지. 재사용 가능한 UI는 `src/components`에 배치
- **상태 관리**: React Context 또는 로컬 상태 사용
- **스타일링**: TailwindCSS 유틸리티 클래스 사용. 인라인 스타일 지양

## 4. 개발 워크플로우

### 데이터베이스 변경
1. `app/db/models.py`에서 모델 수정
2. `alembic revision --autogenerate -m "설명"` 실행
3. `alembic/versions/`에 생성된 마이그레이션 스크립트 검증
4. `alembic upgrade head` 실행

### 새 Agent 추가
1. `app/agents/`에 에이전트 클래스 생성
2. `BaseAgent` 상속
3. `app/agents/orchestrator.py`에 등록

### 테스트
1. `backend/tests/`에 테스트 작성
2. `conftest.py` 픽스처를 활용하여 DB 세션 및 테스트 데이터 설정
3. **중요**: 커밋 전 테스트 통과 필수

## 5. 중요 규칙

### 금지 사항
- **메모 주석 금지**: "여기서 변경함", "기능 X 추가" 같은 주석 작성 금지. 코드는 자체 설명적이어야 함
- **미사용 코드 금지**: 사용하지 않는 import, 변수 제거
- **비밀 정보 커밋 금지**: API 키, 시크릿은 `.env` 사용

### 필수 사항
- **모든 아티팩트는 한글로 작성** (글로벌 규칙)
- 타입 힌트 필수
- 테스트 통과 후 커밋

## 6. 프로젝트 구조

```
qms-agent-system/
├── backend/
│   ├── app/
│   │   ├── agents/      # AI 에이전트 구현
│   │   ├── api/         # API 엔드포인트
│   │   ├── core/        # 핵심 설정
│   │   ├── db/          # 데이터베이스 모델
│   │   ├── models/      # Pydantic 스키마
│   │   ├── services/    # 외부 서비스 연동
│   │   └── utils/       # 유틸리티
│   ├── tests/           # 테스트 코드
│   └── alembic/         # DB 마이그레이션
├── frontend/
│   └── src/
│       ├── components/  # 재사용 컴포넌트
│       ├── pages/       # 페이지 컴포넌트
│       ├── layouts/     # 레이아웃
│       ├── api/         # API 클라이언트
│       └── types/       # TypeScript 타입
├── docs/                # 문서
└── scripts/             # 유틸리티 스크립트
```

# API 설계

## 1. 개요

QMS Agent System API는 RESTful 아키텍처를 따르며, FastAPI로 구현되었습니다. 모든 API는 `/api/v1` 접두사를 사용합니다.

## 2. 인증

### 2.1 인증 방식

- **Bearer Token**: JWT 기반 인증
- **OAuth 2.0**: Google OAuth 2.0 지원

### 2.2 인증 헤더

```http
Authorization: Bearer <access_token>
```

## 3. API 엔드포인트

### 3.1 인증 (Auth)

#### POST /api/v1/auth/register
일반 회원가입

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "string",
  "role": "design_engineer"
}
```

**Response (200):**
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "full_name": "string",
  "role": "design_engineer",
  "is_active": true
}
```

---

#### POST /api/v1/auth/login
일반 로그인 (OAuth2 Password Flow)

**Request Body (form-data):**
```
username: string
password: string
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

#### GET /api/v1/auth/google/login
Google OAuth 로그인 URL 생성

**Query Parameters:**
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| redirect_uri | string | N | 인증 후 리다이렉트할 프론트엔드 URL |

**Response (200):**
```json
{
  "login_url": "https://accounts.google.com/o/oauth2/auth?...",
  "message": "Google 로그인 URL이 생성되었습니다."
}
```

---

#### GET /api/v1/auth/google/callback
Google OAuth 콜백 처리

**Query Parameters:**
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| code | string | Y | Google 인증 코드 |
| state | string | N | 프론트엔드 리다이렉트 URL |

**Response:**
302 Redirect to `{frontend_url}/auth/callback?access_token=...`

---

#### POST /api/v1/auth/google/refresh
Google OAuth 토큰 갱신

**Headers:** `Authorization: Bearer <token>` (필수)

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

#### GET /api/v1/auth/me
현재 로그인 사용자 정보 조회

**Headers:** `Authorization: Bearer <token>` (필수)

**Response (200):**
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "full_name": "string",
  "role": "design_engineer",
  "is_active": true
}
```

---

### 3.2 프로젝트 (Projects)

#### GET /api/v1/projects/
프로젝트 목록 조회

**Query Parameters:**
| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| skip | int | 0 | 건너뛸 항목 수 |
| limit | int | 100 | 조회할 항목 수 |
| status | string | - | 상태 필터 |

**Response (200):**
```json
[
  {
    "id": 1,
    "project_code": "PRJ-2024-001",
    "project_name": "의료기기 A 개발",
    "description": "...",
    "product_type": "Class II",
    "iec_62304_class": "B",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### POST /api/v1/projects/
프로젝트 생성

**Request Body:**
```json
{
  "project_code": "PRJ-2024-001",
  "project_name": "의료기기 A 개발",
  "description": "프로젝트 설명",
  "product_type": "Class II",
  "iec_62304_class": "B"
}
```

---

#### GET /api/v1/projects/{project_id}
프로젝트 상세 조회

---

#### PUT /api/v1/projects/{project_id}
프로젝트 수정

---

#### DELETE /api/v1/projects/{project_id}
프로젝트 삭제

---

### 3.3 설계 변경 (Design Changes)

#### GET /api/v1/design_changes/
설계 변경 목록 조회

**Query Parameters:**
| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| skip | int | 0 | 건너뛸 항목 수 |
| limit | int | 100 | 조회할 항목 수 |
| project_id | int | - | 프로젝트 필터 |
| workflow_status | string | - | 상태 필터 |

**Response (200):**
```json
[
  {
    "id": 1,
    "change_number": "DCR-2024-0001",
    "project_id": 1,
    "title": "로그인 화면 UI 변경",
    "description": "사용자 경험 개선을 위한 UI 수정",
    "change_type": "design",
    "workflow_status": "draft",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### POST /api/v1/design_changes/
설계 변경 생성

**Request Body:**
```json
{
  "change_number": "DCR-2024-0001",
  "project_id": 1,
  "title": "로그인 화면 UI 변경",
  "description": "사용자 경험 개선을 위한 UI 수정",
  "change_type": "design",
  "justification": "사용자 피드백 반영",
  "figma_link": "https://figma.com/...",
  "gdocs_link": "https://docs.google.com/..."
}
```

---

#### GET /api/v1/design_changes/{change_id}
설계 변경 상세 조회

---

#### PUT /api/v1/design_changes/{change_id}
설계 변경 수정

---

#### POST /api/v1/design_changes/{change_id}/transition
워크플로우 상태 변경

**Request Body:**
```json
{
  "action": "submit",
  "comments": "분석 요청합니다."
}
```

**가능한 action 값:**
| action | from_status | to_status |
|--------|-------------|-----------|
| submit | draft | submitted |
| start_analysis | submitted | analysis |
| complete_analysis | analysis | ra_review |
| approve | ra_review | approved |
| reject | ra_review | rejected |
| implement | approved | implemented |
| verify | implemented | verified |
| close | verified | closed |

---

### 3.4 에이전트 (Agents)

#### GET /api/v1/agents/models
사용 가능한 Gemini 모델 목록 조회

**Response (200):**
```json
[
  {
    "name": "models/gemini-1.5-pro",
    "display_name": "Gemini 1.5 Pro",
    "description": "Most capable model"
  }
]
```

---

#### POST /api/v1/agents/analyze/{change_id}
설계 변경에 대한 에이전트 분석 실행

**Query Parameters:**
| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| agents | list[str] | all | 실행할 에이전트 목록 |
| model | string | gemini-1.5-pro | 사용할 Gemini 모델 |

**Response (200):**
```json
{
  "task_id": "uuid",
  "status": "running",
  "agents": ["design_engineer", "pm", "qa", "ra", "risk_manager", "verification"],
  "started_at": "2024-01-01T00:00:00Z"
}
```

---

#### GET /api/v1/agents/status/{task_id}
분석 작업 상태 조회

**Response (200):**
```json
{
  "task_id": "uuid",
  "status": "completed",
  "progress": 100,
  "completed_agents": ["design_engineer", "pm", "qa", "ra", "risk_manager", "verification"],
  "current_agent": null,
  "completed_at": "2024-01-01T00:05:00Z"
}
```

---

#### GET /api/v1/agents/results/{change_id}
설계 변경에 대한 분석 결과 조회

**Response (200):**
```json
{
  "change_id": 1,
  "analyses": [
    {
      "agent_type": "design_engineer",
      "findings": {...},
      "recommendations": [...],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 3.5 문서 (Documents)

#### GET /api/v1/documents/
문서 목록 조회

---

#### POST /api/v1/documents/
문서 메타데이터 생성

---

#### POST /api/v1/documents/{doc_id}/upload
Google Drive에 문서 업로드

---

#### GET /api/v1/documents/{doc_id}/download
문서 다운로드 URL 조회

---

### 3.6 위험 관리 (Risk Management)

#### GET /api/v1/risks/
위험 항목 목록 조회

**Query Parameters:**
| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| project_id | int | - | 프로젝트 필터 |
| risk_level | string | - | 위험 수준 필터 |
| status | string | - | 상태 필터 |

---

#### POST /api/v1/risks/sync
Excel 파일과 위험 항목 동기화

---

#### GET /api/v1/risks/{risk_id}/history
위험 항목 변경 이력 조회

---

## 4. 에러 응답

### 4.1 에러 응답 형식

```json
{
  "detail": "에러 메시지"
}
```

### 4.2 HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 422 | 유효성 검사 실패 |
| 500 | 서버 오류 |

### 4.3 일반 에러 메시지

```json
// 401 Unauthorized
{
  "detail": "잘못된 사용자명 또는 비밀번호입니다."
}

// 400 Bad Request
{
  "detail": "이미 등록된 사용자명입니다."
}

// 404 Not Found
{
  "detail": "설계 변경을 찾을 수 없습니다."
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "유효한 이메일 주소를 입력하세요.",
      "type": "value_error.email"
    }
  ]
}
```

## 5. 페이지네이션

목록 조회 API는 `skip`과 `limit` 파라미터로 페이지네이션을 지원합니다.

```
GET /api/v1/design_changes/?skip=0&limit=20
GET /api/v1/design_changes/?skip=20&limit=20
```

## 6. 필터링

목록 조회 API는 쿼리 파라미터로 필터링을 지원합니다.

```
GET /api/v1/design_changes/?project_id=1&workflow_status=analysis
GET /api/v1/risks/?risk_level=high&status=open
```

## 7. OpenAPI 문서

FastAPI는 자동으로 OpenAPI 문서를 생성합니다.

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 8. CORS 설정

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 9. Rate Limiting (예정)

향후 API Rate Limiting이 적용될 예정입니다.

| 엔드포인트 | 제한 |
|-----------|------|
| /auth/* | 10 req/min |
| /agents/analyze/* | 5 req/min |
| 기타 | 100 req/min |

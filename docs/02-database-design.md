# 데이터베이스 설계

## 1. 개요

QMS Agent System은 SQLAlchemy ORM을 사용하여 관계형 데이터베이스를 관리합니다. 개발 환경에서는 SQLite를, 운영 환경에서는 PostgreSQL을 사용합니다.

## 2. ER 다이어그램

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      users      │       │ design_projects │       │ design_changes  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ username        │       │ project_code    │       │ change_number   │
│ email           │◀──────│ created_by (FK) │       │ project_id (FK) │──────▶│
│ password_hash   │       │ project_name    │◀──────│ title           │       │
│ full_name       │       │ description     │       │ description     │       │
│ role            │       │ product_type    │       │ change_type     │       │
│ is_active       │       │ iec_62304_class │       │ workflow_status │       │
│ google_id       │       │ status          │       │ current_assignee│       │
│ google_*_token  │       │ created_at      │       │ created_by (FK) │       │
│ created_at      │       │ updated_at      │       │ created_at      │       │
│ updated_at      │       └─────────────────┘       │ updated_at      │       │
└─────────────────┘                                 └─────────────────┘       │
        │                                                   │                 │
        │                                                   │                 │
        ▼                                                   ▼                 │
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       │
│workflow_history │       │   risk_items    │       │   documents     │       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤       │
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │       │
│ change_id (FK)  │       │ risk_number     │       │ document_type   │       │
│ from_status     │       │ project_id (FK) │       │ document_code   │       │
│ to_status       │       │ hazard          │       │ document_name   │       │
│ action          │       │ severity        │       │ version         │       │
│ comments        │       │ probability     │       │ gdrive_file_id  │       │
│ performed_by    │       │ risk_level      │       │ project_id (FK) │◀──────┘
│ performed_at    │       │ control_measures│       │ status          │
└─────────────────┘       │ excel_file_id   │       │ created_by (FK) │
                          │ status          │       │ approved_by (FK)│
                          │ created_at      │       │ created_at      │
                          └─────────────────┘       │ updated_at      │
                                  │                 └─────────────────┘
                                  │
                                  ▼
                          ┌─────────────────┐
                          │change_risk_links│
                          ├─────────────────┤
                          │ id (PK)         │
                          │ change_id (FK)  │
                          │ risk_id (FK)    │
                          │ link_type       │
                          │ requires_reass. │
                          │ created_by (FK) │
                          │ created_at      │
                          └─────────────────┘
```

## 3. 테이블 상세 정의

### 3.1 users (사용자)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| username | VARCHAR(100) | UNIQUE, NOT NULL | 사용자명 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 주소 |
| password_hash | VARCHAR(255) | NULLABLE | 암호화된 비밀번호 (Google 사용자는 NULL) |
| full_name | VARCHAR(200) | NOT NULL | 성명 |
| role | VARCHAR(50) | NOT NULL | 역할 (design_engineer, pm, qa, ra, risk_manager, verifier) |
| is_active | BOOLEAN | DEFAULT TRUE | 활성화 상태 |
| google_id | VARCHAR(255) | UNIQUE, NULLABLE | Google 계정 ID |
| google_refresh_token | TEXT | NULLABLE | Google OAuth refresh token |
| google_access_token | TEXT | NULLABLE | Google OAuth access token |
| google_token_expiry | DATETIME | NULLABLE | 토큰 만료 시간 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |
| updated_at | DATETIME | ON UPDATE | 수정 일시 |

### 3.2 design_projects (설계 프로젝트)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| project_code | VARCHAR(50) | UNIQUE, NOT NULL | 프로젝트 코드 (예: PRJ-2024-001) |
| project_name | VARCHAR(255) | NOT NULL | 프로젝트명 |
| description | TEXT | NULLABLE | 설명 |
| product_type | VARCHAR(100) | NULLABLE | 제품 유형 |
| iec_62304_class | VARCHAR(10) | NULLABLE | IEC 62304 소프트웨어 안전 등급 (A, B, C) |
| status | VARCHAR(50) | DEFAULT 'draft' | 상태 (draft, active, completed, archived) |
| created_by | INTEGER | FK(users.id) | 생성자 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |
| updated_at | DATETIME | ON UPDATE | 수정 일시 |

### 3.3 design_changes (설계 변경)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| change_number | VARCHAR(50) | UNIQUE, NOT NULL | 변경 번호 (예: DCR-2024-0001) |
| project_id | INTEGER | FK(design_projects.id) | 프로젝트 ID |
| title | VARCHAR(255) | NOT NULL | 변경 제목 |
| description | TEXT | NOT NULL | 변경 상세 설명 |
| change_type | VARCHAR(50) | NULLABLE | 변경 유형 (design, requirement, document) |
| justification | TEXT | NULLABLE | 변경 사유 |
| figma_link | TEXT | NULLABLE | Figma 디자인 링크 |
| gdocs_link | TEXT | NULLABLE | Google Docs 링크 |
| workflow_status | VARCHAR(50) | DEFAULT 'draft' | 워크플로우 상태 |
| current_assignee | INTEGER | FK(users.id) | 현재 담당자 |
| created_by | INTEGER | FK(users.id) | 생성자 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |
| updated_at | DATETIME | ON UPDATE | 수정 일시 |

**workflow_status 값:**
- `draft`: 초안
- `submitted`: 제출됨
- `analysis`: 에이전트 분석 중
- `ra_review`: RA 검토 중
- `qa_review`: QA 검토 중
- `approved`: 승인됨
- `rejected`: 반려됨
- `implemented`: 구현됨
- `verified`: 검증됨
- `closed`: 종료

### 3.4 workflow_history (워크플로우 이력)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| change_id | INTEGER | FK(design_changes.id) | 설계 변경 ID |
| from_status | VARCHAR(50) | NULLABLE | 이전 상태 |
| to_status | VARCHAR(50) | NOT NULL | 변경 후 상태 |
| action | VARCHAR(50) | NOT NULL | 수행 액션 |
| comments | TEXT | NULLABLE | 코멘트 |
| performed_by | INTEGER | FK(users.id) | 수행자 |
| performed_at | DATETIME | DEFAULT NOW | 수행 일시 |

### 3.5 documents (문서)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| document_type | VARCHAR(50) | NOT NULL | 문서 유형 (SOP, WI, Form, Record) |
| document_code | VARCHAR(100) | UNIQUE, NOT NULL | 문서 코드 |
| document_name | VARCHAR(255) | NOT NULL | 문서명 |
| version | VARCHAR(20) | NOT NULL | 버전 (예: 1.0, 1.1) |
| gdrive_file_id | VARCHAR(255) | UNIQUE, NULLABLE | Google Drive 파일 ID |
| gdrive_file_path | TEXT | NULLABLE | Google Drive 경로 |
| project_id | INTEGER | FK(design_projects.id) | 연관 프로젝트 |
| status | VARCHAR(50) | DEFAULT 'draft' | 상태 (draft, review, approved, obsolete) |
| created_by | INTEGER | FK(users.id) | 생성자 |
| approved_by | INTEGER | FK(users.id) | 승인자 |
| approved_at | DATETIME | NULLABLE | 승인 일시 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |
| updated_at | DATETIME | ON UPDATE | 수정 일시 |

### 3.6 traceability_links (추적성 링크)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| source_type | VARCHAR(50) | NOT NULL, INDEX | 소스 엔티티 타입 |
| source_id | INTEGER | NOT NULL, INDEX | 소스 엔티티 ID |
| target_type | VARCHAR(50) | NOT NULL, INDEX | 타겟 엔티티 타입 |
| target_id | INTEGER | NOT NULL, INDEX | 타겟 엔티티 ID |
| relationship_type | VARCHAR(50) | NULLABLE | 관계 유형 (derives_from, implements, verifies) |
| is_auto_generated | BOOLEAN | DEFAULT FALSE | 자동 생성 여부 |
| confidence_score | FLOAT | NULLABLE | AI 생성 시 신뢰도 점수 |
| created_by | INTEGER | FK(users.id) | 생성자 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |

### 3.7 risk_items (위험 항목)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| risk_number | VARCHAR(50) | UNIQUE, NOT NULL | 위험 번호 (예: RISK-001) |
| project_id | INTEGER | FK(design_projects.id) | 프로젝트 ID |
| hazard | TEXT | NOT NULL | 위험원 |
| hazardous_situation | TEXT | NULLABLE | 위험 상황 |
| harm | TEXT | NULLABLE | 위해 |
| severity | INTEGER | NULLABLE | 심각도 (1-5) |
| probability | INTEGER | NULLABLE | 발생 가능성 (1-5) |
| risk_level | VARCHAR(20) | NULLABLE | 위험 수준 (low, medium, high, unacceptable) |
| control_measures | TEXT | NULLABLE | 통제 수단 |
| residual_risk_level | VARCHAR(20) | NULLABLE | 잔존 위험 수준 |
| excel_file_id | VARCHAR(255) | NULLABLE | 연관 Excel 파일 ID |
| excel_row_number | INTEGER | NULLABLE | Excel 행 번호 |
| last_synced_at | DATETIME | NULLABLE | 마지막 동기화 일시 |
| status | VARCHAR(50) | DEFAULT 'open' | 상태 (open, mitigated, closed) |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |
| updated_at | DATETIME | ON UPDATE | 수정 일시 |

### 3.8 change_risk_links (변경-위험 연관)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| change_id | INTEGER | FK(design_changes.id) | 설계 변경 ID |
| risk_id | INTEGER | FK(risk_items.id) | 위험 항목 ID |
| link_type | VARCHAR(50) | NULLABLE | 연관 유형 (affects, mitigates, introduces) |
| analysis_summary | TEXT | NULLABLE | 분석 요약 |
| requires_reassessment | BOOLEAN | DEFAULT FALSE | 재평가 필요 여부 |
| created_by | INTEGER | FK(users.id) | 생성자 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |

### 3.9 agent_tasks (에이전트 작업)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| task_type | VARCHAR(50) | NOT NULL | 작업 유형 |
| agent_type | VARCHAR(50) | NOT NULL | 에이전트 유형 |
| related_entity_type | VARCHAR(50) | NULLABLE | 관련 엔티티 타입 |
| related_entity_id | INTEGER | NULLABLE | 관련 엔티티 ID |
| status | VARCHAR(50) | DEFAULT 'pending' | 상태 (pending, running, completed, failed) |
| input_data | JSON | NULLABLE | 입력 데이터 |
| output_data | JSON | NULLABLE | 출력 데이터 |
| assigned_to | INTEGER | FK(users.id) | 담당자 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |
| completed_at | DATETIME | NULLABLE | 완료 일시 |

### 3.10 agent_analysis (에이전트 분석 결과)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| change_id | INTEGER | FK(design_changes.id) | 설계 변경 ID |
| agent_type | VARCHAR(50) | NOT NULL | 에이전트 유형 |
| analysis_type | VARCHAR(50) | NULLABLE | 분석 유형 |
| findings | JSON | NULLABLE | 발견 사항 |
| recommendations | JSON | NULLABLE | 권고 사항 |
| affected_items | JSON | NULLABLE | 영향받는 항목 |
| created_at | DATETIME | DEFAULT NOW | 생성 일시 |

### 3.11 electronic_signatures (전자 서명)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTO | 고유 식별자 |
| entity_type | VARCHAR(50) | NOT NULL | 서명 대상 엔티티 타입 |
| entity_id | INTEGER | NOT NULL | 서명 대상 엔티티 ID |
| signer_id | INTEGER | FK(users.id) | 서명자 ID |
| signature_meaning | VARCHAR(100) | NULLABLE | 서명 의미 (approved, reviewed, authored) |
| ip_address | VARCHAR(50) | NULLABLE | 서명 시 IP 주소 |
| user_agent | TEXT | NULLABLE | 브라우저 정보 |
| signed_at | DATETIME | DEFAULT NOW | 서명 일시 |

## 4. 인덱스

```sql
-- 자주 조회되는 컬럼에 인덱스 생성
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_google_id ON users(google_id);

CREATE INDEX ix_design_projects_project_code ON design_projects(project_code);

CREATE INDEX ix_design_changes_change_number ON design_changes(change_number);
CREATE INDEX ix_design_changes_workflow_status ON design_changes(workflow_status);

CREATE INDEX ix_traceability_links_source ON traceability_links(source_type, source_id);
CREATE INDEX ix_traceability_links_target ON traceability_links(target_type, target_id);

CREATE INDEX ix_agent_tasks_status ON agent_tasks(status);
```

## 5. 마이그레이션

Alembic을 사용하여 데이터베이스 스키마를 관리합니다.

```bash
# 새 마이그레이션 생성
cd backend
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1

# 현재 버전 확인
alembic current
```

## 6. 데이터베이스 연결 설정

```python
# backend/app/core/config.py
DATABASE_URL = "sqlite:///./test.db"  # 개발
# DATABASE_URL = "postgresql://user:pass@host:5432/qms"  # 운영
```

## 7. 향후 확장 계획

1. **Vector DB (ChromaDB)**: RAG 기반 지식베이스 저장
2. **Redis**: 세션 캐싱, 작업 큐
3. **감사 추적 테이블**: 21 CFR Part 11 준수
4. **파티셔닝**: 대용량 데이터 대응

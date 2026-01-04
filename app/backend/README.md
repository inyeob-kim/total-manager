# Total Manager Backend API

총무노트 백엔드 API 문서입니다.

## 빠른 시작

### 1. 데이터베이스 시작

```bash
# 프로젝트 루트에서 실행
# Docker Compose V2 (최신 Docker Desktop)
docker compose up -d db

# 또는 Docker Compose V1 (구버전)
docker-compose up -d db

# 또는 스크립트 사용
cd app/backend
./scripts/start-db.sh
```

### 2. 환경 변수 설정

`.env` 파일이 이미 생성되어 있습니다. 필요시 수정하세요:

```env
DATABASE_URL=postgresql://totalmanager:totalmanager123@localhost:5432/totalmanager
SECRET_KEY=dev-secret-key-change-in-production-please-use-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
ENVIRONMENT=development
```

### 3. 가상환경 활성화 및 의존성 설치

```bash
# 가상환경 활성화 (이미 생성했다면)
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate  # Windows

# 의존성 설치 (아직 안 했다면)
pip install -r requirements.txt
```

### 4. 데이터베이스 마이그레이션

```bash
# 마이그레이션 적용
alembic upgrade head
```

### 5. 서버 실행

```bash
# 개발 모드 (hot reload)
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. API 확인

- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 환경 변수

`.env` 파일을 생성하고 다음 변수를 설정하세요 (이미 생성되어 있음):

```env
DATABASE_URL=postgresql://totalmanager:totalmanager123@localhost:5432/totalmanager
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
ENVIRONMENT=development
```

### 의존성 설치

```bash
pip install -r requirements.txt
```

### 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 마이그레이션을 적용합니다:

```bash
# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

## API 엔드포인트

### 그룹 (Groups)

#### POST `/total-manager/groups`
그룹을 생성합니다.

**Request Body:**
```json
{
  "name": "학부모 모임",
  "type": "parents"
}
```

**Response:**
```json
{
  "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "owner_id": "user_123",
  "name": "학부모 모임",
  "type": "parents",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/total-manager/groups`
현재 사용자의 그룹 목록을 조회합니다.

**Response:**
```json
[
  {
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "owner_id": "user_123",
    "name": "학부모 모임",
    "type": "parents",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### 컬렉션 (Collections)

#### POST `/total-manager/groups/{group_id}/collections`
컬렉션을 생성합니다.

**Request Body:**
```json
{
  "title": "학기 초 모금",
  "amount": 50000,
  "due_date": "2024-01-15",
  "payment_type": "bank",
  "payment_value": "123-456-789012"
}
```

#### GET `/total-manager/groups/{group_id}/collections`
그룹의 컬렉션 목록을 조회합니다.

#### GET `/total-manager/collections/{collection_id}`
컬렉션 상세 정보를 조회합니다.

### 멤버 (Members)

#### POST `/total-manager/collections/{collection_id}/members`
멤버를 추가합니다.

**Request Body:**
```json
{
  "display_name": "홍길동",
  "phone": "010-1234-5678"
}
```

#### GET `/total-manager/collections/{collection_id}/members`
컬렉션의 멤버 목록을 조회합니다.

#### POST `/total-manager/members/{member_id}/read`
멤버를 읽음 처리합니다.

#### POST `/total-manager/members/{member_id}/paid`
멤버를 납부 처리합니다.

### 공지 (Notices)

#### POST `/total-manager/collections/{collection_id}/notice`
공지를 발송합니다.

**Request Body:**
```json
{
  "message": "모금 안내 메시지 (선택사항)"
}
```

**부수 효과:**
- `notice_sent` 타입의 이벤트 로그 생성
- `due_date - 1일` 및 `due_date + 1일`에 대한 `reminder_scheduled` 타입의 이벤트 로그 생성

**주의:** 실제 리마인더 발송은 현재 구현되지 않았으며, 로그만 생성됩니다. 추후 스케줄러를 통해 구현 예정입니다.

### 로그 (Logs)

#### GET `/total-manager/collections/{collection_id}/logs`
컬렉션의 이벤트 로그 목록을 조회합니다 (created_at 내림차순).

**Response:**
```json
[
  {
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "collection_id": "01ARZ3NDEKTSV4RRFFQ69G5FAW",
    "type": "notice_sent",
    "message": "모금 안내: 50,000원, 마감일: 2024-01-15",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## 에러 처리

- **404 Not Found**: 그룹/컬렉션/멤버가 존재하지 않을 때
- **403 Forbidden**: 소유자가 아닐 때

## 주요 엔드포인트 curl 예시

### 그룹 생성
```bash
curl -X POST http://localhost:8000/total-manager/groups \
  -H "Content-Type: application/json" \
  -d '{"name": "학부모 모임", "type": "parents"}'
```

### 컬렉션 생성
```bash
curl -X POST http://localhost:8000/total-manager/groups/{group_id}/collections \
  -H "Content-Type: application/json" \
  -d '{
    "title": "학기 초 모금",
    "amount": 50000,
    "due_date": "2024-01-15",
    "payment_type": "bank",
    "payment_value": "123-456-789012"
  }'
```

### 공지 발송
```bash
curl -X POST http://localhost:8000/total-manager/collections/{collection_id}/notice \
  -H "Content-Type: application/json" \
  -d '{"message": "모금 안내 메시지"}'
```

## 데이터베이스 스키마

### 테이블 구조

- `tm_groups`: 그룹 정보
- `tm_collections`: 모금 컬렉션 정보
- `tm_member_status`: 멤버 상태 정보
- `tm_event_logs`: 이벤트 로그

모든 테이블의 `id`는 ULID 문자열을 사용합니다.

### 인덱스

- `tm_groups(owner_id)`
- `tm_collections(group_id)`
- `tm_member_status(collection_id)`
- `tm_event_logs(collection_id, created_at desc)`

## 개발 참고사항

- 모든 Primary Key는 ULID 문자열을 사용합니다 (UUID 아님)
- 인증은 현재 임시로 구현되어 있으며, 실제 프로덕션에서는 JWT 토큰 기반 인증으로 교체해야 합니다
- 리마인더 발송 기능은 현재 로그만 생성하며, 실제 발송은 추후 구현 예정입니다


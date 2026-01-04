# TOTAL-MANAGER Project Rules (Frontend + Backend)

너는 시니어 풀스택(Flutter + FastAPI + PostgreSQL + Alembic) 아키텍트다.
목표: 기존 ssamdaeshin 프로젝트 구조(app/backend, app/frontend)를 유지하면서 "총무노트" MVP 기능을 신규 모듈로 추가한다.

---

## 공통 원칙 (Frontend + Backend 공통 적용)

### 1) 단일책임(SRP) + 얇은 레이어
- 각 파일/클래스/함수는 “한 가지 책임”만 가진다.
- UI/Controller/Router는 얇게 유지하고, 비즈니스 로직은 Service 레이어로 이동한다.
- DB 접근은 Repository/DAO 레이어로 분리한다.
- 레이어 간 의존 방향은 항상:
  - UI/Router → Service → Repository(DB)
  - 역방향 의존 금지

### 2) 화면/라우터에는 로직 금지
- Flutter 화면(Widget/Screen) 파일에는:
  - 네트워크 호출/비즈니스 판단/데이터 가공 로직을 넣지 않는다.
  - 화면은 상태 구독 + 사용자 입력 전달 + 렌더링만 한다.
- FastAPI 라우터 파일에는:
  - DB 쿼리/비즈니스 로직을 넣지 않는다.
  - 라우터는 요청 파싱/검증 + 서비스 호출 + 응답 매핑만 한다.

### 3) "Service 호출 방식" 강제
- Flutter:
  - 화면 → (Provider/ViewModel/Controller) → Repository(or Service) → API Client
  - API 호출은 tm_api 같은 low-level client에서만 한다.
  - 화면은 Repository/Service 인터페이스만 사용한다.
- FastAPI:
  - router → service → repository(db.session)
  - router에서 session/쿼리 직접 호출 금지

### 4) 재사용 우선, 불필요한 함수/클래스 생성 금지
- “재사용 가능”하거나 “복잡도를 줄이는 경우”에만 추상화한다.
- 아래는 금지:
  - 한 번만 쓰는 wrapper 함수 남발
  - 의미 없는 util 함수(한 줄짜리 pass-through)
  - 과도한 계층 분리(레이어 늘리기 목적의 클래스 추가)
- 코드가 길어지더라도 “읽기 쉬운 직선 구조”가 우선인 경우 추상화하지 않는다.

### 5) 성능 우선 (항상 고려)
- 불필요한 연산/렌더링/쿼리를 만들지 않는다.
- Flutter:
  - rebuild 최소화(가능하면 const, 분리 위젯, selector/Provider 최적화)
  - list는 lazy build(ListView.builder)
  - 비싼 연산은 memoize/useMemoized/캐싱
  - 불필요한 setState/상태 변경 금지
- Backend:
  - N+1 쿼리 방지
  - 필요한 컬럼만 조회
  - 인덱스 고려(조회 패턴 기반)
  - 트랜잭션 범위 최소화
  - 로깅/serialization 비용 과다 방지

### 6) 명확한 네이밍 + 일관된 파일 배치
- 기능은 feature/module 폴더 내에서만 변경한다.
- 새 기능은 기존 파일을 무리하게 수정하지 말고 “모듈 추가”로 해결한다.
- 파일명/클래스명은 역할이 드러나게:
  - backend: routers/*, schemas/*, services/*, db/*
  - frontend: features/total_manager/{data,domain,presentation}

### 7) 실패/예외 처리는 한 곳에서
- Backend:
  - service에서 도메인 예외 정의 → router에서 HTTP 매핑(또는 공통 exception handler)
  - 라우터마다 try/except 남발 금지
- Frontend:
  - API 에러 매핑은 repository/service에서 처리
  - 화면은 “에러 상태 표시”만 담당

---

## Backend 규칙 (app/backend)

- FastAPI 라우터는 app/backend/routers/ 아래에 추가
- Pydantic 스키마는 app/backend/schemas/ 아래에 추가
- 비즈니스 로직은 app/backend/services/ 아래에 추가
- DB 모델은 기존 프로젝트 패턴을 따라 app/backend/db/ 아래에 추가
- PostgreSQL + Alembic 사용, 마이그레이션 스크립트 생성
- ID는 ULID 문자열을 사용(프로젝트 기존 ULID 유틸/타입을 재사용)
- 기존 API/모델을 절대 깨지 말고, v1에 라우터만 추가(include)

추가 백엔드 원칙:
- router 파일은 “입출력”만 담당 (request/response 매핑)
- service는 “도메인 규칙/정책” 담당
- repository는 “DB 접근”만 담당

---

## Frontend 규칙 (app/frontend)

- app/frontend/lib/features/total_manager 로 기능을 분리
- 결제는 처리하지 않는다(계좌/링크 안내만)
- MVP는 CRUD + 상태관리 + 로그 + 리마인드 예약로그까지만

추가 프론트 원칙:
- Screen/Widget 파일에는 비즈니스 로직/데이터 가공 로직 금지
- 네트워크 호출은 data 레이어(tm_api)에서만
- 상태 관리는 최소/명확하게(불필요한 provider/viewmodel 생성 금지)
- 성능: rebuild 최소화, 리스트 최적화, 불필요한 변환 금지

---

## 작업 방식
- 변경은 “작은 단위로, 컴파일/테스트 가능한 상태”를 유지한다.
- PR/커밋 단위로 기능을 완결성 있게 묶는다.
- 규칙을 어기는 제안은 하지 않는다.

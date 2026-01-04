# 총무노트 백엔드 기능 설계 문서

## 목차
1. [개요](#개요)
2. [인증 및 사용자 관리](#인증-및-사용자-관리)
3. [그룹 관리](#그룹-관리)
4. [컬렉션 관리](#컬렉션-관리)
5. [멤버 관리](#멤버-관리)
6. [알림 및 공지](#알림-및-공지)
7. [리마인더 관리](#리마인더-관리)
8. [로그 관리](#로그-관리)
9. [사용자 설정](#사용자-설정)
10. [데이터베이스 스키마 확장](#데이터베이스-스키마-확장)

---

## 개요

프론트엔드 화면 구조를 분석하여 필요한 백엔드 API 엔드포인트와 기능을 설계합니다.

### 프론트엔드 화면 구조
```
- 인증 화면
  - 로그인 (카카오톡, 전화번호)
  - 회원가입
  - 온보딩 (첫 회원 전용)

- 메인 네비게이션
  - 노트 (컬렉션 목록)
  - 기록 (로그 목록)
  - 알림 (리마인더 목록)
  - 더보기 (설정)

- 컬렉션 관련
  - 컬렉션 상세
  - 컬렉션 생성
  - 멤버 관리

- 더보기 화면
  - 내 프로필
  - 알림 설정
  - 결제 수단 관리
  - 보안 설정
  - 도움말/약관 (정적)
```

---

## 인증 및 사용자 관리

### 1.1 사용자 모델 확장 필요사항

**기존 `user.py` 모델에 추가할 필드:**
```python
- phone: String (nullable, unique)  # 전화번호
- kakao_id: String (nullable, unique)  # 카카오톡 ID
- name: String (nullable)  # 사용자 이름
- email: String (nullable)  # 이메일
- profile_image_url: String (nullable)  # 프로필 이미지 URL
- is_onboarded: Boolean (default=False)  # 온보딩 완료 여부
- created_at: DateTime
- updated_at: DateTime
```

### 1.2 인증 API 엔드포인트

#### `POST /auth/login/kakao`
**카카오톡 로그인**
- Request Body:
  ```json
  {
    "kakao_token": "string",  // 카카오 액세스 토큰
    "kakao_id": "string"       // 카카오 사용자 ID
  }
  ```
- Response:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": "string",
      "name": "string",
      "email": "string",
      "phone": "string",
      "is_onboarded": boolean
    }
  }
  ```
- 로직:
  - 카카오 토큰 검증 (카카오 API 호출)
  - 기존 사용자면 로그인, 신규면 회원가입 진행
  - JWT 토큰 발급
  - `is_onboarded` 확인하여 온보딩 필요 여부 반환

#### `POST /auth/login/phone`
**전화번호 로그인**
- Request Body:
  ```json
  {
    "phone": "01012345678",
    "verification_code": "string"  // SMS 인증 코드 (선택)
  }
  ```
- Response: 동일 (카카오 로그인과 동일)
- 로직:
  - 전화번호로 사용자 조회
  - SMS 인증 코드 검증 (선택적)
  - JWT 토큰 발급

#### `POST /auth/signup`
**회원가입**
- Request Body:
  ```json
  {
    "name": "string",
    "phone": "string",
    "email": "string (optional)",
    "verification_code": "string (optional)"  // SMS 인증 코드
  }
  ```
- Response:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": "string",
      "name": "string",
      "phone": "string",
      "is_onboarded": false  // 항상 false
    }
  }
  ```
- 로직:
  - 전화번호 중복 확인
  - SMS 인증 코드 검증 (선택적)
  - 사용자 생성 (`is_onboarded=False`)
  - JWT 토큰 발급

#### `POST /auth/send-verification-code`
**SMS 인증 코드 발송**
- Request Body:
  ```json
  {
    "phone": "01012345678"
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "message": "인증 코드가 발송되었습니다"
  }
  ```
- 로직:
  - SMS 서비스 연동 (예: AWS SNS, Twilio 등)
  - 6자리 랜덤 코드 생성 및 저장 (Redis 권장)
  - 5분 유효기간 설정

#### `GET /auth/me`
**현재 사용자 정보 조회**
- Headers: `Authorization: Bearer {token}`
- Response:
  ```json
  {
    "id": "string",
    "name": "string",
    "email": "string",
    "phone": "string",
    "profile_image_url": "string",
    "is_onboarded": boolean,
    "created_at": "datetime"
  }
  ```

#### `POST /auth/onboarding/complete`
**온보딩 완료 처리**
- Headers: `Authorization: Bearer {token}`
- Request Body:
  ```json
  {
    "collection_id": "string"  // 온보딩 중 생성한 첫 컬렉션 ID (선택)
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "is_onboarded": true
  }
  ```
- 로직:
  - `is_onboarded=True`로 업데이트
  - 온보딩 완료 이벤트 로그 생성 (선택)

---

## 그룹 관리

### 2.1 기존 API (이미 구현됨)
- `POST /total-manager/groups` - 그룹 생성
- `GET /total-manager/groups` - 그룹 목록 조회

### 2.2 추가 필요 API

#### `GET /total-manager/groups/{group_id}`
**그룹 상세 조회**
- Response:
  ```json
  {
    "id": "string",
    "owner_id": "string",
    "name": "string",
    "type": "parents|club|study|other",
    "created_at": "datetime",
    "collections_count": 5,  // 컬렉션 개수
    "total_amount": 500000   // 총 모금액
  }
  ```

#### `PATCH /total-manager/groups/{group_id}`
**그룹 수정**
- Request Body:
  ```json
  {
    "name": "string (optional)",
    "type": "parents|club|study|other (optional)"
  }
  ```

#### `DELETE /total-manager/groups/{group_id}`
**그룹 삭제**
- 로직:
  - 소유자 확인
  - 관련 컬렉션 및 멤버 상태도 함께 삭제 (CASCADE)

---

## 컬렉션 관리

### 3.1 기존 API (이미 구현됨)
- `POST /total-manager/groups/{group_id}/collections` - 컬렉션 생성
- `GET /total-manager/groups/{group_id}/collections` - 컬렉션 목록 조회
- `GET /total-manager/collections/{collection_id}` - 컬렉션 상세 조회

### 3.2 추가 필요 API

#### `PATCH /total-manager/collections/{collection_id}`
**컬렉션 수정**
- Request Body:
  ```json
  {
    "title": "string (optional)",
    "amount": "integer (optional)",
    "due_date": "date (optional)",
    "payment_type": "bank|link (optional)",
    "payment_value": "string (optional)"
  }
  ```
- 로직:
  - 소유자 확인 (그룹의 owner_id)
  - 상태 자동 업데이트 (due_date 기반)

#### `DELETE /total-manager/collections/{collection_id}`
**컬렉션 삭제**
- 로직:
  - 소유자 확인
  - 관련 멤버 상태 및 로그도 함께 삭제 (CASCADE)

#### `GET /total-manager/collections/{collection_id}/summary`
**컬렉션 요약 정보**
- Response:
  ```json
  {
    "id": "string",
    "title": "string",
    "amount": 50000,
    "due_date": "date",
    "status": "active|due_soon|closed",
    "total_members": 10,
    "read_members": 7,
    "paid_members": 5,
    "current_amount": 250000,  // 현재 모금액
    "payment_type": "bank",
    "payment_value": "123-456-789012"
  }
  ```

#### `POST /total-manager/collections/{collection_id}/status/update`
**컬렉션 상태 자동 업데이트**
- 로직:
  - `due_date` 기반으로 `status` 자동 계산
  - 마감일 3일 전: `due_soon`
  - 마감일 지남: `closed`
  - 스케줄러로 주기적 실행 (선택)

---

## 멤버 관리

### 4.1 기존 API (이미 구현됨)
- `POST /total-manager/collections/{collection_id}/members` - 멤버 추가
- `GET /total-manager/collections/{collection_id}/members` - 멤버 목록 조회
- `POST /total-manager/members/{member_id}/read` - 읽음 처리
- `POST /total-manager/members/{member_id}/paid` - 납부 처리

### 4.2 추가 필요 API

#### `PATCH /total-manager/members/{member_id}`
**멤버 정보 수정**
- Request Body:
  ```json
  {
    "display_name": "string (optional)",
    "phone": "string (optional)"
  }
  ```

#### `DELETE /total-manager/members/{member_id}`
**멤버 삭제**
- 로직:
  - 컬렉션 소유자 확인
  - 멤버 상태 삭제

#### `POST /total-manager/collections/{collection_id}/members/bulk`
**멤버 일괄 추가**
- Request Body:
  ```json
  {
    "members": [
      {
        "display_name": "string",
        "phone": "string (optional)"
      }
    ]
  }
  ```
- Response:
  ```json
  {
    "created": 5,
    "failed": 0,
    "members": [...]
  }
  ```

---

## 알림 및 공지

### 5.1 기존 API (이미 구현됨)
- `POST /total-manager/collections/{collection_id}/notice` - 공지 발송

### 5.2 추가 필요 API

#### `GET /total-manager/collections/{collection_id}/notices`
**공지 발송 이력 조회**
- Response:
  ```json
  [
    {
      "id": "string",
      "collection_id": "string",
      "message": "string",
      "sent_at": "datetime",
      "recipient_count": 10,
      "read_count": 7
    }
  ]
  ```

#### `POST /total-manager/collections/{collection_id}/notice/test`
**공지 테스트 발송**
- Request Body:
  ```json
  {
    "message": "string",
    "test_phone": "string"  // 테스트용 전화번호
  }
  ```

---

## 리마인더 관리

### 6.1 데이터베이스 모델 추가 필요

**새 테이블: `tm_reminders`**
```python
class TMReminder(Base):
    __tablename__ = "tm_reminders"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    collection_id = Column(String, ForeignKey("tm_collections.id"), nullable=True)  # 선택적
    title = Column(String, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    repeat_type = Column(String, nullable=False)  # "none", "daily", "weekly"
    message = Column(String, nullable=True)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 6.2 API 엔드포인트

#### `POST /total-manager/reminders`
**리마인더 생성**
- Request Body:
  ```json
  {
    "collection_id": "string (optional)",
    "title": "string",
    "scheduled_at": "datetime",  // ISO 8601 형식
    "repeat_type": "none|daily|weekly",
    "message": "string (optional)"
  }
  ```
- Response:
  ```json
  {
    "id": "string",
    "user_id": "string",
    "collection_id": "string",
    "title": "string",
    "scheduled_at": "datetime",
    "repeat_type": "none|daily|weekly",
    "message": "string",
    "is_sent": false,
    "created_at": "datetime"
  }
  ```

#### `GET /total-manager/reminders`
**리마인더 목록 조회**
- Query Parameters:
  - `is_sent`: boolean (optional) - 발송 여부 필터
  - `collection_id`: string (optional) - 컬렉션 필터
  - `from_date`: date (optional) - 시작일
  - `to_date`: date (optional) - 종료일
- Response:
  ```json
  [
    {
      "id": "string",
      "collection_id": "string",
      "collection_title": "string",  // JOIN으로 가져옴
      "title": "string",
      "scheduled_at": "datetime",
      "repeat_type": "none|daily|weekly",
      "message": "string",
      "is_sent": boolean,
      "sent_at": "datetime",
      "created_at": "datetime"
    }
  ]
  ```

#### `GET /total-manager/reminders/{reminder_id}`
**리마인더 상세 조회**

#### `PATCH /total-manager/reminders/{reminder_id}`
**리마인더 수정**
- Request Body:
  ```json
  {
    "title": "string (optional)",
    "scheduled_at": "datetime (optional)",
    "repeat_type": "none|daily|weekly (optional)",
    "message": "string (optional)"
  }
  ```

#### `DELETE /total-manager/reminders/{reminder_id}`
**리마인더 삭제**

#### `POST /total-manager/reminders/{reminder_id}/send`
**리마인더 즉시 발송**
- 로직:
  - `is_sent=True`, `sent_at=now()` 업데이트
  - SMS/푸시 알림 발송
  - 이벤트 로그 생성 (`reminder_sent`)

### 6.3 스케줄러 작업
- **리마인더 자동 발송**: `scheduled_at`이 현재 시간 이전이고 `is_sent=False`인 리마인더 조회 후 발송
- **반복 리마인더 생성**: `repeat_type`이 `daily` 또는 `weekly`인 경우, 발송 후 다음 일정 생성
- **컬렉션 마감일 리마인더**: 컬렉션 생성 시 `due_date - 1일`, `due_date + 1일` 자동 리마인더 생성 (기존 로직과 통합)

---

## 로그 관리

### 7.1 기존 API (이미 구현됨)
- `GET /total-manager/collections/{collection_id}/logs` - 로그 목록 조회

### 7.2 추가 필요 API

#### `GET /total-manager/logs`
**전체 로그 조회 (사용자별)**
- Query Parameters:
  - `collection_id`: string (optional)
  - `type`: string (optional) - 로그 타입 필터
  - `from_date`: datetime (optional)
  - `to_date`: datetime (optional)
  - `limit`: integer (default: 50)
  - `offset`: integer (default: 0)
- Response:
  ```json
  {
    "total": 100,
    "limit": 50,
    "offset": 0,
    "logs": [...]
  }
  ```

#### `GET /total-manager/logs/stats`
**로그 통계**
- Response:
  ```json
  {
    "total_logs": 100,
    "by_type": {
      "notice_sent": 20,
      "read": 30,
      "paid_marked": 25,
      "reminder_scheduled": 15,
      "reminder_sent": 10
    },
    "recent_activity": [
      {
        "date": "2026-01-15",
        "count": 5
      }
    ]
  }
  ```

---

## 사용자 설정

### 8.1 데이터베이스 모델 추가 필요

**새 테이블: `user_settings`**
```python
class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    push_notifications_enabled = Column(Boolean, default=True)
    email_notifications_enabled = Column(Boolean, default=False)
    reminder_notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**새 테이블: `user_payment_methods`**
```python
class UserPaymentMethod(Base):
    __tablename__ = "user_payment_methods"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    bank_name = Column(String, nullable=False)  # 예: "신한은행"
    account_number = Column(String, nullable=False)  # 예: "110-123-456789"
    account_holder = Column(String, nullable=False)  # 예금주명
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**새 테이블: `user_security_settings`**
```python
class UserSecuritySettings(Base):
    __tablename__ = "user_security_settings"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    biometric_enabled = Column(Boolean, default=False)  # 생체 인증
    password_hash = Column(String, nullable=True)  # 비밀번호 해시 (선택적)
    last_password_change = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**새 테이블: `user_login_devices`**
```python
class UserLoginDevice(Base):
    __tablename__ = "user_login_devices"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(String, nullable=False)  # 기기 고유 ID
    device_name = Column(String, nullable=False)  # 예: "iPhone 15 Pro"
    device_type = Column(String, nullable=False)  # "ios", "android", "web"
    last_login_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 8.2 프로필 API

#### `GET /users/me`
**현재 사용자 프로필 조회**
- Response:
  ```json
  {
    "id": "string",
    "name": "string",
    "email": "string",
    "phone": "string",
    "profile_image_url": "string",
    "created_at": "datetime"
  }
  ```

#### `PATCH /users/me`
**프로필 수정**
- Request Body:
  ```json
  {
    "name": "string (optional)",
    "email": "string (optional)",
    "phone": "string (optional)",
    "profile_image_url": "string (optional)"
  }
  ```

#### `POST /users/me/profile-image`
**프로필 이미지 업로드**
- Request: multipart/form-data
  - `file`: image file
- Response:
  ```json
  {
    "profile_image_url": "string"
  }
  ```

### 8.3 알림 설정 API

#### `GET /users/me/settings/notifications`
**알림 설정 조회**
- Response:
  ```json
  {
    "push_notifications_enabled": true,
    "email_notifications_enabled": false,
    "reminder_notifications_enabled": true
  }
  ```

#### `PATCH /users/me/settings/notifications`
**알림 설정 수정**
- Request Body:
  ```json
  {
    "push_notifications_enabled": boolean (optional),
    "email_notifications_enabled": boolean (optional),
    "reminder_notifications_enabled": boolean (optional)
  }
  ```

### 8.4 결제 수단 API

#### `GET /users/me/payment-methods`
**결제 수단 목록 조회**
- Response:
  ```json
  [
    {
      "id": "string",
      "bank_name": "신한은행",
      "account_number": "110-123-456789",
      "account_holder": "홍길동",
      "is_default": true,
      "created_at": "datetime"
    }
  ]
  ```

#### `POST /users/me/payment-methods`
**결제 수단 추가**
- Request Body:
  ```json
  {
    "bank_name": "string",
    "account_number": "string",
    "account_holder": "string",
    "is_default": boolean (optional, default: false)
  }
  ```
- 로직:
  - `is_default=true`인 경우 기존 기본 계좌 해제

#### `PATCH /users/me/payment-methods/{payment_method_id}`
**결제 수단 수정**

#### `DELETE /users/me/payment-methods/{payment_method_id}`
**결제 수단 삭제**

#### `POST /users/me/payment-methods/{payment_method_id}/set-default`
**기본 결제 수단 설정**

### 8.5 보안 설정 API

#### `GET /users/me/settings/security`
**보안 설정 조회**
- Response:
  ```json
  {
    "biometric_enabled": false,
    "has_password": true,
    "last_password_change": "datetime"
  }
  ```

#### `POST /users/me/settings/security/password`
**비밀번호 변경**
- Request Body:
  ```json
  {
    "current_password": "string",
    "new_password": "string"
  }
  ```

#### `POST /users/me/settings/security/biometric`
**생체 인증 설정**
- Request Body:
  ```json
  {
    "enabled": boolean
  }
  ```

#### `GET /users/me/login-devices`
**로그인 기기 목록 조회**
- Response:
  ```json
  [
    {
      "id": "string",
      "device_name": "iPhone 15 Pro",
      "device_type": "ios",
      "last_login_at": "datetime",
      "created_at": "datetime"
    }
  ]
  ```

#### `DELETE /users/me/login-devices/{device_id}`
**기기 로그아웃 (기기 삭제)**

---

## 데이터베이스 스키마 확장

### 9.1 마이그레이션 필요 사항

1. **사용자 모델 확장** (`users` 테이블)
   - `phone`, `kakao_id`, `name`, `email`, `profile_image_url`, `is_onboarded` 컬럼 추가
   - 인덱스: `phone`, `kakao_id`

2. **리마인더 테이블** (`tm_reminders`)
   - 새 테이블 생성
   - 인덱스: `user_id`, `scheduled_at`, `collection_id`

3. **사용자 설정 테이블** (`user_settings`)
   - 새 테이블 생성
   - 인덱스: `user_id` (unique)

4. **결제 수단 테이블** (`user_payment_methods`)
   - 새 테이블 생성
   - 인덱스: `user_id`

5. **보안 설정 테이블** (`user_security_settings`)
   - 새 테이블 생성
   - 인덱스: `user_id` (unique)

6. **로그인 기기 테이블** (`user_login_devices`)
   - 새 테이블 생성
   - 인덱스: `user_id`, `device_id`

### 9.2 인덱스 최적화

- `tm_collections`: `group_id`, `status`, `due_date`
- `tm_member_status`: `collection_id`, `phone`
- `tm_event_logs`: `collection_id`, `created_at` (DESC), `type`
- `tm_reminders`: `user_id`, `scheduled_at`, `is_sent`

---

## 인증 미들웨어

### 10.1 JWT 토큰 관리

- **토큰 발급**: 로그인/회원가입 시
- **토큰 검증**: 모든 보호된 엔드포인트에서 `Authorization: Bearer {token}` 헤더 확인
- **토큰 갱신**: `POST /auth/refresh` 엔드포인트 (선택적)
- **토큰 만료**: 기본 7일 (설정 가능)

### 10.2 권한 확인

- **그룹 소유자**: `owner_id == current_user_id`
- **컬렉션 접근**: 그룹의 `owner_id == current_user_id`
- **멤버 관리**: 컬렉션의 그룹 소유자만 가능

---

## 외부 서비스 연동

### 11.1 카카오톡 로그인
- 카카오 REST API 연동
- 액세스 토큰 검증
- 사용자 정보 조회

### 11.2 SMS 발송
- AWS SNS 또는 Twilio 연동
- 인증 코드 발송
- 알림 발송 (공지, 리마인더)

### 11.3 푸시 알림
- Firebase Cloud Messaging (FCM) 또는 Apple Push Notification Service (APNS)
- 사용자 디바이스 토큰 관리
- 알림 발송

### 11.4 파일 업로드
- 프로필 이미지 업로드
- AWS S3 또는 로컬 스토리지
- 이미지 리사이징 (선택적)

---

## 에러 처리

### 12.1 공통 에러 코드
- `400 Bad Request`: 잘못된 요청 데이터
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `409 Conflict`: 중복 데이터 (전화번호, 이메일 등)
- `422 Unprocessable Entity`: 검증 실패
- `500 Internal Server Error`: 서버 오류

### 12.2 커스텀 에러 응답 형식
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지",
    "details": {}  // 선택적
  }
}
```

---

## 성능 최적화

### 13.1 쿼리 최적화
- N+1 쿼리 방지 (SQLAlchemy `joinedload`, `selectinload` 사용)
- 페이징 처리 (limit/offset 또는 cursor-based)
- 인덱스 활용

### 13.2 캐싱
- Redis 활용 (선택적)
- 사용자 정보 캐싱
- 컬렉션 요약 정보 캐싱

### 13.3 배치 처리
- 리마인더 발송 배치 작업
- 컬렉션 상태 자동 업데이트 배치

---

## 보안 고려사항

### 14.1 데이터 보호
- 비밀번호 해시 (bcrypt)
- 전화번호 마스킹 (API 응답 시)
- 계좌번호 마스킹 (일부만 표시)

### 14.2 API 보안
- Rate Limiting (DDoS 방지)
- CORS 설정
- SQL Injection 방지 (SQLAlchemy ORM 사용)

### 14.3 인증 보안
- JWT 토큰 만료 시간 관리
- 리프레시 토큰 (선택적)
- 기기별 토큰 관리

---

## 구현 우선순위

### Phase 1: 핵심 기능 (필수)
1. 인증 시스템 (카카오톡, 전화번호 로그인)
2. 사용자 모델 확장
3. 온보딩 완료 처리
4. 기존 API 보완 (그룹/컬렉션/멤버)

### Phase 2: 사용자 설정 (중요)
1. 프로필 관리
2. 알림 설정
3. 결제 수단 관리

### Phase 3: 리마인더 시스템 (중요)
1. 리마인더 CRUD
2. 리마인더 스케줄러
3. 알림 발송 연동

### Phase 4: 보안 및 최적화 (선택)
1. 보안 설정
2. 로그인 기기 관리
3. 성능 최적화
4. 캐싱

---

## API 엔드포인트 요약

### 인증 (`/auth`)
- `POST /auth/login/kakao`
- `POST /auth/login/phone`
- `POST /auth/signup`
- `POST /auth/send-verification-code`
- `GET /auth/me`
- `POST /auth/onboarding/complete`

### 사용자 (`/users`)
- `GET /users/me`
- `PATCH /users/me`
- `POST /users/me/profile-image`
- `GET /users/me/settings/notifications`
- `PATCH /users/me/settings/notifications`
- `GET /users/me/payment-methods`
- `POST /users/me/payment-methods`
- `PATCH /users/me/payment-methods/{id}`
- `DELETE /users/me/payment-methods/{id}`
- `POST /users/me/payment-methods/{id}/set-default`
- `GET /users/me/settings/security`
- `POST /users/me/settings/security/password`
- `POST /users/me/settings/security/biometric`
- `GET /users/me/login-devices`
- `DELETE /users/me/login-devices/{id}`

### 리마인더 (`/total-manager/reminders`)
- `POST /total-manager/reminders`
- `GET /total-manager/reminders`
- `GET /total-manager/reminders/{id}`
- `PATCH /total-manager/reminders/{id}`
- `DELETE /total-manager/reminders/{id}`
- `POST /total-manager/reminders/{id}/send`

### 기존 API 보완
- `GET /total-manager/groups/{id}`
- `PATCH /total-manager/groups/{id}`
- `DELETE /total-manager/groups/{id}`
- `PATCH /total-manager/collections/{id}`
- `DELETE /total-manager/collections/{id}`
- `GET /total-manager/collections/{id}/summary`
- `PATCH /total-manager/members/{id}`
- `DELETE /total-manager/members/{id}`
- `POST /total-manager/collections/{id}/members/bulk`
- `GET /total-manager/logs`
- `GET /total-manager/logs/stats`

---

## 다음 단계

1. 데이터베이스 마이그레이션 스크립트 작성
2. 인증 서비스 구현
3. 사용자 설정 서비스 구현
4. 리마인더 서비스 및 스케줄러 구현
5. API 엔드포인트 구현
6. 테스트 작성
7. 문서화 (OpenAPI/Swagger)


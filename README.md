# 총무노트 (Total Manager)

쉽고 빠른 모금 관리 애플리케이션

## 📋 프로젝트 소개

총무노트는 그룹 모금 관리를 쉽고 효율적으로 할 수 있도록 도와주는 애플리케이션입니다. 학부모 모임, 동아리, 스터디 그룹 등 다양한 목적의 모임에서 사용할 수 있습니다.

## 🛠 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Authentication**: JWT

### Frontend
- **Framework**: Flutter 3.9.2+
- **Language**: Dart
- **State Management**: Provider/Listenable
- **HTTP Client**: Dio

## 📦 사전 요구사항

### 공통
- Git
- Docker & Docker Compose (데이터베이스용)

### Backend
- Python 3.11 이상
- pip 또는 pipenv

### Frontend
- Flutter SDK 3.9.2 이상
- Android Studio 또는 Xcode (모바일 빌드용)

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd total-manager
```

### 2. 데이터베이스 실행

```bash
docker-compose up -d
```

PostgreSQL이 `localhost:5432`에서 실행됩니다.

### 3. Backend 설정

#### 3.1 가상환경 생성 및 활성화

```bash
cd app/backend
python3 -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

#### 3.2 의존성 설치

```bash
pip install -r requirements.txt
```

#### 3.3 환경 변수 설정

`.env` 파일을 생성합니다:

```bash
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://totalmanager:totalmanager123@localhost:5432/totalmanager

# Security Configuration
SECRET_KEY=dev-secret-key-change-in-production-please-use-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=true
ENVIRONMENT=development
EOF
```

#### 3.4 데이터베이스 마이그레이션

```bash
# 마이그레이션 실행
alembic upgrade head
```

#### 3.5 서버 실행

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 `http://localhost:8000`에서 실행됩니다.

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

### 4. Frontend 설정

#### 4.1 의존성 설치

```bash
cd app/frontend
flutter pub get
```

#### 4.2 코드 생성 (JSON Serialization)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

#### 4.3 앱 실행

```bash
# iOS 시뮬레이터
flutter run -d ios

# Android 에뮬레이터
flutter run -d android

# 웹 브라우저
flutter run -d chrome
```

## 📁 프로젝트 구조

```
total-manager/
├── app/
│   ├── backend/              # FastAPI 백엔드
│   │   ├── alembic/          # 데이터베이스 마이그레이션
│   │   ├── db/               # 데이터베이스 모델 및 세션
│   │   ├── routers/          # API 라우터
│   │   ├── schemas/          # Pydantic 스키마
│   │   ├── services/         # 비즈니스 로직
│   │   ├── utils/            # 유틸리티 함수
│   │   ├── main.py           # FastAPI 앱 진입점
│   │   └── requirements.txt  # Python 의존성
│   │
│   └── frontend/             # Flutter 프론트엔드
│       ├── lib/
│       │   ├── features/    # 기능별 모듈
│       │   │   ├── data/     # 데이터 레이어 (API, Repository)
│       │   │   ├── domain/  # 도메인 모델
│       │   │   ├── presentation/  # UI 화면
│       │   │   ├── services/     # 서비스 레이어
│       │   │   └── widgets/      # 재사용 가능한 위젯
│       │   └── theme/        # 테마 및 디자인 토큰
│       ├── pubspec.yaml      # Flutter 의존성
│       └── ...
│
├── docker-compose.yml        # PostgreSQL 컨테이너 설정
└── README.md                 # 프로젝트 문서
```

## 🔧 개발 가이드

### Backend 개발

#### 새로운 마이그레이션 생성

```bash
cd app/backend
alembic revision --autogenerate -m "설명"
alembic upgrade head
```

#### API 테스트

```bash
# 서버 실행 후
curl http://localhost:8000/health
```

### Frontend 개발

#### Hot Reload

Flutter는 기본적으로 Hot Reload를 지원합니다. 코드 수정 후 `r` 키를 눌러 즉시 반영할 수 있습니다.

#### 코드 생성 (변경 후)

도메인 모델을 수정한 경우:

```bash
cd app/frontend
flutter pub run build_runner build --delete-conflicting-outputs
```

#### 린트 체크

```bash
flutter analyze
```

## 🌐 API 엔드포인트

### 인증
- `POST /auth/login/phone` - 전화번호 로그인
- `POST /auth/signup` - 회원가입
- `POST /auth/send-verification-code` - 인증번호 발송

### 그룹
- `POST /total-manager/groups` - 그룹 생성
- `GET /total-manager/groups` - 그룹 목록 조회
- `GET /total-manager/groups/{group_id}` - 그룹 상세 조회
- `PATCH /total-manager/groups/{group_id}` - 그룹 수정
- `DELETE /total-manager/groups/{group_id}` - 그룹 삭제

### 컬렉션
- `POST /total-manager/groups/{group_id}/collections` - 컬렉션 생성
- `GET /total-manager/groups/{group_id}/collections` - 컬렉션 목록 조회
- `GET /total-manager/collections/{collection_id}` - 컬렉션 상세 조회

### 멤버
- `POST /total-manager/collections/{collection_id}/members` - 멤버 추가
- `GET /total-manager/collections/{collection_id}/members` - 멤버 목록 조회
- `POST /total-manager/members/{member_id}/read` - 읽음 처리
- `POST /total-manager/members/{member_id}/paid` - 납부 처리

전체 API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## 🗄 데이터베이스

### 연결 정보 (개발 환경)

- **Host**: localhost
- **Port**: 5432
- **Database**: totalmanager
- **Username**: totalmanager
- **Password**: totalmanager123

### 주요 테이블

- `tm_groups` - 그룹 정보
- `tm_collections` - 컬렉션(모금) 정보
- `tm_member_status` - 멤버 상태 정보
- `tm_event_logs` - 이벤트 로그
- `tm_reminders` - 알림 정보

## 🐛 문제 해결

### Backend

#### 데이터베이스 연결 오류

```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재시작
docker-compose restart db
```

#### 포트 충돌

다른 포트 사용:

```bash
uvicorn main:app --reload --port 8001
```

### Frontend

#### 의존성 충돌

```bash
cd app/frontend
flutter clean
flutter pub get
```

#### 빌드 오류

```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

## 📝 환경 변수

### Backend (.env)

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL 연결 문자열 | - |
| `SECRET_KEY` | JWT 서명 키 | - |
| `ALGORITHM` | JWT 알고리즘 | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간(분) | 30 |
| `DEBUG` | 디버그 모드 | true |
| `ENVIRONMENT` | 환경 설정 | development |

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**Happy Coding! 🚀**


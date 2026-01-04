# 환경 변수 설정 가이드

## .env 파일 생성

`app/backend/.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# Database Configuration
DATABASE_URL=postgresql://totalmanager:totalmanager123@localhost:5432/totalmanager

# Security Configuration
SECRET_KEY=dev-secret-key-change-in-production-please-use-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=true
ENVIRONMENT=development
```

## 빠른 생성 방법

터미널에서 실행:

```bash
cd app/backend
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

## 환경 변수 설명

- `DATABASE_URL`: PostgreSQL 연결 문자열 (docker-compose.yml의 설정과 일치해야 함)
- `SECRET_KEY`: JWT 토큰 서명용 비밀키 (프로덕션에서는 강력한 랜덤 키 사용)
- `ALGORITHM`: JWT 알고리즘 (기본값: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 토큰 만료 시간 (분)
- `DEBUG`: 디버그 모드 (개발: true, 프로덕션: false)
- `ENVIRONMENT`: 환경 설정 (development/production)

## 확인

파일이 제대로 생성되었는지 확인:

```bash
cat app/backend/.env
```


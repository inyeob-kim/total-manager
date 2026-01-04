#!/bin/bash
# 데이터베이스 시작 스크립트

set -e

echo "🐳 데이터베이스 컨테이너 시작 중..."

# 프로젝트 루트로 이동
cd "$(dirname "$0")/../../.."

# docker compose 또는 docker-compose 확인
if command -v docker &> /dev/null; then
    if docker compose version &> /dev/null; then
        # Docker Compose V2 (docker compose)
        docker compose up -d db
        echo "✅ 데이터베이스 시작 완료 (docker compose)"
    elif command -v docker-compose &> /dev/null; then
        # Docker Compose V1 (docker-compose)
        docker-compose up -d db
        echo "✅ 데이터베이스 시작 완료 (docker-compose)"
    else
        echo "❌ Docker Compose를 찾을 수 없습니다."
        echo "   Docker Desktop을 설치하거나 docker-compose를 설치해주세요."
        exit 1
    fi
else
    echo "❌ Docker를 찾을 수 없습니다."
    echo "   Docker Desktop을 설치해주세요."
    exit 1
fi

echo ""
echo "📊 데이터베이스 상태 확인 중..."
sleep 2

# 컨테이너 상태 확인
if docker compose ps &> /dev/null; then
    docker compose ps db
elif docker-compose ps &> /dev/null; then
    docker-compose ps db
fi

echo ""
echo "✅ 준비 완료!"
echo "   연결 정보: postgresql://totalmanager:totalmanager123@localhost:5432/totalmanager"


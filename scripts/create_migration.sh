#!/bin/bash
# Alembic 마이그레이션 파일 생성 시 충돌 방지 스크립트
# 새 마이그레이션 생성 전에 main 브랜치와 동기화 확인

set -e

echo "🔄 마이그레이션 생성 전 체크 중..."

# main/master 브랜치의 최신 변경사항 fetch
git fetch origin main 2>/dev/null || git fetch origin master 2>/dev/null || true

# 현재 브랜치가 최신 main과 동기화되어 있는지 확인
MAIN_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
BEHIND_COUNT=$(git rev-list --count HEAD..origin/$MAIN_BRANCH 2>/dev/null || echo "0")

if [ "$BEHIND_COUNT" -gt 0 ]; then
    echo "⚠️  경고: 현재 브랜치가 $MAIN_BRANCH보다 $BEHIND_COUNT 커밋 뒤처져 있습니다."
    echo "마이그레이션 생성 전에 'git pull origin $MAIN_BRANCH'를 권장합니다."
    echo ""
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 마이그레이션 메시지 인자 확인
if [ -z "$1" ]; then
    echo "사용법: ./scripts/create_migration.sh \"마이그레이션_설명\""
    exit 1
fi

echo "📝 마이그레이션 생성 중..."
alembic revision --autogenerate -m "$1"

echo ""
echo "✅ 마이그레이션이 생성되었습니다!"
echo "💡 생성된 파일을 검토하고 필요한 경우 수정하세요."

#!/bin/bash
# Alembic 다중 헤드 체크 스크립트
# CI/CD 파이프라인에서 PR 머지 전에 실행

set -e

echo "🔍 Alembic 마이그레이션 헤드 확인 중..."

# 현재 헤드 수 확인
HEAD_COUNT=$(alembic heads | wc -l)

if [ "$HEAD_COUNT" -gt 1 ]; then
    echo "❌ 에러: 다중 마이그레이션 헤드가 감지되었습니다!"
    echo ""
    echo "현재 헤드 목록:"
    alembic heads
    echo ""
    echo "📋 해결 방법:"
    echo "1. 'alembic merge heads -m \"merge_migrations\"' 명령으로 헤드를 병합하세요"
    echo "2. 또는 마이그레이션 파일의 down_revision을 수정하세요"
    echo ""
    exit 1
fi

echo "✅ 마이그레이션 헤드가 단일 상태입니다 (정상)"
alembic heads
exit 0

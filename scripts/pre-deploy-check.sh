#!/bin/bash
# 로컬에서 배포 전 검증 스크립트
# 사용법: ./scripts/pre-deploy-check.sh

set -e

echo "🔍 배포 전 검증 시작..."
echo "================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# 1. 모든 모듈 Import 체크
echo -e "\n📦 ${YELLOW}[1/5] 모듈 Import 검증${NC}"
python -c "
import sys
import importlib

modules = [
    'asset_management.main',
    'asset_management.app.user.routes',
    'asset_management.app.auth.router',
    'asset_management.app.club.routes',
    'asset_management.app.assets.router',
    'asset_management.app.schedule.router',
    'asset_management.app.club_member.router',
    'asset_management.app.admin.routes',
    'asset_management.database.session',
]

errors = []
for module in modules:
    try:
        importlib.import_module(module)
        print(f'  ✅ {module}')
    except Exception as e:
        errors.append(f'{module}: {e}')
        print(f'  ❌ {module}: {e}')

if errors:
    sys.exit(1)
" || { echo -e "${RED}Import 검증 실패${NC}"; ERRORS=$((ERRORS+1)); }

# 2. FastAPI 앱 로드 체크
echo -e "\n🚀 ${YELLOW}[2/5] FastAPI 앱 로드 검증${NC}"
python -c "
from asset_management.main import app
assert app is not None
print(f'  ✅ 앱 로드 성공 (라우트 {len(app.routes)}개)')
" || { echo -e "${RED}앱 로드 실패${NC}"; ERRORS=$((ERRORS+1)); }

# 3. OpenAPI 스키마 생성 체크
echo -e "\n📄 ${YELLOW}[3/5] OpenAPI 스키마 생성 검증${NC}"
python -c "
from asset_management.main import app
schema = app.openapi()
print(f'  ✅ 스키마 생성 성공 ({len(schema[\"paths\"])} 엔드포인트)')
" || { echo -e "${RED}스키마 생성 실패${NC}"; ERRORS=$((ERRORS+1)); }

# 4. Ruff 린트 체크 (설치되어 있으면)
echo -e "\n🔎 ${YELLOW}[4/5] 린트 검사${NC}"
if command -v ruff &> /dev/null; then
    ruff check asset_management --quiet && echo "  ✅ 린트 통과" || { echo -e "  ${YELLOW}⚠️ 린트 경고 있음${NC}"; }
else
    echo "  ⏭️ ruff 미설치, 스킵"
fi

# 5. 타입 체크 (설치되어 있으면)
echo -e "\n🔬 ${YELLOW}[5/5] 타입 검사${NC}"
if command -v mypy &> /dev/null; then
    mypy asset_management --ignore-missing-imports --no-error-summary 2>/dev/null && echo "  ✅ 타입 체크 통과" || echo -e "  ${YELLOW}⚠️ 타입 경고 있음${NC}"
else
    echo "  ⏭️ mypy 미설치, 스킵"
fi

# 결과 출력
echo -e "\n================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 배포 전 검증 통과!${NC}"
    exit 0
else
    echo -e "${RED}❌ ${ERRORS}개 검증 실패${NC}"
    exit 1
fi

#!/usr/bin/env bash
# PickEarly 배포: 저장소가 만들어진 뒤 이 스크립트 하나로 푸시 + GitHub Pages 활성화까지 끝낸다.
# 사용법:  bash deploy.sh
set -euo pipefail
REPO="happy1ch/pickearly"
cd "$(dirname "$0")"

echo "▶ 빌드"
python3 build.py >/dev/null
git add -A
git diff --cached --quiet || git commit -q -m "deploy: $(date '+%Y-%m-%d %H:%M')"

echo "▶ 저장소 확인"
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  echo "✗ $REPO 저장소가 없습니다. GitHub에서 빈 공개 저장소를 먼저 만들어 주세요."
  echo "  https://github.com/new?name=pickearly&visibility=public"
  exit 1
fi

echo "▶ 원격 연결·병합"
git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$REPO.git"
git fetch -q origin main || true
if git rev-parse --verify -q origin/main >/dev/null; then
  # GitHub에서 저장소를 만들며 README를 추가한 경우를 흡수
  git pull -q --rebase --allow-unrelated-histories origin main || true
fi

echo "▶ 푸시"
git push -u origin main

echo "▶ GitHub Pages 활성화 (main /docs)"
gh api -X POST "repos/$REPO/pages" \
  -f "source[branch]=main" -f "source[path]=/docs" 2>/dev/null \
  || gh api -X PUT "repos/$REPO/pages" \
       -f "source[branch]=main" -f "source[path]=/docs" 2>/dev/null \
  || echo "  (이미 활성화되어 있거나 권한이 없습니다 — Settings → Pages에서 확인)"

gh api "repos/$REPO/pages" --jq '"  상태: \(.status // "building") · 주소: \(.html_url)"' 2>/dev/null || true
echo "▶ 완료: https://happy1ch.github.io/pickearly/  (반영까지 1~2분)"

#!/usr/bin/env bash
# [옛 방식] Direct Upload 로 급히 올릴 때 쓰는 스크립트.
# 이제는 GitHub 저장소 → Cloudflare Pages(Git 연동) 자동 빌드가 기본입니다(README 5장).
# Direct Upload 로 올리면 /admin 관리자 기능(Functions)은 동작하지 않습니다.
# 사용법:  bash deploy-cloudflare.sh
# 그다음 dash.cloudflare.com → Workers 및 Pages → pickearly → 배포 → 배포 생성 → zip 업로드.
set -euo pipefail
cd "$(dirname "$0")"

OUT_ZIP="../worktmp/pickearly-deploy.zip"
mkdir -p ../worktmp

echo "▶ 빌드 (https://pickearly.com 기준)"
python3 build.py

echo "▶ 업로드용 zip 생성"
python3 - "$OUT_ZIP" <<'PY'
import os, sys, zipfile
out = sys.argv[1]
if os.path.exists(out):
    os.remove(out)
count = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, dn, fn in os.walk("docs"):
        for f in sorted(fn):
            if f in (".DS_Store",):
                continue
            p = os.path.join(dp, f)
            z.write(p, os.path.relpath(p, "docs"))
            count += 1
print(f"  {count}개 파일 → {out}")
PY

echo "▶ 완료: Cloudflare Pages → pickearly → 배포 → 배포 생성 → 위 zip 업로드"

#!/usr/bin/env bash
# PickEarly 배포 준비: 사이트 빌드 → Cloudflare Pages(Direct Upload)에 올릴 zip 생성.
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

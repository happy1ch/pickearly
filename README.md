# PickEarly · 픽얼리 — 얼리어답터 연구소

쿠팡(고급 AI 가전)과 알리(AI 아이디어 기기) 제휴 리뷰를 한곳에 모으는 개인 리뷰 사이트입니다.
원고(Markdown)를 `content/`에 두고 `build.py`가 `docs/`에 정적 사이트를 만듭니다. 서버·DB 없이 **Cloudflare Pages**(Direct Upload)로 운영합니다.

- **라이브: https://pickearly.com** (2026-11-25 연결)
- 보조 주소: https://www.pickearly.com · https://pickearly.pages.dev
- Cloudflare Pages 프로젝트: `pickearly` (계정 Iloveyou0191@gmail.com, 계정 ID `3e5ae0542f7fcf9862ef47b5a4ec2f6d`)
- 도메인 `pickearly.com`은 같은 Cloudflare 계정에 등록되어 있어, Pages의 Custom domains 에 추가하면 CNAME(`@`, `www` → `pickearly.pages.dev`, 프록시됨)이 자동 생성됩니다.

## 구조

```
content/            원고 (Markdown, 손대지 않고 그대로 읽음)
theme/style.css     디자인 (다크 모드 자동 대응)
theme/app.js        카테고리 필터 · 검색 · 목차 · 링크 복사
build.py            사이트 빌드 (HTML · sitemap.xml · robots.txt · feed.xml)
gen_images.py       OG 이미지 / 썸네일 생성 (PIL)
docs/               배포되는 결과물 (이 폴더의 내용을 그대로 업로드)
deploy-cloudflare.sh  빌드 + 업로드용 zip 만들기
```

## 원고 추가하기

1. `content/새글.md` 로 원고를 넣습니다. (맨 위 `# 제목`, `##` 소제목, `|표|`, `> 인용`, `👉 **[버튼](링크)**` 지원)
2. `build.py`의 `ARTICLES` 목록에 항목을 추가합니다.
   - `slug`, `file`, `cat`(`coupang` | `ali`), `title`, `excerpt`, `date`, `thumb`, `og`, `tags`, `disclosure`, `takeaways`
3. 썸네일 이미지를 `docs/assets/images/`에, OG 이미지를 `docs/assets/og/`에 넣습니다.
4. 빌드 → Cloudflare Pages 에 재업로드(아래 참고).

## 빌드

```bash
python3 gen_images.py      # OG·썸네일 다시 만들 때만
python3 build.py           # docs/ 생성 (기본 도메인 https://pickearly.com)
```

> 주소 규칙: Cloudflare Pages는 `.html` 주소를 확장자 없는 주소로 308 정규화합니다.
> 그래서 빌드 결과물의 링크·canonical·og:url·sitemap·feed는 모두 확장자 없는 주소
> (`/articles`, `/articles/<slug>`, `/about`)로 나옵니다. 링크를 손으로 넣을 때도 `.html`을 붙이지 마세요.

## 배포 (Cloudflare Pages · Direct Upload)

```bash
bash deploy-cloudflare.sh          # 빌드하고 worktmp/pickearly-deploy.zip 생성
```

그다음 브라우저에서:

1. https://dash.cloudflare.com → **Compute (Workers & Pages)** → **pickearly** 프로젝트
2. **배포** 탭 → **배포 생성(Create deployment)** → `worktmp/pickearly-deploy.zip` 업로드 → **저장 및 배포**
3. 30초 안에 https://pickearly.com 에 반영됩니다.

> **주의** — Workers & Pages 의 **Create → Upload your static files** 는 새 Workers 방식(`*.workers.dev`)입니다.
> `pickearly.pages.dev` 주소를 유지하려면 그 화면 아래의 **"레거시 Pages 워크플로를 사용해야 합니까? Pages로 계속"** 으로 들어가야 합니다.
> 커스텀 도메인(`pickearly.com`, `www.pickearly.com`)은 Pages 프로젝트 → **사용자 지정 도메인**에 연결되어 있습니다.

### (참고) GitHub Pages 경로는 쓰지 않습니다

`deploy.sh`는 초기 GitHub Pages용 스크립트이고, `docs/`의 결과물이 이제 확장자 없는 주소 기준이라
GitHub Pages(`/docs` 소스)에 그대로 올리면 `/articles` 같은 링크가 404가 됩니다.
GitHub 저장소를 미러로 쓰려면 `.html` 주소 기준으로 다시 빌드해야 합니다.

## 제휴 고지

쿠팡 파트너스 및 알리익스프레스 어필리에이트 활동의 일환으로, 링크를 통한 구매 시 일정액의 수수료를 제공받습니다. 구매 가격은 동일합니다.

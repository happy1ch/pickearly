# PickEarly · 픽얼리 — 얼리어답터 연구소

쿠팡(AI 스마트 가전)과 알리(AI 아이디어 기기) 제휴 리뷰를 한곳에 모으는 개인 리뷰 사이트입니다.
원고(Markdown)를 `content/`에 두고 `build.py`가 `docs/`에 정적 사이트를 만듭니다. 서버·DB 없이 **Cloudflare Pages**로 운영합니다.

- **라이브: https://pickearly.com**
- 보조 주소: https://www.pickearly.com · https://pickearly.pages.dev
- GitHub: https://github.com/happy1ch/pickearly
- 관리자 화면: **https://pickearly.com/admin**

---

## 1. 구조

```
content/*.md            글 한 편 = 파일 하나 (맨 위 YAML 프런트매터 + Markdown 본문)
theme/admin.html        관리자 화면(/admin) — 빌드하면 docs/admin/index.html
theme/style.css         사이트 디자인 (다크 모드 자동 대응)
theme/app.js            카테고리 필터 · 검색 · 목차 · 링크 복사
theme/assets/images/    관리자에서 올린 대표 이미지 (빌드가 docs/assets/images/ 로 복사)
functions/api/          Cloudflare Pages Functions — 로그인·글 저장·이미지 업로드
build.py                사이트 빌드 (HTML · sitemap.xml · robots.txt · feed.xml · admin)
frontmatter.py          원고 프런트매터 읽기/쓰기 (외부 라이브러리 없이)
gen_images.py           OG 이미지 / 썸네일 생성 (PIL)
docs/                   배포되는 결과물
```

**글 목록은 코드에 없습니다.** `build.py`가 `content/*.md`를 전부 스캔해 발행일 내림차순으로 사이트를 만듭니다.
그래서 글을 하나 추가·수정·삭제하려면 **md 파일 하나만** 넣거나 고치면 됩니다(관리자 화면이 그 일을 대신 해 줍니다).

---

## 2. 글 쓰는 세 가지 방법

### ① 관리자 화면 (권장) — `pickearly.com/admin`

휴대폰·PC 모두에서 씁니다. 비밀번호 하나로 들어갑니다.

1. **새 글 쓰기** → 제목을 넣으면 주소(슬러그)가 자동으로 만들어집니다(고칠 수 있음).
2. 요약문·카테고리·대표 이미지를 넣고 본문을 씁니다. 오른쪽(모바일은 ‘미리보기’ 탭)에서 바로 확인합니다.
3. **발행하기** → GitHub에 커밋 → Cloudflare Pages가 자동으로 다시 만들어 **약 30초 뒤 사이트에 반영**됩니다.

- **초안으로 저장**은 사이트에 나가지 않습니다(`draft: true`). 나중에 열어 **발행하기**를 누르면 공개됩니다.
- **이미 발행된 글**에서는 버튼이 `저장` / `저장하고 발행`으로 바뀝니다. 실수로 글이 내려가지 않습니다.
  내리려면 저장 줄의 **비공개로** 버튼을 씁니다.
- 도구 버튼: 제휴 고지 넣기 · 구매 링크 목록 · 👉 버튼 · 글 골격(들어가며→포인트→체크리스트→단점→구매 링크→마치며→참고 자료).

### ② 파일로 직접 — `content/*.md`

GitHub 웹 편집기에서 파일을 고치거나 새 파일을 만들어도 똑같이 배포됩니다.
파일 이름은 자유지만 `slug`(주소)는 프런트매터에서 정합니다.

### ③ 피클에게 맡기기

“이 상품 리뷰 써서 올려줘”라고 하면 `content/`에 원고를 쓰고 커밋합니다. 목록·사이트맵·RSS·관리자 목록은 자동으로 따라옵니다.

---

## 3. 원고 형식 (프런트매터)

```markdown
---
slug: bespoke-ai-steam-auto
cat: coupang
title: "삼성 비스포크 AI 스팀 자동 급배수, 물통 안 버려도 되는 로봇청소기의 조건"
short_title: |-
  물통을 버리는 로봇청소기,
  사기 전에 볼 세 가지
excerpt: "직배수는 성능이 아니라 '설치'의 문제입니다. …"
date: 2026-11-25
updated: 2026-11-25
thumb: assets/images/thumb-bespoke-ai-steam.png
thumb_alt: "비스포크 AI 스팀 자동 급배수 모델 비교"
og: assets/og/og-bespoke-ai-steam.png
tags:
  - "비스포크 AI 스팀"
  - "자동 급배수"
disclosure: "이 글은 쿠팡 파트너스 활동의 일환으로, …"
takeaways:
  - "자동 급배수(직배수)는 청소기 성능이 아니라 <b>설치 방식</b>입니다."
collapse_notes:
  - "링크 검증 메모"
featured: true
order: 1
draft: false
---

# 제목

## 들어가며 …

본문. `##` 소제목은 자동으로 목차(sec-1, sec-2 …)가 붙습니다.
```

| 키 | 필수 | 설명 |
|---|---|---|
| `slug` | ✔ | 기사 주소 `/articles/<slug>` · 영소문자·숫자·하이픈 |
| `cat` | ✔ | `coupang`(AI 스마트 가전) 또는 `ali`(AI 아이디어 기기) |
| `title` | ✔ | 기사 제목 (검색 결과·OG 제목) |
| `excerpt` | ✔ | 1~2문장 요약 (목록 카드·meta description) |
| `date` | ✔ | 발행일 `YYYY-MM-DD` — 목록 정렬 기준 |
| `updated` |  | 수정일 (없으면 `date`) |
| `short_title` |  | 홈 커버용 짧은 제목 (줄바꿈 가능) |
| `thumb` / `thumb_alt` |  | 대표 이미지 경로(`assets/images/…`)와 설명 |
| `og` |  | OG 이미지 경로 (없으면 홈 이미지) |
| `tags` |  | 태그 목록 |
| `disclosure` |  | 기사 맨 위 제휴 고지 문구 |
| `takeaways` |  | 3줄 요약 (HTML `<b>` 가능) |
| `collapse_notes` |  | 본문 안에서 접히는 메모 블록의 시작 문구 |
| `featured` |  | 홈 ‘이번 호 커버’로 올리기 |
| `order` |  | 같은 날짜 안에서의 순서 (큰 값이 먼저) |
| `draft` |  | `true`면 사이트에 넣지 않음 |

> 본문 규칙: `#` 제목 / `##` 소제목 / `|표|` / `> 인용` / `- 목록` / `![그림](경로)` /
> `👉 **[버튼](링크)**` / `### 태그`부터는 본문이 아님. 이미지 경로는 파일 이름만 맞으면 `assets/images/`에서 찾습니다.

---

## 4. 빌드

```bash
python3 build.py           # docs/ 생성 (기본 도메인 https://pickearly.com)
python3 build.py --domain https://staging.example.com
```

- 표준 라이브러리만 씁니다(PyYAML 불필요). 빌드 환경에 파이썬 3만 있으면 됩니다.
- `docs/admin/index.html` · `sitemap.xml` · `robots.txt` · `feed.xml` · `_headers`도 함께 만듭니다.
- `content/`에서 사라진 글의 `docs/articles/*.html`은 빌드할 때 정리됩니다.
- 주소 규칙: Cloudflare Pages는 `.html` 주소를 확장자 없는 주소로 308 정규화합니다.
  그래서 링크·canonical·sitemap·feed는 모두 `/articles`, `/articles/<slug>`, `/about` 형태입니다. 링크를 손으로 넣을 때도 `.html`을 붙이지 마세요.

---

## 5. 관리자 모드 준비 (최초 1회)

`/admin`은 **Cloudflare Pages Functions**로 동작합니다. Functions는 **Git 연동 빌드에서만** 함께 배포되므로,
지금의 Direct Upload 프로젝트에서는 쓸 수 없습니다. 아래 순서대로 한 번만 설정하면 됩니다.

> ⚠️ **Direct Upload 프로젝트는 Git 연동으로 바꿀 수 없습니다**(Cloudflare 정책).
> 새 Pages 프로젝트를 만들어 GitHub 저장소와 연결하고, `pickearly.com` 도메인을 그쪽으로 옮깁니다.
> 옮기는 동안에도 사이트는 계속 열려 있습니다(도메인을 새 프로젝트에 붙이는 순간부터 새 빌드가 서비스됨).

### ① GitHub 토큰 만들기 (관리자 화면이 저장소에 커밋할 때 씀)

1. https://github.com/settings/personal-access-tokens/new
2. **Repository access** → *Only select repositories* → `happy1ch/pickearly`
3. **Permissions → Repository permissions → Contents: Read and write** 만 주고 나머지는 *No access*
4. 만료일은 1년(만료되면 새로 만들어 교체). 생성된 `github_pat_…` 값을 복사.

### ② GitHub 저장소에 코드 올리기

```bash
cd pickearly
git push -u origin main      # 원격이 비어 있으면 첫 푸시
```

### ③ Cloudflare Pages 프로젝트를 Git 연동으로 새로 만들기

1. https://dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
2. `happy1ch/pickearly` 선택 (목록에 없으면 *Configure GitHub App*에서 저장소 접근 허용)
3. 빌드 설정:

   | 항목 | 값 |
   |---|---|
   | Project name | `pickearly-git` (기존 `pickearly`와 달라야 함) |
   | Production branch | `main` |
   | Framework preset | `None` |
   | **Build command** | `python3 build.py` |
   | **Build output directory** | `docs` |

4. **Save and Deploy** → 첫 빌드가 끝나면 `https://pickearly-git.pages.dev` 에서 확인.

### ④ 환경변수 (Settings → Variables and Secrets → Production)

| 이름 | 값 | 필수 |
|---|---|---|
| `ADMIN_PASSWORD` | 관리자 로그인 비밀번호 (길게, 다른 곳과 겹치지 않게) | **필수** |
| `GITHUB_TOKEN` | ①에서 만든 `github_pat_…` | **필수** |
| `GITHUB_REPO` | `happy1ch/pickearly` (기본값과 같으면 생략) | 선택 |
| `GITHUB_BRANCH` | `main` (기본값과 같으면 생략) | 선택 |
| `SESSION_SECRET` | 토큰 서명 키. 없으면 `ADMIN_PASSWORD`를 씀 | 선택 |
| `DEPLOY_HOOK_URL` | Deploy Hook 주소 (Git 연동이면 없어도 자동 재빌드) | 선택 |

`ADMIN_PASSWORD`·`GITHUB_TOKEN`은 **Secret(암호화)** 으로 넣으세요. 값을 바꾸면 로그인이 즉시 무효가 되니 다시 로그인하면 됩니다.

### ⑤ 도메인 옮기기

1. 새 프로젝트(`pickearly-git`) → **Custom domains** → `pickearly.com` 추가 → **Begin CNAME setup** → Cloudflare가 기존 레코드 교체를 제안하면 승인.
2. 같은 방법으로 `www.pickearly.com` 도 추가.
3. 확인 후 옛 Direct Upload 프로젝트는 **남겨 두거나**(롤백용) 지웁니다. 지우면 `pickearly.pages.dev` 주소는 사라집니다.

### ⑥ 확인

- `https://pickearly.com/admin` → 비밀번호 입력 → 로그인
- **새 글 쓰기** → 저장 → 30초 뒤 사이트 확인
- 문제가 있으면 `https://pickearly.com/api/posts` 를 브라우저로 열어 봅니다.
  `{"ok":false,"error":"UNAUTHORIZED"}` 가 나오면 Functions가 살아 있다는 뜻입니다(정상).

---

## 6. API (참고)

| 경로 | 메서드 | 하는 일 |
|---|---|---|
| `/api/auth` | POST | `{password}` → 세션 토큰(HMAC-SHA256, 기본 30일) |
| `/api/posts` | GET | `content/*.md` 목록 (원문 + sha) |
| `/api/posts` | PUT | `{file, raw, sha?}` → 커밋 (sha 있으면 수정, 없으면 생성) |
| `/api/posts` | DELETE | `{file, sha}` → 삭제 커밋 |
| `/api/upload` | POST | `{filename, data(base64)}` → `theme/assets/images/` 커밋 |

- 모든 요청은 `Authorization: Bearer <토큰>` 이 필요합니다.
- 비밀번호를 8회 틀리면 10분간 잠깁니다.
- 같은 글을 두 곳에서 동시에 고치면 `CONFLICT`(409)가 나고, 화면은 새로고침 후 다시 저장하라고 안내합니다.

---

## 7. 검색 노출 차단 (`/admin`)

- `docs/admin/index.html` 에 `<meta name="robots" content="noindex, nofollow, noarchive">`
- `robots.txt` 에 `Disallow: /admin`
- `_headers` 로 `/admin/*`·`/api/*` 에 `X-Robots-Tag: noindex, nofollow`
- 관리자 화면은 `sitemap.xml`·`feed.xml`에 넣지 않습니다.

---

## 8. 로컬에서 확인하기

```bash
# 화면만 볼 때
python3 build.py
python3 -m http.server 8000 --directory docs     # http://localhost:8000/admin/

# API까지 (Wrangler)
npx wrangler pages dev docs --compatibility-date=2026-01-01 \
  --binding ADMIN_PASSWORD=test1234 --binding GITHUB_TOKEN=... --binding GITHUB_REPO=happy1ch/pickearly
```

`wrangler pages dev` 는 `docs/`의 정적 파일과 `functions/`를 함께 띄웁니다.

---

## 9. 문제가 생기면

| 증상 | 원인 / 해결 |
|---|---|
| `/admin` 에서 “관리자 API가 아직 연결되지 않았습니다” | Git 연동 프로젝트가 아님(Direct Upload). 5장 ③ 참고 |
| 로그인은 되는데 목록이 안 나옴 | `GITHUB_TOKEN` 권한(Contents: Read and write) 또는 `GITHUB_REPO` 확인 |
| 저장 시 “GitHub 토큰이 거부되었습니다” | 토큰 만료·오타. 새 토큰으로 교체 |
| 저장은 되는데 사이트가 안 바뀜 | ① 빌드 로그 확인 ② `python3 build.py` 실패 여부 ③ `draft: true` 인지 확인 |
| 글이 사라짐 | `draft: true` 로 저장됐을 수 있음. 관리자 목록의 ‘초안’ 배지 확인 → 발행 |
| 로그인이 자꾸 풀림 | `ADMIN_PASSWORD`를 바꾸면 기존 토큰이 모두 무효가 됨(정상) |

---

## 10. 제휴 고지

쿠팡 파트너스 및 알리익스프레스 어필리에이트 활동의 일환으로, 링크를 통한 구매 시 일정액의 수수료를 제공받습니다. 구매 가격은 동일합니다.

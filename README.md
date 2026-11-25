# PickEarly · 픽얼리 — 얼리어답터 연구소

쿠팡(고급 AI 가전)과 알리(AI 아이디어 기기) 제휴 리뷰를 한곳에 모으는 개인 리뷰 사이트입니다.
원고(Markdown)를 `content/`에 두고 `build.py`가 `docs/`에 정적 사이트를 만듭니다. 서버·DB 없이 GitHub Pages로 운영합니다.

- 라이브: https://happy1ch.github.io/pickearly/
- 예정 도메인: `pickearly.com`

## 구조

```
content/            원고 (Markdown, 손대지 않고 그대로 읽음)
theme/style.css     디자인 (다크 모드 자동 대응)
theme/app.js        카테고리 필터 · 검색 · 목차 · 링크 복사
build.py            사이트 빌드 (HTML · sitemap.xml · robots.txt · feed.xml)
gen_images.py       OG 이미지 / 썸네일 생성 (PIL)
docs/               배포되는 결과물 (GitHub Pages 소스)
```

## 원고 추가하기

1. `content/새글.md` 로 원고를 넣습니다. (맨 위 `# 제목`, `##` 소제목, `|표|`, `> 인용`, `👉 **[버튼](링크)**` 지원)
2. `build.py`의 `ARTICLES` 목록에 항목을 추가합니다.
   - `slug`, `file`, `cat`(`coupang` | `ali`), `title`, `excerpt`, `date`, `thumb`, `og`, `tags`, `disclosure`, `takeaways`
3. 썸네일 이미지를 `docs/assets/images/`에, OG 이미지를 `docs/assets/og/`에 넣습니다.
4. 빌드 → 커밋 → 푸시.

```bash
python3 build.py
git add -A && git commit -m "새 글: ..." && git push
```

## 빌드

```bash
python3 gen_images.py      # OG·썸네일 다시 만들 때만
python3 build.py           # docs/ 생성
```

## 배포 (GitHub Pages)

- 저장소 Settings → Pages → Source: `Deploy from a branch` → Branch `main` / folder `/docs`.
- 푸시하면 1~2분 안에 https://happy1ch.github.io/pickearly/ 에 반영됩니다.

## 커스텀 도메인 (`pickearly.com`) 연결

도메인을 등록한 뒤 아래 네 단계만 하면 됩니다.

1. **도메인 등록업체 DNS에 레코드 추가**

   | 타입 | 호스트 | 값 |
   |---|---|---|
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | CNAME | `www` | `happy1ch.github.io` |

2. **`docs/CNAME` 파일 추가** — 내용은 한 줄: `pickearly.com`
3. **도메인 기준으로 다시 빌드** — canonical·OG·sitemap 주소가 `https://pickearly.com` 으로 바뀝니다.

   ```bash
   python3 build.py --domain https://pickearly.com
   ```
4. **저장소 Settings → Pages → Custom domain** 에 `pickearly.com` 입력 후 `Enforce HTTPS` 체크.

> Vercel로 옮길 경우: 이 저장소를 그대로 Import 하고 Root Directory를 `docs/`로, Framework Preset을 `Other`로 두면 됩니다(`vercel.json` 포함).

## 제휴 고지

쿠팡 파트너스 및 알리익스프레스 어필리에이트 활동의 일환으로, 링크를 통한 구매 시 일정액의 수수료를 제공받습니다. 구매 가격은 동일합니다.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PickEarly · 픽얼리 — 얼리어답터 연구소  (static site builder)

원고(content/*.md)를 읽어 docs/ 아래에 정적 사이트를 만든다.
  python3 build.py            # 사이트 빌드
  python3 build.py --domain https://pickearly.com   # 커스텀 도메인 기준으로 빌드

원고는 손대지 않고 그대로 읽는다. 메타데이터는 아래 ARTICLES 에만 있다.
"""

import argparse
import datetime as dt
import html
import json
import math
import os
from urllib.parse import quote
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
THEME = os.path.join(ROOT, "theme")
OUT = os.path.join(ROOT, "docs")

# --------------------------------------------------------------------------
# 사이트 설정
# --------------------------------------------------------------------------
SITE = {
    "url": "https://happy1ch.github.io/pickearly",
    "name": "PickEarly",
    "name_ko": "픽얼리",
    "sub": "얼리어답터 연구소",
    "desc": "쿠팡·알리에서 진짜 쓸 만한 것만 골라, 사기 전에 알아야 할 것부터 정리하는 얼리어답터 리뷰 연구소.",
    "author": "픽얼리 편집부",
    "lang": "ko",
    "email": "",
}

CATS = {
    "coupang": {"label": "AI 스마트 가전", "vendor": "쿠팡", "class": "cat-coupang"},
    "ali": {"label": "AI 아이디어 기기", "vendor": "알리", "class": "cat-ali"},
}

ARTICLES = [
    {
        "slug": "bespoke-ai-steam-auto",
        "file": "bespoke-ai-steam.md",
        "cat": "coupang",
        "title": "삼성 비스포크 AI 스팀 자동 급배수, 물통 안 버려도 되는 로봇청소기의 조건",
        "short_title": "물통을 버리는 로봇청소기,\n사기 전에 볼 세 가지",
        "excerpt": "직배수는 성능이 아니라 '설치'의 문제입니다. 리폼비 포함 여부, 스테이션 구조, 모델명 끝자리 — 돈을 쓰기 전에 확인할 세 가지를 정리했습니다.",
        "date": "2026-11-25",
        "updated": "2026-11-25",
        "thumb": "assets/images/thumb-bespoke-ai-steam.png",
        "thumb_alt": "비스포크 AI 스팀 자동 급배수 모델 비교 (VR70 · VR80 · VR90)",
        "og": "assets/og/og-bespoke-ai-steam.png",
        "tags": ["비스포크 AI 스팀", "자동 급배수", "직배수 로봇청소기", "VR80F01SDG", "리폼비 포함"],
        "disclosure": "이 글은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다. 구매 가격은 동일합니다.",
        "takeaways": [
            "자동 급배수(직배수)는 청소기 성능이 아니라 <b>설치 방식</b>입니다. 배관과 하부장 사진으로 설치 상담을 먼저 받아야 합니다.",
            "100℃ 스팀 살균과 열풍 건조는 본체가 아니라 <b>스테이션</b>이 하는 일입니다. 걸레 냄새 문제를 없애는 핵심입니다.",
            "쿠팡 표시가 기준으로는 <b>플러스(VR80F01SDG, 1,590,000원)</b> 가 일반형·울트라와 각각 10만 원 차이로 가장 균형적입니다.",
        ],
        "collapse_notes": ["링크 검증 메모"],
        "featured": True,
    },
    {
        "slug": "ai-voice-recorder-boya-newyes",
        "file": "ali-ai-recorder.md",
        "cat": "ali",
        "title": "명함보다 얇은 'AI 녹음기', 알리에서 9만 원대 — 회의·상담·강의 다 받아 적는 요즘 아이디어 상품 2종",
        "short_title": "명함보다 얇은 AI 녹음기,\n9만 원대와 5만 원대",
        "excerpt": "스마트폰 녹음은 통화가 오면 끊기고, 한 시간짜리 파일은 다시 듣기 어렵습니다. BOYA Notra Neo와 NEWYES Ailog를 같은 조건에서 비교했습니다.",
        "date": "2026-11-25",
        "updated": "2026-11-25",
        "thumb": "assets/images/boya-notra-neo.jpg",
        "thumb_alt": "BOYA Notra Neo AI 노트테이커",
        "og": "assets/og/og-ai-voice-recorder.png",
        "tags": ["AI 녹음기", "BOYA Notra Neo", "NEWYES Ailog", "AI 메모기", "알리 추천"],
        "disclosure": "이 글은 알리익스프레스 어필리에이트 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.",
        "takeaways": [
            "이 기기는 <b>기기 값보다 '앱 이용 조건'</b>에서 갈립니다. 한국어 전사 지원 여부가 아직 판매 페이지에 확정 표기되어 있지 않습니다.",
            "무료 전사량은 BOYA 월 320분, NEWYES 월 600분이지만 <b>초과 요금</b>은 NEWYES가 훨씬 비쌉니다.",
            "녹음은 오프라인에서도 되고 전사·요약은 나중에 앱에서 합니다. 회의 중 통화가 와도 녹음이 끊기지 않는 것이 핵심입니다.",
        ],
        "collapse_notes": [],
        "featured": False,
    },
]

SITE_NAV = [
    ("index.html", "홈"),
    ("articles.html", "전체 기사"),
    ("about.html", "연구소 소개"),
]

BRAND_MARK = """<svg class="brand-mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
<path d="M3 23h26" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
<path d="M16 24.2V15" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
<path d="M7.6 17.6A9.6 9.6 0 0 1 24.4 17.6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="16" cy="9.4" r="2.5" fill="currentColor"/>
</svg>"""


# --------------------------------------------------------------------------
# Markdown → HTML (이 사이트 원고에 필요한 만큼만)
# --------------------------------------------------------------------------
IMG_MAP = {
    "images/2026-11-25-aliali-ai-recorder/boya-notra-neo-official.jpg": "boya-notra-neo.jpg",
    "images/2026-11-25-aliali-ai-recorder/newyes-ailog-ar0101-rgb.jpg": "newyes-ailog.jpg",
}


def img_src(src: str, depth: int = 1) -> str:
    """원고의 이미지 경로를 배포 경로로 바꾼다."""
    name = IMG_MAP.get(src, os.path.basename(src))
    return ("../" * depth) + "assets/images/" + name


def esc(t: str) -> str:
    return html.escape(t, quote=False)


def inline(text: str, depth: int = 1) -> str:
    t = esc(text)

    codes = []

    def stash(m):
        codes.append(m.group(1))
        return f"\x00C{len(codes) - 1}\x00"

    t = re.sub(r"`([^`]+)`", stash, t)

    # images
    def img(m):
        alt, src = m.group(1), m.group(2)
        return f'<img src="{img_src(src, depth)}" alt="{alt}" loading="lazy">'

    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, t)

    # links
    def link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith("http"):
            return (
                f'<a href="{href}" target="_blank" rel="noopener sponsored nofollow">{label}</a>'
                if ("coupang.com" in href or "aliexpress.com" in href)
                else f'<a href="{href}" target="_blank" rel="noopener">{label}</a>'
            )
        return f'<a href="{href}">{label}</a>'

    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)

    # 남은 생 URL 링크화 (제휴 단축 링크)[변경] — 속성값 안은 제외
    def bare(m):
        url = m.group(1)
        tail = ""
        while url and url[-1] in ".,;:":
            tail = url[-1] + tail
            url = url[:-1]
        rel = "noopener sponsored nofollow" if ("coupang.com" in url or "aliexpress.com" in url) else "noopener"
        return f'<a href="{url}" target="_blank" rel="{rel}">{url}</a>' + tail

    t = re.sub(r'(?<!["\'=<>])(https?://[^\s<>"\')\]|]+)', bare, t)

    t = re.sub(r"~~(.+?)~~", r"<del>\1</del>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w])__(.+?)__(?![\w])", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\*\w])\*([^\*\n]+?)\*(?![\*\w])", r"<em>\1</em>", t)

    def unstash(m):
        return f"<code>{codes[int(m.group(1))]}</code>"

    t = re.sub(r"\x00C(\d+)\x00", unstash, t)
    return t


def slug_id(i: int) -> str:
    return f"sec-{i}"


def parse_table(lines, i):
    header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    i += 2  # skip separator
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
        i += 1
    out = ['<div class="table-wrap"><table>', "<thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in header]
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out), i


def parse_list(lines, i):
    ordered = bool(re.match(r"^\s*\d+\.\s", lines[i]))
    items = []
    while i < len(lines):
        line = lines[i]
        if ordered and re.match(r"^\s*\d+\.\s", line):
            items.append(re.sub(r"^\s*\d+\.\s+", "", line))
        elif not ordered and re.match(r"^\s*[-*]\s+", line):
            items.append(re.sub(r"^\s*[-*]\s+", "", line))
        elif line.strip() == "":
            # 허용: 항목 사이 빈 줄 1개
            if i + 1 < len(lines) and re.match(r"^\s*(\d+\.|[-*])\s+", lines[i + 1]):
                i += 1
                continue
            break
        else:
            break
        i += 1
    tag = "ol" if ordered else "ul"
    is_link_list = not ordered and sum(
        1 for s in items if "coupang.com" in s or "aliexpress.com" in s
    ) >= 2
    cls = ' class="link-list"' if is_link_list else ""
    body = "\n".join(f"<li>{inline(s)}</li>" for s in items)
    return f"<{tag}{cls}>\n{body}\n</{tag}>", i


def parse_quote(lines, i, collapse_keys):
    buf = []
    while i < len(lines) and lines[i].lstrip().startswith(">"):
        buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
        i += 1
    # 내부 블록 처리 (문단 / 목록)
    inner = []
    j = 0
    while j < len(buf):
        if re.match(r"^\s*[-*]\s+", buf[j]):
            html_part, j = parse_list(buf, j)
            inner.append(html_part)
        elif buf[j].strip() == "":
            j += 1
        else:
            para = []
            while j < len(buf) and buf[j].strip() != "" and not re.match(r"^\s*[-*]\s+", buf[j]):
                para.append(buf[j])
                j += 1
            inner.append("<p>" + inline(" ".join(p.strip() for p in para)) + "</p>")
    body = "\n".join(inner)
    text = " ".join(b for b in buf if b.strip())
    for key in collapse_keys:
        if text.startswith(key) or key in text[:40]:
            # summary: «링크 검증 메모(2026-11-25 12:19 확인)» 형태로 다듬는다
            head = text.split("\n")[0]
            m = re.match(r"^(.*?)\((.*?)\)\s*:?\s*", head)
            if m:
                summary = f"{m.group(1).strip()} ({m.group(2)} 확인)"
            else:
                summary = head.split(":")[0].strip() or key
            body_inner = body
            first_p = body_inner.find("</p>")
            if first_p != -1 and body_inner.startswith("<p>") and key in body_inner[:first_p]:
                body_inner = body_inner[first_p + 4 :].lstrip()
            return (
                '<details class="note-details"><summary>'
                + inline(summary)
                + '<span class="nd-caret" aria-hidden="true">▾</span></summary>\n<div class="note-details-body">'
                + body_inner
                + "</div></details>",
                i,
            )
    return f"<blockquote>\n{body}\n</blockquote>", i


def md_to_html(md: str, collapse_keys=None):
    collapse_keys = collapse_keys or []
    lines = md.replace("\r\n", "\n").split("\n")

    # 발행 메모 블록 제거 (원고에만 있는 내부 메모)
    cut = [n for n, l in enumerate(lines) if "발행 전 확인용 메모" in l or "[발행 메모]" in l]
    if cut:
        start = cut[0]
        # 메모를 감싼 주석 시작 지점까지 되돌린다
        while start > 0 and "<!--" not in lines[start]:
            start -= 1
        lines = lines[:start]

    out = []
    toc = []
    i = 0
    h2n = 0
    title_h1 = None
    tags = []
    first_block = True

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if s == "":
            i += 1
            continue

        # 태그 블록
        if s.startswith("#") and ("#" in s[1:]):
            hashtags = re.findall(r"#([0-9A-Za-z가-힣_]+)", s)
            if hashtags and len(s) > 3:
                tags.extend(hashtags)
                i += 1
                continue

        if re.match(r"^#\s+", s):
            title_h1 = re.sub(r"^#\s+", "", s)
            i += 1
            continue

        m = re.match(r"^##\s+(.*)$", s)
        if m:
            h2n += 1
            sid = slug_id(h2n)
            heading = m.group(1)
            out.append(f'<h2 id="{sid}">{inline(heading)}</h2>')
            toc.append((sid, re.sub(r"<[^>]+>", "", inline(heading))))
            i += 1
            continue

        if re.match(r"^###\s+", s):
            h3txt = re.sub(r"^###\s+", "", s).strip()
            if h3txt in ("태그", "Tags", "tag"):
                break  # 태그 블록부터는 본문이 아니다
            out.append("<h3>" + inline(h3txt) + "</h3>")
            i += 1
            continue

        if re.match(r"^####\s+", s):
            out.append("<h4>" + inline(re.sub(r"^####\s+", "", s)) + "</h4>")
            i += 1
            continue

        if re.match(r"^-{3,}$", s) or re.match(r"^\*{3,}$", s):
            out.append("<hr>")
            i += 1
            continue

        if s.startswith(">"):
            part, i = parse_quote(lines, i, collapse_keys)
            # 본문 첫머리의 제휴 고지는 상단 고지 박스로 대신한다
            if first_block and "수수료를 제공받습니다" in part:
                first_block = False
                continue
            out.append(part)
            first_block = False
            continue

        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|?$", lines[i + 1].strip()):
            part, i = parse_table(lines, i)
            out.append(part)
            continue

        if re.match(r"^[-*]\s+", s) or re.match(r"^\d+\.\s+", s):
            part, i = parse_list(lines, i)
            out.append(part)
            continue

        if s.startswith("!["):
            mm = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)$", s)
            if mm:
                alt, src = mm.group(1), mm.group(2)
                out.append(
                    f'<figure><img src="{img_src(src)}" alt="{esc(alt)}" loading="lazy">'
                    + (f"<figcaption>{inline(alt)}</figcaption>" if alt else "")
                    + "</figure>"
                )
                i += 1
                continue

        # 👉 CTA 줄
        if s.startswith("👉"):
            mm = re.search(r"\[([^\]]+)\]\(([^)\s]+)\)", s)
            if mm:
                label, href = mm.group(1), mm.group(2)
                out.append(
                    '<p class="cta-line"><a class="cta" href="'
                    + href
                    + '" target="_blank" rel="noopener sponsored nofollow">'
                    + inline(label)
                    + ' <span class="cta-arrow">→</span></a>'
                    + '<span class="cta-note">제휴 링크 · 구매 가격은 동일합니다</span></p>'
                )
                i += 1
                continue

        # 문단
        para = [s]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if nxt == "":
                break
            if re.match(r"^(#{1,4}\s|>|\||-{3,}$|!\[|👉)", nxt) or re.match(r"^[-*]\s+", nxt) or re.match(r"^\d+\.\s+", nxt):
                break
            para.append(nxt)
            i += 1
        joined = " ".join(para)
        if re.fullmatch(r"\*[^*]+\*", joined.strip()):
            out.append('<p class="dateline">' + inline(joined) + "</p>")
        else:
            out.append("<p>" + inline(joined) + "</p>")
        first_block = False

    body = "\n".join(out)

    # 참고 자료 섹션은 작게
    body = body.replace('<h2 id="sec-', '<h2 id="sec-')
    body = re.sub(r'(<h2 id="sec-\d+">)(참고 자료.*?)</h2>', r'\1\2</h2>', body)
    return body, toc, tags, title_h1


def decorate(body: str) -> str:
    """참고 자료 구획은 작은 글씨로, 출처 리스트임을 드러낸다."""
    m = re.search(r'<h2 id="(sec-\d+)">(참고 자료[^<]*)</h2>', body)
    if not m:
        return body
    head, tail = body[: m.start()], body[m.end() :]
    # 마지막 hr은 구분선으로만 남긴다
    tail = tail.strip()
    return (
        head.rstrip()
        + f'\n<h2 class="sources-h" id="{m.group(1)}">{m.group(2)}</h2>\n<div class="sources">\n'
        + tail
        + "\n</div>"
    )


# --------------------------------------------------------------------------
# 공통 레이아웃
# --------------------------------------------------------------------------
def rel(depth: int, path: str) -> str:
    return ("../" * depth) + path


def head_tags(title, desc, canonical, og_image, depth, extra_json=None, page_type="website"):
    R = lambda p: rel(depth, p)  # noqa: E731
    js = ""
    if extra_json:
        js = "\n".join(
            '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>"
            for o in extra_json
        )
    og = ""
    if og_image:
        og = (
            f'<meta property="og:image" content="{SITE["url"]}/{og_image}">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{esc(SITE["name"])} {esc(SITE["name_ko"])}">\n'
            f'<meta name="twitter:image" content="{SITE["url"]}/{og_image}">\n'
        )
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{esc(SITE['author'])}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#15171b">
<meta property="og:type" content="{page_type}">
<meta property="og:site_name" content="픽얼리 PickEarly">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="ko_KR">
{og}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<link rel="icon" href="{R('assets/favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{R('assets/favicon.svg')}">
<link rel="alternate" type="application/rss+xml" title="픽얼리 PickEarly" href="{R('feed.xml')}">
<link rel="stylesheet" href="{R('assets/style.css')}">
{js}"""


def header_html(depth, current):
    R = lambda p: rel(depth, p)  # noqa: E731
    nav = []
    for href, label in SITE_NAV:
        cur = ' aria-current="page"' if href == current else ""
        nav.append(f'<a href="{R(href)}"{cur}>{label}</a>')
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{R('index.html')}" aria-label="픽얼리 홈">
      {BRAND_MARK}
      <span class="brand-text">
        <span class="brand-name">Pick<span class="thin">Early</span></span>
        <span class="brand-sub">얼리어답터 연구소</span>
      </span>
    </a>
    <nav class="nav" aria-label="주요 메뉴">
      {''.join(nav)}
    </nav>
    <a class="header-cta" href="{R('index.html')}#lab">연구소 원칙 <span aria-hidden="true">↗</span></a>
  </div>
</header>"""


def footer_html(depth):
    R = lambda p: rel(depth, p)  # noqa: E731
    year = dt.date.today().year
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-inner">
      <div>
        <a class="brand" href="{R('index.html')}">
          {BRAND_MARK}
          <span class="brand-text">
            <span class="brand-name">Pick<span class="thin">Early</span></span>
            <span class="brand-sub">얼리어답터 연구소</span>
          </span>
        </a>
        <p>사기 전에 알아야 할 것부터 정리합니다. 쿠팡·알리에서 직접 확인한 값과 후기만으로 쓰는 리뷰 연구소.</p>
      </div>
      <div class="footer-col">
        <h4>Articles</h4>
        <ul>
          <li><a href="{R('articles.html')}">전체 기사</a></li>
          <li><a href="{R('articles.html')}?c=coupang">AI 스마트 가전</a></li>
          <li><a href="{R('articles.html')}?c=ali">AI 아이디어 기기</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>About</h4>
        <ul>
          <li><a href="{R('about.html')}">연구소 소개</a></li>
          <li><a href="{R('about.html')}#disclosure">제휴 고지</a></li>
          <li><a href="{R('feed.xml')}">RSS 구독</a></li>
        </ul>
      </div>
    </div>
    <div class="disclosure">
      <b>제휴 고지</b> · 픽얼리는 쿠팡 파트너스와 알리익스프레스 어필리에이트 활동의 일환으로, 링크를 통한 구매 시 일정액의 수수료를 제공받습니다. 수수료는 글의 결론에 영향을 주지 않으며, 구매 가격은 동일합니다.<br>
      <b>정보 고지</b> · 본 사이트의 가격·재고·사양은 각 글에 적힌 확인 시점의 값이며, 판매처 사정에 따라 달라질 수 있습니다. 중요한 결정 전에는 판매 페이지의 최종 조건을 확인하세요.<br>
      © {year} PickEarly · 픽얼리 얼리어답터 연구소
    </div>
  </div>
</footer>
<script src="{R('assets/app.js')}" defer></script>"""


def page_shell(title, desc, canonical, og_image, depth, body, current, extra_json=None, page_type="website", cls=""):
    return f"""<!doctype html>
<html lang="ko">
<head>
{head_tags(title, desc, canonical, og_image, depth, extra_json, page_type)}
</head>
<body class="{cls}">
{header_html(depth, current)}
<main>
{body}
</main>
{footer_html(depth)}
</body>
</html>
"""


# --------------------------------------------------------------------------
# 카드 / 배지
# --------------------------------------------------------------------------
def cat_badge(cat):
    c = CATS[cat]
    return f'<span class="badge {c["class"]}">{c["vendor"]} · {c["label"]}</span>'


def reading_time(a):
    md = open(os.path.join(CONTENT, a["file"]), encoding="utf-8").read()
    body, *_ = md_to_html(md, a.get("collapse_notes"))
    text = re.sub(r"<[^>]+>", "", body)
    minutes = max(1, math.ceil(len(text) / 480))
    return minutes


def date_dots(d):
    y, m, dd = d.split("-")
    return f"{y}.{m}.{dd}"


def post_card(a, depth):
    R = lambda p: rel(depth, p)  # noqa: E731
    c = CATS[a["cat"]]
    mins = reading_time(a)
    return f"""<a class="post-card" href="{R('articles/' + a['slug'] + '.html')}" data-post data-cat="{a['cat']}" data-search-text="{esc(a['title'] + ' ' + a['excerpt'] + ' ' + ' '.join(a['tags']) + ' ' + c['label'] + ' ' + c['vendor'])}">
  <div class="post-thumb"><img src="{R(a['thumb'])}" alt="{esc(a['thumb_alt'])}" loading="lazy"></div>
  <div class="post-body">
    {cat_badge(a['cat'])}
    <h3>{esc(a['title'])}</h3>
    <p>{esc(a['excerpt'])}</p>
    <div class="spacer"></div>
    <div class="meta-row">
      <span>{date_dots(a['date'])}</span><span class="sep"></span>
      <span>읽는 시간 {mins}분</span>
    </div>
  </div>
</a>"""


# --------------------------------------------------------------------------
# 페이지: 홈
# --------------------------------------------------------------------------
def build_home():
    feats = [a for a in ARTICLES if a.get("featured")] or [ARTICLES[0]]
    f = feats[0]
    mins = reading_time(f)
    rest = [a for a in ARTICLES if a is not f]

    counts = {"all": len(ARTICLES)}
    for k in CATS:
        counts[k] = sum(1 for a in ARTICLES if a["cat"] == k)

    chips = [f'<button class="chip" type="button" data-filter="all" aria-pressed="true">전체 <span class="count">{counts["all"]}</span></button>']
    for k, c in CATS.items():
        chips.append(
            f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{c["vendor"]} · {c["label"]} <span class="count">{counts[k]}</span></button>'
        )

    cards = "\n".join(post_card(a, 0) for a in ARTICLES)

    body = f"""
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-grid">
      <div>
        <p class="eyebrow">Issue 01 · {date_dots(f['date'])}</p>
        <h1>남보다 반 발<br>먼저 사는 사람의 <em>연구소</em></h1>
        <p class="lede">쿠팡과 알리에서 진짜 쓸 만한 것만 골라, 사기 전에 알아야 할 것부터 정리합니다. 스펙 나열이 아니라 <b>돈을 쓰기 전에 걸리는 지점</b>을 씁니다.</p>
        <div class="hero-meta">
          <span>발행 <b>{len(ARTICLES)}</b>편</span>
          <span>확인일 <b>{date_dots(dt.date.today().isoformat())}</b></span>
          <span>운영 <b>{esc(SITE['author'])}</b></span>
        </div>
      </div>
      <aside class="lab-panel">
        <h2>The Lab Rules</h2>
        <p class="lab-title">픽얼리가 글을 쓰는 방식</p>
        <ul class="lab-list">
          <li><span class="num">01</span><span><b>직접 확인한 값만.</b> 가격·재고·평점은 판매 페이지에서 확인한 시점을 함께 적습니다.</span></li>
          <li><span class="num">02</span><span><b>단점을 먼저.</b> 후기에서 반복되는 아쉬운 점이 없으면 그 글은 아직 덜 쓴 글입니다.</span></li>
          <li><span class="num">03</span><span><b>구매 전 확인 순서.</b> 설치·구독·인증처럼 나중에 발목 잡는 조건을 먼저 봅니다.</span></li>
          <li><span class="num">04</span><span><b>제휴는 숨기지 않습니다.</b> 수수료를 받는 글은 맨 위에 먼저 밝힙니다.</span></li>
        </ul>
      </aside>
    </div>
  </div>
</section>

<div class="wrap">
  <section class="section" id="featured">
    <div class="section-head">
      <h2><span class="dot"></span>이번 호 커버</h2>
      <p>{date_dots(f['date'])} 발행</p>
    </div>
    <a class="featured" href="articles/{f['slug']}.html">
      <div class="featured-body">
        {cat_badge(f['cat'])}
        <h3>{esc(f['title'])}</h3>
        <p class="excerpt">{esc(f['excerpt'])}</p>
        <div class="spacer"></div>
        <div class="meta-row" style="margin-bottom:16px">
          <span>{date_dots(f['date'])}</span><span class="sep"></span>
          <span>읽는 시간 {mins}분</span><span class="sep"></span>
          <span>핵심 3가지 정리</span>
        </div>
        <span class="more-link">기사 읽기 <span class="arrow">→</span></span>
      </div>
      <div class="featured-media">
        <img src="{f['thumb']}" alt="{esc(f['thumb_alt'])}" fetchpriority="high">
      </div>
    </a>
  </section>

  <section class="section" id="latest">
    <div class="section-head">
      <h2><span class="dot"></span>최신 리뷰 <span style="font-size:13px;font-weight:600;color:var(--ink-4);letter-spacing:0">(<span data-result-count>{len(ARTICLES)}</span>)</span></h2>
      <p>카테고리를 고르거나 검색해 보세요</p>
    </div>
    <div class="toolbar">
      <div class="chips" role="group" aria-label="카테고리 필터">
        {''.join(chips)}
      </div>
      <label class="search">
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.8"/><path d="m13.5 13.5 3.5 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        <span class="sr-only">기사 검색</span>
        <input type="search" placeholder="제품·키워드 검색  ( / )" data-search autocomplete="off">
      </label>
    </div>
    <div class="post-grid">
{cards}
    </div>
    <div class="empty-state" data-empty>조건에 맞는 기사가 아직 없습니다. 다른 키워드로 찾아보세요.</div>
  </section>
</div>

<section class="principles" id="lab">
  <div class="wrap principles-inner">
    <div class="principle">
      <span class="k">01 / SOURCE</span>
      <h3>확인 시점을 남깁니다</h3>
      <p>가격과 재고는 확인한 날짜를 붙여 적고, 바뀌면 글도 고칩니다.</p>
    </div>
    <div class="principle">
      <span class="k">02 / HONEST</span>
      <h3>아쉬운 점을 먼저 씁니다</h3>
      <p>후기에서 반복되는 단점과 설치·구독 조건을 결론보다 앞에 둡니다.</p>
    </div>
    <div class="principle">
      <span class="k">03 / CLEAR</span>
      <h3>제휴 사실을 밝힙니다</h3>
      <p>수수료를 받는 글은 본문 첫머리에 고지하고, 결론은 수수료와 무관하게 씁니다.</p>
    </div>
  </div>
</section>
"""

    ld = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "픽얼리 PickEarly",
            "alternateName": "픽얼리 얼리어답터 연구소",
            "url": SITE["url"] + "/",
            "description": SITE["desc"],
            "inLanguage": "ko",
            "publisher": {"@type": "Organization", "name": "픽얼리 PickEarly", "url": SITE["url"] + "/"},
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "픽얼리 최신 리뷰",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": n + 1,
                    "url": f"{SITE['url']}/articles/{a['slug']}.html",
                    "name": a["title"],
                }
                for n, a in enumerate(ARTICLES)
            ],
        },
    ]
    title = "픽얼리 PickEarly — 얼리어답터 연구소 | 쿠팡·알리 리뷰"
    return page_shell(
        title,
        SITE["desc"],
        SITE["url"] + "/",
        "assets/og/og-home.png",
        0,
        body,
        "index.html",
        ld,
        "website",
    )


# --------------------------------------------------------------------------
# 페이지: 전체 기사
# --------------------------------------------------------------------------
def build_articles_index():
    counts = {"all": len(ARTICLES)}
    for k in CATS:
        counts[k] = sum(1 for a in ARTICLES if a["cat"] == k)
    chips = [f'<button class="chip" type="button" data-filter="all" aria-pressed="true">전체 <span class="count">{counts["all"]}</span></button>']
    for k, c in CATS.items():
        chips.append(
            f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{c["vendor"]} · {c["label"]} <span class="count">{counts[k]}</span></button>'
        )
    cards = "\n".join(post_card(a, 0) for a in ARTICLES)
    body = f"""
<div class="wrap">
  <div class="page-head" style="border-bottom:0;padding-bottom:8px">
    <p class="eyebrow">Archive</p>
    <h1>전체 기사</h1>
    <p>지금까지 연구소가 확인한 제품과 조건을 모았습니다. 카테고리로 좁히거나 키워드로 찾아보세요.</p>
  </div>
  <div class="toolbar" style="margin-top:26px">
    <div class="chips" role="group" aria-label="카테고리 필터">{''.join(chips)}</div>
    <label class="search">
      <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.8"/><path d="m13.5 13.5 3.5 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      <span class="sr-only">기사 검색</span>
      <input type="search" placeholder="제품·키워드 검색  ( / )" data-search autocomplete="off">
    </label>
  </div>
  <section class="section" style="padding-top:8px">
    <div class="post-grid">
{cards}
    </div>
    <div class="empty-state" data-empty>조건에 맞는 기사가 아직 없습니다. 다른 키워드로 찾아보세요.</div>
  </section>
</div>
"""
    return page_shell(
        "전체 기사 — 픽얼리 PickEarly",
        "픽얼리 얼리어답터 연구소가 확인한 쿠팡·알리 제품 리뷰 전체 목록입니다.",
        SITE["url"] + "/articles.html",
        "assets/og/og-home.png",
        0,
        body,
        "articles.html",
    )


# --------------------------------------------------------------------------
# 페이지: 기사
# --------------------------------------------------------------------------
def build_article(a):
    md = open(os.path.join(CONTENT, a["file"]), encoding="utf-8").read()
    body_html, toc, md_tags, h1 = md_to_html(md, a.get("collapse_notes"))
    body_html = re.sub(r'^(\s*<hr>\s*)+', '', body_html).strip()
    body_html = re.sub(r'(<p class="dateline">.*?</p>)\s*(<hr>\s*)+', r'\1', body_html, flags=re.S)
    body_html = decorate(body_html)
    mins = reading_time(a)
    tags = a["tags"]

    toc_html = ""
    if len(toc) >= 2:
        items = "\n".join(
            f'<li><a href="#{sid}" data-toc-link>{esc(label)}</a></li>' for sid, label in toc
        )
        toc_html = f"""<aside class="toc" aria-label="목차">
  <div class="toc-title">In this article</div>
  <ol>{items}</ol>
</aside>"""

    takeaways = "\n".join(f"<li>{t}</li>" for t in a["takeaways"])
    others = [x for x in ARTICLES if x["slug"] != a["slug"]]
    related = ""
    if others:
        o = others[0]
        related = f"""<section class="related">
  <h2>이어서 읽기</h2>
  <a class="related-card" href="{o['slug']}.html">
    <span class="rc-thumb"><img src="../{o['thumb']}" alt="{esc(o['thumb_alt'])}" loading="lazy"></span>
    <span class="rc-body">
      {cat_badge(o['cat'])}
      <h3>{esc(o['title'])}</h3>
    </span>
  </a>
</section>"""

    canon = f"{SITE['url']}/articles/{a['slug']}.html"
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": a["title"],
            "description": a["excerpt"],
            "inLanguage": "ko",
            "datePublished": a["date"],
            "dateModified": a.get("updated", a["date"]),
            "author": {"@type": "Organization", "name": SITE["author"]},
            "publisher": {"@type": "Organization", "name": "픽얼리 PickEarly"},
            "mainEntityOfPage": {"@type": "WebPage", "@id": canon},
            "image": f"{SITE['url']}/{a['og']}",
            "articleSection": CATS[a["cat"]]["label"],
            "keywords": ", ".join(tags),
            "isAccessibleForFree": True,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE["url"] + "/"},
                {"@type": "ListItem", "position": 2, "name": "전체 기사", "item": SITE["url"] + "/articles.html"},
                {"@type": "ListItem", "position": 3, "name": a["title"], "item": canon},
            ],
        },
    ]

    body = f"""
<div class="progress" data-progress></div>
<article>
  <header class="article-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="위치">
        <a href="../index.html">홈</a><span class="sl">/</span>
        <a href="../articles.html">{esc(CATS[a['cat']]['label'])}</a><span class="sl">/</span>
        <span>{date_dots(a['date'])}</span>
      </nav>
      {cat_badge(a['cat'])}
      <h1 class="article-title">{esc(a['title'])}</h1>
      <p class="article-lede">{esc(a['excerpt'])}</p>
      <div class="article-meta">
        <span class="author"><span class="author-chip">PE</span>{esc(SITE['author'])}</span>
        <span class="sep">·</span>
        <span>{date_dots(a['date'])} 발행</span>
        <span class="sep">·</span>
        <span>읽는 시간 {mins}분</span>
      </div>
      <div class="notice">
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="8.2" stroke="currentColor" stroke-width="1.5"/><path d="M10 9v4.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="10" cy="6.4" r="1" fill="currentColor"/></svg>
        <span><b>제휴 고지</b> · {esc(a['disclosure'])}</span>
      </div>
    </div>
  </header>

  <div class="wrap article-layout">
    <div>
      <aside class="takeaways" style="border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin:0 0 34px;background:var(--paper-2)">
        <p style="margin:0 0 10px;font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-4);font-weight:700">3줄 요약</p>
        <ol style="margin:0;padding-left:1.15em;display:grid;gap:8px;font-size:15px;line-height:1.7;color:var(--ink-2)">{takeaways}</ol>
      </aside>
      <div class="prose">
{body_html}
      </div>
      <footer class="article-end">
        <div class="tags">
          {''.join(f'<span class="tag">#{esc(t)}</span>' for t in tags)}
        </div>
        <div class="share-row">
          <span class="label">공유</span>
          <button class="btn-ghost" type="button" data-copy-link="{canon}">
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M8 12.2 12.2 8M8.7 5.3l1.5-1.5a3.2 3.2 0 1 1 4.5 4.5l-1.5 1.5M11.3 14.7l-1.5 1.5a3.2 3.2 0 1 1-4.5-4.5l1.5-1.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
            <span data-copy-label>링크 복사</span>
          </button>
          <a class="btn-ghost" href="mailto:?subject={quote(a['title'])}&body={quote(canon)}">메일로 보내기</a>
          <a class="btn-ghost" href="../articles.html">전체 기사</a>
        </div>
      </footer>
      {related}
    </div>
    {toc_html}
  </div>
</article>
"""
    return page_shell(
        a["title"] + " — 픽얼리 PickEarly",
        a["excerpt"],
        canon,
        a["og"],
        1,
        body,
        "articles.html",
        ld,
        "article",
        cls="page-article",
    )


# --------------------------------------------------------------------------
# 페이지: 소개
# --------------------------------------------------------------------------
def build_about():
    body = f"""
<div class="wrap">
  <div class="page-head">
    <p class="eyebrow">About the Lab</p>
    <h1>사기 전에 알아야 할 것부터<br>정리하는 연구소</h1>
    <p>픽얼리(PickEarly)는 새로 나온 가전과 아이디어 상품을 직접 확인하고, 사기 전에 걸리는 지점을 먼저 정리하는 개인 리뷰 사이트입니다.</p>
  </div>
  <div class="about-body">
    <h2>왜 '얼리어답터 연구소'인가</h2>
    <p>새 제품을 일찍 사는 사람의 진짜 비용은 제품 값이 아니라 <b>확인하지 않은 조건</b>에서 나옵니다. 직배수 로봇청소기의 배관 조건, AI 녹음기의 한국어 전사 지원 여부와 구독료처럼, 스펙 표에는 잘 보이지 않지만 설치·결제 후에 발목을 잡는 항목들입니다.</p>
    <p>그래서 픽얼리는 이런 순서로 글을 씁니다. <b>① 판매 페이지에서 직접 확인한 값 → ② 사람들이 잘 모르는 구조와 조건 → ③ 단점과 체크리스트 → ④ 그래도 살 만한 경우.</b> 화려한 표현보다 다시 확인할 수 있는 근거를 남기는 쪽을 택합니다.</p>

    <div class="about-facts">
      <div class="fact"><div class="k">Categories</div><div class="v">AI 스마트 가전 · AI 아이디어 기기</div></div>
      <div class="fact"><div class="k">Sources</div><div class="v">판매 페이지 · 제조사 발표 · 실구매 후기</div></div>
      <div class="fact"><div class="k">Update</div><div class="v">가격·재고 변동 시 본문 갱신</div></div>
      <div class="fact"><div class="k">Contact</div><div class="v">사이트 운영자 (픽얼리 편집부)</div></div>
    </div>

    <h2>이렇게 검증합니다</h2>
    <ul>
      <li><b>가격·평점·재고</b>는 확인한 날짜를 글에 적습니다. 판매처·쿠폰에 따라 달라지므로 '오늘의 실구매가'로 비교합니다.</li>
      <li><b>제조사 주장</b>은 발표 자료와 사양 표기를 인용하고, 실사용 후기와 다를 때는 그 차이를 함께 씁니다.</li>
      <li><b>후기</b>는 실구매 인증 여부와 표본 수를 확인합니다. 유사 상품 후기가 섞인 경우도 밝힙니다.</li>
      <li><b>설치·인증·구독</b>처럼 나중에 비용이 되는 조건은 결론 앞에서 다룹니다.</li>
    </ul>

    <h2 id="disclosure">제휴 고지</h2>
    <p>픽얼리는 <b>쿠팡 파트너스</b>와 <b>알리익스프레스 어필리에이트</b> 활동에 참여합니다. 글 안의 구매 링크를 통해 구매가 이루어지면 일정액의 수수료를 제공받습니다. <b>구매 가격은 링크를 쓰지 않았을 때와 동일합니다.</b></p>
    <p>수수료는 어떤 제품을 다룰지, 어떤 결론을 쓸지에 영향을 주지 않습니다. 제휴 링크가 포함된 글은 본문 첫머리에 고지하며, 단점과 '사지 말아야 할 경우'도 같은 비중으로 씁니다.</p>

    <h2>정보의 한계</h2>
    <p>본 사이트의 가격·할인율·배송 일정·재고는 각 글에 적힌 확인 시점의 값입니다. 제품 사양은 제조사 발표와 판매 페이지 표기를 인용한 것이며, 실제 사용 환경에 따라 차이가 있을 수 있습니다. 설치 가능 여부, 통관·인증, 법률에 관한 내용은 일반적인 안내이며 개별 상황의 확정 판단이 아닙니다. 중요한 결정 전에는 판매처와 제조사에 직접 확인하세요.</p>
  </div>
</div>
"""
    return page_shell(
        "연구소 소개 — 픽얼리 PickEarly",
        "픽얼리 얼리어답터 연구소가 제품을 확인하고 글을 쓰는 방식, 제휴 고지와 정보의 한계를 안내합니다.",
        SITE["url"] + "/about.html",
        "assets/og/og-home.png",
        0,
        body,
        "about.html",
    )


def build_404():
    body = """
<div class="wrap" style="padding:90px 0 120px;text-align:center">
  <p class="eyebrow" style="justify-content:center">404</p>
  <h1 style="font-size:clamp(30px,5vw,48px);letter-spacing:-.045em;margin:16px 0 12px">찾으시는 페이지가 없습니다</h1>
  <p style="color:var(--ink-2);margin:0 auto 30px;max-width:44ch">주소가 바뀌었거나, 아직 쓰지 않은 글일 수 있습니다. 전체 기사에서 다시 찾아보세요.</p>
  <a class="cta" href="articles.html" style="display:inline-flex">전체 기사 보기 <span class="cta-arrow">→</span></a>
</div>
"""
    return page_shell(
        "페이지를 찾을 수 없습니다 — 픽얼리 PickEarly",
        "요청하신 페이지가 없습니다.",
        SITE["url"] + "/404.html",
        "assets/og/og-home.png",
        0,
        body,
        "",
    )


# --------------------------------------------------------------------------
# sitemap / robots / rss
# --------------------------------------------------------------------------
def build_feeds():
    today = dt.date.today().isoformat()
    urls = [(SITE["url"] + "/", today, "1.0"), (SITE["url"] + "/articles.html", today, "0.8"), (SITE["url"] + "/about.html", today, "0.5")]
    for a in ARTICLES:
        urls.append((f"{SITE['url']}/articles/{a['slug']}.html", a.get("updated", a["date"]), "0.9"))

    entries = "\n".join(
        f"""  <url>
    <loc>{u}</loc>
    <lastmod>{m}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{p}</priority>
  </url>"""
        for u, m, p in urls
    )
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE['url']}/sitemap.xml
"""
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(robots)

    items = []
    for a in sorted(ARTICLES, key=lambda x: x["date"], reverse=True):
        pub = dt.datetime.fromisoformat(a["date"] + "T09:00:00+09:00").strftime("%a, %d %b %Y %H:%M:%S +0900")
        link = f"{SITE['url']}/articles/{a['slug']}.html"
        items.append(
            f"""    <item>
      <title>{html.escape(a['title'])}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub}</pubDate>
      <category>{html.escape(CATS[a['cat']]['label'])}</category>
      <description>{html.escape(a['excerpt'])}</description>
    </item>"""
        )
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>픽얼리 PickEarly — 얼리어답터 연구소</title>
    <link>{SITE['url']}/</link>
    <description>{html.escape(SITE['desc'])}</description>
    <language>ko</language>
    <atom:link href="{SITE['url']}/feed.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime('%a, %d %b %Y %H:%M:%S +0900')}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8").write(rss)


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="8" fill="#15171b"/>
  <path d="M6 23h20" stroke="#e2502b" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M16 23.4V16" stroke="#e2502b" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M10 18.6a6 6 0 0 1 12 0" stroke="#e2502b" stroke-width="2.6" stroke-linecap="round"/>
  <circle cx="16" cy="11.4" r="2" fill="#e2502b"/>
</svg>
"""


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", help="예: https://pickearly.com")
    args = ap.parse_args()
    if args.domain:
        SITE["url"] = args.domain.rstrip("/")

    os.makedirs(OUT, exist_ok=True)

    # assets
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy(os.path.join(THEME, "style.css"), os.path.join(OUT, "assets", "style.css"))
    shutil.copy(os.path.join(THEME, "app.js"), os.path.join(OUT, "assets", "app.js"))
    open(os.path.join(OUT, "assets", "favicon.svg"), "w", encoding="utf-8").write(FAVICON)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

    pages = {
        "index.html": build_home(),
        "articles.html": build_articles_index(),
        "about.html": build_about(),
        "404.html": build_404(),
    }
    for name, content in pages.items():
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(content)

    for a in ARTICLES:
        open(os.path.join(OUT, "articles", a["slug"] + ".html"), "w", encoding="utf-8").write(build_article(a))

    build_feeds()

    # 검증용 요약
    print("built:")
    for name in list(pages) + [f"articles/{a['slug']}.html" for a in ARTICLES] + ["sitemap.xml", "robots.txt", "feed.xml"]:
        p = os.path.join(OUT, name)
        print(f"  {name:<46} {os.path.getsize(p):>7,} bytes")
    print(f"SITE_URL = {SITE['url']}")


if __name__ == "__main__":
    main()

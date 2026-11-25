#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""content/*.md 상단의 YAML 프런트매터를 읽고 쓰는 아주 작은 모듈.

Cloudflare Pages 빌드 환경에 PyYAML 이 없어도 돌아가도록 외부 의존성 없이
필요한 만큼만 지원한다.

지원 범위
  key: 값                    (한 줄 스칼라 — 따옴표/숫자/true/false/null)
  key: "여러 줄\\n문자열"     (JSON 과 같은 이스케이프)
  key: |                     (블록 스칼라: |, |-, >, >-)
  key:                       (아래에 블록 목록)
    - 값
    - key: 값                (목록 안의 단순 매핑)
      key: 값
  key: [a, b, c]             (한 줄 목록)

쓰기(dumps)는 위 형식만 만든다. build.py 와 admin 이 같은 형식을 쓰므로
관리자 화면에서 저장한 파일을 build.py 가 그대로 읽는다.
"""

import json
import re

BLOCK_SCALAR_RE = re.compile(r"^([|>])([+-]?)$")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]+(.*)|[ \t]*)$")
LIST_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*)$")


# --------------------------------------------------------------------------
# 읽기
# --------------------------------------------------------------------------
def _scalar(raw: str):
    """한 줄 스칼라 값을 해석한다."""
    v = raw.strip()
    if v == "":
        return None
    if v[0] == '"':
        # JSON 문자열과 같은 규칙. 감싸는 따옴표가 없으면 그대로 시도한다.
        try:
            return json.loads(v)
        except ValueError:
            end = v.rfind('"')
            if end > 0:
                try:
                    return json.loads(v[: end + 1])
                except ValueError:
                    pass
            return v.strip('"')
    if v[0] == "'":
        end = v.rfind("'")
        inner = v[1:end] if end > 0 else v[1:]
        return inner.replace("''", "'")
    if v.startswith("["):
        end = v.rfind("]")
        inner = v[1:end] if end > 0 else v[1:]
        return [_scalar(p) for p in _split_inline(inner) if p.strip() != ""]
    low = v.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", v):
        try:
            return int(v)
        except ValueError:
            return v
    if re.fullmatch(r"-?\d+\.\d+", v):
        try:
            return float(v)
        except ValueError:
            return v
    # 주석은 값이 아닌 부분에서만 자른다 (예: 값 # 설명)
    m = re.search(r"\s+#", v)
    if m and not v.startswith("#"):
        return v[: m.start()].rstrip()
    return v


def _split_inline(inner: str):
    """[a, "b, c", d] 를 따옴표를 지키며 나눈다."""
    out, buf, quote = [], [], None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == ",":
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _read_block_scalar(lines, i, parent_indent, style):
    """key: | 다음 줄부터 블록 스칼라 본문을 모은다."""
    body = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            body.append("")
            i += 1
            continue
        if _indent(line) <= parent_indent:
            break
        body.append(line)
        i += 1
    # 공통 들여쓰기 제거
    indents = [_indent(l) for l in body if l.strip()]
    cut = min(indents) if indents else 0
    body = [l[cut:] if l.strip() else "" for l in body]
    while body and body[-1] == "":
        body.pop()
    if style.startswith(">"):
        text = " ".join(p.strip() for p in body if p.strip())
    else:
        text = "\n".join(body)
    if style.endswith("-"):
        return text, i
    return text + "\n", i


def _read_list(lines, i, key_indent):
    """- 로 시작하는 블록 목록을 읽는다."""
    items = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "" or line.lstrip().startswith("#"):
            i += 1
            continue
        ind = _indent(line)
        if ind < key_indent or not line.lstrip().startswith("- "):
            if ind > key_indent and items and isinstance(items[-1], dict):
                # 목록 안 매핑의 이어지는 키
                m = LIST_KEY_RE.match(line.strip())
                if m:
                    items[-1][m.group(1)] = _scalar(m.group(2))
                    i += 1
                    continue
            if ind > key_indent and line.strip() == "-":
                i += 1
                continue
            break
        content = line.lstrip()[2:]
        if content.strip() == "":
            items.append("")
            i += 1
            continue
        m = LIST_KEY_RE.match(content)
        if m and not content.lstrip().startswith(('"', "'")):
            item = {m.group(1): _scalar(m.group(2))}
            i += 1
            # 같은 항목의 추가 키
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    i += 1
                    continue
                if _indent(nxt) <= ind + 1:
                    break
                nm = LIST_KEY_RE.match(nxt.strip())
                if not nm:
                    break
                item[nm.group(1)] = _scalar(nm.group(2))
                i += 1
            items.append(item)
            continue
        items.append(_scalar(content))
        i += 1
    return items, i


def parse(text: str) -> dict:
    """프런트매터 문자열(--- 제외)을 dict 로."""
    lines = text.replace("\r\n", "\n").split("\n")
    data = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "" or line.lstrip().startswith("#"):
            i += 1
            continue
        if _indent(line) > 0:
            # 부모 없는 들여쓰기는 무시
            i += 1
            continue
        m = KEY_RE.match(line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), (m.group(2) or "")
        rest = rest.strip()
        if rest == "":
            # 목록 또는 블록 스칼라 또는 빈 값
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            nxt = lines[j] if j < len(lines) else ""
            if nxt.lstrip().startswith("- ") or nxt.strip() == "-":
                data[key], i = _read_list(lines, i + 1, _indent(nxt))
            else:
                data[key] = None
                i += 1
            continue
        bs = BLOCK_SCALAR_RE.match(rest)
        if bs:
            data[key], i = _read_block_scalar(lines, i + 1, 0, rest)
            continue
        data[key] = _scalar(rest)
        i += 1
    return data


def split(text: str):
    """파일 전체를 (frontmatter dict, 본문) 으로 나눈다."""
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---"):
        return {}, normalized
    first_break = normalized.find("\n")
    if first_break == -1:
        return {}, normalized
    head = normalized[first_break + 1 :]
    end = re.search(r"^---[ \t]*$", head, re.M)
    if not end:
        return {}, normalized
    meta = parse(head[: end.start()])
    body = head[end.end() :]
    if body.startswith("\n"):
        body = body[1:]
    return meta, body


# --------------------------------------------------------------------------
# 쓰기
# --------------------------------------------------------------------------
# 값이 이 모양이면 따옴표 없이 써도 안전하다.
PLAIN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/:+-]*$")


def _dump_scalar(v) -> str:
    if v is True:
        return "true"
    if v is False:
        return "false"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    if PLAIN_RE.fullmatch(s) and s.lower() not in (
        "true", "false", "null", "yes", "no", "on", "off",
    ):
        return s
    return json.dumps(s, ensure_ascii=False)


def dumps(data: dict, order=None) -> str:
    """dict 를 프런트매터 문자열(--- 포함)로."""
    keys = list(order or [])
    for k in data:
        if k not in keys:
            keys.append(k)
    out = ["---"]
    for key in keys:
        if key not in data:
            continue
        v = data[key]
        if v is None:
            out.append(f"{key}: null")
        elif isinstance(v, bool):
            out.append(f"{key}: {'true' if v else 'false'}")
        elif isinstance(v, list):
            if not v:
                out.append(f"{key}: []")
                continue
            out.append(f"{key}:")
            for item in v:
                if isinstance(item, dict):
                    first = True
                    for k2, v2 in item.items():
                        prefix = "  - " if first else "    "
                        out.append(prefix + f"{k2}: {_dump_scalar(v2)}")
                        first = False
                else:
                    s = _dump_scalar(item)
                    out.append("  - " + s)
        elif isinstance(v, str) and "\n" in v:
            body = v.rstrip("\n")
            out.append(f"{key}: |-")
            for line in body.split("\n"):
                out.append("  " + line if line.strip() else "")
        else:
            out.append(f"{key}: {_dump_scalar(v)}")
    out.append("---")
    return "\n".join(out) + "\n"


def join(data: dict, body: str, order=None) -> str:
    """프런트매터 + 본문."""
    fm = dumps(data, order)
    return fm + "\n" + body.lstrip("\n")

/**
 * POST /api/upload — 대표 이미지 업로드
 *   { filename: "bespoke-ai-steam-abc123.png", data: "<base64>" }
 *   → theme/assets/images/<이름> 으로 커밋하고 { path: "assets/images/<이름>" } 를 돌려준다.
 *
 * build.py 가 theme/assets/images/ 를 docs/assets/images/ 로 복사하므로,
 * 커밋만 하면 다음 빌드에서 사이트에 나타난다.
 */

import { json, requireAuth } from './_lib/session.js';

const GH = 'https://api.github.com';
const DIR = 'theme/assets/images';
const MAX_BYTES = 6 * 1024 * 1024;
const EXT_OK = new Set(['png', 'jpg', 'jpeg', 'webp', 'svg', 'avif', 'gif']);
const NAME_RE = /^[a-z0-9][a-z0-9._-]*$/;

function cfg(env) {
  return {
    repo: env.GITHUB_REPO || 'happy1ch/pickearly',
    branch: env.GITHUB_BRANCH || 'main',
    token: env.GITHUB_TOKEN || '',
  };
}

async function gh(c, path, init = {}) {
  const res = await fetch(GH + path, {
    ...init,
    headers: {
      Authorization: `Bearer ${c.token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'pickearly-admin',
      ...(init.headers || {}),
    },
  });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!res.ok) {
    const detail = (data && data.message) || `GitHub ${res.status}`;
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  return data;
}

export async function onRequestPost(context) {
  const denied = await requireAuth(context);
  if (denied) return denied;
  const c = cfg(context.env);
  if (!c.token) {
    return json({ ok: false, error: 'GITHUB_TOKEN_NOT_SET', message: 'GITHUB_TOKEN 환경변수가 없습니다.' }, 500);
  }

  let body = {};
  try {
    body = await context.request.json();
  } catch {
    return json({ ok: false, error: 'BAD_JSON', message: '요청 본문을 읽지 못했습니다.' }, 400);
  }

  const rawName = String(body.filename || '').toLowerCase().replace(/[^a-z0-9._-]/g, '-');
  const ext = (rawName.split('.').pop() || '').replace('jpeg', 'jpg');
  const base = rawName.replace(/\.[a-z0-9]+$/, '').replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '') || 'image';
  const name = `${base}.${ext}`;
  const data = typeof body.data === 'string' ? body.data : '';

  if (!EXT_OK.has(ext)) {
    return json({ ok: false, error: 'BAD_TYPE', message: 'PNG·JPG·WebP·SVG·AVIF·GIF 만 올릴 수 있습니다.' }, 400);
  }
  if (!NAME_RE.test(name)) {
    return json({ ok: false, error: 'BAD_NAME', message: '파일 이름에 쓸 수 없는 글자가 있습니다.' }, 400);
  }
  if (!data) return json({ ok: false, error: 'EMPTY', message: '이미지 데이터가 없습니다.' }, 400);

  const bytes = Math.floor((data.length * 3) / 4);
  if (bytes > MAX_BYTES) {
    return json({ ok: false, error: 'TOO_LARGE', message: '이미지는 6MB 까지 올릴 수 있습니다.' }, 413);
  }

  const path = `${DIR}/${name}`;
  try {
    // 이미 같은 이름이 있으면 덮어쓰기 위해 sha 를 먼저 확인한다.
    let sha;
    try {
      const existing = await gh(c, `/repos/${c.repo}/contents/${path}?ref=${encodeURIComponent(c.branch)}`);
      sha = existing?.sha;
    } catch (e) {
      if (e.status !== 404) throw e;
    }
    const saved = await gh(c, `/repos/${c.repo}/contents/${path}`, {
      method: 'PUT',
      body: JSON.stringify({
        message: `이미지 추가: ${name}`,
        content: data.replace(/\s/g, ''),
        branch: c.branch,
        ...(sha ? { sha } : {}),
      }),
    });
    return json({
      ok: true,
      path: `assets/images/${name}`,
      repo_path: path,
      sha: saved?.content?.sha || '',
      commit_url: saved?.commit?.html_url || '',
    });
  } catch (e) {
    return json({ ok: false, error: 'UPLOAD_FAILED', message: e.message || '업로드하지 못했습니다.' }, e.status === 404 ? 502 : 502);
  }
}

export async function onRequest() {
  return json({ ok: false, error: 'METHOD_NOT_ALLOWED', message: 'POST 만 지원합니다.' }, 405);
}

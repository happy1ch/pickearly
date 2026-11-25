/**
 * /api/posts — 글 목록 · 저장 · 삭제
 *   GET    /api/posts                → content/*.md 전부 (파일별 원문 + sha)
 *   PUT    /api/posts                → { file, raw, sha? } 생성/수정 커밋
 *   DELETE /api/posts                → { file, sha } 삭제 커밋
 *
 * 환경변수
 *   GITHUB_TOKEN  (필수) happy1ch/pickearly 의 contents:write 권한 PAT
 *   GITHUB_REPO   (선택) 기본값 happy1ch/pickearly
 *   GITHUB_BRANCH (선택) 기본값 main
 *   DEPLOY_HOOK_URL (선택) Cloudflare Pages Deploy Hook — 있으면 커밋 후 즉시 재빌드
 */

import { json, requireAuth } from './_lib/session.js';

const GH = 'https://api.github.com';
const FILE_RE = /^content\/[a-z0-9][a-z0-9-]*\.md$/;
const MAX_BYTES = 400 * 1024; // 원고 한 편 상한

function cfg(env) {
  return {
    repo: env.GITHUB_REPO || 'happy1ch/pickearly',
    branch: env.GITHUB_BRANCH || 'main',
    token: env.GITHUB_TOKEN || '',
  };
}

function ghHeaders(c) {
  return {
    Authorization: `Bearer ${c.token}`,
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'pickearly-admin',
  };
}

class GhError extends Error {
  constructor(message, status, code) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function gh(c, path, init = {}) {
  const res = await fetch(GH + path, {
    ...init,
    headers: { ...ghHeaders(c), ...(init.headers || {}) },
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
    if (res.status === 401 || res.status === 403) {
      throw new GhError(`GitHub 토큰이 거부되었습니다 (${detail}). GITHUB_TOKEN 을 확인해 주세요.`, 502, 'GITHUB_AUTH');
    }
    if (res.status === 404) {
      throw new GhError(`저장소나 파일을 찾지 못했습니다 (${detail}). GITHUB_REPO·GITHUB_BRANCH 를 확인해 주세요.`, 502, 'GITHUB_NOT_FOUND');
    }
    if (res.status === 409 || res.status === 422) {
      throw new GhError('다른 곳에서 먼저 수정되었습니다. 새로고침 후 다시 시도해 주세요.', 409, 'CONFLICT');
    }
    throw new GhError(`GitHub 오류: ${detail}`, 502, 'GITHUB_ERROR');
  }
  return data;
}

function b64ToUtf8(b64) {
  const bin = atob(String(b64).replace(/\s/g, ''));
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder('utf-8').decode(bytes);
}

function utf8ToB64(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    bin += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(bin);
}

function branchQuery(c) {
  return `?ref=${encodeURIComponent(c.branch)}`;
}

async function triggerDeploy(env) {
  if (!env.DEPLOY_HOOK_URL) return 'auto';
  try {
    await fetch(env.DEPLOY_HOOK_URL, { method: 'POST' });
    return 'hook';
  } catch {
    return 'auto';
  }
}

function slugOf(file) {
  return file.replace(/^content\//, '').replace(/\.md$/, '');
}

/* ------------------------------------------------------------------ GET */
async function listPosts(c) {
  let dir;
  try {
    dir = await gh(c, `/repos/${c.repo}/contents/content${branchQuery(c)}`);
  } catch (e) {
    if (e.code === 'GITHUB_NOT_FOUND') return [];
    throw e;
  }
  if (!Array.isArray(dir)) return [];
  const files = dir.filter((f) => f.type === 'file' && f.name.endsWith('.md'));
  const posts = await Promise.all(
    files.map(async (f) => {
      const one = await gh(c, `/repos/${c.repo}/contents/${encodeURIComponent(f.path).replace(/%2F/g, '/')}${branchQuery(c)}`);
      return {
        file: f.path,
        sha: one.sha,
        size: one.size,
        raw: one.content ? b64ToUtf8(one.content) : '',
      };
    }),
  );
  posts.sort((a, b) => a.file.localeCompare(b.file));
  return posts;
}

export async function onRequestGet(context) {
  const denied = await requireAuth(context);
  if (denied) return denied;
  const c = cfg(context.env);
  if (!c.token) {
    return json({ ok: false, error: 'GITHUB_TOKEN_NOT_SET', message: 'GITHUB_TOKEN 환경변수가 없습니다.' }, 500);
  }
  try {
    const posts = await listPosts(c);
    return json({ ok: true, repo: c.repo, branch: c.branch, count: posts.length, posts });
  } catch (e) {
    return json({ ok: false, error: e.code || 'LIST_FAILED', message: e.message }, e.status || 502);
  }
}

/* ------------------------------------------------------------------ PUT */
export async function onRequestPut(context) {
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

  const file = String(body.file || '');
  const raw = typeof body.raw === 'string' ? body.raw : '';
  const sha = typeof body.sha === 'string' && body.sha ? body.sha : undefined;

  if (!FILE_RE.test(file)) {
    return json({ ok: false, error: 'BAD_PATH', message: '파일 경로는 content/<영소문자-하이픈>.md 형식이어야 합니다.' }, 400);
  }
  if (!raw.trim()) return json({ ok: false, error: 'EMPTY', message: '내용이 비어 있습니다.' }, 400);
  if (new TextEncoder().encode(raw).length > MAX_BYTES) {
    return json({ ok: false, error: 'TOO_LARGE', message: '글 한 편은 400KB 까지 저장할 수 있습니다.' }, 413);
  }
  if (!raw.startsWith('---')) {
    return json({ ok: false, error: 'NO_FRONTMATTER', message: '파일 맨 위에 프런트매터(---)가 필요합니다.' }, 400);
  }

  const message = `${sha ? '글 수정' : '새 글'}: ${slugOf(file)}`;
  try {
    const data = await gh(c, `/repos/${c.repo}/contents/${file}`, {
      method: 'PUT',
      body: JSON.stringify({
        message,
        content: utf8ToB64(raw),
        branch: c.branch,
        ...(sha ? { sha } : {}),
      }),
    });
    const deploy = await triggerDeploy(context.env);
    return json({
      ok: true,
      file,
      sha: data?.content?.sha || '',
      commit: data?.commit?.sha || '',
      commit_url: data?.commit?.html_url || '',
      deploy,
      note: 'Cloudflare Pages 가 자동으로 다시 만듭니다 (약 30초).',
    });
  } catch (e) {
    return json({ ok: false, error: e.code || 'SAVE_FAILED', message: e.message }, e.status || 502);
  }
}

/* --------------------------------------------------------------- DELETE */
export async function onRequestDelete(context) {
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
  const file = String(body.file || '');
  let sha = typeof body.sha === 'string' && body.sha ? body.sha : '';

  if (!FILE_RE.test(file)) {
    return json({ ok: false, error: 'BAD_PATH', message: '지울 수 없는 경로입니다.' }, 400);
  }
  try {
    if (!sha) {
      const one = await gh(c, `/repos/${c.repo}/contents/${file}${branchQuery(c)}`);
      sha = one.sha;
    }
    const data = await gh(c, `/repos/${c.repo}/contents/${file}`, {
      method: 'DELETE',
      body: JSON.stringify({ message: `글 삭제: ${slugOf(file)}`, sha, branch: c.branch }),
    });
    const deploy = await triggerDeploy(context.env);
    return json({
      ok: true,
      file,
      commit: data?.commit?.sha || '',
      deploy,
      note: '삭제도 약 30초 뒤 사이트에 반영됩니다.',
    });
  } catch (e) {
    return json({ ok: false, error: e.code || 'DELETE_FAILED', message: e.message }, e.status || 502);
  }
}

export async function onRequest(context) {
  const method = context.request.method;
  if (method === 'OPTIONS') return new Response(null, { status: 204 });
  return json({ ok: false, error: 'METHOD_NOT_ALLOWED', message: `${method} 는 지원하지 않습니다.` }, 405);
}

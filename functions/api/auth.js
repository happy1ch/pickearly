/**
 * POST /api/auth — 관리자 비밀번호 확인 → 세션 토큰 발급
 *
 * 환경변수
 *   ADMIN_PASSWORD  (필수) 로그인 비밀번호
 *   SESSION_SECRET  (선택) 토큰 서명 키. 없으면 ADMIN_PASSWORD 를 쓴다.
 */

import { issueToken, json, passwordMatches } from './_lib/session.js';

// 같은 IP 의 연속 실패를 잠시 묶어 둔다 (인스턴스 안에서만 유효한 완충 장치).
const attempts = new Map();
const WINDOW_MS = 10 * 60 * 1000;
const MAX_TRIES = 8;

function throttled(ip) {
  const now = Date.now();
  const rec = attempts.get(ip);
  if (!rec) return false;
  if (now - rec.first > WINDOW_MS) {
    attempts.delete(ip);
    return false;
  }
  return rec.count >= MAX_TRIES;
}

function noteFailure(ip) {
  const now = Date.now();
  const rec = attempts.get(ip);
  if (!rec || now - rec.first > WINDOW_MS) attempts.set(ip, { count: 1, first: now });
  else rec.count += 1;
}

export async function onRequestPost({ request, env }) {
  const expected = env.ADMIN_PASSWORD;
  if (!expected) {
    return json({
      ok: false,
      error: 'ADMIN_PASSWORD_NOT_SET',
      message: '서버에 ADMIN_PASSWORD 환경변수가 없습니다. Cloudflare Pages → Settings → Variables 에 추가해 주세요.',
    }, 500);
  }

  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  if (throttled(ip)) {
    return json({
      ok: false,
      error: 'TOO_MANY_ATTEMPTS',
      message: '비밀번호를 여러 번 틀렸습니다. 10분 뒤에 다시 시도해 주세요.',
    }, 429);
  }

  let body = {};
  try {
    body = await request.json();
  } catch {
    body = {};
  }

  const password = String(body.password ?? '');
  if (!password) {
    return json({ ok: false, error: 'NO_PASSWORD', message: '비밀번호를 입력해 주세요.' }, 400);
  }

  if (!(await passwordMatches(password, expected))) {
    noteFailure(ip);
    // 무차별 대입을 늦춘다 (Cloudflare CPU 제한 안에서 짧게).
    await new Promise((r) => setTimeout(r, 300));
    return json({ ok: false, error: 'BAD_PASSWORD', message: '비밀번호가 맞지 않습니다.' }, 401);
  }

  attempts.delete(ip);
  const days = Math.min(Math.max(Number(body.days) || 30, 1), 90);
  const { token, exp } = await issueToken(env, days * 86400);
  return json({ ok: true, token, exp, days });
}

export async function onRequest() {
  return json({ ok: false, error: 'METHOD_NOT_ALLOWED', message: 'POST 로만 로그인할 수 있습니다.' }, 405);
}

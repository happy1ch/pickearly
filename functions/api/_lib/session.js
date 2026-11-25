/**
 * 픽얼리 관리자 — 세션 토큰 (HMAC-SHA256, 서버 저장소 없음)
 *
 * Cloudflare Pages Functions 는 요청마다 실행되므로 세션을 메모리에 둘 수 없다.
 * 대신 ADMIN_PASSWORD(또는 SESSION_SECRET)로 서명한 토큰을 발급하고 검증한다.
 *   토큰 = "v1.<만료시각 base36>.<HMAC 서명 base64url>"
 */

const enc = new TextEncoder();

export function getSecret(env) {
  return env.SESSION_SECRET || env.ADMIN_PASSWORD || '';
}

export function b64url(bytes) {
  let bin = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    bin += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function hmac(secret, data) {
  const key = await crypto.subtle.importKey(
    'raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'],
  );
  return new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(data)));
}

export function timingSafeEqual(a, b) {
  const x = String(a || '');
  const y = String(b || '');
  if (x.length !== y.length) return false;
  let diff = 0;
  for (let i = 0; i < x.length; i += 1) diff |= x.charCodeAt(i) ^ y.charCodeAt(i);
  return diff === 0;
}

/** 비밀번호 비교 — 길이 차이도 숨기도록 둘 다 SHA-256 으로 접어서 비교한다. */
export async function passwordMatches(input, expected) {
  if (!expected) return false;
  const [a, b] = await Promise.all([
    crypto.subtle.digest('SHA-256', enc.encode(String(input || ''))),
    crypto.subtle.digest('SHA-256', enc.encode(String(expected))),
  ]);
  return timingSafeEqual(b64url(new Uint8Array(a)), b64url(new Uint8Array(b)));
}

export async function issueToken(env, ttlSeconds = 30 * 86400) {
  const secret = getSecret(env);
  if (!secret) throw new Error('SESSION_SECRET / ADMIN_PASSWORD 가 없습니다.');
  const exp = Math.floor(Date.now() / 1000) + Math.floor(ttlSeconds);
  const payload = `v1.${exp.toString(36)}`;
  const sig = b64url(await hmac(secret, payload));
  return { token: `${payload}.${sig}`, exp };
}

export async function verifyToken(env, token) {
  const secret = getSecret(env);
  if (!secret || !token) return false;
  const parts = String(token).split('.');
  if (parts.length !== 3 || parts[0] !== 'v1') return false;
  const exp = parseInt(parts[1], 36);
  if (!Number.isFinite(exp) || exp * 1000 < Date.now()) return false;
  const expected = b64url(await hmac(secret, `v1.${parts[1]}`));
  return timingSafeEqual(expected, parts[2]);
}

export function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Robots-Tag': 'noindex, nofollow',
      ...extra,
    },
  });
}

/** Authorization: Bearer <token> 을 확인한다. 통과하면 null, 아니면 401 Response. */
export async function requireAuth(context) {
  const { request, env } = context;
  const header = request.headers.get('Authorization') || '';
  const token = header.startsWith('Bearer ') ? header.slice(7).trim() : '';
  if (!getSecret(env)) {
    return json({
      ok: false,
      error: 'ADMIN_PASSWORD_NOT_SET',
      message: '서버에 ADMIN_PASSWORD 환경변수가 없습니다. Cloudflare Pages 설정에서 추가해 주세요.',
    }, 500);
  }
  if (!(await verifyToken(env, token))) {
    return json({
      ok: false,
      error: 'UNAUTHORIZED',
      message: '로그인이 필요합니다. 비밀번호를 다시 입력해 주세요.',
    }, 401);
  }
  return null;
}

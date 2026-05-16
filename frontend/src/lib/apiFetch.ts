/**
 * Thin fetch wrapper that:
 *  - prefixes the API base from VITE_API_BASE_URL
 *  - sets credentials: 'include' so the httpOnly auth cookie travels
 *  - parses JSON errors into Error objects with .status attached
 *
 * Use this for every API call so the cookie behavior stays consistent.
 */

export class ApiError extends Error {
  status: number
  body: unknown

  constructor(status: number, message: string, body?: unknown) {
    super(message)
    this.status = status
    this.body = body
  }
}

function apiBase(): string {
  return import.meta.env.VITE_API_BASE_URL ?? ''
}

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const res = await fetch(`${apiBase()}${path}`, {
    credentials: 'include',
    ...init,
  })
  return res
}

export async function apiJson<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, {
    headers: { 'Content-Type': 'application/json', ...(init.headers ?? {}) },
    ...init,
  })
  if (!res.ok) {
    let body: unknown = undefined
    try { body = await res.json() } catch { /* not json */ }
    const msg = (body && typeof body === 'object' && 'detail' in body && typeof (body as { detail: unknown }).detail === 'string')
      ? (body as { detail: string }).detail
      : `Request failed (${res.status})`
    throw new ApiError(res.status, msg, body)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

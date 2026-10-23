import type { VercelRequest, VercelResponse } from '@vercel/node'

/**
 * Checks that the request carries a valid PAYPULSE_ADMIN_KEY.
 * Set PAYPULSE_ADMIN_KEY in Vercel env vars (any strong random string).
 * Pass it as:  Authorization: Bearer <key>  OR  X-Admin-Key: <key>
 * Returns true and sends 401 if invalid, returns false if valid (proceed).
 */
export function requireAdminKey(req: VercelRequest, res: VercelResponse): boolean {
  const adminKey = process.env.PAYPULSE_ADMIN_KEY
  if (!adminKey) {
    // Not configured — open access (dev mode). Log a warning.
    console.warn('[PayPulse] PAYPULSE_ADMIN_KEY not set — admin routes are unprotected')
    return false
  }

  const authHeader = req.headers['authorization'] ?? ''
  const xAdminKey = req.headers['x-admin-key'] ?? ''
  const provided =
    (typeof authHeader === 'string' && authHeader.startsWith('Bearer ')
      ? authHeader.slice(7)
      : '') ||
    (typeof xAdminKey === 'string' ? xAdminKey : '')

  if (provided !== adminKey) {
    res.status(401).json({
      error: 'Unauthorized',
      hint: 'Pass your admin key as Authorization: Bearer <key> or X-Admin-Key: <key>',
    })
    return true // caller should return immediately
  }
  return false
}

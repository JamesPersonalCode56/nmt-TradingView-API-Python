# 11 - SESSION and SIGNATURE (safe handling)

These values act like cookies for your TradingView account.
Treat them as secrets.

## How to obtain

1) Log in to https://www.tradingview.com
2) Open Developer Tools in your browser (F12)
3) Go to Application (or Storage) -> Cookies -> tradingview.com
4) Copy these cookie values:
   - `sessionid`
   - `sessionid_sign`

These map to env vars:

- `SESSION` = sessionid
- `SIGNATURE` = sessionid_sign

## Safe usage

- Do not commit them into git.
- Use environment variables or a local `.env` (ignored by git).
- Do not share screenshots or logs that include them.
- Rotate them by logging out and back in if leaked.

## Optional: loginUser

`loginUser(username, password)` can fetch session/signature, but it sends
credentials over HTTP. Use it only in trusted environments.
Prefer browser cookies for safety.

## Common errors

- "Wrong or expired sessionid/signature": tokens are invalid or expired
- "Credentials error": same cause

## Best practices

- Use a dedicated TradingView account for API access.
- Keep SESSION/SIGNATURE scoped to minimal privileges.
- If possible, use a password manager and short-lived sessions.


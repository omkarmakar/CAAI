# CAAI Frontend (frontend-new)

This is a minimal Next.js + TypeScript + Tailwind scaffold created to integrate with the existing CAAI backend auth endpoints.

Quick start (on Windows PowerShell):

```powershell
cd C:\Users\OM\Documents\Projects\CAAI\frontend-new
npm install
npm run dev
```

Environment:
- The frontend expects the backend API base URL to be in `NEXT_PUBLIC_API_BASE` (defaults to `http://localhost:8000`).

Auth flow implemented:
- Login: POST /auth/login -> stores access_token and refresh_token in localStorage
- Register: POST /auth/register -> same token storage
- Protected endpoints use Authorization: Bearer <access_token>

Notes & next steps:
- Token refresh is not fully automatic yet (refresh endpoint wiring can be added).
- If you prefer cookies for refresh tokens (safer), we can update the backend and wire cookie-based auth.

Files created:
- `src/lib/auth.tsx` - AuthContext (client) and `useAuth()` hook.
- `src/lib/api.ts` - axios instance and token helper.
- Basic pages: `/login`, `/register`, `/dashboard`, `/admin` and root.

If you want me to continue and wire automatic token refresh + role-protected route wrappers, tell me and I'll proceed.

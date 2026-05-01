---
summary: Next.js App Router + Supabase integration patterns (SSR, auth callback, server actions, realtime)
tags: [nextjs, supabase, ssr, auth, realtime]
related: [supabase-auth-rls, fullstack-architecture]
source: synthetic-memory/nextjs-supabase.md
---

# Next.js + Supabase Integration Patterns

## Project Setup

Install the Supabase client library:

```bash
npm install @supabase/supabase-js @supabase/ssr
```

For Next.js App Router (v13+), use `@supabase/ssr` instead of the deprecated `@supabase/auth-helpers-nextjs`.

## Client Initialization

Create a utility file for Supabase clients:

- **Browser client** (`createBrowserClient`): Used in Client Components. Reads cookies automatically.
- **Server client** (`createServerClient`): Used in Server Components, Route Handlers, and Server Actions. Requires passing cookie handlers from `next/headers`.
- **Service role client**: For admin operations bypassing RLS. Never expose the service role key to the client. (Security model: [supabase-auth-rls](supabase-auth-rls.md).)

```typescript
// utils/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export function createClient() {
  const cookieStore = cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { /* get, set, remove handlers */ } }
  )
}
```

## Authentication Flow

Use Supabase Auth with PKCE flow for server-side rendering:

(Full PKCE detail: [supabase-auth-rls](supabase-auth-rls.md#auth-flow-pkce).)

1. **Sign-up/Sign-in**: Call `supabase.auth.signInWithOAuth()` or `signInWithPassword()`.
2. **Callback route**: Create `/auth/callback/route.ts` to exchange the auth code for a session.
3. **Middleware**: Use `middleware.ts` to refresh the session on every request. Call `supabase.auth.getUser()` (not `getSession()` — `getSession` doesn't validate the JWT).

## Data Fetching Patterns

- **Server Components**: Fetch data directly with the server client. Data is fetched at request time by default in the App Router.
- **Client Components**: Use `useEffect` or a library like SWR/React Query.
- **Server Actions**: Use `"use server"` functions for mutations. Call `revalidatePath()` after writes.

See [fullstack-architecture](fullstack-architecture.md#api-design-patterns) for guidance on when to choose Server Actions vs API Routes vs direct client queries.

## Real-time Subscriptions

```typescript
supabase.channel('table-changes')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'messages' }, handler)
  .subscribe()
```

Real-time requires the `realtime` publication to include the relevant tables (configured in Supabase Dashboard or via SQL).

## Environment Variables

Required in `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # server-only
```

The `NEXT_PUBLIC_` prefix exposes variables to the browser. Never prefix the service role key with `NEXT_PUBLIC_`.

## Common Patterns

- **Optimistic UI**: Update local state immediately, then sync with Supabase. Roll back on error.
- **Row-Level Security**: Always enable RLS on tables. The anon key is public; security depends entirely on RLS policies. (Policy patterns: [supabase-auth-rls](supabase-auth-rls.md).)
- **Type generation**: Run `supabase gen types typescript` to generate TypeScript types from your database schema.

## Related

- [supabase-auth-rls](supabase-auth-rls.md) — RLS policy syntax and helper functions used to secure the data layer this page integrates with.
- [fullstack-architecture](fullstack-architecture.md) — broader stack rationale (Next.js + Supabase + Vercel) and where this integration fits in the architecture layers.

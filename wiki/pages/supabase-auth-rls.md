---
summary: Supabase Auth providers, PKCE flow, and PostgreSQL Row-Level Security (RLS) policies
tags: [supabase, auth, rls, postgresql, security]
related: [nextjs-supabase, fullstack-architecture]
source: synthetic-memory/supabase-auth-rls.md
---

# Supabase Auth + Row Level Security

## Authentication Setup

Supabase Auth supports multiple providers:

- **Email/Password**: Built-in, with email confirmation flow.
- **Magic Link**: Passwordless email login.
- **OAuth**: Google, GitHub, Apple, Discord, etc.
- **Phone/SMS**: OTP-based authentication.

Enable providers in Dashboard → Authentication → Providers.

## Auth Flow (PKCE)

For server-side frameworks (Next.js, SvelteKit), use the PKCE flow. Framework-specific wiring for Next.js App Router is in [nextjs-supabase](nextjs-supabase.md#authentication-flow):

1. Client calls `signInWithOAuth({ provider: 'google' })`.
2. User is redirected to the provider.
3. Provider redirects back to your callback URL with a `code` parameter.
4. Server exchanges `code` for session tokens via `exchangeCodeForSession(code)`.
5. Session is stored in cookies.

## Row Level Security (RLS)

RLS is PostgreSQL's built-in row-level access control. When enabled on a table, **no rows are accessible by default** — you must create policies to grant access.

### Enable RLS

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
```

### Policy Structure

```sql
CREATE POLICY "policy_name" ON table_name
  FOR [ALL | SELECT | INSERT | UPDATE | DELETE]
  TO [role]
  USING (condition)           -- filter rows for SELECT/UPDATE/DELETE
  WITH CHECK (condition);     -- validate rows for INSERT/UPDATE
```

### Common Patterns

**Users can read all rows:**

```sql
CREATE POLICY "public_read" ON posts FOR SELECT USING (true);
```

**Users can only modify their own rows:**

```sql
CREATE POLICY "owner_update" ON posts FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

**Insert with ownership:**

```sql
CREATE POLICY "insert_own" ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

## Auth Helper Functions

Supabase provides SQL helper functions:

- `auth.uid()` — Returns the authenticated user's UUID.
- `auth.jwt()` — Returns the full JWT claims (for custom claims).
- `auth.role()` — Returns the role (`anon` or `authenticated`).

## Service Role Bypass

The `service_role` key bypasses RLS entirely. Use it only on the server for admin operations (cf. service role client in [nextjs-supabase](nextjs-supabase.md#client-initialization)):

```typescript
const supabaseAdmin = createClient(url, serviceRoleKey);
```

## Multi-tenant RLS

For multi-tenant apps, add an `org_id` column:

```sql
CREATE POLICY "tenant_isolation" ON resources
  FOR ALL USING (
    org_id IN (
      SELECT org_id FROM org_members WHERE user_id = auth.uid()
    )
  );
```

## RLS Performance

- **Index the columns used in policies** (e.g., `user_id`, `org_id`).
- Avoid complex subqueries in policies; use materialized views or denormalized columns.
- Use `security definer` functions for complex access patterns (but be careful — they bypass RLS).

## Testing RLS

Test policies in the SQL Editor using role impersonation:

```sql
SET request.jwt.claims = '{"sub": "user-uuid-here"}';
SET role = 'authenticated';
SELECT * FROM posts;  -- should only return accessible rows
```

## Common Gotchas

- Forgetting to enable RLS leaves the table fully accessible to anyone with the anon key.
- `USING` filters reads; `WITH CHECK` validates writes. Both are needed for UPDATE.
- Foreign key references may fail if the referenced row isn't visible under RLS. Use `security definer` functions for cross-table lookups.

## Related

- [nextjs-supabase](nextjs-supabase.md) — how the PKCE flow and RLS-protected queries are wired into Next.js App Router (server clients, middleware, callback routes).
- [fullstack-architecture](fullstack-architecture.md) — where RLS sits in the overall stack ("RLS from day one" principle, auth architecture).

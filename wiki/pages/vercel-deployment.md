---
summary: Vercel deployment patterns — vercel.json config, env vars, deployment pipeline (preview/production/rollback), CLI, serverless function limits, ISR/caching, custom domains, monitoring, monorepo
tags: [vercel, deployment, nextjs, serverless, cdn, isr]
related: [nextjs-supabase, fullstack-architecture, domain-dns, github-actions]
source: synthetic-memory/vercel-deployment.md
---

# Vercel Deployment Best Practices

## Project Configuration

Vercel auto-detects Next.js projects (see [nextjs-supabase](nextjs-supabase.md) for the framework integration). Key settings in `vercel.json`:

```json
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "regions": ["icn1"],
  "headers": [
    { "source": "/api/(.*)", "headers": [{ "key": "Cache-Control", "value": "no-store" }] }
  ]
}
```

## Environment Variables

- Set via Dashboard → Settings → Environment Variables or `vercel env pull`.
- Scoped to Production, Preview, or Development.
- Sensitive values (API keys, DB URLs) should be Production-only when possible.
- Use `vercel env pull .env.local` to sync env vars to local development.

## Deployment Pipeline

1. **Push to GitHub**: Vercel auto-deploys on push.
2. **Preview deployments**: Every PR gets a unique URL (`project-git-branch-team.vercel.app`).
3. **Production**: Merges to `main` (or configured production branch) deploy to the production URL.
4. **Instant rollback**: Click "Promote to Production" on any previous deployment.

For Actions-driven deploys (alternative or hybrid setup), see [github-actions](github-actions.md).

## CLI Deployment

```bash
npm i -g vercel
vercel          # preview deployment
vercel --prod   # production deployment
```

Use `--force` to bypass build cache. Use `--token` for CI environments.

## API Routes & Serverless Functions

- Each API route becomes a serverless function.
- Default timeout: 10s (Hobby), 60s (Pro). Configure with `maxDuration` in route config.
- Cold starts: ~250ms for Node.js. Keep functions small.
- Use Edge Runtime (`export const runtime = 'edge'`) for lower latency on simple routes.

## Caching Strategies

- **ISR (Incremental Static Regeneration)**: Use `revalidate` in `fetch` or `generateStaticParams`.
- **On-demand revalidation**: Call `revalidatePath()` or `revalidateTag()` from webhooks or Server Actions.
- **CDN caching**: Static assets are cached on Vercel's CDN automatically.

## Custom Domains

1. Add domain in Dashboard → Settings → Domains.
2. Configure DNS: CNAME to `cname.vercel-dns.com` or A record to `76.76.21.21`. DNS-only (gray cloud) on Cloudflare — Vercel handles SSL. See [domain-dns](domain-dns.md#vercel) for the full DNS recipe.
3. SSL certificates are provisioned automatically via Let's Encrypt.
4. Redirect `www` to apex (or vice versa) in domain settings.

## Monitoring

- **Analytics**: Enable Web Analytics in Dashboard for Core Web Vitals.
- **Logs**: Real-time function logs via Dashboard or `vercel logs`.
- **Speed Insights**: Track real-user performance metrics.
- **API**: Query analytics programmatically via `https://vercel.com/api/web/insights/stats/{type}`.

## Monorepo Support

Use `vercel.json` root filter or Dashboard "Root Directory" setting to deploy specific packages. Turbo Remote Caching integrates natively with Vercel. Monorepo trade-offs vs polyrepo: see [fullstack-architecture](fullstack-architecture.md#monorepo-vs-polyrepo).

## Related

- [nextjs-supabase](nextjs-supabase.md) — primary framework Vercel auto-detects; env-var prefixing rules apply directly.
- [fullstack-architecture](fullstack-architecture.md) — where Vercel's Edge Network sits in the stack layers; environment strategy table maps onto preview/production deploys.
- [domain-dns](domain-dns.md) — exact DNS records for pointing custom domains at Vercel projects.
- [github-actions](github-actions.md) — CI-driven deploys as alternative or supplement to Vercel's git-push trigger.

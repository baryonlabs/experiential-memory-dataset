---
summary: Technical SEO (meta, OG, JSON-LD, sitemap, robots), blog crossposting strategy with canonical URLs, social media for developer products, analytics
tags: [seo, marketing, og-tags, canonical, social, analytics]
related: [hugo-blog, docusaurus-docs, vercel-deployment, domain-dns]
source: synthetic-memory/seo-marketing.md
---

# Technical SEO, Blog Crossposting, and Social Media

## Technical SEO Fundamentals

### Meta Tags

Every page needs:

```html
<title>Page Title — Site Name</title>
<meta name="description" content="150-160 character description">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://example.com/page">
```

Canonical URL setup interacts with DNS (`www` vs apex) and redirects — see [domain-dns](domain-dns.md#page-rules--redirect-rules).

### Open Graph (Social Sharing)

```html
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Description">
<meta property="og:image" content="https://example.com/og-image.png">
<meta property="og:url" content="https://example.com/page">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
```

OG images: 1200×630px recommended. Use dynamic OG image generation (e.g., `@vercel/og`) for blog posts.

(`@vercel/og` runs natively on [vercel-deployment](vercel-deployment.md).)

### Structured Data (JSON-LD)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Title",
  "author": { "@type": "Person", "name": "Author" },
  "datePublished": "2024-01-15"
}
</script>
```

### Sitemap & Robots

- `sitemap.xml`: List all indexable URLs. Most frameworks generate automatically. (E.g. [hugo-blog](hugo-blog.md), [docusaurus-docs](docusaurus-docs.md).)
- `robots.txt`: Control crawler access. `Disallow: /api/` for API routes.

## Blog Crossposting Strategy

### Primary Blog (Your Domain)

Always publish on your own domain first. This establishes canonical ownership.

### Crossposting Platforms

1. **Dev.to**: Import via RSS or paste. Set canonical URL to your original post.
2. **Hashnode**: Custom domain support. Can auto-import from RSS.
3. **Medium**: Import tool available. Set canonical URL in post settings.
4. **Hacker News**: Submit link to your original post for tech content.

### Canonical URLs

Always set `rel="canonical"` pointing to the original URL on your domain. This tells search engines which version is authoritative and prevents duplicate content penalties.

### RSS Feed

Expose an RSS feed (`/feed.xml` or `/rss.xml`). [Hugo](hugo-blog.md#configuration-hugotoml) and [Docusaurus](docusaurus-docs.md) generate these automatically. Use RSS for:

- Automated crossposting.
- Newsletter distribution.
- Podcast directories (if applicable).

## Social Media for Developer Products

### Twitter/X

- Share blog posts with key takeaway, not just the title.
- Use relevant hashtags sparingly (#webdev, #gamedev, #AI).
- Thread format for technical deep-dives.
- Pin important announcements.

### Reddit

- Share in relevant subreddits (r/programming, r/webdev, r/gamedev).
- Follow self-promotion rules (10:1 ratio of community engagement to self-promotion).
- Engage authentically in comments.

### Product Hunt

- Launch on a Tuesday–Thursday for best visibility.
- Prepare assets: tagline, description, screenshots, maker comment.
- Engage with every comment on launch day.

## Analytics

- **Google Search Console**: Monitor indexing, search queries, click-through rates.
- **Google Analytics / Plausible / Fathom**: Traffic, user behavior.
- **Core Web Vitals**: LCP < 2.5s, FID < 100ms, CLS < 0.1. Vercel exposes these via Web Analytics — see [vercel-deployment](vercel-deployment.md#monitoring).

## Related

- [hugo-blog](hugo-blog.md) — most blog SEO concerns (meta tags, RSS, sitemap) plug into Hugo themes directly.
- [docusaurus-docs](docusaurus-docs.md) — same SEO concerns for the docs site; Algolia/local search complement organic discovery.
- [vercel-deployment](vercel-deployment.md) — Web Analytics, Speed Insights, dynamic OG image generation hosted natively.
- [domain-dns](domain-dns.md) — canonical URL choice (`www` vs apex), redirects, and how DNS interacts with SEO.

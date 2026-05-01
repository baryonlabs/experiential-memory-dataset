---
summary: Domain registration, Cloudflare DNS records, SSL/TLS modes, and common configuration recipes (Vercel, GitHub Pages, email)
tags: [dns, cloudflare, ssl, domains, infra]
related: [vercel-deployment, seo-marketing, trademark-ip]
source: synthetic-memory/domain-dns.md
---

# Domain Management, Cloudflare DNS, and SSL

## Domain Registration

Register domains through registrars: Cloudflare Registrar, Namecheap, Google Domains (now Squarespace), Porkbun.

Cloudflare Registrar offers at-cost pricing (no markup). Transfer existing domains by unlocking at the current registrar and requesting transfer at Cloudflare. For trademark considerations on domain choice, see [trademark-ip](trademark-ip.md).

## DNS Record Types

| Type | Purpose | Example |
|------|---------|---------|
| A | Maps domain to IPv4 | `example.com → 76.76.21.21` |
| AAAA | Maps domain to IPv6 | `example.com → 2606:4700::` |
| CNAME | Alias to another domain | `www → example.com` |
| MX | Mail server | `example.com → mx.email.com` |
| TXT | Text records (SPF, DKIM, verification) | `v=spf1 include:...` |
| NS | Nameserver delegation | `ns1.cloudflare.com` |
| SRV | Service location | `_sip._tcp.example.com` |

## Cloudflare DNS Setup

1. Add site in Cloudflare Dashboard.
2. Update nameservers at your registrar to Cloudflare's assigned NS records.
3. DNS propagation: typically 1–48 hours (usually under 1 hour with low TTLs).

### Proxy vs DNS-Only

- **Proxied (orange cloud)**: Traffic flows through Cloudflare's CDN. Enables caching, DDoS protection, WAF, and hides origin IP.
- **DNS-only (gray cloud)**: Direct resolution. Use for MX records, non-HTTP services, or when Cloudflare proxy is unwanted.

## SSL/TLS Modes

Configure in Cloudflare → SSL/TLS:

- **Off**: No encryption (not recommended).
- **Flexible**: HTTPS between visitor and Cloudflare; HTTP to origin. Causes redirect loops if origin forces HTTPS.
- **Full**: HTTPS end-to-end, but doesn't validate origin certificate.
- **Full (Strict)**: HTTPS end-to-end with valid origin certificate. **Recommended.**

### Origin Certificates

Cloudflare issues free origin certificates (valid 15 years, only trusted by Cloudflare):

1. SSL/TLS → Origin Server → Create Certificate.
2. Install on your origin server.
3. Set SSL mode to Full (Strict).

## Common Configurations

### Vercel

```
Type: CNAME
Name: @  (or subdomain)
Target: cname.vercel-dns.com
Proxy: DNS-only (gray cloud) — Vercel handles SSL
```

For full Vercel domain configuration see [vercel-deployment](vercel-deployment.md#custom-domains).

### GitHub Pages

```
Type: CNAME
Name: @
Target: username.github.io

Type: A (if apex)
Name: @
Target: 185.199.108.153 (and .109, .110, .111)
```

### Email (Google Workspace)

```
Type: MX  Priority: 1   Target: aspmx.l.google.com
Type: MX  Priority: 5   Target: alt1.aspmx.l.google.com
Type: TXT Value: v=spf1 include:_spf.google.com ~all
```

## Page Rules / Redirect Rules

Redirect `www` to apex (or vice versa):

- Cloudflare Rules → Redirect Rules.
- Match: `www.example.com/*` → Redirect to `https://example.com/$1` (301).

Canonical URL setup matters for SEO — see [seo-marketing](seo-marketing.md#meta-tags).

## Best Practices

- Use short TTLs (300s) during migrations, longer (3600s+) for stable records.
- Enable DNSSEC in Cloudflare and at your registrar.
- Use `dig` or `nslookup` to verify DNS propagation.
- Keep registrar account secured with 2FA and registrar lock enabled.

## Related

- [vercel-deployment](vercel-deployment.md) — DNS recipe for pointing custom domains at Vercel projects (CNAME to `cname.vercel-dns.com`).
- [seo-marketing](seo-marketing.md) — canonical URL setup, www-to-apex redirects, and how DNS choices interact with search indexing.
- [trademark-ip](trademark-ip.md) — domain availability vs trademark availability are separate concerns; both matter for brand protection.

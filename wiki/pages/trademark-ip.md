---
summary: Trademark filing process — Korea (KIPRIS/KIPO), United States (USPTO), Madrid Protocol; Nice Classification, intent-to-use vs use-based, maintenance
tags: [trademark, ip, legal, kipo, uspto, madrid]
related: [npm-publishing, domain-dns]
source: synthetic-memory/trademark-ip.md
---

# Trademark Filing Process (Korea + US)

## Trademark Basics

A trademark protects brand names, logos, and slogans used in commerce. Registration provides:

- Legal presumption of ownership.
- Exclusive right to use the mark in registered classes.
- Ability to bring federal/national infringement actions.
- Basis for international registration (Madrid Protocol).

## Nice Classification

Trademarks are registered under specific classes (1–45). Common classes for software:

- **Class 9**: Software, mobile apps, downloadable digital content.
- **Class 35**: Online retail, advertising services, SaaS marketplaces.
- **Class 41**: Education, entertainment, gaming services.
- **Class 42**: SaaS, cloud computing, software development services.

Register in all classes where you use or intend to use the mark.

## Korea (KIPRIS / KIPO)

### Filing Process

1. **Search**: Check existing marks at kipris.or.kr (free) or via patent attorney.
2. **Application**: File at Korean Intellectual Property Office (KIPO). Online filing via KePS system.
3. **Examination**: ~10-12 months. Examiner checks distinctiveness, conflicts.
4. **Publication**: 2-month opposition period after approval.
5. **Registration**: If no opposition, registration certificate issued. Valid 10 years, renewable.

### Costs (Approximate)

- Government filing fee: ~46,000 KRW per class.
- Attorney fees: 500,000–1,000,000 KRW per class.
- Registration fee: ~211,000 KRW per class (for 10 years).

### Documents Needed

- Applicant info (name, address, business registration).
- Mark specimen (wordmark or logo image).
- Goods/services description per class.
- Priority claim (if filing within 6 months of another country's filing).

## United States (USPTO)

### Filing Process

1. **Search**: USPTO TESS database (tess2.uspto.gov). Also search state registrations.
2. **Application**: File via TEAS (Trademark Electronic Application System).
   - **TEAS Plus** ($250/class): Stricter requirements, cheaper.
   - **TEAS Standard** ($350/class): More flexible descriptions.
3. **Examination**: ~8-12 months. Examining attorney reviews.
4. **Publication**: 30-day opposition period in the Official Gazette.
5. **Registration**: Certificate issued. Valid 10 years, renewable.

### Intent-to-Use vs Use-Based

- **Use-based (1a)**: Mark already in use in commerce. Submit specimen showing use.
- **Intent-to-use (1b)**: Plan to use. Must file Statement of Use within 6 months of allowance (extendable up to 3 years).

### Maintenance

- **Section 8 Declaration**: File between 5th and 6th year to confirm continued use.
- **Section 9 Renewal**: Every 10 years.

## Madrid Protocol (International)

File one application through WIPO to register in multiple countries. Requires a "home" registration or application as basis. Designate target countries; each conducts its own examination.

## General Tips

- File early — trademark rights strengthen with earlier filing dates.
- Use the ™ symbol immediately (no registration required). Use ® only after registration.
- Monitor for infringement using watch services.
- Document first use in commerce with dated evidence (screenshots, invoices).

## Practical Coordination

When choosing a brand name, three availability checks must align:

- **Trademark availability** (this page) — KIPRIS and USPTO TESS.
- **Domain availability** — see [domain-dns](domain-dns.md).
- **npm package-name availability** — see [npm-publishing](npm-publishing.md#pre-publish-checklist) (especially for scoped packages where the scope itself may need protection).

A name that clears all three is much rarer than one that clears any single check.

## Related

- [npm-publishing](npm-publishing.md) — package-name conflicts can de-facto reserve mindshare even without a registered trademark; check both registries before locking in.
- [domain-dns](domain-dns.md) — domain availability is independent of trademark availability; both matter for a defensible brand.

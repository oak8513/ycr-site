# Task #51 — SEO refresh: computer repair York PA

**Date:** 2026-04-24
**Reason:** Only 1/49 geo cells ranked in local pack for 'computer repair York PA'

## What was done

- Added 2 new paragraphs to `blog/computer-repair-york-pa.html`:
  1. Common problems paragraph (targets "York PA computer repair", boot failures, overheating, spill damage)
  2. Local neighborhood paragraph (West York, Springettsbury Township, Hellam, Dallastown)
- FAQ already had 5 items — no expansion needed
- Meta description already contained exact phrase 'computer repair York PA' — no change needed
- Related Services section already present with 2 /blog/ links — no change needed
- Sitemap lastmod already 2026-04-24 — no change needed
- Committed and pushed: `4043c71` on main

## Outcome

All acceptance criteria met. Task done.

---

# Task #66 — SEO refresh: computer repair York PA (second pass)

**Date:** 2026-04-28
**Reason:** Same URL flagged again by seo_recommendations.py 2026-04-25 — only 1/49 geo cells ranked in local pack. Treating as a freshness refresh on top of the 2026-04-24 work.

## What was done

- Added 2 fresh body paragraphs:
  1. Spring 2026 / Windows 11 24H2 angle (boot loops, missing drivers, Wi-Fi drops post-update)
  2. Slow-PC / tune-up angle (malware cleanup, startup trim, SSD swap)
- Added a 6th FAQ: "What areas around York, PA do you serve?" — also added to the FAQPage JSON-LD schema so the schema and visible UI stay in sync
- Bumped `sitemap.xml` lastmod for this URL from 2026-04-24 → 2026-04-28
- Committed and pushed: `a23ac3e` on main — "SEO: refresh computer repair York PA landing page"

## Outcome

All acceptance criteria met. Task done.

---

# Task #69 — Shorten meta descriptions over 160 chars

**Date:** 2026-04-28
**Reason:** SEO audit flagged meta description length > 160 chars on multiple pages.

## What was done

Site-wide scan caught 5 pages with descriptions > 160 chars across `<meta name="description">`, `<meta property="og:description">`, and Jekyll front-matter `description`. Rewrote each to fit under 155 chars while keeping the primary keyword near the start:

- `blog/notebook-repair-near-me-york-pa.html` — meta + og (was 176 chars each → 144)
- `blog/repair-laptop.html` — meta + og (was 171 chars each → 142)
- `services/ssd-ram-upgrades.html` — front-matter description (was 165 → 145)
- `blog/computer-and-laptop-repairs-near-me-york-pa.html` — og only (was 181 → 144)
- `blog/laptop-screen-black-spot.html` — og only (was 174 → 138)

Re-ran the scan after edits — zero remaining length violations across the repo.

## Outcome

All meta descriptions and og:descriptions site-wide now under 160 characters. Task done.

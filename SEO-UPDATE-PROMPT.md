# SEO Website Update Prompt — York Computer Repair
_Generated 2026-04-23 based on weekly SEO tracker data_

---

## Context

You are updating the York Computer Repair website to improve its Google search rankings.
The site is a **Jekyll static site** hosted on **GitHub Pages** at `yorkcomputerrepair.com`.

Working directory: `C:\Users\Owner\Documents\Claude\Projects\ycr-site\`

Repo: https://github.com/oak8513/ycr-site

Current file structure:
```
index.html          ← homepage
services.html       ← all services
about.html
contact.html
blog/               ← landing pages + posts
  index.html
  fix-laptop-near-me-york-pa.html
  repair-laptop-near-me-york-pa.html
  computer-and-laptop-repairs-near-me-york-pa.html
_posts/             ← Jekyll blog posts (YYYY-MM-DD-slug.html)
_layouts/
_includes/
_config.yml
```

Business info:
- **Name:** York Computer Repair
- **Address:** 2069 Carlisle Rd, York, PA 17408
- **Phone:** 717-739-9675
- **Hours:** Monday–Saturday 9 AM–6 PM (confirm from about.html or contact.html)
- **URL:** https://yorkcomputerrepair.com
- **Services:** Windows laptop repair, desktop/PC repair, virus & malware removal,
  data recovery, laptop screen replacement, SSD/RAM upgrades, computer tune-up,
  PC repair in Shiloh PA

---

## SEO Problem

The weekly rank tracker shows York Computer Repair is **not appearing** in Google
organic results OR the Google Maps 3-Pack for any tracked keyword. The geo-grid
(49 location cells across the service area) shows:

| Keyword | Geo cells ranked | Best rank |
|---|---|---|
| computer repair York PA | 1 / 49 | #1 |
| virus removal York PA | 1 / 49 | #1 |
| laptop screen replacement York PA | 1 / 49 | #2 |
| desktop repair York PA | 1 / 49 | #3 |
| computer repair near me | 1 / 49 | #3 |
| SSD upgrade York PA | 1 / 49 | #11 |
| laptop repair York PA | 0 / 49 | — |
| laptop repair near me | 0 / 49 | — |
| malware removal York PA | 0 / 49 | — |
| data recovery York PA | 0 / 49 | — |
| computer tune up York PA | 0 / 49 | — |
| PC repair Shiloh PA | 0 / 49 | — |

**Root cause:** The site lacks dedicated, keyword-focused pages for each service.
Google can't tell the site is relevant for these specific searches.

---

## Tasks — implement all of these

### 1. Add JSON-LD LocalBusiness schema to `index.html`

Inside `<head>` or just before `</body>`, add a `<script type="application/ld+json">` block:

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "York Computer Repair",
  "url": "https://yorkcomputerrepair.com",
  "telephone": "+17177399675",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "2069 Carlisle Rd",
    "addressLocality": "York",
    "addressRegion": "PA",
    "postalCode": "17408",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 39.9526,
    "longitude": -76.7277
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
      "opens": "09:00",
      "closes": "18:00"
    }
  ],
  "priceRange": "$$",
  "image": "https://yorkcomputerrepair.com/assets/storefront.jpg",
  "description": "Expert laptop and PC repair in York, PA. Virus removal, data recovery, screen replacement, SSD upgrades, and more. Walk-ins welcome.",
  "areaServed": [
    {"@type": "City", "name": "York, PA"},
    {"@type": "City", "name": "Shiloh, PA"},
    {"@type": "City", "name": "Spring Grove, PA"},
    {"@type": "City", "name": "Hanover, PA"}
  ],
  "sameAs": [
    "https://www.google.com/maps?cid=YOUR_GMB_CID"
  ]
}
```

### 2. Create dedicated service landing pages

For each of the following keywords, create a standalone HTML page in `blog/`.
Each page should be a full Jekyll page (with front matter `layout: default`),
not a `_posts` blog post. Name files exactly as shown.

Pages to create (use these exact filenames):

| File | Primary keyword | Secondary keywords |
|---|---|---|
| `blog/laptop-repair-york-pa.html` | laptop repair York PA | laptop repair near me, fix laptop York PA |
| `blog/virus-removal-york-pa.html` | virus removal York PA | malware removal York PA, spyware removal York PA |
| `blog/data-recovery-york-pa.html` | data recovery York PA | hard drive recovery York PA, deleted file recovery |
| `blog/laptop-screen-replacement-york-pa.html` | laptop screen replacement York PA | cracked screen repair York PA |
| `blog/pc-repair-shiloh-pa.html` | PC repair Shiloh PA | computer repair Shiloh PA, PC repair near Shiloh |
| `blog/desktop-repair-york-pa.html` | desktop repair York PA | desktop computer repair York PA |
| `blog/malware-removal-york-pa.html` | malware removal York PA | ransomware removal York PA, spyware removal York PA |
| `blog/ssd-upgrade-york-pa.html` | SSD upgrade York PA | computer upgrade York PA, speed up computer York PA |
| `blog/computer-tune-up-york-pa.html` | computer tune up York PA | slow computer fix York PA, PC tune up York PA |

**Each page must include:**
- Front matter with `title`, `description`, `canonical` (full URL), `layout: default`
- `<h1>` containing the primary keyword exactly
- 3–4 paragraphs of natural, helpful content about the service in York PA
- A bulleted list of what's included in the service
- A clear price/process mention (e.g., "$39.99 diagnostic fee", "walk-ins welcome")
- Business NAP (Name, Address, Phone) in the content or footer section
- An internal link back to `/services.html` and one other relevant landing page
- A Service JSON-LD schema block:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "<Service Name>",
    "provider": {
      "@type": "LocalBusiness",
      "name": "York Computer Repair",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "2069 Carlisle Rd",
        "addressLocality": "York",
        "addressRegion": "PA",
        "postalCode": "17408"
      }
    },
    "areaServed": "York, PA",
    "description": "<one sentence description>"
  }
  ```
- An FAQ section at the bottom (3–5 questions) using `<details>`/`<summary>` or simple HTML,
  plus FAQPage JSON-LD schema

**Style guide:** Match the existing site look — use the Tailwind/utility classes from
`index.html`. The existing hero style uses `bg-ycr-blue text-white py-12 px-4 text-center`
for page heroes. Service content uses `max-w-4xl mx-auto px-4 py-12`. Use the same color
variables: `text-ycr-blue`, `text-ycr-steel`, `bg-ycr-orange`, `text-ycr-signal`.

### 3. Update `services.html` anchor links

After creating the landing pages above, update `services.html` so the "Learn more →"
links for each service section point to the new dedicated landing pages instead of
same-page anchors (#laptop, #virus, etc.). For example:
- Laptop Repair "Learn more" → `/blog/laptop-repair-york-pa.html`
- Virus & Malware Removal → `/blog/virus-removal-york-pa.html`
- Data Recovery → `/blog/data-recovery-york-pa.html`
- Screen Replacement → `/blog/laptop-screen-replacement-york-pa.html`
- SSD & RAM Upgrades → `/blog/ssd-upgrade-york-pa.html`
- Desktop Repair → `/blog/desktop-repair-york-pa.html`

### 4. Add a "Service Areas" section to `index.html`

Below the services grid, add a new section:

```html
<section class="bg-ycr-offwhite py-12 px-4">
  <div class="max-w-4xl mx-auto text-center">
    <h2 class="font-heading font-bold text-2xl text-ycr-blue mb-3">
      Serving York County & Surrounding Areas
    </h2>
    <p class="text-ycr-steel mb-6">
      We're located at 2069 Carlisle Rd in York, PA and serve customers from
      across York County — including Shiloh, Spring Grove, Hanover, Red Lion,
      Dover, Shrewsbury, and beyond.
    </p>
    <div class="flex flex-wrap justify-center gap-3 text-sm font-heading">
      <!-- each tag links to the most relevant landing page -->
      <a href="/blog/computer-repair-york-pa.html" class="bg-white border border-ycr-gray px-4 py-2 rounded-full text-ycr-blue hover:bg-ycr-blue hover:text-white transition">York, PA</a>
      <a href="/blog/pc-repair-shiloh-pa.html" class="bg-white border border-ycr-gray px-4 py-2 rounded-full text-ycr-blue hover:bg-ycr-blue hover:text-white transition">Shiloh, PA</a>
      <span class="bg-white border border-ycr-gray px-4 py-2 rounded-full text-ycr-steel">Spring Grove, PA</span>
      <span class="bg-white border border-ycr-gray px-4 py-2 rounded-full text-ycr-steel">Hanover, PA</span>
      <span class="bg-white border border-ycr-gray px-4 py-2 rounded-full text-ycr-steel">Red Lion, PA</span>
      <span class="bg-white border border-ycr-gray px-4 py-2 rounded-full text-ycr-steel">Dover, PA</span>
    </div>
  </div>
</section>
```

### 5. Update `index.html` meta description

Change the existing meta description to include more keyword signals:

```
York Computer Repair fixes laptops, desktops, viruses, and cracked screens in York, PA.
Serving York County including Shiloh, Spring Grove & Hanover. Walk-ins welcome at
2069 Carlisle Rd. Call 717-739-9675.
```

### 6. Update `sitemap.xml`

Add entries for all new landing pages with today's `<lastmod>` date (2026-04-23).

---

## Deployment

After all edits:
1. `git add -A`
2. `git commit -m "SEO: add service landing pages and schema markup"`
3. `git push origin main`

GitHub Pages will auto-deploy within ~2 minutes.

---

## What NOT to change

- Do not change the phone number, address, or business name anywhere.
- Do not touch `_config.yml` secrets or tokens.
- Do not modify `_layouts/` or `_includes/` unless necessary for a new page.
- Do not delete existing blog posts or landing pages.
- Keep the existing visual design — only add content, don't restyle.

"""
content_engine.py — York Computer Repair autonomous SEO content engine.

Pipeline:
  1. Read york-computer-repair-content-gaps.csv (keyword opportunities)
  2. Read content-log.csv (already-published keywords)
  3. Pick highest-opportunity unpublished keyword
  4. Call Claude API (generate_post.py) to write 800-1200 word SEO blog post
  5. Save as ycr-site/blog/YYYY-MM-DD-{slug}.html
  6. Update blog/index.html listing (between BEGIN_POSTS / END_POSTS markers)
  7. git add + commit + push → GitHub Pages auto-deploys
  8. Append result to content-log.csv

Usage:
    python content_engine.py             # normal run
    python content_engine.py --dry-run   # generate post locally, don't push or log
"""

import argparse
import csv
import html as html_mod
import logging
import os
import re
import sys
import textwrap
from datetime import date
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
SITE_DIR      = Path(__file__).parent
BLOG_DIR      = SITE_DIR / "blog"
BLOG_INDEX    = BLOG_DIR / "index.html"
CONTENT_LOG   = SITE_DIR / "content-log.csv"
GAP_CSV       = Path("C:/Users/Owner/Documents/Claude/Projects/content-strategy/output/york-computer-repair-content-gaps.csv")

LOG_FIELDS    = ["date", "keyword", "cluster", "slug", "filename", "url", "status", "error"]

# Cluster priority (lower index = higher priority)
CLUSTER_ORDER = [
    "Laptop Repair",
    "Desktop & PC Repair",
    "Screen & Hardware",
    "Local City Keywords",
    "Other",
]


# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("content_engine")


# ── Helper: load published keywords ───────────────────────────────────────
def load_published_keywords() -> set:
    if not CONTENT_LOG.exists():
        return set()
    published = set()
    with open(CONTENT_LOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status") == "published":
                published.add(row["keyword"].lower().strip())
    return published


# ── Helper: pick best keyword ──────────────────────────────────────────────
def pick_keyword(published: set) -> dict | None:
    if not GAP_CSV.exists():
        log.error("Gap CSV not found: %s", GAP_CSV)
        return None

    rows = []
    with open(GAP_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            kw = row["keyword"].lower().strip()
            if kw in published:
                continue
            # Parse search volume (may be empty string)
            try:
                vol = int(row.get("avg_monthly_searches") or 0)
            except (ValueError, TypeError):
                vol = 0
            # Cluster priority rank
            cluster = row.get("cluster", "Other")
            try:
                prio = CLUSTER_ORDER.index(cluster)
            except ValueError:
                prio = len(CLUSTER_ORDER)
            rows.append({**row, "_vol": vol, "_prio": prio})

    if not rows:
        log.info("All keywords in gap CSV have already been published.")
        return None

    # Sort: cluster priority ASC, then volume DESC, then keyword length ASC
    rows.sort(key=lambda r: (r["_prio"], -r["_vol"], len(r["keyword"])))
    return rows[0]


# ── Helper: build blog post HTML ───────────────────────────────────────────
NAV = """\
  <nav class="bg-ycr-blue sticky top-0 z-50 shadow-lg">
    <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
      <a href="/" class="flex items-center gap-2 text-white leading-none">
        <img src="/assets/logo.png" alt="York Computer Repair logo" class="h-10 w-auto">
        <span class="font-impact text-2xl tracking-wide">York Computer Repair</span>
      </a>
      <div class="hidden md:flex items-center space-x-6 font-heading font-semibold text-white text-sm">
        <a href="/" class="hover:text-ycr-gray transition">Home</a>
        <a href="/services.html" class="hover:text-ycr-gray transition">Services</a>
        <a href="/about.html" class="hover:text-ycr-gray transition">About</a>
        <a href="/contact.html" class="hover:text-ycr-gray transition">Contact</a>
        <a href="/blog/" class="border-b-2 border-white pb-0.5">Blog</a>
      </div>
      <a href="tel:7177399675" class="bg-ycr-orange hover:bg-orange-700 text-white px-5 py-2 rounded font-heading font-bold text-sm transition">Call 717-739-9675</a>
    </div>
  </nav>"""

FOOTER = """\
  <footer class="bg-ycr-black text-gray-300 py-12 px-4">
    <div class="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
      <div><div class="font-impact text-white text-xl mb-3">York Computer Repair</div><p class="text-sm text-gray-400 leading-relaxed">Your trusted local computer repair shop in York, PA.</p></div>
      <div><h4 class="font-heading font-semibold text-white mb-3">Contact</h4><p class="text-sm">2069 Carlisle Rd<br>York, PA 17408</p><p class="text-sm mt-2"><a href="tel:7177399675" class="hover:text-white">717-739-9675</a></p></div>
      <div><h4 class="font-heading font-semibold text-white mb-3">Hours</h4><p class="text-sm">Mon&ndash;Fri: 9:00 AM &ndash; 5:00 PM</p><p class="text-sm text-gray-500">Saturday: Closed</p><p class="text-sm text-gray-500">Sunday: Closed</p></div>
    </div>
    <div class="max-w-6xl mx-auto mt-8 pt-6 border-t border-gray-700 flex flex-col md:flex-row justify-between text-xs text-gray-500">
      <p>&copy; 2026 York Computer Repair. All rights reserved.</p>
      <nav class="flex gap-4 mt-2 md:mt-0"><a href="/" class="hover:text-gray-300">Home</a><a href="/services.html" class="hover:text-gray-300">Services</a><a href="/about.html" class="hover:text-gray-300">About</a><a href="/contact.html" class="hover:text-gray-300">Contact</a><a href="/blog/" class="hover:text-gray-300">Blog</a></nav>
    </div>
  </footer>"""


def text_to_paragraphs(text: str) -> str:
    """Convert plain text (double-newline separated) to HTML <p> tags."""
    paras = [p.strip() for p in re.split(r"\n{2,}", text.strip()) if p.strip()]
    return "\n".join(
        f'      <p class="text-ycr-steel leading-relaxed mb-5">{html_mod.escape(p)}</p>'
        for p in paras
    )


def build_post_html(post: dict, pub_date: str) -> str:
    """Render the full blog post HTML page."""
    sections_html = ""
    for sec in post.get("sections", []):
        h2 = html_mod.escape(sec.get("h2", ""))
        body = text_to_paragraphs(sec.get("content", ""))
        sections_html += f"""
      <h2 class="font-heading font-bold text-2xl text-ycr-blue mt-10 mb-4">{h2}</h2>
{body}"""

    title_esc   = html_mod.escape(post["title"])
    meta_esc    = html_mod.escape(post["meta_description"])
    h1_esc      = html_mod.escape(post["h1"])
    slug        = post["slug"]
    intro_html  = text_to_paragraphs(post.get("intro", ""))
    concl_html  = text_to_paragraphs(post.get("conclusion", ""))
    cta_esc     = html_mod.escape(post.get("cta_text", "Ready to get your computer fixed?"))

    # Estimate read time (~200 wpm)
    word_count = sum(
        len(re.findall(r"\w+", v))
        for v in [post.get("intro",""), post.get("conclusion","")]
        + [s.get("content","") for s in post.get("sections",[])]
    )
    read_min = max(1, round(word_count / 200))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_esc} | York Computer Repair</title>
  <meta name="description" content="{meta_esc}">
  <link rel="canonical" href="https://yorkcomputerrepair.com/blog/{slug}.html">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title_esc}">
  <meta property="og:description" content="{meta_esc}">
  <meta property="og:url" content="https://yorkcomputerrepair.com/blog/{slug}.html">
  <meta property="article:published_time" content="{pub_date}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            'ycr-blue': '#0B3D91','ycr-steel': '#4A5568','ycr-white': '#F7FAFC',
            'ycr-black': '#1A202C','ycr-signal': '#3182CE','ycr-green': '#38A169',
            'ycr-orange': '#DD6B20','ycr-gray': '#CBD5E0',
          }},
          fontFamily: {{
            sans: ['"Open Sans"','Helvetica','sans-serif'],
            heading: ['Montserrat','Arial','sans-serif'],
            impact: ['Impact','"Arial Narrow"','sans-serif'],
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="font-sans bg-ycr-white text-ycr-black">

{NAV}

  <div class="max-w-3xl mx-auto px-4 py-12">

    <!-- Breadcrumb -->
    <nav class="text-sm text-ycr-steel mb-6">
      <a href="/" class="hover:text-ycr-signal">Home</a>
      <span class="mx-2">&rsaquo;</span>
      <a href="/blog/" class="hover:text-ycr-signal">Blog</a>
      <span class="mx-2">&rsaquo;</span>
      <span class="text-ycr-black">{h1_esc}</span>
    </nav>

    <!-- Article header -->
    <header class="mb-8">
      <h1 class="font-heading font-bold text-3xl md:text-4xl text-ycr-black leading-tight mb-4">{h1_esc}</h1>
      <div class="flex items-center gap-4 text-sm text-ycr-steel">
        <span>York Computer Repair</span>
        <span>&bull;</span>
        <time datetime="{pub_date}">{pub_date}</time>
        <span>&bull;</span>
        <span>{read_min} min read</span>
      </div>
    </header>

    <!-- Article body -->
    <article class="prose max-w-none">
{intro_html}
{sections_html}
{concl_html}
    </article>

    <!-- CTA Box -->
    <div class="mt-10 bg-ycr-blue text-white rounded-xl p-8 text-center">
      <p class="font-heading font-semibold text-lg mb-4">{cta_esc}</p>
      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <a href="tel:7177399675" class="bg-ycr-orange hover:bg-orange-700 text-white font-heading font-bold py-3 px-6 rounded-lg transition">Call 717-739-9675</a>
        <a href="/contact.html" class="border-2 border-white text-white font-heading font-bold py-3 px-6 rounded-lg hover:bg-blue-800 transition">Get Directions</a>
      </div>
      <p class="mt-3 text-blue-200 text-sm">2069 Carlisle Rd, York, PA 17408 &bull; Walk-ins welcome</p>
    </div>

    <!-- Back link -->
    <div class="mt-8 text-center">
      <a href="/blog/" class="text-ycr-signal hover:underline font-heading font-semibold text-sm">&larr; Back to all articles</a>
    </div>

  </div>

{FOOTER}

</body>
</html>
"""


# ── Helper: build blog listing card ───────────────────────────────────────
def build_listing_card(post: dict, pub_date: str) -> str:
    title_esc = html_mod.escape(post["title"])
    desc_esc  = html_mod.escape(post["meta_description"])
    slug      = post["slug"]
    return f"""
    <article class="bg-white border border-ycr-gray rounded-xl p-6 hover:shadow-lg transition mb-6">
      <div class="text-sm text-ycr-steel mb-2">{pub_date}</div>
      <h2 class="font-heading font-bold text-xl text-ycr-blue mb-2">
        <a href="/blog/{slug}.html" class="hover:underline">{title_esc}</a>
      </h2>
      <p class="text-ycr-steel text-sm leading-relaxed">{desc_esc}</p>
      <a href="/blog/{slug}.html" class="mt-4 inline-block text-ycr-signal font-semibold text-sm hover:underline">Read more &rarr;</a>
    </article>"""


# ── Helper: inject card into blog/index.html ──────────────────────────────
def update_blog_index(card_html: str) -> None:
    content = BLOG_INDEX.read_text(encoding="utf-8")

    # Remove the "coming soon" placeholder block if still present
    # Match from the outer div opening to the line containing "Articles coming soon"
    # and everything up to the next </div> after it
    content = re.sub(
        r"\s*<div[^>]*text-center py-16[^>]*>.*?Articles coming soon.*?</p>\s*</div>\s*",
        "\n",
        content,
        flags=re.DOTALL,
    )
    # Also strip any orphaned "coming soon" paragraphs left over from partial removal
    content = re.sub(
        r"\s*<p[^>]*>Articles coming soon</p>\s*<p[^>]*>.*?</p>\s*</div>\s*",
        "\n",
        content,
        flags=re.DOTALL,
    )

    # Insert card after BEGIN_POSTS marker
    marker = "<!-- BEGIN_POSTS -->"
    if marker not in content:
        log.warning("BEGIN_POSTS marker not found in blog/index.html — skipping index update")
        return

    content = content.replace(marker, marker + "\n" + card_html, 1)
    BLOG_INDEX.write_text(content, encoding="utf-8")
    log.info("Updated blog/index.html with new post card")


# ── Helper: log result ─────────────────────────────────────────────────────
def log_result(row: dict) -> None:
    is_new = not CONTENT_LOG.exists()
    with open(CONTENT_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)


# ── Main ───────────────────────────────────────────────────────────────────
def main(dry_run: bool = False) -> int:
    log.info("=== York Computer Repair Content Engine ===")
    today = date.today().isoformat()

    # 1. Pick keyword
    published = load_published_keywords()
    log.info("Already published: %d keywords", len(published))
    candidate = pick_keyword(published)
    if not candidate:
        log.info("No unpublished keywords remaining — nothing to do.")
        return 0

    keyword = candidate["keyword"]
    cluster = candidate.get("cluster", "Other")
    vol     = candidate.get("avg_monthly_searches", "?")
    log.info("Selected keyword: '%s' (cluster: %s, vol: %s)", keyword, cluster, vol)

    # 2. Generate post via Claude API
    from generate_post import generate_post  # local import
    log.info("Calling Claude API to generate post...")
    try:
        post = generate_post(keyword, cluster)
    except Exception as e:
        log.error("Claude API failed: %s", e)
        log_result({"date": today, "keyword": keyword, "cluster": cluster,
                    "slug": "", "filename": "", "url": "", "status": "failed", "error": str(e)})
        return 1

    slug     = post["slug"]
    filename = f"{slug}.html"
    filepath = BLOG_DIR / filename
    url      = f"https://yorkcomputerrepair.com/blog/{filename}"
    log.info("Post slug: %s | File: %s", slug, filename)

    # 3. Build and save HTML
    post_html = build_post_html(post, today)
    if dry_run:
        log.info("[DRY RUN] Would write: %s", filepath)
        log.info("[DRY RUN] Post title: %s", post.get("title"))
        return 0

    filepath.write_text(post_html, encoding="utf-8")
    log.info("Saved: %s", filepath)

    # 4. Update blog index
    card = build_listing_card(post, today)
    update_blog_index(card)

    # 5. Git push
    from publish_post import git_push
    commit_msg = f"SEO: add post '{post.get('h1', keyword)}' ({today})"
    ok = git_push(commit_msg)
    if not ok:
        log.error("Git push failed — post saved locally but not deployed")
        log_result({"date": today, "keyword": keyword, "cluster": cluster,
                    "slug": slug, "filename": filename, "url": url,
                    "status": "push_failed", "error": "git push returned non-zero"})
        return 1

    # 6. Log success
    log_result({"date": today, "keyword": keyword, "cluster": cluster,
                "slug": slug, "filename": filename, "url": url,
                "status": "published", "error": ""})
    log.info("=== Done — post live at %s ===", url)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="York Computer Repair SEO content engine")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate post locally without saving, pushing, or logging")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))

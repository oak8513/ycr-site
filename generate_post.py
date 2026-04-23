"""
generate_post.py — York Computer Repair blog post generator.

Uses Claude API with prompt caching (system prompt) to write SEO-optimized
800–1200 word blog posts targeting identified keyword gaps.

Posts are generated as Jekyll-ready HTML files with front matter.
They are written to _posts/YYYY-MM-DD-{slug}.html and served by Jekyll
at /blog/{slug}.html — no manual blog/index.html update needed.

Usage:
    python generate_post.py "laptop screen repair york pa" "Screen & Hardware"
"""
import os
import json
import re
import sys
from datetime import date
import anthropic

# ── Brand / site context (cached as system prompt) ───────────────────────────
SITE_CONTEXT = """You are the content writer for York Computer Repair, a local walk-in computer repair shop in York, Pennsylvania.

Business facts (use exactly as written):
- Business name: York Computer Repair
- Address: 2069 Carlisle Rd, York, PA 17408
- Phone: 717-739-9675
- Email: help@yorkcomputerrepair.com
- Hours: Mon–Fri 9AM–5PM only. Closed Saturday and Sunday.
- Services: laptop repair, desktop repair, gaming PC repair, custom PC builds, virus & malware removal, data recovery, screen replacement, SSD/RAM upgrades
- We service Windows PCs only: HP, Dell, Lenovo, ASUS, Acer, Sony VAIO, Gateway, and custom/gaming builds
- We do NOT service Apple / Mac computers, iPhones, iPads, Android phones, tablets, or Microsoft Surface devices — never mention these as services we offer
- Walk-ins always welcome
- We charge a diagnostic fee (never say "free diagnostics")
- Do NOT mention any specific dollar amounts or prices in articles — prices change and articles must stay evergreen

Voice & tone:
- Approachable — the reader's laptop just died and they're stressed
- Plain English — no jargon, explain what's wrong and how we can help
- Reassuring — "we've seen this before, here's how we fix it"
- Local York PA angle — mention York, PA, York County, the local community
- Honest — tell readers when they can DIY vs. when to bring it in for professional repair
- Fast and direct — get to the point, don't pad word count with filler

Internal page slugs you may reference naturally in the text:
- Services: /services.html
- Contact & directions: /contact.html
- About us: /about.html"""


def _get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    # Fallback: .secrets/anthropic.txt (one line: the key)
    secrets = os.path.join(os.path.dirname(__file__), "..", "..", ".secrets", "anthropic.txt")
    if os.path.exists(secrets):
        return open(secrets).read().strip()
    # Fallback: .secrets/anthropic.json {"api_key": "..."}
    secrets_json = secrets.replace(".txt", ".json")
    if os.path.exists(secrets_json):
        data = json.load(open(secrets_json))
        return data.get("api_key") or data.get("ANTHROPIC_API_KEY", "")
    raise ValueError(
        "ANTHROPIC_API_KEY not found. Set the env var or create "
        "C:\\Users\\Owner\\Documents\\Claude\\.secrets\\anthropic.txt"
    )


def keyword_to_slug(keyword: str) -> str:
    slug = keyword.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:60]


def generate_post(keyword: str, cluster: str) -> dict:
    """
    Call Claude API and return structured blog post data.

    Returns dict with keys:
        title, meta_description, slug, h1, intro,
        sections (list of {h2, content}), conclusion, cta_text
    """
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    kwargs = {"api_key": _get_api_key()}
    if base_url:
        kwargs["base_url"] = base_url
    client = anthropic.Anthropic(**kwargs)

    user_prompt = f"""Write an SEO blog post targeting this keyword: "{keyword}"
Topic cluster: {cluster}

Requirements:
- Total length: 800–1,200 words across all fields combined
- Include "{keyword}" in the title, H1, and at least 2 of the H2 headings
- Include a York, PA local angle (mention York, PA residents, York County, etc.)
- Reference our service page (/services.html) or contact page (/contact.html) naturally at least once
- End with a call to action to call 717-739-9675 or visit 2069 Carlisle Rd, York, PA
- Practical, genuinely helpful — not a sales pitch
- No filler phrases like "in today's world" or "it's important to note"
- Never mention specific prices, dollar amounts, or fees — articles must be evergreen
- Generate content-only HTML body (no DOCTYPE, no <html>, no <head>, no <nav>, no <footer>)
- The output will be wrapped in a Jekyll layout that provides the full page shell

Return ONLY valid JSON (no markdown fences, no extra text):
{{
  "title": "Page <title> tag — 50-60 chars, includes keyword",
  "meta_description": "Meta description — 150-160 chars, includes keyword + York PA",
  "slug": "url-friendly-slug",
  "h1": "H1 heading shown to reader",
  "intro": "Opening 2-3 sentence paragraph",
  "sections": [
    {{"h2": "H2 heading", "content": "Body paragraphs as plain text. Separate paragraphs with a blank line."}},
    {{"h2": "H2 heading", "content": "..."}},
    {{"h2": "H2 heading", "content": "..."}}
  ],
  "conclusion": "1-2 sentence closing paragraph",
  "cta_text": "Single CTA sentence (do not include phone/address — those are added by the template)"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        system=[
            {
                "type": "text",
                "text": SITE_CONTEXT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences in case the model wraps anyway
    if "```" in raw:
        raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()

    # Find the outermost JSON object (handles leading/trailing prose)
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: json_repair handles bare newlines inside strings,
        # smart quotes, trailing commas, etc.
        try:
            import json_repair
            data = json_repair.loads(raw)
        except Exception:
            # Last resort: sanitise smart-quotes then retry
            raw_clean = (raw
                         .replace("\u2018", "'").replace("\u2019", "'")
                         .replace("\u201c", '"').replace("\u201d", '"')
                         .replace("\u2013", "-").replace("\u2014", "-"))
            data = json.loads(raw_clean)

    # Normalise slug
    slug = data.get("slug") or keyword_to_slug(keyword)
    data["slug"] = keyword_to_slug(slug)

    return data


def render_jekyll_post(data: dict, post_date: str) -> str:
    """
    Render a Jekyll-compatible HTML file with front matter.
    Content only — no DOCTYPE/html/head/nav/footer (provided by _layouts/default.html).
    """
    slug = data["slug"]
    canonical = f"https://yorkcomputerrepair.com/blog/{slug}.html"

    front_matter = f"""---
layout: default
title: "{data['title']}"
description: "{data['meta_description']}"
canonical: "{canonical}"
permalink: /blog/{slug}.html
og_type: article
og_title: "{data['title']}"
og_description: "{data['meta_description']}"
date: {post_date}
excerpt: "{data['intro'][:160]}"
---"""

    # Build article body
    paragraphs = []
    for para in data["intro"].split("\n\n"):
        para = para.strip()
        if para:
            paragraphs.append(f'      <p class="text-ycr-steel leading-relaxed mb-5">{para}</p>')

    sections_html = []
    for section in data.get("sections", []):
        h2 = section.get("h2", "")
        content = section.get("content", "")
        section_parts = [f'      <h2 class="font-heading font-bold text-2xl text-ycr-blue mt-10 mb-4">{h2}</h2>']
        for para in content.split("\n\n"):
            para = para.strip()
            if para:
                section_parts.append(f'      <p class="text-ycr-steel leading-relaxed mb-5">{para}</p>')
        sections_html.append("\n".join(section_parts))

    conclusion_paras = []
    for para in data.get("conclusion", "").split("\n\n"):
        para = para.strip()
        if para:
            conclusion_paras.append(f'      <p class="text-ycr-steel leading-relaxed mb-5">{para}</p>')

    cta_text = data.get("cta_text", "Stop by our shop or give us a call to get your computer running again.")

    body = f"""
  <div class="max-w-3xl mx-auto px-4 py-12">

    <!-- Breadcrumb -->
    <nav class="text-sm text-ycr-steel mb-6">
      <a href="/" class="hover:text-ycr-signal">Home</a>
      <span class="mx-2">&rsaquo;</span>
      <a href="/blog/" class="hover:text-ycr-signal">Blog</a>
      <span class="mx-2">&rsaquo;</span>
      <span class="text-ycr-black">{data['h1']}</span>
    </nav>

    <!-- Article header -->
    <header class="mb-8">
      <h1 class="font-heading font-bold text-3xl md:text-4xl text-ycr-black leading-tight mb-4">{data['h1']}</h1>
      <div class="flex items-center gap-4 text-sm text-ycr-steel">
        <span>York Computer Repair</span>
        <span>&bull;</span>
        <time datetime="{post_date}">{post_date}</time>
        <span>&bull;</span>
        <span>5 min read</span>
      </div>
    </header>

    <!-- Article body -->
    <article class="prose max-w-none">
{chr(10).join(paragraphs)}

{chr(10).join(chr(10).join(s) for s in [s.split(chr(10)) for s in sections_html])}

{chr(10).join(conclusion_paras)}
    </article>

    <!-- CTA Box -->
    <div class="mt-10 bg-ycr-blue text-white rounded-xl p-8 text-center">
      <p class="font-heading font-semibold text-lg mb-4">{cta_text}</p>
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

  </div>"""

    return front_matter + "\n" + body + "\n"


def save_post(data: dict, site_dir: str = None) -> str:
    """
    Save rendered post to _posts/YYYY-MM-DD-{slug}.html.
    Returns the path of the written file.
    """
    if site_dir is None:
        site_dir = os.path.dirname(os.path.abspath(__file__))

    post_date = date.today().isoformat()
    slug = data["slug"]
    filename = f"{post_date}-{slug}.html"
    posts_dir = os.path.join(site_dir, "_posts")
    os.makedirs(posts_dir, exist_ok=True)
    filepath = os.path.join(posts_dir, filename)

    content = render_jekyll_post(data, post_date)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


# ── CLI quick-test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "laptop screen repair york pa"
    cl = sys.argv[2] if len(sys.argv) > 2 else "Screen & Hardware"
    result = generate_post(kw, cl)
    filepath = save_post(result)
    print(f"[generate_post] Saved: {filepath}")
    print(json.dumps(result, indent=2))

"""
generate_post.py — York Computer Repair blog post generator.

Uses Claude API with prompt caching (system prompt) to write SEO-optimized
800–1200 word blog posts targeting identified keyword gaps.

Usage:
    python generate_post.py "laptop screen repair york pa" "Screen & Hardware"
"""
import os
import json
import re
import sys
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
- Walk-ins always welcome
- Diagnostic fee: $39.99 for standard computers, $99 for gaming PCs (fee applied toward repair if customer proceeds)
- Never say "free diagnostics" — we charge a diagnostic fee

Voice & tone:
- Approachable — the reader's laptop just died and they're stressed
- Plain English — no jargon, explain what's wrong and what it costs
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


# ── CLI quick-test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "laptop screen repair york pa"
    cl = sys.argv[2] if len(sys.argv) > 2 else "Screen & Hardware"
    result = generate_post(kw, cl)
    print(json.dumps(result, indent=2))

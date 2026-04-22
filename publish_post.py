"""
publish_post.py — Git commit and push for York Computer Repair site.

Stages all changes in the ycr-site repo, commits, and pushes to GitHub Pages.
GitHub Pages auto-deploys within ~30 seconds of push.

Posts are now Jekyll-based: written to _posts/YYYY-MM-DD-{slug}.html
and auto-listed by Jekyll via site.posts — no blog/index.html update needed.

Usage:
    python publish_post.py "SEO: add post on laptop screen repair"
    python publish_post.py          # uses default message
"""
import subprocess
import sys
from pathlib import Path

SITE_DIR = Path(__file__).parent
REMOTE = "origin"
BRANCH = "main"


def git_push(commit_message: str = "SEO: auto-publish blog post") -> bool:
    """
    Stage all changes, commit, push.
    Returns True on success, False on any git error.
    """
    def run(cmd, **kwargs):
        return subprocess.run(
            cmd, cwd=SITE_DIR,
            capture_output=True, text=True,
            **kwargs
        )

    # Stage everything
    r = run(["git", "add", "-A"])
    if r.returncode != 0:
        print(f"[git add] Error: {r.stderr.strip()}", file=sys.stderr)
        return False

    # Check if there's actually anything staged
    status = run(["git", "status", "--porcelain"])
    if not status.stdout.strip():
        print("[publish] Nothing new to commit — site already up to date.")
        return True

    # Commit
    r = run(["git", "commit", "-m", commit_message])
    if r.returncode != 0:
        print(f"[git commit] Error: {r.stderr.strip()}", file=sys.stderr)
        return False
    print(f"[git commit] {r.stdout.strip()}")

    # Push
    r = run(["git", "push", REMOTE, BRANCH])
    if r.returncode != 0:
        print(f"[git push] Error: {r.stderr.strip()}", file=sys.stderr)
        return False
    print(f"[git push] Pushed to {REMOTE}/{BRANCH} — GitHub Pages will deploy in ~30s")
    return True


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "SEO: auto-publish blog post"
    ok = git_push(msg)
    sys.exit(0 if ok else 1)

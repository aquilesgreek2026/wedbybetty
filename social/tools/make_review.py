"""Build social/out/<week>/REVIEW.md from social/calendar/<week>.json.
Run from repo root:  python social/tools/make_review.py 2026-W48"""
import json
import sys

wk = sys.argv[1]
cal = json.load(open(f"social/calendar/{wk}.json", encoding="utf-8"))
o = [
    f"# Review sheet — {wk}  (posts at Pacific Time)\n",
    "Reply per post: **APPROVE**, **CHANGE: <what>**, or **REJECT**. Nothing is scheduled until a post is approved.\n",
]
for n, p in enumerate(cal["posts"], 1):
    o += [
        f"\n---\n\n## Post {n} · {p['day']} {p['time']} · {p['pillar']}  — status: `{p['status']}`\n",
        f"![post {n}]({p['image'].split('/')[-1]})\n",
        f"**Goal:** {p['goal']}  \n**Format:** {p['format']}  \n**Image source:** {p['image_source']}  \n**Consent/notes:** {p['image_notes']}\n",
        "**Caption (Spanish first, then English):**\n",
        "```\n" + p["caption"] + "\n```\n",
        "**Facebook only, add at the end:** `" + p.get("facebook_suffix", "").strip() + "`\n",
        f"**Alt text ES:** {p['alt_es']}  \n**Alt text EN:** {p['alt_en']}\n",
        "**Facts used:** " + "; ".join(p["facts_used"]) + "\n",
    ]
    if p.get("flags"):
        o.append("**⚠️ Flags for the approver:** " + " ".join(p["flags"]) + "\n")
open(f"social/out/{wk}/REVIEW.md", "w", encoding="utf-8").write("\n".join(o))
print("wrote REVIEW.md")

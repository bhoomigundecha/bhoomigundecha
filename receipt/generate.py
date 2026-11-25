#!/usr/bin/env python3
"""Prints Bhoomi's profile receipt (receipt.svg) with live GitHub numbers.

Run locally:   python3 receipt/generate.py
In Actions:    GITHUB_TOKEN is used for contribution counts (GraphQL).
No third-party dependencies.
"""
import datetime as dt
import hashlib
import json
import os
import urllib.request
from collections import Counter
from html import escape

USER = "bhoomigundecha"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "receipt.svg")
TOKEN = os.environ.get("GITHUB_TOKEN")

# ── layout ────────────────────────────────────────────────────────────────
COLS = 40            # characters per receipt line
FS = 14              # font size
CW = FS * 0.6        # monospace char width
LH = 21              # line height
PAD = 28
PAPER_W = int(COLS * CW + PAD * 2)
W = PAPER_W + 60     # canvas incl. printer overhang
PX = (W - PAPER_W) // 2
INK = "#2a2722"
FADED = "#8a857b"
PAPER = "#fbf9f3"


# ── data ──────────────────────────────────────────────────────────────────
def api(url, body=None):
    headers = {"User-Agent": "profile-receipt", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def ago(iso, now):
    d = (now - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    return "today" if d == 0 else "1 day ago" if d == 1 else f"{d} days ago"


def stats():
    now = dt.datetime.now(dt.timezone.utc)
    s = {"repos": None, "lang": None, "latest": None, "latest_ago": None, "contrib": None}
    try:
        repos = [r for r in api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
                 if not r["fork"] and r["name"] != USER]
        s["repos"] = len(repos)
        langs = Counter(r["language"] for r in repos if r["language"])
        s["lang"] = langs.most_common(1)[0][0] if langs else None
        if repos:
            s["latest"], s["latest_ago"] = repos[0]["name"], ago(repos[0]["pushed_at"], now)
    except Exception as e:  # offline / rate limited: print without live numbers
        print("repo stats skipped:", e)
    if TOKEN:
        try:
            q = {"query": f'{{user(login:"{USER}"){{contributionsCollection{{contributionCalendar{{totalContributions}}}}}}}}'}
            r = api("https://api.github.com/graphql", q)
            s["contrib"] = r["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        except Exception as e:
            print("contributions skipped:", e)
    return s


# ── receipt lines ─────────────────────────────────────────────────────────
# Each line: (kind, payload). kinds: center, lr, text, rule, gap, title, barcode
def lr(left, right, fill="."):
    room = COLS - len(left) - len(right) - 2
    return ("lr", (left, right, fill * max(room, 1)))


def build(s):
    ist = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    L = [
        ("gap", 1),
        ("title", "BHOOMI & CO."),
        ("center", "AI . BACKEND . SHIPPING DEPT."),
        ("center", "IIIT Pune, Maharashtra"),
        ("faint", "est. 2023 . open 24/7 . no refunds"),
        ("rule", "="),
        ("lr2", (f"RECEIPT #{ist:%Y%m%d}", ist.strftime("%d %b %Y %H:%M"))),
        ("lr2", ("CASHIER: bhoomi", "TERMINAL: 01")),
        ("rule", "-"),
        ("lr2", ("ITEM", "STATUS")),
        ("rule", "-"),
        lr("AI Engineer", "IN STOCK"),
        lr("Backend Developer", "IN STOCK"),
        lr("AI Internship '26", "ACTIVE"),
        lr("Smart India Hackathon '24", "WON"),
        ("gap", 0.5),
        ("head", "-- PROJECTS --"),
        lr("Jugaad", "LIVE"),
        ("note", "voice AI that haggles in 13 languages"),
        lr("PayCore", "SHIPPED"),
        ("note", "payments that never double-charge"),
        lr("FaultLens", "SHIPPED"),
        ("note", "root cause straight from telemetry"),
        lr("FlowPilot", "BREWING"),
        ("note", "multi-agent enterprise copilot"),
        ("gap", 0.5),
        ("head", "-- STACK (bulk) --"),
        ("text", "JS  TS  PYTHON  C++  JAVA"),
        ("text", "NEXT.JS  REACT  TAILWIND  FIGMA"),
        ("text", "NODE  EXPRESS  FASTAPI  SPRING"),
        ("text", "POSTGRES  MONGO  REDIS  KAFKA"),
        ("text", "LANGCHAIN  GROQ  GEMINI  OPENAI"),
        ("text", "DOCKER  AWS  GCP  LINUX"),
        ("gap", 0.5),
        ("head", "-- RECURRING CHARGES --"),
        lr("Coffee", "ALWAYS"),
        lr("LeetCode", "too much"),
        lr("Overthinking", "included"),
        lr("Seedhe Maut", "on repeat"),
    ]
    live = []
    if s["repos"] is not None:
        live.append(lr("Public repos", str(s["repos"])))
    if s["contrib"] is not None:
        live.append(lr(f"Contributions ({ist.year})", str(s["contrib"])))
    if s["lang"]:
        live.append(lr("Most used language", s["lang"]))
    if s["latest"]:
        live.append(lr("Last push", s["latest"]))
        live.append(("note", s["latest_ago"]))
    if live:
        L += [("gap", 0.5), ("head", "-- TODAY'S ACTIVITY --"), *live]
    L += [
        ("rule", "-"),
        lr("SUBTOTAL", "many ideas", " "),
        lr("DISCOUNT", "-100% planning", " "),
        ("rule", "-"),
        ("total", ("TOTAL", "SHIPPED")),
        ("rule", "="),
        lr("PAID WITH", "caffeine+adrenaline", " "),
        lr("CHANGE", "users > stars", " "),
        ("gap", 0.6),
        ("barcode", f"{USER}{ist:%Y%m%d}"),
        ("faint", f"*{USER.upper()}*"),
        ("gap", 0.5),
        ("center", "THANK YOU FOR VISITING"),
        ("faint", "keep this receipt for your records"),
        ("faint", "reprinted daily by github actions"),
        ("gap", 1.4),
    ]
    return L


# ── svg ───────────────────────────────────────────────────────────────────
def t(x, y, s, anchor="start", size=FS, weight="normal", fill=INK, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def barcode(seed, x0, y, width, height):
    h = hashlib.sha256(seed.encode()).digest() * 4
    bars, x, i = [], x0, 0
    while x < x0 + width - 4:
        w = 1 + h[i] % 3
        if i % 2 == 0:
            bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{height}" fill="{INK}"/>')
        x += w + (h[i + 1] % 2)
        i += 1
    return "".join(bars)


def render(lines):
    left, right, mid = PX + PAD, PX + PAPER_W - PAD, W / 2
    full = COLS * CW
    y = 52  # first baseline (below printer slot)
    out = []
    for kind, p in lines:
        if kind == "gap":
            y += LH * p
            continue
        if kind == "title":
            y += 8
            out.append(t(mid, y, p, "middle", 26, "bold", extra='letter-spacing="3"'))
            y += 8
        elif kind == "center":
            out.append(t(mid, y, p, "middle"))
        elif kind == "faint":
            out.append(t(mid, y, p, "middle", 12, fill=FADED))
        elif kind == "head":
            out.append(t(mid, y, p, "middle", weight="bold"))
        elif kind == "text":
            out.append(t(mid, y, p, "middle"))
        elif kind == "note":
            out.append(t(left + CW * 2, y - 3, p, size=12, fill=FADED, extra='font-style="italic"'))
        elif kind == "rule":
            out.append(t(left, y, p * COLS, extra=f'textLength="{full:.0f}" lengthAdjust="spacing" fill-opacity=".55"'))
        elif kind in ("lr", "lr2"):
            if kind == "lr":
                a, b, dots = p
            else:
                a, b = p
                dots = ""
            out.append(t(left, y, a))
            out.append(t(right, y, b, "end", weight="bold" if kind == "lr" else "normal"))
            if dots.strip():
                x1 = left + (len(a) + 1) * CW
                x2 = right - (len(b) + 1) * CW
                out.append(f'<line x1="{x1:.1f}" y1="{y-3:.1f}" x2="{x2:.1f}" y2="{y-3:.1f}" '
                           f'stroke="{FADED}" stroke-width="1.4" stroke-dasharray="1.4 4.2" stroke-linecap="round"/>')
        elif kind == "total":
            y += 6
            out.append(t(left, y, p[0], size=22, weight="bold"))
            out.append(t(right, y, p[1] + " ✓", "end", 22, "bold"))
            y += 6
        elif kind == "barcode":
            bw = PAPER_W * 0.62
            out.append(barcode(p, mid - bw / 2, y - 14, bw, 46))
            y += 38
        y += LH

    paper_h = y
    H = paper_h + 40
    # torn bottom edge
    teeth, tw = [], 10
    n = int(PAPER_W / tw)
    for i in range(n + 1):
        teeth.append(f"{PX + i * tw:.1f},{paper_h + (6 if i % 2 else 0):.1f}")
    paper_path = (f"M{PX},22 L{PX + PAPER_W},22 L{PX + PAPER_W},{paper_h} "
                  + " ".join("L" + p for p in reversed(teeth)) + " Z")

    feed = 3.2  # seconds
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Bhoomi Gundecha: profile receipt">
<style>
  text {{ font-family: "Courier New", Courier, ui-monospace, monospace; }}
  .feed {{ animation: feed {feed}s steps(36, end) .3s both; }}
  .head {{ animation: jitter .12s linear .3s {int(feed/.12)}; }}
  @keyframes feed {{ from {{ transform: translateY(-{paper_h - 20}px); }} to {{ transform: translateY(0); }} }}
  @keyframes jitter {{ 50% {{ transform: translateY(.6px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .feed, .head {{ animation: none; }} }}
</style>
<defs>
  <filter id="shadow" x="-10%" y="-2%" width="120%" height="104%">
    <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" flood-opacity=".28"/>
  </filter>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/>
    <feColorMatrix values="0 0 0 0 .4  0 0 0 0 .35  0 0 0 0 .3  0 0 0 .06 0"/></filter>
  <clipPath id="slot"><rect x="0" y="20" width="{W}" height="{H}"/></clipPath>
  <clipPath id="paperclip"><path d="{paper_path}"/></clipPath>
</defs>
<g clip-path="url(#slot)">
  <g class="feed">
    <path d="{paper_path}" fill="{PAPER}" filter="url(#shadow)"/>
    <rect x="{PX}" y="20" width="{PAPER_W}" height="{paper_h}" filter="url(#grain)" clip-path="url(#paperclip)"/>
    {"".join(out)}
  </g>
</g>
<g class="head">
  <rect x="6" y="4" width="{W - 12}" height="24" rx="12" fill="#1c1f24"/>
  <rect x="{PX - 6}" y="16" width="{PAPER_W + 12}" height="6" rx="3" fill="#000"/>
  <circle cx="24" cy="16" r="3.5" fill="#3fb950"/>
</g>
</svg>
'''


if __name__ == "__main__":
    svg = render(build(stats()))
    with open(OUT, "w") as f:
        f.write(svg)
    print("printed", os.path.normpath(OUT))

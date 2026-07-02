#!/usr/bin/env python3
"""Generate a themed WakaTime "weekly coding activity" SVG card from the
WakaTime API. Self-contained (stdlib only) so it renders reliably on GitHub
and updates daily via GitHub Actions. Requires env WAKATIME_API_KEY."""
from __future__ import annotations

import base64
import json
import os
import urllib.request

API = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
OUT = "assets/wakatime.svg"

# Palette (tokyonight-ish, matches the profile theme)
BG = "#0d1117"
BORDER = "rgba(255,255,255,0.08)"
TITLE = "#818cf8"
SUB = "#6b7280"
NAME = "#c9d1d9"
TIME = "#6b7280"
PCT = "#a5b4fc"
TRACK = "rgba(255,255,255,0.06)"
GRAD_A = "#818cf8"
GRAD_B = "#6366f1"

# Languages we don't want to surface on a portfolio card
SKIP = {"Other", "Text"}
MAX_ROWS = 6

W = 500
PAD = 24
ROW_H = 38
BAR_X = 150
BAR_W = 250
HEAD = 58


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def short_time(h: int, m: int) -> str:
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def fetch():
    key = os.environ["WAKATIME_API_KEY"]
    b64 = base64.b64encode(key.encode()).decode()
    req = urllib.request.Request(API, headers={"Authorization": f"Basic {b64}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def build_svg(data) -> str:
    total = data.get("human_readable_total", "")
    langs = [l for l in data.get("languages", []) if l.get("name") not in SKIP]
    langs = [l for l in langs if l.get("percent", 0) >= 0.5][:MAX_ROWS]

    rows = []
    for i, l in enumerate(langs):
        y = HEAD + i * ROW_H
        pct = l["percent"]
        fill_w = max(4, round(BAR_W * pct / 100))
        name = esc(l["name"])
        t = short_time(int(l.get("hours", 0)), int(l.get("minutes", 0)))
        rows.append(f'''
    <g transform="translate(0 {y})" opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{0.15 + i*0.12}s" dur="0.5s" fill="freeze"/>
      <text x="{PAD}" y="14" fill="{NAME}" font-size="13" font-weight="600">{name}</text>
      <text x="{PAD}" y="28" fill="{TIME}" font-size="10">{t}</text>
      <rect x="{BAR_X}" y="6" width="{BAR_W}" height="9" rx="4.5" fill="{TRACK}"/>
      <rect x="{BAR_X}" y="6" width="0" height="9" rx="4.5" fill="url(#g)">
        <animate attributeName="width" from="0" to="{fill_w}" begin="{0.2 + i*0.12}s" dur="0.8s" fill="freeze"
                 calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>
      </rect>
      <text x="{W-PAD}" y="15" fill="{PCT}" font-size="12" text-anchor="end">{pct:.1f}%</text>
    </g>''')

    h = HEAD + len(langs) * ROW_H + 14
    body = "".join(rows)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" fill="none" font-family="'Segoe UI',Helvetica,Arial,sans-serif">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{GRAD_A}"/>
      <stop offset="1" stop-color="{GRAD_B}"/>
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
  <text x="{PAD}" y="34" fill="{TITLE}" font-size="15" font-weight="700">Weekly Coding Activity</text>
  <text x="{W-PAD}" y="34" fill="{SUB}" font-size="11" text-anchor="end">Last 7 days &#183; {esc(total)}</text>
  {body}
</svg>
'''


def main():
    data = fetch()
    os.makedirs("assets", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build_svg(data))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

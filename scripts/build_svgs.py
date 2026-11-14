#!/usr/bin/env python3
"""Generate the README SVGs in the leonardolopes.tech 2.0 language:
"Light Means Production". Neon on midnight, one light source per screen,
Geist for words, Geist Mono for figures.

Usage: python3 scripts/build_svgs.py

Content mirrors ~/www/leonardolopes.tech/src/utils/mock.ts (EXPERIENCES,
HOME_HERO, OUTCOMES, STACK_GROUPS, CONTACT_LINKS). Visual rules come from
that repo's DESIGN.md. The career length and ruler are computed from
today's date, so the daily workflow re-runs this script.

GitHub renders README SVGs inside <img>: no external requests, so the
portrait and signature (assets/source/brand/) are inlined. Animations are
CSS, gated on prefers-reduced-motion; the static state is the final frame.
"""

import datetime as dt
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "source" / "brand"
OUT = ROOT / "assets"

# ---------------------------------------------------------------- tokens
# leonardolopes.tech globals.css @theme + .dark (oklch converted to hex)
MIDNIGHT = "#030407"
BACKGROUND = "#030407"   # oklch(0.107 0.011 266.5)
CARD = "#0a0e18"         # oklch(0.165 0.022 267.2)
FG = "#e8eef9"           # oklch(0.948 0.016 262.8)
MUTED = "#8c98b0"        # oklch(0.678 0.038 264.3)
COBALT = "#1558c9"
NEON = "#2f6bff"
NEON_SOFT = "#7aa6ff"

SANS = "Geist, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
EASE = "cubic-bezier(0.16, 1, 0.3, 1)"  # house easing

W = 1200
GUTTER = 64
CYCLE = 14  # seconds; every intro replays on this loop

TODAY = dt.date.today()

# ------------------------------------------------------------------ content
# Mirrors src/utils/mock.ts in the portfolio. Keep the two in sync.

CAREER_START = dt.date(2020, 6, 1)

HERO = {
    "name": "Leonardo Lopes",
    "role": "Tech Lead · Software Engineer & Architect",
    "current": "Tech Lead at Buildbox, leading Horizontes, the Callink super app",
    "availability": "Open to full-time, contract and freelance · Remote from Brazil (UTC−3) or relocation",
}

# The featured outcome (isFeatured): the cost slab under the hero. No beam.
SLAB = {
    "client": "Linda Lifetech",
    "metric": "−38%",
    "ratio": 0.62,
    "caption": "Monthly cloud bill of the Linda Lifetech platform, from about USD 2,100 to about USD 1,300, after a zero-downtime move from AWS to GCP.",
}

# OUTCOMES minus the current (Callink) and featured (Linda) ones, like the home.
LEDGER = [
    ("−80%", "worst-case app load time", "2023 – 2024",
     "Took the worst-case load of the field-sales app behind about 97% of Grupo Petrópolis’ USD 4B yearly revenue from 8 minutes to 1 min 37 s.",
     ["React", "React Native", "Node.js"], "Grupo Petrópolis", "Software Engineer at Buildbox"),
    ("27", "Brazilian states, one pricing platform", "2024 – 2025",
     "National pricing platform with regional tax rules for Lactalis, the largest dairy group in the world.",
     ["Node.js", "TypeScript"], "Lactalis Group", "Software Engineer at Buildbox"),
    ("0.5×", "the estimated delivery time", "2022 – 2023",
     "Shipped the internal web and mobile gamification platform for MSD Brazil with near-zero production defects.",
     [], "MSD", "Software Engineer at Buildbox"),
    ("580+", "teaching units served", "2021 – 2022",
     "Go service that turns MP4 uploads into adaptive HLS streams for Poliedro, built for peak load.",
     ["Go", "HLS"], "Poliedro", "Software Engineer at Nkey"),
]

# EXPERIENCES as career lanes: (label, start, end or None, [(engagement, start, end or None)])
LANES = [
    ("Buildbox", dt.date(2022, 5, 1), None, [
        ("MSD", dt.date(2022, 5, 1), dt.date(2023, 5, 1)),
        ("Grupo Petrópolis", dt.date(2023, 5, 1), dt.date(2024, 11, 1)),
        ("Lactalis Group", dt.date(2024, 11, 1), dt.date(2025, 8, 1)),
        ("Linda Lifetech", dt.date(2025, 8, 1), dt.date(2026, 8, 1)),
        ("Callink", dt.date(2026, 8, 1), None),
    ]),
    ("Nkey", dt.date(2021, 8, 1), dt.date(2022, 4, 30), [
        ("Poliedro Educação", dt.date(2021, 8, 1), dt.date(2022, 4, 30)),
    ]),
    ("Freelance", dt.date(2020, 6, 1), dt.date(2021, 7, 31), []),
]

STACK_GROUPS = [
    ("Interfaces", ["React", "Next.js", "React Native", "Expo", "Tailwind CSS", "Storybook"]),
    ("Services", ["TypeScript", "Node.js", "Go", "NestJS", "GraphQL", "Fastify"]),
    ("Data and messaging", ["PostgreSQL", "MongoDB", "Redis", "Apache Kafka", "Prisma", "MySQL"]),
    ("Cloud and infrastructure", ["AWS", "Google Cloud", "Azure", "Terraform", "Kubernetes", "OpenTelemetry"]),
]

CONTACT_ROWS = [
    ("mail", "Email", "leonardolopesdeveloper@gmail.com"),
    ("calendar", "Schedule a call", ""),
    ("message", "WhatsApp", ""),
    ("linkedin", "LinkedIn", ""),
    ("github", "GitHub", ""),
]

CLOSING_LINE = "Send the role or the project."

NUMBER_WORDS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve"]

# lucide icons (24x24, stroke)
LUCIDE = {
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "message": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "github": '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
    "arrow-up-right": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
}


# ------------------------------------------------------------------ helpers

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def years_between(a: dt.date, b: dt.date) -> int:
    return b.year - a.year - ((b.month, b.day) < (a.month, a.day))


def career_words() -> str:
    n = years_between(CAREER_START, TODAY)
    return NUMBER_WORDS[n] if n < len(NUMBER_WORDS) else str(n)


def fmt_month(d: dt.date | None) -> str:
    return "Present" if d is None else d.strftime("%b %Y")


def wrap(text: str, max_px: float, size: float, ratio: float = 0.5) -> list[str]:
    max_chars = max(1, int(max_px / (size * ratio)))
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > max_chars and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def lucide(name: str, x: float, y: float, size: float, color: str, sw: float = 2) -> str:
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({size / 24:.3f})" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{LUCIDE[name]}</g>'
    )


def brand_vector(name: str) -> tuple[str, str]:
    """(viewBox, inner markup) of a single-colour brand SVG."""
    raw = (BRAND / f"{name}.svg").read_text()
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", raw, flags=re.S)
    return vb, inner


def text(x, y, s, size, color=FG, weight=400, family=SANS, anchor="start", tracking=None, extra="") -> str:
    ls = f' letter-spacing="{tracking}"' if tracking is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{ls}{extra}>{s}</text>'
    )


def mono(x, y, s, size, color=FG, weight=400, anchor="start", tracking=None) -> str:
    return text(x, y, esc(s), size, color, weight, MONO, anchor, tracking,
                extra=' style="font-feature-settings:\'tnum\',\'zero\'"')


def anim(cls: str, delay: float = 0.0) -> str:
    return f'class="{cls}" style="animation-delay:{delay:.2f}s"'


# Shared CSS: every loop is gated on prefers-reduced-motion. Without the
# media match (or without CSS animation support) the static final frame shows.
BASE_CSS = f"""
    .in, .draw, .retract, .pulse, .float, .drift, .rise {{ transform-box: fill-box; }}
    @media (prefers-reduced-motion: no-preference) {{
      .in {{ animation: in {CYCLE}s {EASE} infinite both; }}
      .draw {{ transform-origin: left center; animation: draw {CYCLE}s {EASE} infinite both; }}
      .pulse {{ animation: pulse 2s ease-in-out infinite; }}
      .float {{ transform-origin: center; animation: float 9s ease-in-out infinite alternate; }}
      .retract {{ transform-origin: right center; animation: retract {CYCLE}s {EASE} infinite both; }}
      .drift {{ animation: drift 18s ease-in-out infinite alternate; }}
      .rise {{ animation: rise {CYCLE}s {EASE} infinite both; }}
    }}
    @keyframes in {{ 0% {{ opacity: 0; transform: translateY(12px); }} 6%, 95% {{ opacity: 1; transform: none; }} 100% {{ opacity: 0; }} }}
    @keyframes draw {{ 0% {{ transform: scaleX(0); }} 9%, 95% {{ transform: scaleX(1); }} 100% {{ transform: scaleX(0); opacity: 0; }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
    @keyframes float {{ from {{ transform: translateY(4px) rotate(-0.6deg); }} to {{ transform: translateY(-8px) rotate(0.6deg); }} }}
    @keyframes drift {{ from {{ transform: translateX(-36px); }} to {{ transform: translateX(36px); }} }}
    @keyframes rise {{ 0% {{ opacity: 0; transform: translateY(28px); }} 10%, 95% {{ opacity: 1; transform: none; }} 100% {{ opacity: 0; }} }}
"""


def svg(height: int, body: str, label: str, defs: str = "", css: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" fill="none" role="img" aria-label="{esc(label)}">
  <style>{BASE_CSS}{css}  </style>
  <defs>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
    <filter id="haze" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
    <pattern id="grid" width="56" height="56" patternUnits="userSpaceOnUse">
      <path d="M56 0H0V56" stroke="{NEON_SOFT}" stroke-opacity=".07"/>
    </pattern>
    <linearGradient id="fadeY" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".15" stop-color="#fff"/>
      <stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="gridMask"><rect width="{W}" height="{height}" fill="url(#fadeY)"/></mask>
    <clipPath id="frame"><rect width="{W}" height="{height}" rx="24"/></clipPath>
{defs}  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{height}" fill="{MIDNIGHT}"/>
{body}
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{height - 1}" rx="23.5" stroke="#fff" stroke-opacity=".08"/>
</svg>
"""


def blueprint(height: int, pool_x: float = 0.12, pool_y: float = 0.2) -> str:
    """.blueprint: faint cobalt grid + a pool of light at the start."""
    return (
        f'    <ellipse cx="{W * pool_x:.0f}" cy="{height * pool_y:.0f}" rx="{W * .3:.0f}" ry="{height * .4:.0f}" fill="{COBALT}" opacity=".32" filter="url(#blur)"/>\n'
        f'    <rect width="{W}" height="{height}" fill="url(#grid)" mask="url(#gridMask)"/>\n'
    )


def section_title(y: float, title: str, sub: str = "", delay: float = 0) -> str:
    """SECTION_TITLE: medium, -0.03em, max 24ch; supporting text in muted."""
    out = f'    <g {anim("in", delay)}>\n'
    out += "      " + text(GUTTER, y, esc(title), 44, FG, 500, tracking="-1.3") + "\n"
    for i, line in enumerate(wrap(sub, 640, 17)) if sub else []:
        out += "      " + text(GUTTER, y + 44 + i * 27, esc(line), 17, MUTED) + "\n"
    return out + "    </g>\n"


def link_line(x: float, y: float, label: str, delay: float = 0) -> str:
    w = len(label) * 16 * 0.455
    return (
        f'    <g {anim("in", delay)}>{text(x, y, esc(label), 16, NEON_SOFT, 500)}'
        f'{lucide("arrow-right", x + w + 8, y - 13, 16, NEON_SOFT)}</g>\n'
    )


def status(x: float, y: float, label: str, size: int = 14) -> str:
    """Status marker: neon-soft dot + neon-soft 500 text. Live work only."""
    return (
        f'<circle {anim("pulse")} cx="{x + 3:.1f}" cy="{y - size * .34:.1f}" r="3.2" fill="{NEON_SOFT}"/>'
        + text(x + 14, y, esc(label), size, NEON_SOFT, 500)
    )


# -------------------------------------------------------------------- hero

def build_hero() -> str:
    TOP = 720  # copy + badge area; the cost slab sits below it
    H = TOP + 300
    body = blueprint(H, 0.1, 0.18)
    # page-glow: ambient cobalt from the top
    body += f'    <ellipse cx="{W / 2:.0f}" cy="-40" rx="560" ry="300" fill="{COBALT}" opacity=".35" filter="url(#blur)"/>\n'

    # --- badge (the caricature, lit from below), floating beside the copy
    bw, bh = 300, 390
    bx, by = 756, (TOP - bh) / 2
    badge_cx = bx + bw / 2
    pvb, pinner = brand_vector("portrait")
    pw, ph = 196, 228
    px, py = bx + (bw - pw) / 2, by + 34
    body += f"""    <ellipse cx="{badge_cx:.0f}" cy="{by + bh / 2:.0f}" rx="230" ry="260" fill="{COBALT}" opacity=".28" filter="url(#blur)"/>
    <g class="float">
      <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18" fill="#05070c" stroke="#fff" stroke-opacity=".12"/>
      <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18" fill="url(#grid)" opacity=".8"/>
      <ellipse cx="{badge_cx:.0f}" cy="{py + ph * .78:.0f}" rx="90" ry="70" fill="{COBALT}" opacity=".55" filter="url(#haze)"/>
      <rect x="{px:.0f}" y="{py:.0f}" width="{pw}" height="{ph}" fill="{NEON}" mask="url(#portraitMask)" filter="url(#glow)" opacity=".75"/>
      <rect x="{px:.0f}" y="{py:.0f}" width="{pw}" height="{ph}" fill="url(#ink)" mask="url(#portraitMask)"/>
      {text(bx + 26, by + bh - 82, "Leonardo Lopes", 25, FG, 600, tracking="-0.6")}
      {text(bx + 26, by + bh - 56, "Tech Lead · Software Engineer &amp; Architect", 13, MUTED)}
      {mono(bx + 26, by + bh - 28, "IN PRODUCTION SINCE 2020", 13, NEON_SOFT, tracking="1.6")}
    </g>
"""
    defs = (
        f'    <linearGradient id="ink" x1="0" y1="0" x2="0" y2="1"><stop offset=".4" stop-color="{FG}"/><stop offset="1" stop-color="{NEON_SOFT}"/></linearGradient>\n'
        f'    <mask id="portraitMask" maskUnits="userSpaceOnUse"><svg x="{px:.0f}" y="{py:.0f}" width="{pw}" height="{ph}" viewBox="{pvb}" style="color:#fff">{pinner}</svg></mask>\n'
    )

    # --- copy column
    x = GUTTER
    body += (
        f'    <g {anim("in", 0)}>{text(x, 150, esc(HERO["name"]), 20, FG, 500)}'
        f'{text(x, 176, esc(HERO["role"]), 15, NEON_SOFT)}</g>\n'
    )
    years = career_words()
    lines = [
        (f"{years} years of software", None),
        ("running in ", "production"),
        ("Now I lead the team", None),
        ("that ships it.", None),
    ]
    y = 262
    for i, (a, lit) in enumerate(lines):
        content = esc(a) + (f'<tspan fill="{NEON_SOFT}">{esc(lit)}</tspan><tspan fill="{FG}">.</tspan>' if lit else "")
        body += f'    <g {anim("in", 0.12 + 0.08 * i)}>{text(x, y, content, 60, FG, 600, tracking="-2.4")}</g>\n'
        y += 62
    y += 8
    body += (
        f'    <g {anim("in", 0.5)}>{text(x, y, esc(HERO["current"]), 16, FG)}'
        f'{status(x, y + 28, "Now · in production", 14)}'
        f'{text(x, y + 56, esc(HERO["availability"]), 15, MUTED)}</g>\n'
    )
    by2 = y + 84
    body += (
        f'    <g {anim("in", 0.65)}>'
        # One light CTA; the whole hero image links to leonardolopes.tech
        f'<rect x="{x}" y="{by2}" width="166" height="48" rx="24" fill="#fff"/>'
        f'{text(x + 28, by2 + 30, "Know more", 16, MIDNIGHT, 500)}'
        f'{lucide("arrow-up-right", x + 120, by2 + 15, 18, MIDNIGHT)}</g>\n'
    )

    # --- cost slab: the featured result, lit because the platform runs in production
    sy = TOP + 10
    bar_y, bar_h = sy + 168, 56
    bar_x0, bar_x1 = GUTTER, W - GUTTER
    cut_w = (bar_x1 - bar_x0) * (1 - SLAB["ratio"])
    lit_x = bar_x0 + cut_w
    cap_x = 760
    defs += f'    <linearGradient id="slabLit" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NEON}"/><stop offset=".7" stop-color="{NEON_SOFT}"/><stop offset="1" stop-color="#fff"/></linearGradient>\n'
    slab_label = "Cloud bill · " + SLAB["client"] + " · in production"
    body += (
        f'    <g {anim("in", 0.9)}>{status(GUTTER, sy, slab_label, 15)}'
        f'{mono(GUTTER - 6, sy + 116, SLAB["metric"], 128, FG, 500, tracking="-5")}</g>\n'
    )
    cap = wrap(SLAB["caption"], bar_x1 - cap_x, 16, 0.49)
    body += f'    <g {anim("in", 1.0)}>' + "".join(
        text(cap_x, sy + 116 - (len(cap) - 1 - i) * 26, esc(line), 16, MUTED) for i, line in enumerate(cap)
    ) + "</g>\n"
    body += (
        f'    <g {anim("in", 1.1)}><ellipse cx="{lit_x + (bar_x1 - lit_x) / 2:.0f}" cy="{bar_y + bar_h + 30}" rx="{(bar_x1 - lit_x) / 2:.0f}" ry="70" fill="{NEON}" opacity=".32" filter="url(#haze)"/></g>\n'
        f'    <g {anim("in", 1.0)}><rect x="{bar_x0 + .5}" y="{bar_y + .5}" width="{cut_w - 1:.0f}" height="{bar_h - 1}" rx="5" stroke="#fff" stroke-opacity=".25" stroke-dasharray="5 5"/></g>\n'
        f'    <g {anim("retract", 1.0)}>\n'
        f'      <rect x="{lit_x:.0f}" y="{bar_y}" width="{bar_x1 - lit_x:.0f}" height="{bar_h}" rx="5" fill="{NEON}" filter="url(#haze)" opacity=".7"/>\n'
        f'      <rect x="{lit_x:.0f}" y="{bar_y}" width="{bar_x1 - lit_x:.0f}" height="{bar_h}" rx="5" fill="url(#slabLit)"/>\n'
        f"    </g>\n"
        f'    <g {anim("in", 2.2)}>{text(bar_x0 + 18, bar_y + 35, "Before " + f"<tspan fill=\"{FG}\" font-weight=\"500\">100%</tspan>", 16, MUTED)}'
        f'{text(lit_x + 18, bar_y + 35, "Now <tspan font-weight=\"600\">" + str(round(SLAB["ratio"] * 100)) + "%</tspan>", 16, MIDNIGHT, 500)}</g>\n'
    )
    # the lit segment starts full width and retracts to the real ratio (900ms on the site)
    css = (
        "\n    @media (prefers-reduced-motion: no-preference) {\n"
        f"      @keyframes retract {{ 0% {{ transform: scaleX({1 / SLAB['ratio']:.4f}); opacity: 0; }} 2% {{ transform: scaleX({1 / SLAB['ratio']:.4f}); opacity: 1; }} 9%, 95% {{ transform: scaleX(1); opacity: 1; }} 100% {{ opacity: 0; }} }}\n"
        "    }\n"
    )
    return svg(H, body, f"Leonardo Lopes, Tech Lead · Software Engineer & Architect. {years} years of software running in production. Now leading the team that ships it. Linda Lifetech cloud bill: " + SLAB["metric"] + ".", defs, css)


# ------------------------------------------------------------------ ledger

def build_ledger() -> str:
    row_h = 150
    top = 220
    H = top + len(LEDGER) * row_h + 90
    body = blueprint(H)
    body += section_title(96, "Measured in production.",
                          "Numbers from systems I helped ship before my current role. Full role descriptions are in the experience history.")
    c1, c2, c3 = GUTTER, GUTTER + 250, W - GUTTER - 230
    body += f'    <path d="M{GUTTER} {top} H{W - GUTTER}" stroke="#fff" stroke-opacity=".12"/>\n'
    for i, (metric, unit, period, summary, stack, client, role) in enumerate(LEDGER):
        y = top + i * row_h
        d = 0.25 + 0.15 * i
        lines = wrap(summary, c3 - c2 - 40, 16, 0.48)
        summ = "".join(text(c2, y + 46 + j * 25, esc(l), 16, FG, extra=' fill-opacity=".85"') for j, l in enumerate(lines))
        stack_txt = text(c2, y + 46 + len(lines) * 25 + 10, esc(" · ".join(stack)), 14, NEON_SOFT) if stack else ""
        body += f"""    <g {anim("in", d)}>
      {mono(c1, y + 66, metric, 52, FG, 500, tracking="-1.5")}
      {text(c1, y + 94, esc(unit), 14, MUTED)}
      {mono(c1, y + 118, period, 13, MUTED)}
      {summ}{stack_txt}
      {text(c3, y + 46, esc(client), 15, FG, 500)}
      {text(c3, y + 70, esc(role), 14, MUTED)}
    </g>
    <path d="M{GUTTER} {y + row_h} H{W - GUTTER}" stroke="#fff" stroke-opacity=".12"/>
"""
    fy = top + len(LEDGER) * row_h + 50
    body += f'    <g {anim("in", 0.9)}>{text(GUTTER, fy, "Before that: React Native apps for freelance clients, from 2020.", 15, MUTED)}</g>\n'
    body += link_line(W - GUTTER - 168, fy, "See my experience", 1.0)
    return svg(H, body, "Earlier results: −80% worst-case load time at Grupo Petrópolis, 27 Brazilian states on one pricing platform for Lactalis, 0.5× the estimated delivery time at MSD, 580+ teaching units served for Poliedro.")


# ------------------------------------------------------------------ career

def build_career() -> str:
    H = 160 + 64 + 44 + sum(50 + (56 if e else 12) + 14 for *_, e in LANES) + 40
    body = ""
    # FloatingLines: faint cobalt filaments drifting behind the section
    for i in range(5):
        y0 = 120 + i * 22
        amp = 26 + i * 6
        d = f"M-80 {y0} C 240 {y0 - amp}, 480 {y0 + amp}, 720 {y0} S 1120 {y0 - amp}, 1300 {y0}"
        body += f'    <path class="drift" style="animation-delay:-{i * 3}s" d="{d}" stroke="{COBALT}" stroke-opacity="{.35 - i * .05:.2f}" stroke-width="1.2"/>\n'
    body += section_title(96, f"Continuous production work since {CAREER_START.strftime('%B %Y')}.")

    px, py, pw = GUTTER, 150, W - GUTTER * 2
    ph = H - py - 48
    body += f'    <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="22" fill="{BACKGROUND}" fill-opacity=".72" stroke="{NEON_SOFT}" stroke-opacity=".15"/>\n'
    ix0, ix1 = px + 40, px + pw - 40
    span_days = (TODAY - CAREER_START).days

    def xo(d: dt.date | None) -> float:
        d = d or TODAY
        return ix0 + (ix1 - ix0) * (d - CAREER_START).days / span_days

    # ruler: year labels + one tick per month
    ry = py + 64
    body += f'    <g {anim("in", 0.1)}>\n'
    for year in range(CAREER_START.year, TODAY.year + 1):
        d = CAREER_START if year == CAREER_START.year else dt.date(year, 1, 1)
        x = xo(d)
        anchor = "start" if year == CAREER_START.year else ("end" if x > ix1 - 30 else "middle")
        body += "      " + mono(x, ry - 14, str(year), 13, MUTED, anchor=anchor) + "\n"
    months = (TODAY.year - CAREER_START.year) * 12 + TODAY.month - CAREER_START.month
    ticks = "".join(f"M{ix0 + (ix1 - ix0) * m / months:.1f} {ry} v-6" for m in range(months + 1))
    body += f'      <path d="{ticks}" stroke="#fff" stroke-opacity=".18"/>\n'
    body += f'      <path d="M{px} {ry + .5} H{px + pw}" stroke="#fff" stroke-opacity=".12"/>\n    </g>\n'

    defs = f'    <linearGradient id="filament" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NEON}"/><stop offset="1" stop-color="{NEON_SOFT}"/></linearGradient>\n'
    y = ry + 44
    for i, (label, start, end, engagements) in enumerate(LANES):
        d = 0.3 + 0.25 * i
        live = end is None
        x0, x1 = xo(start), xo(end)
        lane = f'    <g {anim("in", d)}>\n'
        lane += "      " + text(ix0, y, esc(label), 19, FG, 500) + "\n"
        lane += "      " + mono(ix1, y, f"{fmt_month(start)} – {fmt_month(end)}", 13, MUTED, anchor="end") + "\n"
        lane += f'      <rect x="{ix0}" y="{y + 16}" width="{ix1 - ix0}" height="8" rx="4" fill="#fff" fill-opacity=".05"/>\n'
        lane += "    </g>\n"
        fill = 'fill="url(#filament)"' if live else f'fill="{FG}" fill-opacity=".45"'
        glow = f'<rect x="{x0:.1f}" y="{y + 16}" width="{x1 - x0:.1f}" height="8" rx="4" fill="{NEON}" filter="url(#glow)" opacity=".8"/>' if live else ""
        lane += f'    <g {anim("draw", d + 0.2)}>{glow}<rect x="{x0:.1f}" y="{y + 16}" width="{x1 - x0:.1f}" height="8" rx="4" {fill}/></g>\n'
        y_e = y + 50
        if engagements:
            lane += f'    <g {anim("in", d + 0.4)}>\n'
            for j, (name, s, e) in enumerate(engagements):
                ex = xo(s)
                ey = y_e + (0 if j % 2 == 0 else 24)
                tw = len(name) * 14 * 0.5
                if ex + 10 + tw > ix1:  # keep labels inside the panel
                    lane += f'      <path d="M{ex:.1f} {ey - 14} v18" stroke="#fff" stroke-opacity=".12"/>' + text(ex - 8, ey, esc(name), 14, NEON_SOFT if e is None else MUTED, anchor="end") + "\n"
                else:
                    lane += f'      <path d="M{ex:.1f} {ey - 14} v18" stroke="#fff" stroke-opacity=".12"/>' + text(ex + 8, ey, esc(name), 14, NEON_SOFT if e is None else MUTED) + "\n"
            lane += "    </g>\n"
            y += 50 + 56
        else:
            y += 50 + 12
        if i < len(LANES) - 1:
            lane += f'    <path d="M{ix0} {y - 18} H{ix1}" stroke="#fff" stroke-opacity=".07"/>\n'
        body += lane
        y += 14
    return svg(H, body, f"Career ruler since {CAREER_START.strftime('%B %Y')}: Freelance, Nkey (Poliedro), then Buildbox for MSD, Grupo Petrópolis, Lactalis Group, Linda Lifetech and Callink.", defs)


# ------------------------------------------------------------------- stack

def build_stack() -> str:
    item_h = 50
    top = 220
    H = top + 44 + len(STACK_GROUPS[0][1]) * item_h + 96
    body = blueprint(H, 0.85, 0.15)
    body += section_title(96, "Built across the whole system.",
                          "Interfaces, services, data and the cloud they run on: tools I’ve used in production. Each system gets the ones it needs.")
    gap = 40
    cw = (W - GUTTER * 2 - gap * 3) / 4
    for c, (title, techs) in enumerate(STACK_GROUPS):
        x = GUTTER + c * (cw + gap)
        d = 0.2 + 0.12 * c
        col = f'    <g {anim("in", d)}>\n'
        col += "      " + text(x, top + 20, esc(title), 15, NEON_SOFT, 500) + "\n"
        col += f'      <path d="M{x:.1f} {top + 36} h{cw:.1f}" stroke="{NEON}" stroke-opacity=".6"/>\n'
        for i, tech in enumerate(techs):
            iy = top + 36 + (i + 1) * item_h
            col += "      " + text(x, iy - 17, esc(tech), 18, FG) + "\n"
            col += f'      <path d="M{x:.1f} {iy} h{cw:.1f}" stroke="#fff" stroke-opacity=".08"/>\n'
        body += col + "    </g>\n"
    body += link_line(GUTTER, H - 46, "The full catalog, personal projects included", 0.8)
    return svg(H, body, "Stack. Interfaces: React, Next.js, React Native, Expo, Tailwind CSS, Storybook. Services: TypeScript, Node.js, Go, NestJS, GraphQL, Fastify. Data and messaging: PostgreSQL, MongoDB, Redis, Apache Kafka, Prisma, MySQL. Cloud: AWS, Google Cloud, Azure, Terraform, Kubernetes, OpenTelemetry.")


# ----------------------------------------------------------------- contact

def build_contact() -> str:
    row_h = 74
    top = 230
    H = top + len(CONTACT_ROWS) * row_h + 56
    body = section_title(96, "Hiring, or have a product to build?",
                         "I’m Leonardo Lopes, a tech lead, software engineer and architect working remotely from Brazil (UTC−3). Every channel below reaches me directly.")
    body += f'    <path d="M{GUTTER} {top} H{W - GUTTER}" stroke="#fff" stroke-opacity=".12"/>\n'
    for i, (icon, label, detail) in enumerate(CONTACT_ROWS):
        y = top + i * row_h
        cy = y + row_h / 2
        row = f'    <g {anim("in", 0.2 + 0.1 * i)}>'
        row += lucide(icon, GUTTER, cy - 11, 22, NEON_SOFT)
        if detail:
            row += text(GUTTER + 40, cy - 3, esc(label), 22, FG, 500) + text(GUTTER + 40, cy + 21, esc(detail), 14, MUTED)
        else:
            row += text(GUTTER + 40, cy + 8, esc(label), 22, FG, 500)
        row += lucide("arrow-up-right", W - GUTTER - 22, cy - 11, 22, MUTED)
        row += f'</g>\n    <path d="M{GUTTER} {y + row_h} H{W - GUTTER}" stroke="#fff" stroke-opacity=".12"/>\n'
        body += row
    return svg(H, body, "Hiring, or have a product to build? Email, schedule a call, WhatsApp, LinkedIn or GitHub.")


# ------------------------------------------------------------------ finale

def build_finale() -> str:
    H = 420
    svb, sinner = brand_vector("signature")
    sw = 460
    sh = sw * float(svb.split()[3]) / float(svb.split()[2])
    sx, sy = (W - sw) / 2, 110
    body = f"""    <g {anim("in", 0)}>
      <ellipse cx="{W / 2:.0f}" cy="{H * .6:.0f}" rx="{W * .42:.0f}" ry="{H * .36:.0f}" fill="{COBALT}" opacity=".42" filter="url(#blur)"/>
      <ellipse cx="{W / 2:.0f}" cy="{H + 40}" rx="{W * .6:.0f}" ry="{H * .32:.0f}" fill="{NEON}" opacity=".3" filter="url(#blur)"/>
    </g>
    <g {anim("rise", 0.3)}>
      <svg x="{sx:.0f}" y="{sy + 6}" width="{sw}" height="{sh:.0f}" viewBox="{svb}" style="color:{MIDNIGHT}" filter="url(#glow)" opacity=".9">{sinner}</svg>
      <svg x="{sx:.0f}" y="{sy}" width="{sw}" height="{sh:.0f}" viewBox="{svb}" style="color:{FG}">{sinner}</svg>
    </g>
    <g {anim("in", 1.0)}>
      {text(W / 2, sy + sh + 70, esc(CLOSING_LINE), 30, FG, 500, anchor="middle", tracking="-0.8")}
      {text(W / 2, sy + sh + 102, "Tech Lead · Software Engineer &amp; Architect · leonardolopes.tech", 15, MUTED, anchor="middle")}
    </g>
"""
    return svg(H, body, f"Signature of Leonardo Lopes. {CLOSING_LINE}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, fn in [
        ("hero", build_hero),
        ("ledger", build_ledger),
        ("career", build_career),
        ("stack", build_stack),
        ("contact", build_contact),
        ("finale", build_finale),
    ]:
        content = fn()
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}.svg ({len(content) // 1024} KB)")


if __name__ == "__main__":
    main()

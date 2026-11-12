#!/usr/bin/env python3
"""Generate the README SVGs in the leonardolopes.tech visual language:
neon on midnight, glass cards, mono eyebrows.

Usage: python3 scripts/build_svgs.py

GitHub renders README SVGs inside <img>, which blocks external requests, so
the memoji and tech icons (vendored from the site repo into assets/source/)
are embedded as data URIs.
"""

import base64
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source"
OUT = ROOT / "assets"

# Tokens from leonardolopes.tech globals.css (.dark), oklch converted to hex
MIDNIGHT = "#030407"
CARD = "#0a0e18"
FG = "#e8eef9"
MUTED = "#8c98b0"
COBALT = "#1558c9"
NEON = "#2f6bff"
NEON_SOFT = "#7aa6ff"

SANS = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

W = 1200
CYCLE = 14.0  # seconds; every intro animation replays on this loop

# lucide icons (24x24, stroke)
LUCIDE = {
    "layers": '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "server": '<rect width="20" height="8" x="2" y="2" rx="2"/><rect width="20" height="8" x="2" y="14" rx="2"/><path d="M6 6h.01"/><path d="M6 18h.01"/>',
    "smartphone": '<rect width="14" height="20" x="5" y="2" rx="2"/><path d="M12 18h.01"/>',
    "arrow": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
}


# ------------------------------------------------------------------ helpers

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def data_uri(path: pathlib.Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def _k(t: float) -> str:
    return f"{min(max(t / CYCLE, 0), 1):.4f}"


def loop(attr: str, a, b, start: float, dur: float = 0.7) -> str:
    """a -> b at `start`, hold, back to a at the end of the cycle, repeat.
    Give the element `b` as its static value so non-SMIL renderers show
    the finished state."""
    return (
        f'<animate attributeName="{attr}" values="{a};{a};{b};{b};{a}" '
        f'keyTimes="0;{_k(start)};{_k(start + dur)};{_k(CYCLE - 0.6)};1" '
        f'dur="{CYCLE:.0f}s" repeatCount="indefinite"/>'
    )


def fade(delay: float) -> str:
    return loop("opacity", 0, 1, delay)


def rise(delay: float, dy: int = 14) -> str:
    return (
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 {dy};0 {dy};0 0;0 0;0 {dy}" '
        f'keyTimes="0;{_k(delay)};{_k(delay + 0.7)};{_k(CYCLE - 0.6)};1" '
        f'calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1;0 0 1 1;0 0 1 1" '
        f'dur="{CYCLE:.0f}s" repeatCount="indefinite"/>'
    )


def enter(delay: float) -> str:
    return fade(delay) + rise(delay)


def wrap(text: str, max_px: float, size: float, ratio: float = 0.53) -> list[str]:
    max_chars = int(max_px / (size * ratio))
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > max_chars and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def lucide(name: str, x: float, y: float, size: float, color: str = NEON, sw: float = 2) -> str:
    return (
        f'<g transform="translate({x:.0f} {y:.0f}) scale({size / 24:.3f})" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{LUCIDE[name]}</g>'
    )


def svg(height: int, body: str, label: str, defs: str = "", width: int = W) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" role="img" aria-label="{esc(label)}">
  <defs>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
    <filter id="glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="12"/></filter>
    <linearGradient id="glassEdge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".16"/>
      <stop offset="1" stop-color="#fff" stop-opacity=".06"/>
    </linearGradient>
{defs}  </defs>
{body}
</svg>
"""


def panel(x, y, w, h, r=24, border=None, border_opacity=1.0) -> str:
    stroke = f'stroke="{border}" stroke-opacity="{border_opacity}"' if border else 'stroke="url(#glassEdge)"'
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{CARD}" {stroke}/>'


def page_bg(height: int, width: int = W) -> str:
    return (
        f'  <rect width="{width}" height="{height}" rx="28" fill="{MIDNIGHT}"/>\n'
        f'  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="27.5" stroke="#fff" stroke-opacity=".08"/>\n'
    )


def heading(x: int, y: int, eyebrow: str, title: str, delay: float = 0) -> str:
    return (
        f'  <g opacity="1">{enter(delay)}\n'
        f'    <text x="{x}" y="{y}" fill="{NEON}" font-family="{MONO}" font-size="14" letter-spacing="2.5">{esc(eyebrow.upper())}</text>\n'
        f'    <text x="{x}" y="{y + 46}" fill="{FG}" font-family="{SANS}" font-size="36" font-weight="700" letter-spacing="-0.5">{esc(title)}</text>\n'
        f"  </g>\n"
    )


def mesh(x, y, w, h, r, clip_id: str) -> tuple[str, str]:
    """The site's .neon-mesh: three neon radial fields plus a drifting blob."""
    defs = f'    <clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>\n'
    blobs = [
        (x + w * 0.18, y + h * 0.14, w * 0.33, h * 0.55, COBALT, 0.95),
        (x + w * 0.88, y + h * 0.28, w * 0.26, h * 0.5, NEON, 0.85),
        (x + w * 0.50, y + h * 1.05, w * 0.36, h * 0.42, NEON, 0.7),
    ]
    body = f'  <g clip-path="url(#{clip_id})">\n    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{MIDNIGHT}"/>\n'
    for cx, cy, rx, ry, c, o in blobs:
        body += f'    <ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{c}" opacity="{o}" filter="url(#blur)"/>\n'
    body += (
        f'    <ellipse cx="{x + w * 0.6:.0f}" cy="{y + h * 0.6:.0f}" rx="{w * 0.24:.0f}" ry="{h * 0.4:.0f}" fill="{COBALT}" opacity=".6" filter="url(#blur)">'
        f'<animateTransform attributeName="transform" type="translate" values="{-w * .04:.0f} {-h * .03:.0f};{w * .06:.0f} {h * .05:.0f};{-w * .04:.0f} {-h * .03:.0f}" '
        f'dur="{CYCLE:.0f}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></ellipse>\n'
        f"  </g>\n"
        f'  <rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r}" stroke="#fff" stroke-opacity=".1"/>\n'
    )
    return defs, body


def neon_text(x, y, text, size, anchor="middle", delay=0.0) -> str:
    attrs = f'x="{x:.0f}" y="{y}" text-anchor="{anchor}" font-family="{SANS}" font-size="{size}" font-weight="700" letter-spacing="-1.5"'
    return (
        f'  <g opacity="1">{enter(delay)}\n'
        f'    <text {attrs} fill="{NEON}" filter="url(#glow)" opacity=".9">{esc(text)}'
        f'<animate attributeName="opacity" values=".65;1;.65" dur="4s" repeatCount="indefinite"/></text>\n'
        f'    <text {attrs} fill="#fff">{esc(text)}</text>\n'
        f"  </g>\n"
    )


def pill(cx, y, text, solid=None, text_color="#fff", size=14, mono=True, pad=22, h=34, arrow=False) -> str:
    font = MONO if mono else SANS
    spacing = 2.4 if mono else 0
    text_w = len(text) * (size * (0.62 if mono else 0.55) + spacing) - spacing
    tw = text_w + (22 if arrow else 0)
    w = tw + pad * 2
    x = cx - w / 2
    if solid:
        out = f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="{h / 2}" fill="{solid}"/>'
    else:
        out = f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="{h / 2}" fill="#fff" fill-opacity=".06" stroke="#fff" stroke-opacity=".2"/>'
    # textLength pins the exact width, so the pill fits whatever font renders
    ls = f' letter-spacing="{spacing}" textLength="{text_w:.0f}" lengthAdjust="spacing"' if mono else ""
    tx = cx - (11 if arrow else 0)
    out += (
        f'<text x="{tx:.0f}" y="{y + h / 2 + size * 0.36:.0f}" text-anchor="middle" fill="{text_color}" '
        f'font-family="{font}" font-size="{size}" font-weight="{400 if mono else 600}"{ls}>{esc(text)}</text>'
    )
    if arrow:
        out += lucide("arrow", cx + tw / 2 - 16, y + h / 2 - 8, 16, text_color)
    return out


# -------------------------------------------------------------------- hero

def build_hero() -> str:
    H = 460
    defs, body = mesh(0, 0, W, H, 40, "heroClip")
    cx = W / 2
    body += f'  <g opacity="1">{enter(0)}{pill(cx, 92, "SOFTWARE ENGINEER & ARCHITECT")}</g>\n'
    body += neon_text(cx, 212, "Leonardo Lopes", 84, delay=0.2)
    body += (
        f'  <g opacity="1">{enter(0.45)}\n'
        f'    <text x="{cx:.0f}" y="266" text-anchor="middle" fill="#fff" fill-opacity=".85" font-family="{SANS}" font-size="21">'
        f'Tech Lead <tspan fill="{NEON_SOFT}">@Linda Lifetech</tspan> · Buildbox</text>\n'
        f'    <text x="{cx:.0f}" y="298" text-anchor="middle" fill="#fff" fill-opacity=".65" font-family="{SANS}" font-size="17">'
        f"Web, backend and mobile, built to be easy to change and to keep running after launch.</text>\n"
        f"  </g>\n"
    )
    body += (
        f'  <g opacity="1">{enter(0.7)}'
        f'{pill(cx - 112, 346, "leonardolopes.tech", solid="#fff", text_color=MIDNIGHT, mono=False, size=16, h=48, pad=26, arrow=True)}'
        f'{pill(cx + 122, 346, "Get in touch", mono=False, size=16, h=48, pad=28)}'
        f"</g>\n"
    )
    return svg(H, body, "Leonardo Lopes, Software Engineer & Architect, Tech Lead at Linda Lifetech (Buildbox)", defs)


# ------------------------------------------------------------------ layers

def build_layers() -> str:
    H = 430
    body = page_bg(H)
    body += heading(48, 70, "What I work on", "Three layers, one standard")
    cards = [
        ("layers", "Frontend", "Interfaces that feel fast. Component systems, accessible markup, and state that stays predictable as the product grows."),
        ("server", "Backend", "APIs and services in Node.js, TypeScript and Go. I focus on clear boundaries, observability and running cost."),
        ("smartphone", "Mobile", "React Native apps with native modules when the device needs it, shipped with the same care as the web."),
    ]
    gap = 16
    cw = (W - 96 - gap * 2) / 3
    for i, (icon, title, desc) in enumerate(cards):
        x = 48 + i * (cw + gap)
        y = 146
        lines = wrap(desc, cw - 56, 15.5)
        text = "".join(
            f'<text x="{x + 28:.0f}" y="{y + 132 + j * 24}" fill="{MUTED}" font-family="{SANS}" font-size="15.5">{esc(l)}</text>'
            for j, l in enumerate(lines)
        )
        body += (
            f'  <g opacity="1">{enter(0.2 + 0.15 * i)}\n'
            f"    {panel(x, y, cw, 252)}\n"
            f'    <rect x="{x + 28:.0f}" y="{y + 26}" width="44" height="44" rx="12" fill="{NEON}" fill-opacity=".15" stroke="{NEON}" stroke-opacity=".3"/>\n'
            f"    {lucide(icon, x + 40, y + 38, 20)}\n"
            f'    <text x="{x + 28:.0f}" y="{y + 102}" fill="{FG}" font-family="{SANS}" font-size="21" font-weight="600">{esc(title)}</text>\n'
            f"    {text}\n"
            f"  </g>\n"
        )
    return svg(H, body, "What I work on: Frontend, Backend and Mobile")


# ------------------------------------------------------------------- about

def build_about() -> str:
    H = 420
    body = page_bg(H)
    memoji = data_uri(SRC / "memoji.png", "image/png")
    lx, ly, lw, lh = 32, 32, 700, H - 64
    desc = (
        "Healthtech product for early breast-cancer detection using AI. Led a zero-downtime "
        "migration of a live system from a monolith to Go and Node.js/TypeScript microservices, "
        "micro frontends and React Native. Cut cloud cost by ~59%, introduced OpenTelemetry and "
        "defined infrastructure as code with Terraform."
    )
    lines = wrap(desc, lw - 64, 15.5)
    text = "\n".join(
        f'    <text x="{lx + 32}" y="{ly + 176 + j * 25}" fill="{MUTED}" font-family="{SANS}" font-size="15.5">{esc(l)}</text>'
        for j, l in enumerate(lines)
    )
    ty = ly + 176 + len(lines) * 25 + 22
    body += f"""  <g opacity="1">{enter(0)}
    {panel(lx, ly, lw, lh, border=NEON, border_opacity=0.3)}
    <rect x="{lx + 32}" y="{ly + 32}" width="140" height="26" rx="8" fill="{NEON}" fill-opacity=".15"/>
    <text x="{lx + 102}" y="{ly + 50}" text-anchor="middle" fill="{NEON}" font-family="{MONO}" font-size="12" letter-spacing="2" textLength="112" lengthAdjust="spacing">CURRENT ROLE</text>
    <text x="{lx + 32}" y="{ly + 104}" fill="{FG}" font-family="{SANS}" font-size="30" font-weight="600">Tech Lead @Linda Lifetech</text>
    <text x="{lx + 32}" y="{ly + 136}" fill="{MUTED}" font-family="{SANS}" font-size="17">Buildbox · Software Engineer &amp; Architect</text>
{text}
    <text x="{lx + 32}" y="{ty}" fill="{NEON}" font-family="{SANS}" font-size="15" font-weight="500">Full experience history</text>
    {lucide("arrow", lx + 202, ty - 13, 16)}
    <image x="{lx + lw - 124}" y="{ly + 24}" width="96" height="96" href="{memoji}">
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
    </image>
  </g>
"""
    stats = [
        ("~59%", "Cloud cost reduction on a live system"),
        ("Zero downtime", "Monolith to microservices migration"),
        ("6+ years", "Shipping web, backend and mobile"),
    ]
    rx = lx + lw + 16
    rw = W - rx - 32
    gap = 14
    rh = (lh - gap * 2) / 3
    for i, (num, label) in enumerate(stats):
        y = ly + i * (rh + gap)
        body += (
            f'  <g opacity="1">{enter(0.2 + 0.15 * i)}\n'
            f"    {panel(rx, y, rw, rh)}\n"
            f'    <text x="{rx + 28}" y="{y + rh / 2 + 4:.0f}" fill="{FG}" font-family="{SANS}" font-size="34" font-weight="700">{esc(num)}</text>\n'
            f'    <text x="{rx + 28}" y="{y + rh / 2 + 30:.0f}" fill="{MUTED}" font-family="{SANS}" font-size="14">{esc(label)}</text>\n'
            f"  </g>\n"
        )
    return svg(H, body, "Current role: Tech Lead at Linda Lifetech (Buildbox). ~59% cloud cost reduction, zero-downtime migration, 6+ years.")


# -------------------------------------------------------------- experience

def build_experience() -> str:
    H = 430
    body = page_bg(H)
    body += heading(48, 70, "Experience", "Six years of shipping")
    # (when, project, role, line1, line2, via_buildbox)
    jobs = [
        ("2020 → 2021", "Freelance", "Mobile Engineer", "React Native apps,", "multiple clients", False),
        ("2021 → 2022", "Poliedro", "Software Engineer", "Go HLS streaming,", "580+ teaching units", False),
        ("2022 → 2023", "MSD", "Software Engineer", "Gamification app,", "in half the ETA", True),
        ("2023 → 2024", "Petrópolis", "Software Engineer", "Main app (97% rev.)", "−50% load time", True),
        ("2024 → 2025", "Lactalis", "Software Engineer", "Pricing platform,", "27 states of rules", True),
        ("2025 → now", "Linda Lifetech", "Tech Lead", "Go microservices,", "−59% cloud, IaC", True),
    ]
    line_y = 236
    x_start = 72
    step = (W - 48 - 150 - x_start) / (len(jobs) - 1)
    length = (W - 48) - x_start
    draw = loop("stroke-dashoffset", f"{length:.0f}", 0, 0.2, 2.4)
    body += (
        f'  <line x1="{x_start}" y1="{line_y}" x2="{W - 48}" y2="{line_y}" stroke="#fff" stroke-opacity=".1" stroke-width="2"/>\n'
        f'  <line x1="{x_start}" y1="{line_y}" x2="{W - 48}" y2="{line_y}" stroke="{NEON}" stroke-width="3" filter="url(#glowSoft)" '
        f'stroke-dasharray="{length:.0f}" stroke-dashoffset="0">{draw}</line>\n'
        f'  <line x1="{x_start}" y1="{line_y}" x2="{W - 48}" y2="{line_y}" stroke="{NEON}" stroke-width="2" '
        f'stroke-dasharray="{length:.0f}" stroke-dashoffset="0">{draw}</line>\n'
    )
    bb = [i for i, j in enumerate(jobs) if j[5]]
    bx1, bx2, by = x_start + step * bb[0] - 12, W - 48, line_y - 46
    body += (
        f'  <g opacity="1">{fade(0.3)}\n'
        f'    <path d="M{bx1:.0f} {by + 14} V{by} H{bx2} V{by + 14}" stroke="{NEON}" stroke-opacity=".45" stroke-width="1.5"/>\n'
        f'    <rect x="{bx1 + 18:.0f}" y="{by - 14}" width="196" height="28" rx="8" fill="{MIDNIGHT}"/>\n'
        f'    <rect x="{bx1 + 18:.0f}" y="{by - 14}" width="196" height="28" rx="8" fill="{NEON}" fill-opacity=".15"/>\n'
        f'    <text x="{bx1 + 116:.0f}" y="{by + 5}" text-anchor="middle" fill="{NEON}" font-family="{MONO}" font-size="12" letter-spacing="2" textLength="164" lengthAdjust="spacing">BUILDBOX PROJECTS</text>\n'
        f"  </g>\n"
    )
    for i, (when, company, role, d1, d2, _) in enumerate(jobs):
        cx = x_start + step * i
        current = i == len(jobs) - 1
        delay = 0.4 + 0.3 * i
        pulse = ""
        if current:
            pulse = (
                f'<circle cx="{cx:.0f}" cy="{line_y}" r="8" fill="none" stroke="{NEON}" stroke-width="2">'
                '<animate attributeName="r" values="8;24" dur="1.8s" repeatCount="indefinite"/>'
                '<animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>'
            )
        node = f'<circle cx="{cx:.0f}" cy="{line_y}" r="8" fill="{NEON if current else MIDNIGHT}" stroke="{NEON}" stroke-width="2"/>'
        tx = cx - 8
        body += f"""  <g opacity="1">{enter(delay)}
    {pulse}{node}
    <text x="{tx:.0f}" y="{line_y + 46}" fill="{NEON if current else MUTED}" font-family="{MONO}" font-size="14">{esc(when)}</text>
    <text x="{tx:.0f}" y="{line_y + 76}" fill="{FG}" font-family="{SANS}" font-size="20" font-weight="600">{esc(company)}</text>
    <text x="{tx:.0f}" y="{line_y + 99}" fill="{NEON_SOFT if current else MUTED}" font-family="{SANS}" font-size="16">{esc(role)}</text>
    <text x="{tx:.0f}" y="{line_y + 128}" fill="{MUTED}" fill-opacity=".8" font-family="{MONO}" font-size="13">{esc(d1)}</text>
    <text x="{tx:.0f}" y="{line_y + 148}" fill="{MUTED}" fill-opacity=".8" font-family="{MONO}" font-size="13">{esc(d2)}</text>
  </g>
"""
    defs = '    <filter id="glowSoft" x="-5%" y="-500%" width="110%" height="1100%"><feGaussianBlur stdDeviation="4"/></filter>\n'
    return svg(H, body, "Experience since 2020: Freelance, Poliedro, then Buildbox projects for MSD, Grupo Petrópolis, Lactalis and Linda Lifetech", defs)


# ------------------------------------------------------------------- stack

STACK = [
    ("Languages", ["typescript", "javascript", "go", "rust", "python", "node", "bun", "deno"]),
    ("Frameworks & UI", ["react", "next", "expo", "nest", "express", "fastify", "elysiajs", "electron", "tauri", "tailwind", "shadcn", "react-query"]),
    ("Data", ["postgres", "mysql", "mariadb", "mongo", "redis", "sqlite", "prisma", "drizzle", "sequelize", "supabase", "graphql"]),
    ("Cloud & infra", ["aws", "cloudflare", "vercel", "firebase", "docker", "kubernetes", "terraform", "pulumi", "sst", "apachekafka", "github-actions", "opentelemetry"]),
    ("Testing & DX", ["jest", "vitest", "cypress", "storybook", "biome", "eslint", "git", "vscode", "cursor", "claude", "figma"]),
]
# Icons drawn in dark ink that vanish on midnight: render them as a light silhouette
DARK_ICONS = {"rust", "prisma", "apachekafka", "cypress", "mysql", "electron"}


def build_stack() -> str:
    tile, icon, gap = 58, 34, 12
    label_w = 230
    row_h = tile + 16
    H = 150 + len(STACK) * row_h + 32
    body = page_bg(H)
    body += heading(48, 70, "Technologies", "The stack I use daily")
    y = 150
    for r, (label, icons) in enumerate(STACK):
        body += (
            f'  <g opacity="1">{fade(0.1 + 0.12 * r)}<text x="48" y="{y + tile / 2 + 5:.0f}" fill="{MUTED}" '
            f'font-family="{MONO}" font-size="13" letter-spacing="1.8">{esc(label.upper())}</text></g>\n'
        )
        for i, name in enumerate(icons):
            x = 48 + label_w + i * (tile + gap)
            uri = data_uri(SRC / "icons" / f"{name}.svg", "image/svg+xml")
            off = (tile - icon) / 2
            filt = ' filter="url(#whiten)"' if name in DARK_ICONS else ""
            body += (
                f'  <g opacity="1">{enter(0.15 + 0.12 * r + 0.035 * i)}'
                f"{panel(x, y, tile, tile, r=14)}"
                f'<image x="{x + off:.0f}" y="{y + off:.0f}" width="{icon}" height="{icon}" href="{uri}"{filt}>'
                f"<title>{esc(name)}</title></image>"
                f"</g>\n"
            )
        y += row_h
    whiten = (
        '    <filter id="whiten"><feColorMatrix type="matrix" '
        'values="0 0 0 0 .91  0 0 0 0 .93  0 0 0 0 .98  0 0 0 1 0"/></filter>\n'
    )
    return svg(H, body, "Tech stack: TypeScript, Go, Rust, React, Next.js, Expo, NestJS, PostgreSQL, Redis, AWS, Cloudflare, Docker, Kubernetes, Terraform, OpenTelemetry and more", whiten)


# ----------------------------------------------------------------- explore

def build_explore_card(label: str, desc: str, delay: float) -> str:
    w, h = 590, 112
    body = (
        f'  <g opacity="1">{fade(delay)}\n'
        f'    <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="{CARD}" stroke="url(#glassEdge)"/>\n'
        f'    <text x="32" y="50" fill="{FG}" font-family="{SANS}" font-size="21" font-weight="600">{esc(label)}</text>\n'
        f'    <text x="32" y="78" fill="{MUTED}" font-family="{SANS}" font-size="15">{esc(desc)}</text>\n'
        f'    <g>{lucide("arrow", w - 58, h / 2 - 12, 24, MUTED)}'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;3 -3;0 0" dur="2.4s" repeatCount="indefinite"/></g>\n'
        f"  </g>"
    )
    return svg(h, body, f"{label}: {desc}", width=w)


# --------------------------------------------------------------------- cta

def build_cta() -> str:
    H = 260
    defs, body = mesh(0, 0, W, H, 40, "ctaClip")
    body += (
        f'  <g opacity="1">{enter(0)}\n'
        f'    <text x="72" y="116" fill="#fff" font-family="{SANS}" font-size="40" font-weight="700" letter-spacing="-0.8">Want to build something together?</text>\n'
        f'    <text x="72" y="158" fill="#fff" fill-opacity=".75" font-family="{SANS}" font-size="19">Tell me what you are working on and we can see if it is a good fit.</text>\n'
        f"  </g>\n"
    )
    bx, by, bw, bh = W - 72 - 190, 104, 190, 54
    body += (
        f'  <g opacity="1">{enter(0.3)}\n'
        f'    <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="27" fill="{NEON}" filter="url(#glow)" opacity=".8">'
        f'<animate attributeName="opacity" values=".5;.95;.5" dur="3s" repeatCount="indefinite"/></rect>\n'
        f'    <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="27" fill="{NEON}"/>\n'
        f'    <text x="{bx + 32}" y="{by + 33}" fill="#fff" font-family="{SANS}" font-size="17" font-weight="600">Get in touch</text>\n'
        f'    {lucide("arrow", bx + bw - 50, by + 18, 18, "#fff")}\n'
        f"  </g>\n"
    )
    return svg(H, body, "Want to build something together? Get in touch", defs)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    files = {
        "hero": build_hero(),
        "layers": build_layers(),
        "about": build_about(),
        "experience": build_experience(),
        "stack": build_stack(),
        "cta": build_cta(),
        "explore-about": build_explore_card("About", "Who I am and how I work", 0.0),
        "explore-experience": build_explore_card("Experience", "Roles and what shipped", 0.15),
        "explore-technologies": build_explore_card("Technologies", "The stack I use daily", 0.3),
        "explore-contact": build_explore_card("Contact", "Start a conversation", 0.45),
    }
    for name, content in files.items():
        (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}.svg ({len(content) // 1024} KB)")


if __name__ == "__main__":
    main()

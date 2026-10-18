"""Builds the profile SVGs.

GitHub renders README images through a proxy that blocks external fonts and
images, so fonts and icons are inlined as base64. Edit assets/src/*.svg or the
data below, then run:  python3 assets/build.py
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).parent
W = 1200

# --------------------------------------------------------------------------- fonts

# css class -> (family, weight, style, file)
FACES = {
    "g4": ("Manrope", 400, "normal", "manrope-400.woff2"),
    "g5": ("Manrope", 500, "normal", "manrope-500.woff2"),
    "g7": ("Manrope", 700, "normal", "manrope-700.woff2"),
    "g8": ("Manrope", 800, "normal", "manrope-800.woff2"),
    "mono": ("Geist Mono", 400, "normal", "geist-mono-400.woff2"),
}
SANS = 'Manrope, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
CLASS_CSS = "\n      ".join([
    f".g4 {{ font-family: {SANS}; font-weight: 400; }}",
    f".g5 {{ font-family: {SANS}; font-weight: 500; }}",
    f".g7 {{ font-family: {SANS}; font-weight: 700; }}",
    f".g8 {{ font-family: {SANS}; font-weight: 800; }}",
    '.mono { font-family: "Geist Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-weight: 400; }',
])


def font_faces(svg):
    """@font-face rules for only the font classes this SVG actually uses."""
    used = {c for group in re.findall(r'class="([^"]*)"', svg) for c in group.split()}
    rules = []
    for cls, (family, weight, style, file) in FACES.items():
        if cls in used:
            data = base64.b64encode((ROOT / "fonts" / file).read_bytes()).decode()
            rules.append(
                f'@font-face {{ font-family: "{family}"; font-weight: {weight}; font-style: {style}; '
                f'src: url(data:font/woff2;base64,{data}) format("woff2"); }}'
            )
    return "\n      ".join(rules)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------- canvas

PALETTE = {"blue": "#0D99FF", "violet": "#A259FF", "pink": "#FF4D8D", "mint": "#3DDC97", "indigo": "#5B5BFF", "orange": "#FF7A45"}


def panel(h, blobs, body, title, desc, css=""):
    """A full-width rounded panel: gradient base, drifting aurora, vignette, glass edge."""
    grads, circles, anims = [], [], []
    for i, (color, cx, cy, r, a, dx, dy, dur) in enumerate(blobs):
        hexc = PALETTE[color]
        grads.append(
            f'<radialGradient id="g{i}"><stop offset="0" stop-color="{hexc}" stop-opacity="{a}"/>'
            f'<stop offset=".45" stop-color="{hexc}" stop-opacity="{a * .3:.2f}"/>'
            f'<stop offset="1" stop-color="{hexc}" stop-opacity="0"/></radialGradient>'
        )
        circles.append(f'<circle class="b{i}" cx="{cx}" cy="{cy}" r="{r}" fill="url(#g{i})"/>')
        anims.append(f".b{i} {{ animation: d{i} {dur}s ease-in-out infinite alternate; }} "
                     f"@keyframes d{i} {{ to {{ transform: translate({dx}px, {dy}px) }} }}")
    nl = "\n    "
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-labelledby="t d">
  <title id="t">{esc(title)}</title>
  <desc id="d">{esc(desc)}</desc>
  <defs>
    <linearGradient id="base" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#05060B"/><stop offset=".55" stop-color="#090C1A"/><stop offset="1" stop-color="#0E0A1C"/>
    </linearGradient>
    {nl.join(grads)}
    <radialGradient id="vignette" cx="45%" cy="45%" r="80%">
      <stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/>
    </radialGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".26"/><stop offset=".4" stop-color="#FFFFFF" stop-opacity=".05"/>
      <stop offset=".75" stop-color="#FFFFFF" stop-opacity=".04"/><stop offset="1" stop-color="#A259FF" stop-opacity=".35"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#151827" stop-opacity=".72"/><stop offset="1" stop-color="#0A0C14" stop-opacity=".6"/>
    </linearGradient>
    <linearGradient id="glassedge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".2"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity=".05"/><stop offset="1" stop-color="#FFFFFF" stop-opacity=".1"/>
    </linearGradient>
    <linearGradient id="serifgrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8FD0FF"/><stop offset=".5" stop-color="#C9A6FF"/><stop offset="1" stop-color="#FF9CC2"/>
    </linearGradient>
    <clipPath id="frame"><rect width="{W}" height="{h}" rx="28"/></clipPath>
    <style>
      /*@fonts*/
      {CLASS_CSS}
      {(nl + "  ").join(anims)}
      {css}
      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
    </style>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{h}" fill="url(#base)"/>
    {nl.join(circles)}
    <rect width="{W}" height="{h}" fill="url(#vignette)"/>
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{h - 1.5}" rx="27.5" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
{body}
</svg>
"""


def heading(index, label, plain, fancy, color="#4DB5FF"):
    """Section label + mixed grotesk/serif headline, shared by every panel."""
    return f"""
  <text x="64" y="76" class="mono" font-size="15" fill="{color}" letter-spacing="1.5">{index} <tspan fill="#4A5063">/</tspan> {label}</text>
  <text x="62" y="140" class="g8" font-size="50" letter-spacing="-1.6" fill="#F4F5F7">{plain} <tspan fill="url(#serifgrad)">{fancy}</tspan></text>"""


def glass(x, y, w, h, rx=16):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#glass)"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{rx - .5}" fill="none" stroke="url(#glassedge)"/>')


# --------------------------------------------------------------------------- about

def about():
    tiles = [
        ("End-to-end engineering", "Frontend, backend, APIs, data, mobile."),
        ("Product thinking", "The real problem, not just the ticket."),
        ("Architecture & ownership", "Planning, reviews, releases."),
    ]
    tw, gap = 344, 24
    tile_svg = []
    for i, (t, s) in enumerate(tiles):
        x = 64 + i * (tw + gap)
        tile_svg.append(f"""  {glass(x, 330, tw, 104)}
  <text x="{x + 24}" y="{372}" class="g7" font-size="21" fill="#F4F5F7">{esc(t)}</text>
  <text x="{x + 24}" y="{404}" class="g4" font-size="18" fill="#9AA0B1">{esc(s)}</text>""")
    para = [
        "I’m a full stack engineer from Sri Lanka. I work across the whole product — React and",
        "Next.js on the web, React Native on mobile, Node, Laravel and Postgres underneath — and I",
        "care about making it useful, maintainable and fast. Lately: what AI changes about how we build.",
    ]
    lines = "\n  ".join(f'<text x="64" y="{204 + i * 36}">{esc(l)}</text>' for i, l in enumerate(para))
    body = f"""{heading("01", "ABOUT", "Database to", "pixel.")}
  <g class="g4" font-size="24" fill="#A3A9BA">
  {lines}
  </g>
{chr(10).join(tile_svg)}"""
    return panel(480, [
        ("violet", 1120, 60, 420, .5, -150, 60, 20),
        ("blue", 80, 520, 380, .4, 160, -60, 18),
        ("mint", 640, -120, 300, .18, 120, 40, 16),
    ], body, "About Himesh",
        "Database to pixel. " + " ".join(para).replace("’", "'") + " "
        + " ".join(f"{t}: {s}" for t, s in tiles))


# --------------------------------------------------------------------------- work (flat cards)

ILLUSTRATIONS = {
    # phone with skeleton rows + shimmer + offline pill
    "scolaris": """
  <defs>
    <clipPath id="screen"><rect x="446" y="40" width="106" height="208" rx="15"/></clipPath>
    <linearGradient id="shine" x1="0" x2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset=".5" stop-color="#FFFFFF" stop-opacity=".14"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="440" y="34" width="118" height="220" rx="20" fill="#08090D" stroke="#2A2E3A" stroke-width="2"/>
  <rect x="481" y="44" width="36" height="7" rx="3.5" fill="#1C202B"/>
  <g clip-path="url(#screen)">
    <rect x="456" y="62" width="86" height="16" rx="5" fill="{accent}"/>
    <g fill="#1C202B">
      <circle cx="466" cy="100" r="8"/><rect x="480" y="93" width="58" height="6" rx="3"/><rect x="480" y="104" width="38" height="5" rx="2.5"/>
      <circle cx="466" cy="132" r="8"/><rect x="480" y="125" width="52" height="6" rx="3"/><rect x="480" y="136" width="44" height="5" rx="2.5"/>
      <circle cx="466" cy="164" r="8"/><rect x="480" y="157" width="58" height="6" rx="3"/><rect x="480" y="168" width="30" height="5" rx="2.5"/>
      <circle cx="466" cy="196" r="8"/><rect x="480" y="189" width="46" height="6" rx="3"/><rect x="480" y="200" width="40" height="5" rx="2.5"/>
    </g>
    <rect class="shine" x="380" y="40" width="60" height="208" fill="url(#shine)"/>
  </g>
  <rect x="460" y="220" width="78" height="20" rx="10" fill="{accent}" fill-opacity=".14" stroke="{accent}" stroke-opacity=".5"/>
  <text x="499" y="234" class="mono" font-size="11" fill="{accent}" text-anchor="middle">offline ✓</text>""",

    # gauge + sparkline
    "analyzer": """
  <circle cx="494" cy="104" r="54" fill="none" stroke="#1C202B" stroke-width="10"/>
  <circle class="arc" cx="494" cy="104" r="54" fill="none" stroke="{accent}" stroke-width="10" stroke-linecap="round" pathLength="100" stroke-dasharray="62 100" transform="rotate(-90 494 104)"/>
  <text x="494" y="100" class="mono" font-size="12" fill="#6B7184" text-anchor="middle" letter-spacing="1">CPU</text>
  <text x="494" y="122" class="g8" font-size="16" fill="{accent}" text-anchor="middle">calm</text>
  <rect x="426" y="182" width="140" height="62" rx="12" fill="#08090D" stroke="#20232D"/>
  <path class="spark" d="M436 228 L452 220 L466 224 L480 206 L494 214 L508 198 L522 210 L536 202 L556 208" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/>
  <circle class="blip" cx="556" cy="208" r="4" fill="{accent}"/>""",

    # 3x3 tool grid + command bar
    "memonaiq": """
  <g fill="#141720" stroke="#252936">
    <rect class="t t1" x="428" y="40" width="40" height="40" rx="10"/><rect class="t t2" x="478" y="40" width="40" height="40" rx="10"/><rect class="t t3" x="528" y="40" width="40" height="40" rx="10"/>
    <rect class="t t4" x="428" y="90" width="40" height="40" rx="10"/><rect class="t t5" x="478" y="90" width="40" height="40" rx="10"/><rect class="t t6" x="528" y="90" width="40" height="40" rx="10"/>
    <rect class="t t7" x="428" y="140" width="40" height="40" rx="10"/><rect class="t t8" x="478" y="140" width="40" height="40" rx="10"/><rect class="t t9" x="528" y="140" width="40" height="40" rx="10"/>
  </g>
  <g fill="none" stroke="#3A3F4E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M440 55 l6 5 -6 5 M450 66 h8"/>
    <path d="M492 52 h12 v16 h-12 z M492 58 h12"/>
    <circle cx="548" cy="60" r="8"/><path d="M548 52 v8 l5 3"/>
    <path d="M440 110 h16 M440 104 h10 M440 116 h12"/>
    <path d="M498 100 l-7 10 h14 z"/><circle cx="498" cy="114" r="1"/>
    <path d="M540 104 a8 8 0 1 0 16 0 a8 8 0 1 0 -16 0 M548 96 v16"/>
    <path d="M448 152 v16 M440 160 h16"/>
    <path d="M490 154 h16 v12 h-16 z M494 154 v-4 h8 v4"/>
    <path d="M540 168 l8 -16 8 16 z"/>
  </g>
  <rect x="428" y="204" width="140" height="36" rx="10" fill="#08090D" stroke="#20232D"/>
  <text x="442" y="227" class="mono" font-size="12" fill="#6B7184"><tspan fill="{accent}">⌘K</tspan> search<tspan class="caret" fill="#F4F5F7">▏</tspan></text>""",

    # topo map + route + hazard pulse
    "terra": """
  <defs><clipPath id="map"><rect x="420" y="32" width="148" height="212" rx="14"/></clipPath></defs>
  <rect x="420" y="32" width="148" height="212" rx="14" fill="#08090D" stroke="#20232D"/>
  <g clip-path="url(#map)" fill="none" stroke="#1F2330" stroke-width="1.5">
    <path d="M470 60 C520 40 580 70 570 120 C562 170 500 180 470 150 C440 125 430 75 470 60 Z"/>
    <path d="M478 76 C515 62 556 84 550 118 C545 152 504 160 482 140 C460 122 452 88 478 76 Z"/>
    <path d="M486 92 C512 84 536 98 532 118 C528 138 504 142 492 130 C478 118 472 98 486 92 Z"/>
    <path d="M496 104 C510 100 520 108 518 118 C516 126 504 128 498 122 C490 116 488 108 496 104 Z"/>
    <path d="M400 200 C440 180 470 210 520 196 C560 186 590 210 600 230"/>
    <path d="M400 222 C440 204 476 232 524 218 C560 208 590 232 600 252"/>
  </g>
  <path class="route" clip-path="url(#map)" d="M432 236 C452 210 448 190 472 176 C498 162 470 140 508 122 C530 112 534 84 556 50" fill="none" stroke="#F4F5F7" stroke-opacity=".7" stroke-width="2" stroke-dasharray="5 6" stroke-linecap="round"/>
  <circle class="pulse" cx="522" cy="104" r="14" fill="none" stroke="{accent}" stroke-width="2"/>
  <circle cx="522" cy="104" r="6" fill="{accent}"/>
  <rect x="432" y="44" width="62" height="20" rx="6" fill="{accent}" fill-opacity=".14" stroke="{accent}" stroke-opacity=".5"/>
  <text x="463" y="58" class="mono" font-size="11" fill="{accent}" text-anchor="middle">HIGH ▲</text>""",
}

CARD_CSS = """.dot { animation: live 2.4s ease-in-out infinite; }
      @keyframes live { 50% { opacity: .3 } }
      .shine { animation: shine 2.2s cubic-bezier(.4,0,.2,1) infinite; }
      @keyframes shine { to { transform: translateX(200px) } }
      .arc { animation: arc 6s cubic-bezier(.65,0,.35,1) infinite; }
      @keyframes arc { 0%,100% { stroke-dasharray: 38 100 } 50% { stroke-dasharray: 72 100 } }
      .spark { stroke-dasharray: 100; animation: spark 4s cubic-bezier(.2,.8,.2,1) infinite; }
      @keyframes spark { 0% { stroke-dashoffset: 100 } 60%,100% { stroke-dashoffset: 0 } }
      .blip { animation: live 1.2s ease-in-out infinite; }
      .t { animation: tile 4.5s infinite; }
      TILES
      @keyframes tile { 0%,14%,100% { fill: #141720; stroke: #252936 } 4%,8% { fill: #A259FF; fill-opacity: .18; stroke: #A259FF } }
      .caret { animation: blink 1.1s steps(1) infinite; }
      @keyframes blink { 50% { opacity: 0 } }
      .route { animation: march 1.6s linear infinite; }
      @keyframes march { to { stroke-dashoffset: -22 } }
      .pulse { transform-box: fill-box; transform-origin: center; animation: pulse 2s cubic-bezier(.2,.8,.2,1) infinite; }
      @keyframes pulse { 0% { transform: scale(.5); opacity: 1 } 100% { transform: scale(2); opacity: 0 } }""".replace(
    "TILES", " ".join(f".t{i} {{ animation-delay: {(i - 1) * .5}s; }}" for i in range(1, 10)))

CARDS = [
    dict(key="scolaris", title="Scolaris GO", accent="#0D99FF",
         status="SHIPPING", meta="School management · Mobile",
         desc=["Leading architecture &amp; delivery of", "a school app — offline-first, secure."],
         chips=["TypeScript", "React Native", "Expo"],
         alt="Scolaris GO (shipping): a school management mobile app — leading architecture, milestones, code reviews and app-store delivery, with offline support and security work. TypeScript, React Native, Expo."),
    dict(key="analyzer", title="System Analyzer", accent="#3DDC97",
         status="IN PROGRESS", meta="Native macOS · Observability",
         desc=["A calm, native workbench that explains", "what your Mac is doing — not just stats."],
         chips=["macOS", "Apple Silicon", "Perf"],
         alt="System Analyzer (in progress): a native macOS monitoring and recovery workbench that explains system health instead of dumping raw metrics."),
    dict(key="memonaiq", title="MemonaIQ", accent="#A259FF",
         status="BUILDING", meta="SaaS · Developer tools",
         desc=["Small, sharp utilities for web, infra", "&amp; security — each solving one thing."],
         chips=["Next.js", "PostgreSQL", "Prisma"],
         alt="MemonaIQ (building): an independent SaaS of focused utilities for web workflows, digital infrastructure and security. Next.js, PostgreSQL, Prisma."),
    dict(key="terra", title="Terra Watch", accent="#FF7A45",
         status="CONCEPT", meta="Geospatial · Public safety",
         desc=["A trail-hazard map that helps people", "choose safer routes, with confidence."],
         chips=["Next.js", "MapLibre", "PostGIS"],
         alt="Terra Watch (concept): a trail-hazard map with confidence-aware severity that helps people choose safer routes. Next.js, MapLibre GL JS, PostGIS, Drizzle."),
]


def chip_row(chips, y=270):
    out, x = [], 32
    for c in chips:
        w = round(len(c) * 8.2 + 24)
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="32" rx="9" fill="#151821" stroke="#252936"/>'
                   f'<text x="{x + w / 2}" y="{y + 21}" text-anchor="middle">{c}</text>')
        x += w + 8
    assert x < 580, chips
    return "\n    ".join(out)


def card(c, tx, ty, s):
    """A flat dark 600x340 project card, placed at (tx, ty) and scaled by s."""
    a, k = c["accent"], c["key"]
    status_w = round(len(c["status"]) * 8.4 + 46)
    desc = "\n    ".join(f'<text x="32" y="{200 + i * 27}">{line}</text>' for i, line in enumerate(c["desc"]))
    return f"""
  <g transform="translate({tx} {ty}) scale({s})">
  <defs>
    <radialGradient id="glow-{k}" cx="100%" cy="0%" r="80%">
      <stop offset="0" stop-color="{a}" stop-opacity=".16"/><stop offset="1" stop-color="{a}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x=".5" y=".5" width="599" height="339" rx="22" fill="#0E1016"/>
  <rect x=".5" y=".5" width="599" height="339" rx="22" fill="url(#glow-{k})" stroke="#20232D"/>
  <rect x="32" y="34" width="{status_w}" height="28" rx="14" fill="{a}" fill-opacity=".12" stroke="{a}" stroke-opacity=".35"/>
  <circle class="dot" cx="48" cy="48" r="4" fill="{a}"/>
  <text x="60" y="53" class="mono" font-size="13" fill="{a}" letter-spacing="1.2">{c['status']}</text>
  <text x="31" y="122" class="g8" font-size="42" letter-spacing="-1.2" fill="#FFFFFF">{c['title']}</text>
  <text x="32" y="156" class="mono" font-size="14" fill="#6B7184">{c['meta']}</text>
  <g class="g4" font-size="18" fill="#AEB3C2">
    {desc}
  </g>
  <g class="mono" font-size="14" fill="#C9CCD6">
    {chip_row(c['chips'])}
  </g>
{ILLUSTRATIONS[k].format(accent=a)}
  </g>"""


def work():
    s, gap, top = 0.9, 24, 176
    cw, ch = 600 * s, 340 * s
    cards = "".join(
        card(c, 48 + (i % 2) * (cw + gap), top + (i // 2) * (ch + gap), s)
        for i, c in enumerate(CARDS))
    h = round(top + 2 * ch + gap + 48)
    body = heading("02", "SELECTED WORK", "Things I’m", "building.") + cards
    return panel(h, [
        ("blue", 1140, 40, 460, .5, -160, 80, 20),
        ("pink", 40, h, 440, .32, 160, -80, 22),
        ("violet", 620, h / 2, 360, .22, -120, 40, 18),
    ], body, "Selected work",
        "Things I'm building. " + " ".join(c["alt"] for c in CARDS).replace("&amp;", "&"), CARD_CSS)


# --------------------------------------------------------------------------- toolkit

TOOLKIT = [
    ("FRONTEND & MOBILE", ["ts", "js", "react", "nextjs", "tailwind", "sass", "redux", "html", "css", "threejs", "figma"]),
    ("BACKEND & APIS", ["nodejs", "express", "laravel", "php", "py", "java"]),
    ("DATA & INFRA", ["postgres", "mysql", "mongodb", "prisma", "docker", "git", "linux", "nginx"]),
]
ALSO = ["React Native", "Expo", "MapLibre GL JS", "PostGIS", "Drizzle"]
EXPLORING = ["AI engineering", "AI-assisted workflows", "macOS tooling", "Performance"]
ICON_NAMES = {"ts": "TypeScript", "js": "JavaScript", "react": "React", "nextjs": "Next.js", "tailwind": "Tailwind CSS",
              "sass": "Sass", "redux": "Redux", "html": "HTML", "css": "CSS", "threejs": "Three.js", "figma": "Figma",
              "nodejs": "Node.js", "express": "Express", "laravel": "Laravel", "php": "PHP", "py": "Python", "java": "Java",
              "postgres": "PostgreSQL", "mysql": "MySQL", "mongodb": "MongoDB", "prisma": "Prisma", "docker": "Docker",
              "git": "Git", "linux": "Linux", "nginx": "Nginx"}


def pills(items, x, y, color="#D3D6DF", accent=None):
    out = []
    for it in items:
        w = round(len(it) * 9.7 + 32)
        stroke = accent or "#FFFFFF"
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="20" fill="{accent or "#FFFFFF"}" fill-opacity="{.12 if accent else .05}" '
                   f'stroke="{stroke}" stroke-opacity="{.45 if accent else .14}"/>'
                   f'<text x="{x + w / 2}" y="{y + 26}" text-anchor="middle" fill="{accent or color}">{esc(it)}</text>')
        x += w + 10
    assert x < W - 48, items
    return "\n  ".join(out)


def toolkit():
    size, step, x0 = 56, 68, 328
    rows, y = [], 186
    for label, icons in TOOLKIT:
        imgs = []
        for j, name in enumerate(icons):
            data = base64.b64encode((ROOT / "icons" / f"{name}.svg").read_bytes()).decode()
            imgs.append(f'<image class="ic" x="{x0 + j * step}" y="{y}" width="{size}" height="{size}" '
                        f'href="data:image/svg+xml;base64,{data}"><title>{ICON_NAMES[name]}</title></image>')
        rows.append(f'<text x="64" y="{y + 34}" class="mono" font-size="15" fill="#7A8197" letter-spacing="1.5">{esc(label)}</text>\n  '
                    + "\n  ".join(imgs))
        y += 84
    rows.append(f'<text x="64" y="{y + 26}" class="mono" font-size="15" fill="#7A8197" letter-spacing="1.5">ALSO</text>\n  '
                f'<g class="mono" font-size="16">{pills(ALSO, x0, y)}</g>')
    y += 64
    rows.append(f'<text x="64" y="{y + 26}" class="mono" font-size="15" fill="#5BE3A8" letter-spacing="1.5">EXPLORING ✦</text>\n  '
                f'<g class="mono" font-size="16">{pills(EXPLORING, x0, y, accent="#5BE3A8")}</g>')
    h = y + 40 + 56
    body = heading("03", "TOOLKIT", "The right tool,", "not the familiar one.", "#5BE3A8") + "\n  " + "\n  ".join(rows)
    names = [ICON_NAMES[n] for _, icons in TOOLKIT for n in icons]
    return panel(h, [
        ("mint", 1120, 80, 400, .3, -140, 60, 20),
        ("indigo", 160, h + 40, 420, .4, 160, -60, 22),
        ("blue", 700, -100, 320, .25, 100, 50, 17),
    ], body, "Toolkit",
        "The right tool, not the familiar one. " + ", ".join(names + ALSO) + ". Exploring: " + ", ".join(EXPLORING) + ".")


# --------------------------------------------------------------------------- how I build (code editor)

KW, STR, KEY, PUN, TYP, COM = "#C09BFF", "#5BE3A8", "#4DB5FF", "#7A8197", "#FF9CC2", "#4A5063"
CODE = [
    [("// the short version", COM)],
    [("const ", KW), ("himesh", "#F4F5F7"), (" = {", PUN)],
    [("  role", KEY), (": ", PUN), ('"Full Stack Engineer"', STR), (",", PUN)],
    [("  basedIn", KEY), (": ", PUN), ('"Sri Lanka"', STR), (",", PUN)],
    [("  buildsFor", KEY), (": [", PUN), ('"web"', STR), (", ", PUN), ('"mobile"', STR), (", ", PUN), ('"APIs"', STR), ("],", PUN)],
    [("  curiousAbout", KEY), (": [", PUN), ('"AI engineering"', STR), (", ", PUN), ('"developer tools"', STR), (", ", PUN), ('"performance"', STR), ("],", PUN)],
    [],
    [("  principles", KEY), (": [", PUN)],
    [("    ", PUN), ('"Simplicity over cleverness."', STR), (",", PUN)],
    [("    ", PUN), ('"Measure first, optimise second."', STR), (",", PUN)],
    [("    ", PUN), ('"Reusable components, not copy-paste."', STR), (",", PUN)],
    [("    ", PUN), ('"Real user value over features that only look impressive."', STR), (",", PUN)],
    [("    ", PUN), ('"Sometimes the best engineering is knowing what not to build."', STR), (",", PUN)],
    [("  ],", PUN)],
    [("} ", PUN), ("satisfies ", KW), ("Engineer", TYP), (";", PUN)],
]


def how_i_build():
    top, lh, fs = 176, 32, 19
    ex, ew = 48, W - 96
    code_top = top + 44 + 34
    eh = 44 + 34 + len(CODE) * lh + 20 + 36
    lines = []
    for i, toks in enumerate(CODE):
        y = code_top + i * lh
        spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in toks)
        lines.append(f'<text x="{ex + 28}" y="{y}" fill="#3A3F4E" text-anchor="end" font-size="15">{i + 1}</text>'
                     f'<text x="{ex + 52}" y="{y}" xml:space="preserve">{spans}</text>')
    last = code_top + (len(CODE) - 1) * lh
    caret_x = ex + 52 + len("} satisfies Engineer;") * fs * .6 + 4
    sb = top + eh - 36
    body = heading("04", "HOW I BUILD", "Principles,", "compiled.", "#C09BFF") + f"""
  {glass(ex, top, ew, eh, 18)}
  <line x1="{ex + 1}" y1="{top + 44}" x2="{ex + ew - 1}" y2="{top + 44}" stroke="#FFFFFF" stroke-opacity=".08"/>
  <circle cx="{ex + 24}" cy="{top + 22}" r="6" fill="#FF5F57"/><circle cx="{ex + 44}" cy="{top + 22}" r="6" fill="#FEBC2E"/><circle cx="{ex + 64}" cy="{top + 22}" r="6" fill="#28C840"/>
  <rect x="{ex + 92}" y="{top + 8}" width="128" height="36" rx="8" fill="#FFFFFF" fill-opacity=".06"/>
  <text x="{ex + 110}" y="{top + 31}" class="mono" font-size="14" fill="#D3D6DF"><tspan fill="#4DB5FF">TS</tspan>  himesh.ts</text>
  <g class="mono" font-size="{fs}">
  {chr(10).join("  " + l for l in lines)}
  </g>
  <rect class="caret" x="{caret_x}" y="{last - 18}" width="2.5" height="23" fill="#F4F5F7"/>
  <line x1="{ex + 1}" y1="{sb}" x2="{ex + ew - 1}" y2="{sb}" stroke="#FFFFFF" stroke-opacity=".08"/>
  <g class="mono" font-size="13" fill="#7A8197">
    <text x="{ex + 24}" y="{sb + 23}"><tspan fill="#5BE3A8">✓</tspan> 0 problems</text>
    <text x="{ex + ew - 24}" y="{sb + 23}" text-anchor="end">TypeScript · UTF-8 · Ln {len(CODE)}, Col 22</text>
  </g>"""
    h = top + eh + 48
    plain = "\n".join("".join(t for t, _ in toks) for toks in CODE)
    return panel(h, [
        ("violet", 1100, 120, 440, .45, -140, 80, 21),
        ("pink", 100, h + 60, 420, .3, 180, -60, 19),
        ("blue", 520, -120, 340, .25, 120, 60, 17),
    ], body, "How I build", "Principles, compiled. " + plain,
        ".caret { animation: blink 1.1s steps(1) infinite; } @keyframes blink { 50% { opacity: 0 } }")


# --------------------------------------------------------------------------- output

def write(name, svg):
    svg = svg.replace("/*@fonts*/", font_faces(svg))
    (ROOT / name).write_text(svg)
    print(f"wrote assets/{name}  ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    for src in sorted((ROOT / "src").glob("*.svg")):
        write(src.name, src.read_text())
    write("about.svg", about())
    write("work.svg", work())
    write("toolkit.svg", toolkit())
    write("how-i-build.svg", how_i_build())

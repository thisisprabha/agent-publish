"""OKLch color generation for agent-publish themes.

Zero-dependency OKLch → sRGB conversion. Generates deterministic palettes
for 5 curated directions with automatic dark-mode variants.
"""

import math
from typing import Union

Number = Union[int, float]

# ---------------------------------------------------------------------------
# Matrix helpers
# ---------------------------------------------------------------------------


def _mulmv(m: list[list[float]], v: list[float]) -> list[float]:
    """Multiply 3x3 matrix by 3-vector."""
    return [
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    ]


def _inv3x3(m: list[list[float]]) -> list[list[float]]:
    """Inverse of a 3x3 matrix."""
    # Cofactor matrix
    c = [[0.0] * 3 for _ in range(3)]
    c[0][0] = m[1][1] * m[2][2] - m[1][2] * m[2][1]
    c[0][1] = -(m[1][0] * m[2][2] - m[1][2] * m[2][0])
    c[0][2] = m[1][0] * m[2][1] - m[1][1] * m[2][0]
    c[1][0] = -(m[0][1] * m[2][2] - m[0][2] * m[2][1])
    c[1][1] = m[0][0] * m[2][2] - m[0][2] * m[2][0]
    c[1][2] = -(m[0][0] * m[2][1] - m[0][1] * m[2][0])
    c[2][0] = m[0][1] * m[1][2] - m[0][2] * m[1][1]
    c[2][1] = -(m[0][0] * m[1][2] - m[0][2] * m[1][0])
    c[2][2] = m[0][0] * m[1][1] - m[0][1] * m[1][0]

    det = m[0][0] * c[0][0] + m[0][1] * c[0][1] + m[0][2] * c[0][2]
    inv = [[0.0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            inv[i][j] = c[j][i] / det
    return inv


# ---------------------------------------------------------------------------
# OKLab matrices (Björn Ottosson)
# ---------------------------------------------------------------------------

# XYZ(D65) → LMS
_M1 = [
    [0.8189330101, 0.3618667424, -0.1288597137],
    [0.0329845436, 0.9293220910, 0.0361456387],
    [0.0482003018, 0.2643662691, 0.6335017077],
]

# LMS' → OKLab
_M2 = [
    [0.2104542553, 0.7936177850, -0.0040720468],
    [1.9779984951, -2.4285922050, 0.4505937099],
    [0.0259040371, 0.7827717662, -0.8086757660],
]

_INV_M1 = _inv3x3(_M1)
_INV_M2 = _inv3x3(_M2)

# XYZ(D65) → linear sRGB
_XYZ_TO_LINEAR_SRGB = [
    [3.240969941904521, -1.537383177570093, -0.498610760293056],
    [-0.969243636280880, 1.875967501507720, 0.041555057407176],
    [0.055630079696993, -0.203976958888976, 1.056971514242878],
]


# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------


def _cbrt(x: float) -> float:
    if x >= 0:
        return x ** (1.0 / 3.0)
    return -((-x) ** (1.0 / 3.0))


def _srgb_gamma(x: float) -> float:
    if x >= 0.0031308:
        return 1.055 * (x ** (1.0 / 2.4)) - 0.055
    return 12.92 * x


def _srgb_degammify(x: float) -> float:
    if x >= 0.04045:
        return ((x + 0.055) / 1.055) ** 2.4
    return x / 12.92


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _float_to_hex(c: float) -> str:
    ival = int(round(_clamp(c) * 255))
    return f"{ival:02x}"


# ---------------------------------------------------------------------------
# OKLch ↔ sRGB
# ---------------------------------------------------------------------------


def oklch_to_srgb(L: Number, C: Number, H: Number) -> str:
    """Convert OKLch(L, C, H°) to a hex string (#RRGGBB).

    Args:
        L: Lightness 0..1
        C: Chroma (typically 0..0.4)
        H: Hue in degrees 0..360

    Returns:
        Hex string including leading #.
    """
    hrad = math.radians(float(H))
    a = float(C) * math.cos(hrad)
    b = float(C) * math.sin(hrad)
    lab = [float(L), a, b]

    # OKLab → LMS'
    lms_ = _mulmv(_INV_M2, lab)
    # LMS' → LMS (cube)
    lms = [x**3 for x in lms_]
    # LMS → XYZ
    xyz = _mulmv(_INV_M1, lms)
    # XYZ → linear sRGB
    lin = _mulmv(_XYZ_TO_LINEAR_SRGB, xyz)
    # gamma + clamp
    srgb = [_clamp(_srgb_gamma(c)) for c in lin]

    r, g, bhex = (_float_to_hex(c) for c in srgb)
    return f"#{r}{g}{bhex}"


def rgb_to_oklch(r: Number, g: Number, b: Number) -> tuple[float, float, float]:
    """Convert sRGB (0-255) to OKLch (L, C, H).

    Useful for validating the round-trip in tests.
    """
    lin = [_srgb_degammify(c / 255.0) for c in (r, g, b)]
    # linear sRGB → XYZ (inverse of _XYZ_TO_LINEAR_SRGB)
    inv_srgb = _inv3x3(_XYZ_TO_LINEAR_SRGB)
    xyz = _mulmv(inv_srgb, lin)
    # XYZ → LMS
    lms = _mulmv(_M1, xyz)
    # LMS → LMS' (cbrt)
    lms_ = [_cbrt(x) for x in lms]
    # LMS' → OKLab
    lab = _mulmv(_M2, lms_)
    L, a, bval = lab
    C = math.sqrt(a * a + bval * bval)
    H = math.degrees(math.atan2(bval, a)) % 360
    return L, C, H


# ---------------------------------------------------------------------------
# Palette directions
# ---------------------------------------------------------------------------

# Each direction maps CSS variable name → OKLch(L, C, H)
# Dark variants are generated algorithmically.

_PALETTES: dict[str, dict[str, tuple[float, float, float]]] = {
    "editorial": {
        "bg": (0.97, 0.012, 55),
        "fg": (0.20, 0.02, 55),
        "muted": (0.55, 0.03, 55),
        "accent": (0.55, 0.14, 25),
        "accent-2": (0.65, 0.10, 50),
        "border": (0.90, 0.015, 55),
        "surface": (0.98, 0.01, 55),
        "code-bg": (0.94, 0.01, 55),
    },
    "modern-minimal": {
        "bg": (0.995, 0.005, 260),
        "fg": (0.15, 0.01, 260),
        "muted": (0.55, 0.015, 260),
        "accent": (0.52, 0.11, 240),
        "accent-2": (0.62, 0.08, 210),
        "border": (0.89, 0.01, 260),
        "surface": (1.0, 0.0, 0),
        "code-bg": (0.965, 0.005, 260),
    },
    "warm-soft": {
        "bg": (0.96, 0.018, 80),
        "fg": (0.30, 0.025, 80),
        "muted": (0.58, 0.035, 80),
        "accent": (0.55, 0.11, 45),
        "accent-2": (0.65, 0.09, 70),
        "border": (0.91, 0.015, 80),
        "surface": (0.97, 0.015, 80),
        "code-bg": (0.93, 0.015, 80),
    },
    "tech-utility": {
        "bg": (0.97, 0.008, 220),
        "fg": (0.18, 0.018, 220),
        "muted": (0.50, 0.025, 220),
        "accent": (0.55, 0.17, 220),
        "accent-2": (0.60, 0.12, 200),
        "border": (0.88, 0.012, 220),
        "surface": (0.99, 0.005, 220),
        "code-bg": (0.95, 0.008, 220),
    },
    "brutalist": {
        "bg": (1.0, 0.0, 0),
        "fg": (0.0, 0.0, 0),
        "muted": (0.50, 0.0, 0),
        "accent": (0.55, 0.20, 145),
        "accent-2": (0.65, 0.15, 120),
        "border": (0.70, 0.0, 0),
        "surface": (1.0, 0.0, 0),
        "code-bg": (0.95, 0.0, 0),
    },
}


def _dark_transform(
    L: float, C: float, H: float, reduce_chroma: bool = True
) -> tuple[float, float, float]:
    """Generate a dark-mode variant from a light-mode OKLch triple.

    Strategy:
      - Invert lightness around 0.5 (clamped).
      - Slightly reduce chroma for comfort.
      - Preserve hue.
    """
    L_dark = 1.0 - L
    # Keep dark values within readable bounds
    L_dark = max(0.03, min(0.97, L_dark))
    C_dark = C * 0.75 if reduce_chroma else C
    return L_dark, C_dark, H


def generate_palette(direction: str) -> dict[str, dict[str, str]]:
    """Generate light + dark hex palettes for a direction.

    Returns:
        {"light": {"bg": "#...", ...}, "dark": {"bg": "#...", ...}}
    """
    if direction not in _PALETTES:
        raise ValueError(f"Unknown direction: {direction}. Choose from {list(_PALETTES)}")

    src = _PALETTES[direction]
    light: dict[str, str] = {}
    dark: dict[str, str] = {}
    for name, (L, C, H) in src.items():
        light[name] = oklch_to_srgb(L, C, H)
        dark[name] = oklch_to_srgb(*_dark_transform(L, C, H))
    return {"light": light, "dark": dark}


# ---------------------------------------------------------------------------
# CSS generation
# ---------------------------------------------------------------------------


def _layout_css() -> str:
    """Default structural CSS that uses the color variables."""
    return """
*{box-sizing:border-box}
html{font-size:16px;scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
line-height:1.7;color:var(--fg);background:var(--bg);margin:0;padding:0;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent;transition:border-color .15s,color .15s}
a:hover{border-bottom-color:var(--accent)}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-bottom-color:transparent}
.skip-link{position:absolute;top:-40px;left:0;background:var(--accent);color:var(--bg);padding:.5rem 1rem;z-index:100;text-decoration:none;border-bottom:0;font-size:.875rem;font-weight:500}
.skip-link:focus{top:0}
.back{display:inline-block;margin:2rem auto 0;font-size:.8125rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;transition:color .15s}
.back:hover{color:var(--fg)}
.back:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
header,.main{max-width:720px;margin:0 auto;padding:1.75rem}
header{padding-bottom:.5rem}
.main{padding-top:0}
h1{font-size:1.625rem;font-weight:700;line-height:1.2;letter-spacing:-0.025em;margin:0;color:var(--fg)}
h2{font-size:1.125rem;font-weight:600;margin:2.5rem 0 1rem;padding-top:.5rem;border-top:2px solid var(--accent);color:var(--fg);position:relative}
h3{font-size:1rem;font-weight:600;margin:1.5rem 0 .5rem;color:var(--fg);position:relative}
h2 a.anchor,h3 a.anchor{opacity:0;position:absolute;left:-1.2em;top:.15em;font-size:.85em;text-decoration:none;border-bottom:0;transition:opacity .15s}
h2:hover a.anchor,h3:hover a.anchor{opacity:1}
p{margin:0 0 1.125rem}
.meta{font-size:.8125rem;color:var(--muted);margin-top:.5rem;letter-spacing:.01em}
table{width:100%;border-collapse:collapse;font-size:.875rem;margin:1.25rem 0;background:var(--surface);border-radius:6px;overflow:hidden}
tr{transition:background .12s}
tr:hover{background:rgba(0,0,0,.06)}
th,td{text-align:left;padding:.6rem .9rem;border-bottom:1px solid var(--border)}
thead th{font-weight:600;color:var(--fg);background:var(--code-bg);border-bottom:2px solid var(--border)}
ul{margin:0 0 1.125rem;padding-left:1.5rem}
li{margin-bottom:.4rem}
blockquote{border-left:3px solid var(--accent-2);margin:1.75rem 0;padding:.5rem 0 .5rem 1.25rem;color:var(--muted);font-style:italic;background:none}
code{background:var(--code-bg);padding:.18em .45em;border-radius:4px;font-size:.85em;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;color:var(--fg)}
pre{background:var(--code-bg);padding:1rem 1.25rem;border-radius:8px;overflow-x:auto;font-size:.82rem;margin:1.25rem 0;line-height:1.6;border:1px solid var(--border);transition:border-color .15s,box-shadow .15s}
pre:hover{border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,0,0,.06)}
pre:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,0,0,.06)}
pre code{background:none;padding:0;font-size:inherit}
.toc{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem 1.25rem;margin:0 0 1.75rem;font-size:.8125rem}
.toc ul{list-style:none;padding-left:0;margin:0}
.toc ul ul{padding-left:1.1rem;margin-top:.2rem}
.toc li{margin:0 0 .15rem}
.toc a{color:var(--accent);text-decoration:none;border-bottom:0}
.toc a:hover{text-decoration:underline}
.toc a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:640px){html{font-size:15px}header,.main{padding:1rem}h1{font-size:1.35rem}h2{font-size:1.05rem}table{font-size:.8rem;display:block;overflow-x:auto}pre{padding:.75rem}.toc{padding:.75rem}}
@media (max-width:1024px){header,.main{padding:1.25rem}}
@media print{body{background:#fff}a[href]:after{content:" (" attr(href) ")";font-size:.75rem;color:var(--muted)}.back{display:none}.toc{display:none}.skip-link{display:none}}
""".strip()


def generate_css(direction: str) -> str:
    """Generate a complete theme CSS string for a direction.

    Includes :root variables, layout, responsive, print, and dark mode.
    """
    palette = generate_palette(direction)
    light = palette["light"]
    dark = palette["dark"]

    root_vars = "\n".join(
        f"  --{name}:{light[name]};" for name in light
    )

    dark_vars = "\n".join(
        f"    --{name}:{dark[name]};" for name in dark
    )

    layout = _layout_css()

    # tr:hover needs a dark-mode variant because the rgba(0,0,0,.06)
    # works on light bg but not dark bg. We override it in the dark block.
    return f""":root{{
{root_vars}
}}
{layout}
@media (prefers-color-scheme:dark){{
{dark_vars}
  body{{background:var(--bg);color:var(--fg)}}
  a{{color:var(--accent)}}
  h2{{border-top-color:var(--accent)}}
  table{{background:var(--surface)}}
  thead th{{background:var(--code-bg)}}
  tr:hover{{background:rgba(255,255,255,.06)}}
  pre:hover{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(255,255,255,.08)}}
  blockquote{{border-left-color:var(--accent-2);color:var(--muted)}}
}}
"""


def list_directions() -> list[str]:
    """Return available direction names."""
    return list(_PALETTES.keys())

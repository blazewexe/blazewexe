"""Generate the self-contained LED-board header (dot-matrix scrolling sign)."""
from pathlib import Path

MESSAGE = "BLAZEEEEEE"
COLS_PER_SEC = 28          # scroll speed, in LED columns per second
GAP_COLS = 10              # blank columns between repeats
PITCH = 16                 # distance between LEDs in px
LIT = "#3dff7a"            # lit LED color
UNLIT = "#171a18"          # unlit LED color
BG = "#030403"             # board background

W, H = 900, 240
DX, DY = 34, 32            # display origin
COLS, ROWS = 52, 11        # display size in LEDs (832 x 176)

FONT = {
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
}

# build one unit of the strip: message + gap, as a list of lit (col, row)
lit, col = [], 0
for ch in MESSAGE:
    glyph = FONT[ch]
    for r, line in enumerate(glyph):
        for c, bit in enumerate(line):
            if bit == "1":
                lit.append((col + c, r))
    col += 6
unit_cols = col + GAP_COLS

row_off = (ROWS - 7) // 2
repeats = 2 + (COLS // unit_cols)
pix = []
for k in range(repeats):
    for c, r in lit:
        cx = (k * unit_cols + c) * PITCH + PITCH / 2
        cy = (r + row_off) * PITCH + PITCH / 2
        pix.append(
            f'<circle cx="{cx:g}" cy="{cy:g}" r="7.5" fill="{LIT}" opacity=".18"/>'
            f'<circle cx="{cx:g}" cy="{cy:g}" r="5" fill="{LIT}"/>'
        )
pix = "\n    ".join(pix)

dur = unit_cols / COLS_PER_SEC
shift = unit_cols * PITCH

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="LED board scrolling {MESSAGE.lower()}">
<defs>
  <pattern id="off" x="{DX}" y="{DY}" width="{PITCH}" height="{PITCH}" patternUnits="userSpaceOnUse">
    <circle cx="{PITCH/2:g}" cy="{PITCH/2:g}" r="4.5" fill="{UNLIT}"/>
  </pattern>
  <clipPath id="screen"><rect x="{DX}" y="{DY}" width="{COLS*PITCH}" height="{ROWS*PITCH}"/></clipPath>
  <style>
    .strip {{ animation: scroll {dur:.3f}s steps({unit_cols}, end) infinite }}
    @keyframes scroll {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-{shift}px) }} }}
    @media (prefers-reduced-motion: reduce) {{ .strip {{ animation: none }} }}
  </style>
</defs>
<rect width="{W}" height="{H}" fill="#000"/>
<rect x="18" y="18" width="864" height="204" rx="6" fill="{BG}" stroke="#2a2d2b" stroke-width="2"/>
<rect x="{DX}" y="{DY}" width="{COLS*PITCH}" height="{ROWS*PITCH}" fill="url(#off)"/>
<g clip-path="url(#screen)">
  <g transform="translate({DX} {DY})">
    <g class="strip">
    {pix}
    </g>
  </g>
</g>
</svg>
'''

Path(__file__).resolve().parents[1].joinpath("assets/header.svg").write_text(svg)
print(f"wrote assets/header.svg ({len(svg)} bytes, {dur:.2f}s loop)")

"""Generates assets/header.svg: equalizer bars and typed text, all locked to BPM.

Edit BPM / LINES, then run:  python scripts/make_header.py
"""
from pathlib import Path

BPM = 120
LINES = [
    "hi, im blaze",
    "github: blazewexe",
    "just a programmer",
    "building things on beat",
]
BEATS_PER_LINE = 4

W, H = 900, 240
BG, FG, ACCENT, MUTED = "#0d1117", "#e6edf3", "#1db954", "#7d8590"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
FS, CW = 38, 23  # font size, approx glyph advance for monospace
TX, TY = 48, 112

beat = 60 / BPM
line_dur = beat * BEATS_PER_LINE
cycle = line_dur * len(LINES)
type_pct = 100 * 2 * beat / cycle  # typing takes two beats

bars = []
n, x0, bw, pitch, base, maxh = 40, 48, 12, 20.1, 215, 64
for i in range(n):
    pat = i % 4
    delay = -((i * 0.37) % 2) * beat
    bars.append(
        f'<rect class="bar p{pat}" x="{x0 + i * pitch:.1f}" y="{base - maxh}" '
        f'width="{bw}" height="{maxh}" rx="2" style="animation-delay:{delay:.3f}s"/>'
    )

texts = []
for i, line in enumerate(LINES):
    width = len(line) * CW + 8
    delay = i * line_dur
    texts.append(
        f'''<g class="line" style="animation-delay:{delay:.3f}s">
  <text x="{TX}" y="{TY}" font-family="{FONT}" font-size="{FS}" fill="{FG}" xml:space="preserve">{line}</text>
  <rect class="cover" x="{TX}" y="{TY - FS}" width="{width}" height="{FS + 16}" fill="{BG}"
        style="animation-timing-function:steps({len(line)},end);animation-delay:{delay:.3f}s"/>
</g>'''
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"
     aria-label="hi, im blaze. github blazewexe. just a programmer.">
<style>
  .bar {{ fill:{ACCENT}; transform-box:fill-box; transform-origin:50% 100%;
         animation-duration:{beat * 2:.3f}s; animation-iteration-count:infinite;
         animation-timing-function:ease-in-out; opacity:.9 }}
  .p0 {{ animation-name:b0 }} .p1 {{ animation-name:b1 }}
  .p2 {{ animation-name:b2 }} .p3 {{ animation-name:b3 }}
  @keyframes b0 {{ 0%,100% {{ transform:scaleY(.12) }} 25% {{ transform:scaleY(1) }} 55% {{ transform:scaleY(.35) }} 80% {{ transform:scaleY(.7) }} }}
  @keyframes b1 {{ 0%,100% {{ transform:scaleY(.2) }} 20% {{ transform:scaleY(.55) }} 50% {{ transform:scaleY(.95) }} 75% {{ transform:scaleY(.3) }} }}
  @keyframes b2 {{ 0%,100% {{ transform:scaleY(.15) }} 30% {{ transform:scaleY(.8) }} 60% {{ transform:scaleY(.25) }} 85% {{ transform:scaleY(1) }} }}
  @keyframes b3 {{ 0%,100% {{ transform:scaleY(.25) }} 15% {{ transform:scaleY(.9) }} 45% {{ transform:scaleY(.4) }} 70% {{ transform:scaleY(.65) }} }}
  .pulse {{ fill:none; stroke:{ACCENT}; stroke-width:2; transform-box:fill-box; transform-origin:50% 50%;
           animation:ring {beat:.3f}s ease-out infinite }}
  @keyframes ring {{ 0% {{ transform:scale(.4); opacity:1 }} 100% {{ transform:scale(1.6); opacity:0 }} }}
  .dot {{ fill:{ACCENT} }}
  .line {{ opacity:0; animation-name:show; animation-duration:{cycle:.3f}s; animation-timing-function:linear;
          animation-iteration-count:infinite; animation-fill-mode:backwards }}
  @keyframes show {{ 0% {{ opacity:0 }} 1% {{ opacity:1 }} 24% {{ opacity:1 }} 25%,100% {{ opacity:0 }} }}
  .cover {{ transform-box:fill-box; transform-origin:100% 50%;
           animation-name:type; animation-duration:{cycle:.3f}s; animation-iteration-count:infinite; animation-fill-mode:backwards }}
  @keyframes type {{ 0% {{ transform:scaleX(1) }} {type_pct:.2f}% {{ transform:scaleX(0) }} 100% {{ transform:scaleX(0) }} }}
  @media (prefers-reduced-motion: reduce) {{
    .bar, .pulse, .cover, .line {{ animation:none }}
    .bar {{ transform:scaleY(.5) }} .cover {{ transform:scaleX(0) }}
    .line {{ opacity:0 }} .line:first-of-type {{ opacity:1 }}
  }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>
<text x="{W - 48}" y="44" text-anchor="end" font-family="{FONT}" font-size="14" fill="{MUTED}">{BPM} bpm</text>
<circle class="dot" cx="{TX + 4}" cy="44" r="4"/>
<circle class="pulse" cx="{TX + 4}" cy="44" r="9"/>
<text x="{TX + 22}" y="49" font-family="{FONT}" font-size="14" fill="{MUTED}">now playing</text>
{chr(10).join(texts)}
{chr(10).join(bars)}
</svg>
'''
Path(__file__).resolve().parents[1].joinpath("assets/header.svg").write_text(svg)
print("wrote assets/header.svg")

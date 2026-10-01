"""Generate the self-contained Pac-Man-inspired profile visualizer."""
from pathlib import Path

BPM = 67
USERNAME = "@blazewexe"
W, H = 900, 240
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BEAT = 60 / BPM

bars = []
heights = [34, 58, 82, 46, 68, 38, 92, 52, 74, 42, 64, 30]
for index, height in enumerate(heights):
    x = 330 + index * 22
    pattern = index % 4
    bars.append(
        f'''<rect class="bar p{pattern}" x="{x}" y="{198 - height}" width="12" height="{height}" rx="3" style="animation-delay:-{index * .17:.2f}s"/>'''
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Pac-Man-inspired music visualizer for {USERNAME}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop stop-color="#111936"/>
    <stop offset="1" stop-color="#080b19"/>
  </linearGradient>
  <linearGradient id="bars" x1="0" y1="0" x2="0" y2="1">
    <stop stop-color="#ffe66d"/>
    <stop offset="1" stop-color="#ff9f43"/>
  </linearGradient>
  <style>
    .bar {{ fill:url(#bars); transform-box:fill-box; transform-origin:50% 100%; animation-duration:{BEAT * 2:.2f}s; animation-iteration-count:infinite; animation-timing-function:ease-in-out }}
    .p0 {{ animation-name:low }} .p1 {{ animation-name:mid }} .p2 {{ animation-name:high }} .p3 {{ animation-name:jump }}
    .pac {{ animation:chomp .45s steps(2,end) infinite }}
    .ticker {{ animation:run 11s linear infinite }}
    @keyframes low {{ 0%,100% {{ transform:scaleY(.35) }} 50% {{ transform:scaleY(1) }} }}
    @keyframes mid {{ 0%,100% {{ transform:scaleY(.6) }} 50% {{ transform:scaleY(.25) }} }}
    @keyframes high {{ 0%,100% {{ transform:scaleY(.25) }} 50% {{ transform:scaleY(.9) }} }}
    @keyframes jump {{ 0%,100% {{ transform:scaleY(.8) }} 50% {{ transform:scaleY(.35) }} }}
    @keyframes chomp {{ from {{ opacity:1 }} to {{ opacity:.72 }} }}
    @keyframes run {{ from {{ transform:translateX(920px) }} to {{ transform:translateX(-360px) }} }}
    @media (prefers-reduced-motion:reduce) {{ .bar, .pac, .ticker {{ animation:none }} .ticker {{ transform:translateX(300px) }} }}
  </style>
</defs>
<rect width="{W}" height="{H}" rx="12" fill="url(#bg)" stroke="#343b61"/>
<path d="M28 39h28M28 39v28M872 201h-28M872 201v-28" fill="none" stroke="#ffdf5d" stroke-width="2"/>
<text x="54" y="49" fill="#9da9d8" font-family="{FONT}" font-size="13" letter-spacing="3">PAC//PLAY  |  {BPM} BPM</text>
<circle class="pac" cx="91" cy="101" r="29" fill="#ffdf5d"/>
<path class="pac" d="M91 101L120 84A29 29 0 0 0 120 118Z" fill="#111936"/>
<circle cx="98" cy="87" r="3" fill="#111936"/>
<g fill="#ffdf5d">
  <circle cx="139" cy="101" r="4"/><circle cx="160" cy="101" r="4"/><circle cx="181" cy="101" r="4"/>
</g>
<path d="M207 113h75" stroke="#ffdf5d" stroke-width="2" stroke-dasharray="2 8"/>
<path d="M239 89c8-13 28-13 36 0v34h-36z" fill="#ff5c8a"/>
<circle cx="250" cy="101" r="4" fill="#fff"/><circle cx="264" cy="101" r="4" fill="#fff"/>
<circle cx="250" cy="101" r="2" fill="#111936"/><circle cx="264" cy="101" r="2" fill="#111936"/>
<text x="54" y="166" fill="#f5f2df" font-family="{FONT}" font-size="31" font-weight="700" letter-spacing="2">{USERNAME}</text>
<text x="55" y="190" fill="#8490bd" font-family="{FONT}" font-size="12" letter-spacing="2">RUNNING ON GOOD VIBES</text>
<g>{chr(10).join(bars)}</g>
<path d="M330 198H594" stroke="#566087"/>
<g class="ticker" fill="#7cf7ff" font-family="{FONT}" font-size="13" letter-spacing="3">
  <text x="0" y="224">{USERNAME}  |  {USERNAME}  |  {USERNAME}  |  {USERNAME}</text>
</g>
</svg>
'''

Path(__file__).resolve().parents[1].joinpath("assets/header.svg").write_text(svg)
print("wrote assets/header.svg")

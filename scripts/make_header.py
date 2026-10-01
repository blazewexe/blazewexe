"""Generate the self-contained LED-board header."""
from pathlib import Path

USERNAME = "blazewexe"
W, H = 900, 240
FONT = "Courier New, monospace"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="LED board displaying {USERNAME}">
<defs>
  <pattern id="leds" width="12" height="12" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#37100b"/>
  </pattern>
  <filter id="glow" x="-20%" y="-80%" width="140%" height="260%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    .name {{ animation:scroll 18s ease-in-out infinite, flicker 6s linear infinite }}
    @keyframes scroll {{ 0%,100% {{ transform:translateX(-18px) }} 50% {{ transform:translateX(18px) }} }}
    @keyframes flicker {{ 0%,94%,100% {{ opacity:1 }} 95% {{ opacity:.72 }} 96% {{ opacity:1 }} }}
    @media (prefers-reduced-motion:reduce) {{ .name {{ animation:none }} }}
  </style>
</defs>
<rect width="{W}" height="{H}" fill="#080606"/>
<rect x="18" y="18" width="864" height="204" rx="3" fill="#120907" stroke="#642016" stroke-width="2"/>
<rect x="32" y="32" width="836" height="176" fill="url(#leds)"/>
<text class="name" x="450" y="153" text-anchor="middle" fill="#ff4b24" filter="url(#glow)" font-family="{FONT}" font-size="64" font-weight="700" letter-spacing="8">{USERNAME}</text>
</svg>
'''

Path(__file__).resolve().parents[1].joinpath("assets/header.svg").write_text(svg)
print("wrote assets/header.svg")

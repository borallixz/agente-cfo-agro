from urllib.parse import quote

VERDE = "#4CAF50"


def _uri(svg):
    return "data:image/svg+xml," + quote(svg)


def _icone(conteudo):
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64' fill='none' "
           f"stroke='{VERDE}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'>"
           + conteudo + "</svg>")
    return _uri(svg)


# ---------- ícones dos cartões ----------
MOEDA = _icone("<circle cx='32' cy='32' r='26'/><circle cx='32' cy='32' r='19'/>"
               f"<text x='32' y='41' font-size='26' text-anchor='middle' fill='{VERDE}' "
               "stroke='none' font-family='Arial'>$</text>")
GRAFICO = _icone("<path d='M6 56 H60'/><rect x='10' y='34' width='12' height='22'/>"
                 "<rect x='26' y='20' width='12' height='36'/><rect x='42' y='8' width='12' height='48'/>")
VAGEM = _icone("<path d='M6 44 C14 14 44 8 58 20 C52 50 22 58 6 44 Z'/>"
               "<circle cx='22' cy='38' r='5'/><circle cx='33' cy='31' r='5'/><circle cx='44' cy='26' r='5'/>")
BALANCA = _icone("<path d='M32 8 V54 M18 54 H46 M12 18 H52'/>"
                 "<path d='M12 18 L4 36 H20 Z'/><path d='M52 18 L44 36 H60 Z'/>")
TRATOR = _icone("<rect x='4' y='28' width='36' height='14' rx='3'/><path d='M24 28 V12 H38 V28'/>"
                "<path d='M10 28 V16'/><circle cx='44' cy='44' r='13'/><circle cx='44' cy='44' r='4'/>"
                "<circle cx='12' cy='48' r='8'/>")

# ---------- padrão de fundo (ícones de contorno bem suaves) ----------
_PADRAO = f"""<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 400 400'>
<g fill='none' stroke='{VERDE}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' opacity='0.11'>
<g transform='translate(40 50)'><circle r='22'/><circle r='16'/><text y='7' font-size='20' text-anchor='middle' fill='{VERDE}' stroke='none' font-family='Arial'>$</text></g>
<g transform='translate(150 40) rotate(-20)'><path d='M0 0 C20 -14 60 -14 80 0 C60 14 20 14 0 0 Z'/><circle cx='22' r='6'/><circle cx='40' r='6'/><circle cx='58' r='6'/></g>
<g transform='translate(300 20) rotate(8)'><rect width='44' height='56' rx='6'/><rect x='6' y='6' width='32' height='12' rx='2'/><circle cx='12' cy='30' r='2'/><circle cx='22' cy='30' r='2'/><circle cx='32' cy='30' r='2'/><circle cx='12' cy='40' r='2'/><circle cx='22' cy='40' r='2'/><circle cx='32' cy='40' r='2'/><circle cx='12' cy='49' r='2'/><circle cx='22' cy='49' r='2'/><circle cx='32' cy='49' r='2'/></g>
<g transform='translate(70 150) rotate(-8)'><line x1='0' y1='0' x2='0' y2='70'/><ellipse cx='-6' cy='10' rx='4' ry='8' transform='rotate(-30 -6 10)'/><ellipse cx='6' cy='10' rx='4' ry='8' transform='rotate(30 6 10)'/><ellipse cx='-6' cy='26' rx='4' ry='8' transform='rotate(-30 -6 26)'/><ellipse cx='6' cy='26' rx='4' ry='8' transform='rotate(30 6 26)'/><ellipse cx='-6' cy='42' rx='4' ry='8' transform='rotate(-30 -6 42)'/><ellipse cx='6' cy='42' rx='4' ry='8' transform='rotate(30 6 42)'/><ellipse cx='0' cy='-4' rx='4' ry='8'/></g>
<g transform='translate(170 190)'><rect x='0' y='14' width='46' height='16' rx='3'/><path d='M24 14 V0 H40 V14'/><line x1='6' y1='14' x2='6' y2='4'/><circle cx='38' cy='34' r='14'/><circle cx='38' cy='34' r='5'/><circle cx='8' cy='40' r='8'/></g>
<g transform='translate(340 200)'><circle r='14'/><circle r='10'/><text y='5' font-size='14' text-anchor='middle' fill='{VERDE}' stroke='none' font-family='Arial'>$</text></g>
<g transform='translate(40 300)'><line x1='0' y1='40' x2='46' y2='40'/><rect x='4' y='24' width='9' height='16'/><rect x='19' y='12' width='9' height='28'/><rect x='34' y='0' width='9' height='40'/></g>
<g transform='translate(140 320) rotate(15)'><path d='M0 0 C20 -14 60 -14 80 0 C60 14 20 14 0 0 Z'/><circle cx='22' r='6'/><circle cx='40' r='6'/><circle cx='58' r='6'/></g>
<g transform='translate(290 310) rotate(12)'><line x1='0' y1='0' x2='0' y2='70'/><ellipse cx='-6' cy='10' rx='4' ry='8' transform='rotate(-30 -6 10)'/><ellipse cx='6' cy='10' rx='4' ry='8' transform='rotate(30 6 10)'/><ellipse cx='-6' cy='26' rx='4' ry='8' transform='rotate(-30 -6 26)'/><ellipse cx='6' cy='26' rx='4' ry='8' transform='rotate(30 6 26)'/><ellipse cx='0' cy='-4' rx='4' ry='8'/></g>
<text x='108' y='128' font-size='30' fill='{VERDE}' stroke='none' font-family='Arial'>+</text>
<text x='232' y='132' font-size='30' fill='{VERDE}' stroke='none' font-family='Arial'>=</text>
<text x='352' y='120' font-size='28' fill='{VERDE}' stroke='none' font-family='Arial'>%</text>
<text x='20' y='250' font-size='30' fill='{VERDE}' stroke='none' font-family='Arial'>=</text>
<text x='356' y='372' font-size='30' fill='{VERDE}' stroke='none' font-family='Arial'>+</text>
</g></svg>"""

# ---------- ilustração do cabeçalho ----------
_HERO = """<svg xmlns='http://www.w3.org/2000/svg' width='360' height='160' viewBox='0 0 360 160'>
<circle cx='286' cy='42' r='22' fill='#F4B942' opacity='0.95'/>
<path d='M0 118 Q90 78 180 108 T360 96 V160 H0 Z' fill='#1B5E20' opacity='0.45'/>
<path d='M0 138 Q110 108 220 130 T360 124 V160 H0 Z' fill='#0F3D1E' opacity='0.55'/>
<g stroke='#A5D6A7' stroke-width='2' opacity='0.55'><path d='M10 160 L110 128'/><path d='M60 160 L130 130'/><path d='M120 160 L152 133'/><path d='M180 160 L180 134'/></g>
<g transform='translate(200 92)' stroke='none'>
<rect x='0' y='18' width='54' height='20' rx='4' fill='#E8F5E9'/>
<path d='M30 18 V2 H50 V18 Z' fill='#E8F5E9' opacity='0.85'/>
<rect x='6' y='6' width='4' height='14' fill='#E8F5E9'/>
<circle cx='44' cy='42' r='17' fill='#C8E6C9'/><circle cx='44' cy='42' r='6' fill='#1B5E20'/>
<circle cx='10' cy='48' r='10' fill='#C8E6C9'/><circle cx='10' cy='48' r='4' fill='#1B5E20'/>
</g>
<g transform='translate(320 130)'><ellipse cx='0' cy='10' rx='16' ry='5' fill='#F4B942'/><ellipse cx='0' cy='4' rx='16' ry='5' fill='#FFD36B'/><ellipse cx='0' cy='-2' rx='16' ry='5' fill='#F4B942'/></g>
<g transform='translate(30 30) rotate(-20)' fill='#C8E6C9' opacity='0.6'><path d='M0 0 C20 -12 56 -12 76 0 C56 12 20 12 0 0 Z'/></g>
</svg>"""

CSS = """<style>
.stApp {background-image: url("__PADRAO__"); background-size: 400px 400px; background-attachment: fixed;}
[data-testid="stHeading"] h3 {border-left: 4px solid #4CAF50; padding-left: 10px;}
.hero {position: relative; padding: 26px 30px; border-radius: 18px; margin-bottom: 18px; min-height: 140px; background-color: #2E7D32; background-image: url("__HERO__"), linear-gradient(135deg,#1F5A34,#2E7D32 60%,#4CAF50); background-repeat: no-repeat, no-repeat; background-position: right bottom, center; background-size: auto 100%, cover;}
.hero h1 {margin: 0; font-size: 2rem; color: #fff; padding: 0;}
.hero p {margin: 6px 0 0; color: #E8F5E9; font-size: 0.95rem; max-width: 60%;}
@media (max-width: 800px) {.hero {background-size: 0 0, cover;} .hero p {max-width: 100%;}}
.kpi {position: relative; overflow: hidden; background: #17271E; border: 1px solid #2A4034; border-radius: 14px; padding: 16px 18px; margin-bottom: 10px;}
.kpi::after {content: ""; position: absolute; right: 12px; bottom: 10px; width: 52px; height: 52px; opacity: 0.18; background-repeat: no-repeat; background-size: contain;}
.kpi.ic-coin::after {background-image: url("__MOEDA__");}
.kpi.ic-chart::after {background-image: url("__GRAFICO__");}
.kpi.ic-pod::after {background-image: url("__VAGEM__");}
.kpi.ic-scale::after {background-image: url("__BALANCA__");}
.kpi.ic-tractor::after {background-image: url("__TRATOR__");}
.kpi .label {font-size: 0.75rem; color: #9DB5A5; text-transform: uppercase; letter-spacing: 0.06em;}
.kpi .value {font-size: 1.6rem; font-weight: 700; color: #fff; margin-top: 4px;}
.kpi .sub {font-size: 0.8rem; color: #9DB5A5; margin-top: 2px; max-width: 75%;}
.verdict {border-radius: 14px; padding: 16px 20px; margin: 14px 0 8px;}
.verdict h3 {margin: 0 0 4px; font-size: 1.2rem; padding: 0;}
.verdict p {margin: 0; font-size: 0.92rem; color: #E8F0EA;}
</style>"""

for _chave, _valor in {"__PADRAO__": _uri(_PADRAO), "__HERO__": _uri(_HERO),
                       "__MOEDA__": MOEDA, "__GRAFICO__": GRAFICO, "__VAGEM__": VAGEM,
                       "__BALANCA__": BALANCA, "__TRATOR__": TRATOR}.items():
    CSS = CSS.replace(_chave, _valor)
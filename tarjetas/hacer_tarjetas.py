"""Imágenes de las tarjetas de la página principal (1200×560, versión clara y oscura), todas con el mismo diseño:
etiqueta, título en Fraunces con una palabra resaltada, subtítulo en Source Sans 3 e ilustración a la derecha.

Uso: python tarjetas/hacer_tarjetas.py <carpeta_con_los_repositorios>
Escribe en <repo>/docs/img/<nombre>_light.png y _dark.png de cada repositorio. Necesita Node.js con Playwright (Chromium).
"""
import sys
from pathlib import Path

import json
import subprocess
import tempfile

V, V2, V3, G, G2, G3 = "#774D78", "#AF8EB1", "#E6DAE7", "#5E8F88", "#8DB2AC", "#B7D0CC"

ILUS = {
    "comercio": f'''<svg viewBox="0 0 320 260"><path d="M30 190 Q160 240 290 190" fill="none" stroke="{G2}" stroke-width="5" stroke-dasharray="12 10"/>
      <rect x="70" y="90" width="150" height="120" rx="12" fill="#fff"/><rect x="70" y="90" width="150" height="30" rx="12" fill="{G}"/><rect x="132" y="90" width="22" height="120" fill="{G3}"/>
      <text x="80" y="172" font-family="Source Sans 3" font-weight="700" font-size="26" fill="#1d1a1c">ACE 18</text>
      <g transform="rotate(8 230 110)"><rect x="170" y="35" width="115" height="140" rx="12" fill="#fff" stroke="{V2}" stroke-width="5"/>
      <rect x="190" y="62" width="70" height="8" rx="4" fill="{V2}"/><rect x="190" y="82" width="60" height="8" rx="4" fill="{V3}"/><rect x="190" y="102" width="65" height="8" rx="4" fill="{V3}"/>
      <circle cx="252" cy="142" r="18" fill="{V}"/><path d="M243 142l7 7 12-13" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></g></svg>''',
    "aduana": f'''<svg viewBox="0 0 320 260"><rect x="60" y="20" width="185" height="230" rx="12" fill="#fff"/>
      <rect x="85" y="55" width="130" height="10" rx="5" fill="{G2}"/><rect x="85" y="85" width="105" height="10" rx="5" fill="{G3}"/><rect x="85" y="115" width="120" height="10" rx="5" fill="{G3}"/><rect x="85" y="145" width="90" height="10" rx="5" fill="{G3}"/>
      ''' + "".join(f'<rect x="{85+i*4.6:.1f}" y="185" width="{2 if i%3 else 3.5}" height="40" fill="#1d1a1c"/>' for i in range(22)) + f'''
      <g transform="rotate(-14 245 120)"><circle cx="245" cy="120" r="62" fill="none" stroke="{V}" stroke-width="7"/><circle cx="245" cy="120" r="50" fill="none" stroke="{V}" stroke-width="2.5"/>
      <text x="245" y="130" text-anchor="middle" font-family="Source Sans 3" font-weight="700" font-size="19" fill="{V}">ADUANA</text></g></svg>''',
    "tesis": f'''<svg viewBox="0 0 320 260"><circle cx="190" cy="28" r="14" fill="{G2}" opacity=".7"/><circle cx="208" cy="12" r="9" fill="{G2}" opacity=".6"/>
      <rect x="180" y="40" width="22" height="100" fill="{G}"/><path d="M40 125 L90 90 V125 L140 90 V125 L180 100 V215 H40 Z" fill="#fff"/><rect x="40" y="125" width="190" height="90" rx="10" fill="#fff"/>
      <rect x="60" y="150" width="32" height="30" rx="6" fill="{G2}"/><rect x="108" y="150" width="32" height="30" rx="6" fill="{G2}"/><rect x="156" y="150" width="32" height="30" rx="6" fill="{G2}"/>
      <path d="M255 100l50 18v40c0 34-22 52-50 64-28-12-50-30-50-64v-40z" fill="{V}"/><path d="M255 100l50 18v40c0 34-22 52-50 64z" fill="{V2}" opacity=".55"/>
      <path d="M236 160l14 14 26-28" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "normativa": f'''<svg viewBox="0 0 320 260"><rect x="190" y="14" width="100" height="50" rx="12" fill="{V}"/><path d="M206 64l-4 18 22-18z" fill="{V}"/>
      <circle cx="218" cy="39" r="6" fill="#fff"/><circle cx="240" cy="39" r="6" fill="#fff"/><circle cx="262" cy="39" r="6" fill="#fff"/>
      <path d="M140 52v26" stroke="{G}" stroke-width="6" stroke-linecap="round"/><circle cx="140" cy="46" r="10" fill="{V2}"/>
      <rect x="62" y="122" width="26" height="44" rx="10" fill="{G}"/><rect x="192" y="122" width="26" height="44" rx="10" fill="{G}"/>
      <rect x="80" y="78" width="120" height="104" rx="26" fill="{G}"/><rect x="96" y="96" width="88" height="66" rx="16" fill="#f5eef1"/>
      <path d="M113 124 q9-10 18 0 M149 124 q9-10 18 0" fill="none" stroke="#1f3f3a" stroke-width="5.5" stroke-linecap="round"/>
      <path d="M128 140 q12 11 24 0" fill="none" stroke="#1f3f3a" stroke-width="5.5" stroke-linecap="round"/>
      <rect x="54" y="196" width="172" height="54" rx="22" fill="{G2}"/><rect x="122" y="182" width="36" height="18" fill="{G}"/>
      <circle cx="140" cy="222" r="10" fill="#fff" opacity=".8"/></svg>''',
    "nomenclaturas": f'''<svg viewBox="0 0 320 260">''' + "".join(
        f'<g transform="translate({10+i*34},{14+i*88})"><rect width="245" height="58" rx="12" fill="#fff"/><rect width="62" height="58" rx="12" fill="{c}"/>'
        f'<text x="31" y="36" text-anchor="middle" font-family="Source Sans 3" font-weight="700" font-size="19" fill="{tc}">{a}</text>'
        f'<text x="78" y="39" font-family="ui-monospace,Menlo,monospace" font-weight="700" font-size="26" fill="#1d1a1c">{cod}</text></g>'
        for i, (a, cod, c, tc) in enumerate([("2002", "8525.20.22", G2, "#1d1a1c"), ("2007", "8517.12.31", G, "#fff"), ("2026", "8517.13.00", V, "#fff")]))
        + "".join(f'<path d="M{24+i*34} {76+i*88} v10 q0 12 12 12 h12" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>'
                  f'<path d="M{46+i*34} {91+i*88} l10 7 -10 7z" fill="currentColor"/>' for i in range(2)) + '</svg>',
    "listas": f'''<svg viewBox="0 0 320 260">''' + "".join(
        f'<g transform="translate({20+(i%2)*18},{18+i*58})"><rect width="270" height="46" rx="23" fill="#fff"/><rect width="78" height="46" rx="23" fill="{c}"/>'
        f'<text x="39" y="31" text-anchor="middle" font-family="Source Sans 3" font-weight="700" font-size="20" fill="{tc}">{s}</text>'
        f'<text x="94" y="30" font-family="Source Sans 3" font-weight="600" font-size="18" fill="#1d1a1c">{t}</text>'
        '</g>'
        for i, (s, t, c, tc) in enumerate([("BK", "Bienes de capital", V, "#fff"), ("BIT", "Informática", G, "#fff"),
                                           ("LNE", "Excepciones", V2, "#1d1a1c"), ("RMP", "Materias primas", G2, "#1d1a1c")])) + '</svg>',
    "textos": f'''<svg viewBox="0 0 320 260"><rect x="95" y="20" width="150" height="190" rx="12" fill="{G3}" transform="rotate(8 170 115)"/>
      <rect x="75" y="30" width="150" height="190" rx="12" fill="#fff"/><path d="M190 30h23a12 12 0 0 1 12 12v23z" fill="{G3}"/>
      <text x="95" y="72" font-family="Source Sans 3" font-weight="700" font-size="20" fill="{G}">ACE 72</text>
      <rect x="95" y="92" width="100" height="9" rx="4.5" fill="{G2}"/><rect x="95" y="114" width="110" height="9" rx="4.5" fill="{G3}"/><rect x="95" y="136" width="90" height="9" rx="4.5" fill="{G3}"/><rect x="95" y="158" width="105" height="9" rx="4.5" fill="{G3}"/>
      <circle cx="230" cy="170" r="42" fill="{V}"/><circle cx="230" cy="170" r="22" fill="none" stroke="#fff" stroke-width="8"/><path d="M246 186l20 20" stroke="#fff" stroke-width="10" stroke-linecap="round"/></svg>''',
    "graficos": f'''<svg viewBox="0 0 320 260"><rect x="20" y="20" width="135" height="105" rx="12" fill="#fff"/>
      <rect x="40" y="80" width="18" height="30" rx="3" fill="{G3}"/><rect x="66" y="62" width="18" height="48" rx="3" fill="{G2}"/><rect x="92" y="44" width="18" height="66" rx="3" fill="{G}"/><rect x="118" y="70" width="18" height="40" rx="3" fill="{G2}"/>
      <rect x="165" y="20" width="135" height="105" rx="12" fill="#fff"/>
      <path d="M182 105 L210 82 L235 92 L262 55 L285 45" fill="none" stroke="{V}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="285" cy="45" r="7" fill="{V}"/>
      <rect x="20" y="135" width="280" height="105" rx="12" fill="#fff"/>
      <path d="M50 170 H190" stroke="{G}" stroke-width="6" stroke-linecap="round"/><path d="M180 160 l14 10 -14 10" fill="none" stroke="{G}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="50" cy="170" r="7" fill="{G3}"/>
      <path d="M250 208 H110" stroke="{V2}" stroke-width="6" stroke-linecap="round"/><path d="M120 198 l-14 10 14 10" fill="none" stroke="{V2}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="250" cy="208" r="7" fill="{V3}"/></svg>''',
}

TARJ = [  # repositorio, archivo, etiqueta, título (con *resaltado*), subtítulo, ilustración
    ("comercio-exterior-paraguay-dnit-mic", "tarjeta", "Comercio exterior · Paraguay", "¿Cuánto comercio usa *de verdad* cada acuerdo?",
     "Despachos de la DNIT y certificados de origen de la VUE, 2011–2026.", "comercio"),
    ("comercio-exterior-paraguay-dnit-mic", "tarjeta_aduana", "Datos de aduana · Paraguay", "Cada despacho, *explicado* y para descargar",
     "Regímenes, aranceles, Turismo de Compras y archivos por año.", "aduana"),
    ("paraguay-exports-industrial-policy", "tarjeta", "Tesis · políticas industriales", "¿Un acuerdo comercial *protege* a Paraguay?",
     "Subsidios de los socios y exportaciones paraguayas, 2012–2022.", "tesis"),
    ("normativa-mercosur", "tarjeta", "Normativa del MERCOSUR", "Preguntale a *Commun[ia]* por las normas",
     "Las 1.130 decisiones del Consejo del Mercado Común, 1991–2026.", "normativa"),
    ("nomenclaturas-y-correlaciones-del-mercosur", "tarjeta", "Nomenclatura Común del MERCOSUR", "Cada código NCM, de *cualquier año* a hoy",
     "Versiones 2002–2026 y tablas de correlación encadenadas.", "nomenclaturas"),
    ("nomenclaturas-y-correlaciones-del-mercosur", "tarjeta_listas", "Listas de la nomenclatura · Paraguay", "Qué productos tienen un arancel *especial*",
     "Bienes de capital, informática, excepciones y materias primas, 2018–2026.", "listas"),
    ("silvia-mov.github.io", "tarjeta_graficos", "Gráficos interactivos · Paraguay", "El comercio exterior de Paraguay *en gráficos*",
     "A quién se le vende, con qué acuerdo y cuánto vale de verdad cada preferencia.", "graficos"),
    ("textos-acuerdos-paraguay", "tarjeta", "Acuerdos comerciales · Paraguay", "Cada acuerdo, *completo* y en un solo lugar",
     "Textos, anexos y protocolos de la ALADI: ACE 35, 36, 58, 59 y 72.", "textos"),
]

TEMAS = {"light": dict(g1=G3, g2=V3, t="#1d1a1c", r=V, s="#5b5160", pill="#fff", pt="#1d1a1c"),
         "dark": dict(g1="#24403c", g2="#3a2a3b", t="#f5eef1", r=V2, s="#bfb3b8", pill="#f5eef1", pt="#1d1a1c")}


def html(et, tit, sub, ilus, k):
    tit = tit.replace("*", "<em>", 1).replace("*", "</em>", 1)
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<style>html,body{{margin:0}}body{{width:1200px;height:560px;background:linear-gradient(120deg,{k["g1"]},{k["g2"]});font-family:"Source Sans 3";display:flex;align-items:center;box-sizing:border-box;padding:0 70px}}
.izq{{flex:1}}.pill{{display:inline-block;background:{k["pill"]};color:{k["pt"]};font-weight:700;font-size:21px;padding:8px 18px;border-radius:99px}}
h1{{font-family:Fraunces;font-weight:600;font-size:64px;line-height:1.08;color:{k["t"]};margin:22px 0 18px;max-width:640px;letter-spacing:-.5px}}em{{font-style:normal;color:{k["r"]}}}
p{{font-size:24px;color:{k["s"]};margin:0;max-width:620px;line-height:1.35}}.der{{color:{k["t"]}}}.der svg{{width:330px;height:270px;display:block}}</style></head>
<body><div class="izq"><span class="pill">{et}</span><h1>{tit}</h1><p>{sub}</p></div><div class="der">{ILUS[ilus]}</div></body></html>'''


NODE = """const {chromium}=require('playwright');const fs=require('fs');(async()=>{const L=JSON.parse(fs.readFileSync(process.argv[2]));
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:560}});
for(const [h,o] of L){await p.setContent(fs.readFileSync(h,'utf8'),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:o});console.log(o);}
await b.close()})();"""


def main(raiz):
    raiz = Path(raiz)
    tmp = Path(tempfile.mkdtemp())
    lista = []
    for repo, nombre, et, tit, sub, il in TARJ:
        for modo, k in TEMAS.items():
            h = tmp / f"{repo}_{nombre}_{modo}.html"
            h.write_text(html(et, tit, sub, il, k), encoding="utf-8")
            carpeta = raiz / repo / "img" if repo == "silvia-mov.github.io" else raiz / repo / "docs" / "img"
            lista.append([str(h), str(carpeta / f"{nombre}_{modo}.png")])
    (tmp / "lista.json").write_text(json.dumps(lista))
    (tmp / "render.js").write_text(NODE)
    subprocess.run(["node", str(tmp / "render.js"), str(tmp / "lista.json")], check=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "..")

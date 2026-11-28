"""Gráficos de Datawrapper de la página «Gráficos de comercio exterior» (graficos/index.html).

Uso: python graficos_datawrapper.py <carpeta docs/datos del repositorio comercio-exterior-paraguay-acuerdos>
Crea o actualiza cada gráfico (números en graficos/datawrapper_ids.json) y guarda los datos de cada uno en
graficos/datos/ (CSV y Excel). Necesita acceso a api.datawrapper.de con la clave configurada.
"""
import json
import os
import sys
from pathlib import Path

import gettext

import pandas as pd
import pycountry
import requests

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "graficos" / "datos"
IDS = RAIZ / "graficos" / "datawrapper_ids.json"
API = "https://api.datawrapper.de/v3"
H = {"Authorization": "Bearer " + os.environ.get("DATAWRAPPER_TOKEN", "proxy-injected")}
PUBLICAR = {"blocks": {"logo": {"enabled": False}, "embed": False, "download-pdf": False, "download-svg": False,
                       "get-the-data": True, "download-image": True}, "autoDarkMode": True}
FUENTE = {"source-name": "DNIT, despachos de exportación (cálculo propio)",
          "source-url": "https://silvia-mov.github.io/comercio-exterior-paraguay-acuerdos/", "byline": ""}


def guardar(df, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA / f"{nombre}.csv", index=False, encoding="utf-8-sig")
    df.to_excel(SALIDA / f"{nombre}.xlsx", index=False)


def grafico(clave, tipo, titulo, df, describe, visualize, notas="", extra=None):
    ids = json.loads(IDS.read_text()) if IDS.exists() else {}
    if clave not in ids:
        r = requests.post(f"{API}/charts", headers=H, json={"title": titulo, "type": tipo}, timeout=60)
        r.raise_for_status()
        ids[clave] = r.json()["id"]
        IDS.parent.mkdir(parents=True, exist_ok=True)
        IDS.write_text(json.dumps(ids, indent=1, ensure_ascii=False))
    cid = ids[clave]
    requests.put(f"{API}/charts/{cid}/data", headers={**H, "Content-Type": "text/csv"},
                 data=df.to_csv(index=False).encode("utf-8"), timeout=60).raise_for_status()
    meta = {"describe": {**FUENTE, **describe}, "annotate": {"notes": notas},
            "visualize": {"dark-mode-invert": True, "show-tooltips": True, **visualize}, "publish": PUBLICAR, **(extra or {})}
    requests.patch(f"{API}/charts/{cid}", headers=H, timeout=60,
                   json={"title": titulo, "type": tipo, "language": "es-AR", "metadata": meta}).raise_for_status()
    requests.post(f"{API}/charts/{cid}/publish", headers=H, timeout=120).raise_for_status()
    print(clave, f"https://datawrapper.dwcdn.net/{cid}/")
    return cid


ES = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["es"])
CORTOS = {"KOR": "Corea del Sur", "PRK": "Corea del Norte", "RUS": "Rusia", "TWN": "Taiwán", "IRN": "Irán", "SYR": "Siria",
          "VNM": "Vietnam", "LAO": "Laos", "MDA": "Moldavia", "TZA": "Tanzania", "COD": "República Democrática del Congo", "CIV": "Costa de Marfil"}


def nombre_es(iso3):
    """Nombre del país en español, corto: «Bolivia, Estado plurinacional de» -> «Bolivia»."""
    if iso3 in CORTOS:
        return CORTOS[iso3]
    return ES.gettext(pycountry.countries.get(alpha_3=iso3).name).split(",")[0]


def numeros(d, cols):
    for c in cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d


def mapa(datos):
    d = pd.read_csv(Path(datos) / "exportaciones_por_pais.csv", keep_default_na=False, na_values=[""], encoding="utf-8-sig")
    anio = int(pd.read_csv(Path(datos) / "utilizacion_por_anio.csv", encoding="utf-8-sig").query("MESES == 12")["AÑO"].max())
    a = numeros(d[d["AÑO"] == anio].copy(), ["DNIT_EXPORTADO_USD", "DNIT_CON_ACUERDO_USD"])
    a = a[a["DNIT_EXPORTADO_USD"] >= 1e6]                                   # menos de USD 1 millón: sin color
    a["ISO3"] = [getattr(pycountry.countries.get(alpha_2=c), "alpha_3", None) for c in a["CODIGO_PAIS"]]
    a = a.dropna(subset=["ISO3"])
    w = pd.DataFrame({"ISO3": a["ISO3"], "Pais": a["ISO3"].map(nombre_es), "Exportado": (a["DNIT_EXPORTADO_USD"] / 1e6).round(1),
                      "ConAcuerdo": (a["DNIT_CON_ACUERDO_USD"] / 1e6).round(1),
                      "Pct": (100 * a["DNIT_CON_ACUERDO_USD"] / a["DNIT_EXPORTADO_USD"]).round(1)})
    guardar(w, "mapa_preferencias")
    fuera = w[~w["ISO3"].isin(["ARG", "BRA", "URY", "CHL", "BOL", "PER", "COL", "ECU", "VEN", "MEX"])]
    pct_fuera = 100 * fuera["ConAcuerdo"].sum() / fuera["Exportado"].sum()
    return grafico("mapa", "d3-maps-choropleth",
                   f"Fuera de América Latina, casi nada entra con preferencia: el {pct_fuera:.1f}% de lo que Paraguay vende allí".replace(".", ","),
                   w, {"intro": f"% de lo que Paraguay exportó a cada país en {anio} que entró pagando menos aranceles gracias a un acuerdo "
                                "comercial. Pasá el mouse o el dedo por un país para ver cuánto se le vendió."},
                   {"basemap": "world-2019", "map-key-attr": "DW_STATE_CODE",
                    "colorscale": {"enabled": True, "mode": "continuous", "interpolation": "equidistant", "stops": "equidistant",
                                   "stopCount": 4, "rangeMin": 0, "rangeMax": 100, "rangeCenter": "", "customStops": [],
                                   "colors": [{"color": "#efe9ee", "position": 0}, {"color": "#af8eb1", "position": 0.5},
                                              {"color": "#4f3050", "position": 1}]},
                    "tooltip": {"enabled": True, "title": "{{ pais }}",
                                "body": "Exportó USD {{ FORMAT(exportado, \"0,0.[0]\") }} millones; con acuerdo, "
                                        "{{ FORMAT(pct, \"0.[0]\") }}%."},
                    "legends": {"color": {"enabled": True, "title": "% con acuerdo", "labels": "ranges", "position": "above", "size": 170}}},
                   "Países con exportaciones de al menos USD 1 millón; el resto, en gris. El país es el destino declarado en el despacho.",
                   extra={"axes": {"keys": "ISO3", "values": "Pct"}})


def flechas(datos):
    u = pd.read_csv(Path(datos) / "utilizacion_por_socio.csv", keep_default_na=False, na_values=[""], encoding="utf-8-sig")
    u = numeros(u, ["TASA_UTILIZACION_PCT", "DNIT_EXPORTADO_USD"])
    nom = {"ARGENTINA": "Argentina", "BRASIL": "Brasil", "URUGUAY": "Uruguay", "CHILE": "Chile", "BOLIVIA": "Bolivia",
           "PERU": "Perú", "COLOMBIA": "Colombia", "MEXICO": "México", "ISRAEL": "Israel"}
    w = u[u["PAIS"].isin(nom) & u["AÑO"].isin([2011, 2025])].pivot_table(index="PAIS", columns="AÑO", values="TASA_UTILIZACION_PCT")
    w = w.rename(index=nom).round(1).reset_index().rename(columns={"PAIS": "Socio", 2011: "2011", 2025: "2025"})
    w = w.sort_values("2025", ascending=False)
    guardar(w, "uso_por_socio_2011_2025")
    return grafico("flechas", "d3-arrow-plot",
                   "Desde 2011, el uso de los acuerdos subió con Bolivia, Chile, Perú y Uruguay, y bajó con Brasil y México", w,
                   {"intro": "% de lo exportado a cada socio que entró con preferencia arancelaria. La flecha va de 2011 a 2025.",
                    "number-format": "0.[0]", "number-append": "%"},
                   {"range-extent": "custom", "custom-range": ["0", "100"], "show-color-key": True, "range-value-labels": "both",
                    "label-first-range": True, "base-color": "#5e8f88", "thick": True, "sort-range": {"enabled": False}},
                   "Socios con acuerdo vigente y al menos USD 20 millones exportados en 2025.")


if __name__ == "__main__":
    mapa(sys.argv[1])
    flechas(sys.argv[1])

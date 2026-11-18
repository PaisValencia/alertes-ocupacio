"""Programa principal: executa cada font i publica els resultats a la carpeta docs/.

Ús:
    python principal.py                       # totes les fonts
    python principal.py --fonts boe,cido      # només algunes
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import traceback
from html import escape
from pathlib import Path

from fonts import bop_valencia, boe, cido, comu

ARREL = Path(__file__).resolve().parent
DOCS = ARREL / "docs"
DADES = ARREL / "dades"  # memòria cau i historials (es guarden al repositori)

FONTS = {
    "boe": ("BOE (API oficial)", lambda: boe.executa(DOCS, DADES / "cache_boe.json")),
    "cido": ("CIDO, Catalunya (API oficial)", lambda: cido.executa(DOCS)),
    "bop_valencia": ("BOP de València (experimental)", lambda: bop_valencia.executa(DOCS, DADES / "historial_bop_valencia.json")),
}


def pagina_index(estat: dict) -> str:
    files = "".join(
        f"<tr><td>{escape(v['nom'])}</td><td>{'✔' if v['ok'] else '✖'}</td><td>{v['total']}</td>"
        f"<td><a href='{k}.json'>{k}.json</a></td><td><a href='{k}.xml'>{k}.xml</a></td>"
        f"<td>{escape(v.get('error') or '')}</td></tr>"
        for k, v in estat["fonts"].items()
    )
    return f"""<!DOCTYPE html><html lang="ca"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alertes ocupació filologia</title>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#222}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #ddd;padding:.5rem;text-align:left}}
code{{background:#f4f4f4;padding:.1rem .3rem}}</style></head><body>
<h1>Alertes ocupació filologia</h1>
<p>Última actualització: <strong>{escape(estat['actualitzat'])}</strong> (UTC).</p>
<p>Totes les fonts juntes: <a href="totes.json">totes.json</a> · <a href="totes.xml">totes.xml (RSS)</a> · <a href="estat.json">estat.json</a></p>
<table><tr><th>Font</th><th>Estat</th><th>Places</th><th>JSON</th><th>RSS</th><th>Error</th></tr>{files}</table>
<p>Els terminis marcats com a «estimat» s'han calculat a partir del text; confirma'ls sempre en les bases.</p>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", default=",".join(FONTS))
    args = ap.parse_args()
    DOCS.mkdir(exist_ok=True)
    DADES.mkdir(exist_ok=True)

    estat_path = DOCS / "estat.json"
    anterior = json.loads(estat_path.read_text(encoding="utf-8")) if estat_path.exists() else {"fonts": {}}
    estat = {"actualitzat": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "fonts": anterior.get("fonts", {})}

    totes = []
    for clau in [f.strip() for f in args.fonts.split(",") if f.strip()]:
        nom, funcio = FONTS[clau]
        print(f"== {nom}")
        try:
            res = funcio()
            estat["fonts"][clau] = {"nom": nom, "ok": True, "total": len(res), "error": None}
            print(f"   {len(res)} convocatòries")
        except Exception as exc:
            traceback.print_exc()
            estat["fonts"][clau] = {"nom": nom, "ok": False, "total": 0, "error": f"{exc.__class__.__name__}: {exc}"[:300]}

    # Fitxer conjunt amb el que hi haja publicat de cada font (també el d'execucions anteriors)
    for clau in FONTS:
        f = DOCS / f"{clau}.json"
        if f.exists():
            totes += json.loads(f.read_text(encoding="utf-8")).get("convocatories", [])
    comu.desa("totes", "Alertes ocupació filologia: totes les fonts",
              "BOE, CIDO i BOP de València: convocatòries de filologia i llengua amb el termini obert.",
              totes, DOCS, "")
    estat_path.write_text(json.dumps(estat, ensure_ascii=False, indent=2), encoding="utf-8")
    (DOCS / "index.html").write_text(pagina_index(estat), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    return 0 if any(v["ok"] for v in estat["fonts"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())

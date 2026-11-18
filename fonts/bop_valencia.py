"""Font BOP de València (EXPERIMENTAL).

La web bop.dival.es genera els enllaços amb JavaScript i no té API ni RSS. Este mòdul obri la
web amb un navegador sense pantalla (Playwright), passa per totes les pàgines del butlletí del
dia, llig el text de cada anunci i aplica les paraules clau. Només s'executa si robots.txt ho permet.

Com que cada dia només es veu el butlletí del dia, els resultats es guarden en un historial
de 45 dies perquè no es perden.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

from . import comu

URL = "https://bop.dival.es/bop/"
DIES_HISTORIAL = 45
MAX_PAGINES = 60
RE_REGISTRE = re.compile(r"N[úu]m\.?\s*registre:?\s*(\d{4}/\d+)", re.IGNORECASE)


def _anuncis_del_dia() -> list[dict]:
    from playwright.sync_api import sync_playwright  # només cal en GitHub Actions

    anuncis, vistos = [], set()
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(user_agent=comu.USER_AGENT)
        pag.goto(URL, wait_until="networkidle", timeout=90_000)
        for _ in range(MAX_PAGINES):
            text = pag.inner_text("body")
            # Cada anunci porta «Núm. registre: AAAA/NNNNN»: tallem el text per ahí.
            trossos = RE_REGISTRE.split(text)
            # trossos = [abans, reg1, després1, reg2, després2, ...]; el títol va just abans del registre
            for i in range(1, len(trossos), 2):
                registre = trossos[i]
                if registre in vistos:
                    continue
                vistos.add(registre)
                titol = comu.normalitza(trossos[i - 1][-600:])
                anuncis.append({"registre": registre, "text": titol})
            # Pàgina següent. Si el botó no respon, ens quedem amb el que ja s'ha llegit.
            try:
                seguent = pag.locator(".ui-paginator-next:not(.ui-state-disabled)").first
                if seguent.count() == 0 or not seguent.is_visible():
                    break
                seguent.click(timeout=10_000)
                pag.wait_for_load_state("networkidle", timeout=30_000)
            except Exception as exc:
                print(f"BOP València: no es pot passar de pàgina ({exc.__class__.__name__}); es continua amb {len(anuncis)} anuncis.")
                break
        nav.close()
    if not anuncis:
        raise RuntimeError("no s'ha trobat cap anunci amb «Núm. registre» a la pàgina (potser ha canviat la web)")
    print(f"BOP València: {len(anuncis)} anuncis llegits")
    return anuncis


def executa(carpeta: Path, historial_path: Path) -> list[dict]:
    avui = dt.date.today()
    historial = json.loads(historial_path.read_text(encoding="utf-8")) if historial_path.exists() else {}
    error = None
    if not comu.permes(URL):
        error = "robots.txt no permet llegir bop.dival.es"
        print("BOP València: robots.txt no ho permet; no es llig.")
    else:
        try:
            for a in _anuncis_del_dia():
                ok, motiu = comu.interessa(a["text"])
                if not ok or a["registre"] in historial:
                    continue
                historial[a["registre"]] = {
                    "id": f"BOPV-{a['registre']}",
                    "font": "BOP València",
                    "titol": a["text"][-300:],
                    "organisme": None,
                    "data_publicacio": avui.isoformat(),
                    "font_publicacio": "BOP València",
                    "enllac": URL,
                    "registre": a["registre"],
                    "termini_text": "Consulta l'anunci (cerca el número de registre al BOP)",
                    "data_fi": None,
                    "termini_estimat": True,
                    "reservada": comu.es_reservada(a["text"]),
                    "motiu": motiu,
                }
        except Exception as exc:
            error = f"{exc.__class__.__name__}: {str(exc).splitlines()[0][:200]}"
            print(f"BOP València: error ({error}); es manté l'historial anterior.")
    limit = (avui - dt.timedelta(days=DIES_HISTORIAL)).isoformat()
    historial = {k: v for k, v in historial.items() if v["data_publicacio"] >= limit}
    historial_path.write_text(json.dumps(historial, ensure_ascii=False, indent=1), encoding="utf-8")
    resultats = list(historial.values())
    comu.desa("bop_valencia", "BOP de València: anuncis de filologia i llengua (experimental)",
              "Anuncis dels últims 45 dies del BOP de València filtrats per paraules clau. "
              "Busca el número de registre a bop.dival.es per a obrir l'anunci.",
              resultats, carpeta, URL)
    if error:
        raise RuntimeError(error + " (es publica l'historial anterior)")
    return resultats

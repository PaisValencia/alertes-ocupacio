"""Font CIDO: API oficial de dades obertes de la Diputació de Barcelona.

Recull els processos selectius i les borses de tot Catalunya (DOGC, BOE i els quatre BOP catalans).
Documentació: https://dadesobertes.diba.cat/sites/default/files/public/documentacio_api_cido.pdf
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from . import comu

API = "https://api.diba.cat/dadesobertes/cido/v1/oposicions"
# Fragments de paraula (sense accents) que es busquen dins del títol
FRAGMENTS = ["ling", "normalitzaci", "catal", "valenci", "llengua", "professor", "portugu",
             "correcci", "corrector", "traducci", "traductor", "assessor", "filologia", "lector"]


def _consulta(fragment: str, avui: dt.date) -> list[dict]:
    # Els claudàtors van codificats (%5B %5D): sense això l'API no torna res.
    url = (f"{API}?filter%5Btitol%5D%5BLIKE%5D=%25{fragment}%25"
           f"&filter%5BdataFinalitzacio%5D%5BGE%5D={avui.isoformat()}&page%5Blimit%5D=500")
    eixida = []
    while url:
        r = comu.obte(url)
        dades = r.json()
        eixida += dades.get("data", [])
        seg = dades.get("links", {}).get("next")
        url = seg if seg and seg != url else None
    # Borses i processos sense data final però amb el termini obert (estat 3)
    url = f"{API}?filter%5Btitol%5D%5BLIKE%5D=%25{fragment}%25&filter%5BidEstat%5D=3&page%5Blimit%5D=500"
    eixida += comu.obte(url).json().get("data", [])
    return eixida


def executa(carpeta: Path) -> list[dict]:
    avui = dt.date.today()
    vistos, resultats = set(), []
    for frag in FRAGMENTS:
        try:
            registres = _consulta(frag, avui)
        except Exception as exc:
            print(f"CIDO «{frag}»: error ({exc})")
            continue
        for reg in registres:
            a = reg.get("attributes", {})
            ident = reg.get("id")
            if ident in vistos:
                continue
            text = " ".join(filter(None, [a.get("titol"), a.get("titulacioRequerida"), a.get("altresRequisits")]))
            ok, motiu = comu.interessa(text)
            if not ok:
                continue
            vistos.add(ident)
            fi = a.get("dataFinalitzacio")
            resultats.append({
                "id": f"CIDO-{ident}",
                "font": "CIDO",
                "titol": comu.normalitza(a.get("titol", "")),
                "organisme": a.get("institucioDesenvolupat"),
                "data_publicacio": (a.get("maxDataPublicacioDocument") or "")[:10] or None,
                "font_publicacio": "CIDO (DOGC/BOE/BOP)",
                "enllac": a.get("urlCido"),
                "inscripcio": a.get("accesTramit") or a.get("urlWeb"),
                "sistema": a.get("sistemaSeleccio"),
                "tipus_personal": a.get("tipusPersonal"),
                "grup": a.get("grupTitulacio"),
                "borsa": a.get("borsaTreball"),
                "requisits": a.get("titulacioRequerida"),
                "altres_requisits": a.get("altresRequisits"),
                "termini_text": (f"fins al {fi}" + (f" a les {a['horaFinalitzacio']}" if a.get("horaFinalitzacio") else ""))
                if fi else (a.get("observacionsTermini") or a.get("estat")),
                "data_fi": fi,
                "termini_estimat": False,
                "reservada": comu.es_reservada(text) or "promoció interna" in (a.get("sistemaSeleccio") or "").lower(),
                "motiu": motiu,
            })
    resultats = [e for e in resultats if comu.oberta(e, avui)]
    comu.desa("cido", "CIDO: convocatòries de filologia i llengua a Catalunya",
              "Processos selectius i borses amb el termini obert (API oficial del CIDO, Diputació de Barcelona).",
              resultats, carpeta, "https://cido.diba.cat/oposicions")
    return resultats

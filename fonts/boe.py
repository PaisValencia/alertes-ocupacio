"""Font BOE: API oficial de sumaris (https://boe.es/datosabiertos/).

Recorre els sumaris dels últims DIES dies, secció II.B (oposicions i concursos),
es queda amb les administracions dels territoris de parla catalana i amb l'Estat,
llig el text complet de cada disposició i aplica les paraules clau.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from . import comu

API = "https://boe.es/datosabiertos/api/boe/sumario/{data}"
DIES = 30

TERRITORIS = re.compile(
    r"\((Valencia|València|Alicante|Alacant|Castellón|Castelló|Barcelona|Girona|Gerona|Lleida|Lérida|"
    r"Tarragona|Illes Balears|Balears|Baleares|Huesca|Teruel)\)",
    re.IGNORECASE,
)
DEPARTAMENTS_TERRITORI = re.compile(
    r"COMUNITAT VALENCIANA|COMUNIDAD VALENCIANA|CATALU|ILLES BALEARS|BALEARS|ARAG", re.IGNORECASE
)
UNIVERSITATS = re.compile(
    r"Universitat|Universidad (de Valencia|de Alicante|Jaume|Politécnica de Valencia|Miguel Hernández|"
    r"de Barcelona|Autónoma de Barcelona|Pompeu|de Girona|de Lleida|Rovira|de las Illes Balears|de Zaragoza)",
    re.IGNORECASE,
)


def _llista(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def items_sumari(sumari: dict) -> list[dict]:
    """Extrau els items de la secció II.B d'un sumari JSON del BOE."""
    eixida = []
    diaris = _llista(sumari.get("data", {}).get("sumario", {}).get("diario"))
    data_pub = sumari.get("data", {}).get("sumario", {}).get("metadatos", {}).get("fecha_publicacion")
    for diari in diaris:
        for seccio in _llista(diari.get("seccion")):
            codi = str(seccio.get("codigo", "")).upper()
            nom_seccio = seccio.get("nombre", "")
            if codi != "2B" and "oposiciones" not in nom_seccio.lower():
                continue
            for dep in _llista(seccio.get("departamento")):
                nom_dep = dep.get("nombre", "")
                blocs = _llista(dep.get("epigrafe")) or [dep]
                for bloc in blocs:
                    for it in _llista(bloc.get("item")):
                        url_pdf = it.get("url_pdf")
                        eixida.append({
                            "id": it.get("identificador"),
                            "titol": comu.normalitza(it.get("titulo", "")),
                            "departament": nom_dep,
                            "epigraf": bloc.get("nombre", ""),
                            "url_html": it.get("url_html"),
                            "url_xml": it.get("url_xml"),
                            "url_pdf": url_pdf.get("texto") if isinstance(url_pdf, dict) else url_pdf,
                            "data": data_pub,
                        })
    return eixida


def candidat(item: dict) -> bool:
    """Primer filtre, només amb el títol i el departament (sense descarregar res)."""
    t, d = item["titol"], item["departament"]
    if DEPARTAMENTS_TERRITORI.search(d):
        return True
    if "ADMINISTRACIÓN LOCAL" in d.upper() and TERRITORIS.search(t):
        return True
    if "UNIVERSIDADES" in d.upper() and UNIVERSITATS.search(t):
        return True
    # Estat i altres: només si el títol ja parla de llengua, traducció o portuguès
    return comu.interessa(t)[0]


def text_complet(item: dict) -> str:
    """Text complet de la disposició.

    El robots.txt del BOE no permet llegir /diario_boe/xml.php?id=… ni txt.php?id=…,
    així que es llig el PDF oficial (/boe/dias/…/pdfs/…), que sí que està permés.
    Si algun dia es permet l'XML, s'usa primer perquè és més net.
    """
    if item.get("url_xml") and comu.permes(item["url_xml"]):
        arrel = ET.fromstring(comu.obte(item["url_xml"]).content)
        texte = arrel.find(".//texto")
        return " ".join((texte if texte is not None else arrel).itertext())
    from io import BytesIO

    from pypdf import PdfReader

    # Mateix servidor que l'API (boe.es): així només cal autoritzar un domini.
    url_pdf = item["url_pdf"].replace("https://www.boe.es/", "https://boe.es/")
    pdf = PdfReader(BytesIO(comu.obte(url_pdf).content))
    return " ".join((p.extract_text() or "") for p in pdf.pages)


def executa(carpeta: Path, cache_path: Path) -> list[dict]:
    avui = dt.date.today()
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    resultats, sumaris_llegits, docs_ok, docs_err = [], 0, 0, 0
    for i in range(DIES):
        dia = avui - dt.timedelta(days=i)
        try:
            r = comu.obte(API.format(data=dia.strftime("%Y%m%d")), headers={"Accept": "application/json"})
            sumaris_llegits += 1
        except Exception as exc:  # dies sense BOE (diumenges) tornen 404
            print(f"BOE {dia}: sense sumari ({exc.__class__.__name__})")
            continue
        for it in items_sumari(r.json()):
            if not candidat(it) or not (it.get("url_pdf") or it.get("url_xml")):
                continue
            if it["id"] in cache:
                fitxa = cache[it["id"]].get("fitxa")
            else:
                try:
                    text = text_complet(it)
                    docs_ok += 1
                except Exception as exc:
                    docs_err += 1
                    print(f"BOE {it['id']}: no s'ha pogut llegir ({exc.__class__.__name__}: {str(exc)[:120]})")
                    continue
                ok, motiu = comu.interessa(it["titol"] + " " + text)
                fitxa = None
                if ok:
                    pub = dt.datetime.strptime(it["data"], "%Y%m%d").date() if it.get("data") else dia
                    term = comu.calcula_termini(text, pub)
                    fitxa = {
                        "id": it["id"],
                        "font": "BOE",
                        "titol": it["titol"],
                        "organisme": it["departament"],
                        "data_publicacio": pub.isoformat(),
                        "font_publicacio": "BOE",
                        "enllac": it["url_html"] or it["url_pdf"],
                        "pdf": it["url_pdf"],
                        "termini_text": term["text"],
                        "data_fi": term["data_fi"],
                        "termini_estimat": term["estimat"],
                        "reservada": comu.es_reservada(it["titol"], text),
                        "motiu": motiu,
                    }
                cache[it["id"]] = {"vist": avui.isoformat(), "fitxa": fitxa}
            if fitxa:
                resultats.append(fitxa)
    print(f"BOE: {sumaris_llegits} sumaris, {docs_ok} documents llegits, {docs_err} amb error")
    if docs_err and not docs_ok:
        raise RuntimeError(f"no s'ha pogut llegir cap document del BOE ({docs_err} errors)")
    if sumaris_llegits == 0:
        raise RuntimeError("no s'ha pogut llegir cap sumari del BOE (connexió bloquejada o API caiguda)")
    # La memòria cau només guarda el que s'ha vist en els últims 60 dies
    limit = (avui - dt.timedelta(days=60)).isoformat()
    cache = {k: v for k, v in cache.items() if v.get("vist", "9999") >= limit}
    cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    vistos, unics = set(), []
    for e in resultats:
        if e["id"] not in vistos and comu.oberta(e, avui):
            vistos.add(e["id"])
            unics.append(e)
    comu.desa("boe", "BOE: convocatòries de filologia i llengua (territoris de parla catalana i Estat)",
              "Oposicions i concursos del BOE (secció II.B) filtrats per paraules clau. Termini estimat.",
              unics, carpeta, "https://www.boe.es")
    return unics

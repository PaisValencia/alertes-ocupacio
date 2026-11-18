"""Funcions comunes: paraules clau, terminis, robots.txt, JSON i RSS."""
from __future__ import annotations

import datetime as dt
import json
import re
import unicodedata
import urllib.robotparser
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

import requests

USER_AGENT = "AlertesOcupacioFilologia/1.0 (consulta diaria de convocatories; us personal)"
SESSIO = requests.Session()
SESSIO.headers.update({"User-Agent": USER_AGENT})

# ---------------------------------------------------------------------------
# Paraules clau
# ---------------------------------------------------------------------------
# FORTES: si apareixen en qualsevol lloc del text, la convocatòria interessa.
FORTES = [
    r"normali[tz]aci[oó]n? ling[uü][ií]stica",
    r"promoci[oó]n? ling[uü][ií]stica",
    r"planificaci[oó]n? ling[uü][ií]stica",
    r"(edici[oó]n?|assessorament|asesoramiento) (i|y) (assessorament|asesoramiento|edici[oó]n?) ling",
    r"promoci[oó]n? del valenci[aà]",
    r"promoci[oó]n? del catal[aàá]",
    r"\bt[eèé]cnic[oa]?(/a)? (de|en) (normali|ling|valenci[aà]n|catal[aàá]\b)",
    r"\bt[eèé]cnic[oa]?(/a)? ling[uü][ií]stic",
    r"assessor(a|ament)? ling[uü][ií]stic",
    r"asesor(a|amiento)? ling[uü][ií]stic",
    r"agent(e)? (de )?(promoci|dinamitzaci|dinamizaci)[oó]n? ling",
    r"dinamitzador(a)? ling",
    r"servei de pol[ií]tica ling",
    r"servicio de pol[ií]tica ling",
    r"(subescala|escala) (t[eèé]cnica )?(superior |mitjana |media )?(de )?ling[uü][ií]stica",
    r"assessorament en valenci[aà]",
    r"asesoramiento en valenciano",
    r"\bspv\b",
    r"filolog[ií]a (catalana|valenciana|portuguesa|catal[aàá]n?)",
    r"llengua catalana i literatura",
    r"lengua catalana y literatura",
    r"valenci[aà]: llengua i literatura",
    r"(llengua|lengua) valenciana",
    r"lengua y literatura valenciana",
    r"lectorat|lector(a)? de (catal|valenci|portugu)",
    r"traductor(a)?[- ]int[eè]rpret",
    r"corrector(a)? (de textos|ling)",
    r"correcci[oó]n? (de textos|ling)",
    r"\bportugu[eèé]s\b.{0,40}(especialitat|especialidad|professor|profesor|traduc)",
    r"(especialitat|especialidad|professor|profesor|traduc).{0,40}\bportugu[eèé]s\b",
]

# FEBLES: només compten si apareixen prop de «denominació», «especialitat», «plaça»...,
# perquè «valencià» o «català» com a requisit de llengua surt en quasi totes les bases.
# Ull: «València», «Catalunya», «Generalitat Valenciana» o «Agència Catalana» NO han de comptar.
FEBLES = [r"\bvalencià\b", r"\bvalenciano\b", r"\bcatalà\b", r"\bcatalán\b", r"\bportugu[eèé]s\b",
          r"ling[uü][ií]stic", r"\btraduc", r"\bfilolog"]
CONTEXT = r"(denominaci[oó]n?|especialitat|especialidad|pla[cç]a de|plaza de|lloc de|puesto de|categor[ií]a|cos de|cuerpo de|escala)"

RE_FORTES = re.compile("|".join(FORTES), re.IGNORECASE)
RE_FEBLE = re.compile("|".join(FEBLES), re.IGNORECASE)
RE_CONTEXT = re.compile(CONTEXT, re.IGNORECASE)

# Exclusions habituals: el valencià o el català com a REQUISIT («Nivell C1 de català»),
# o com a part d'un nom propi («Institut Català de la Salut»).
RE_REQUISIT = re.compile(
    r"(certificat|certificado|coneixements?|conocimientos?|nivel|nivell|requisit|requisito|acreditar|acreditació|"
    r"acreditación|suficiència|suficiencia|C1|C2|B2)\W*(\w+\W+){0,3}$",
    re.IGNORECASE,
)
RE_NOM_PROPI = re.compile(r"[A-ZÀ-Ý][\w'’]+\s+$")


def normalitza(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    return re.sub(r"\s+", " ", text)


def interessa(text: str) -> tuple[bool, str]:
    """Torna (interessa?, motiu)."""
    t = normalitza(text)
    m = RE_FORTES.search(t)
    if m:
        return True, m.group(0)
    for m in RE_FEBLE.finditer(t):
        abans = t[max(0, m.start() - 120): m.start()]
        if not RE_CONTEXT.search(abans):
            continue  # cal «denominació», «especialitat», «plaça de»... poc abans
        if RE_REQUISIT.search(t[max(0, m.start() - 40): m.start()]):
            continue  # és un requisit de llengua, no la plaça
        if m.group(0)[0].isupper() and RE_NOM_PROPI.search(t[max(0, m.start() - 30): m.start()]):
            continue  # nom propi: «Institut Català», «Servei Valencià»...
        return True, t[max(0, m.start() - 50): m.end()].strip()
    return False, ""


def es_reservada(titol: str, text: str = "") -> bool:
    """Plaça reservada a qui ja és funcionari (promoció interna, mobilitat, trasllats...).

    Es mira el títol i l'inici del text, perquè les bases de torn lliure també citen
    la promoció interna en altres apartats.
    """
    inici = normalitza(titol + " " + (text or "")[:1500]).lower()
    if re.search(r"(acceso|acc[eé]s) lliure|turno libre|torn lliure|sistema general de acceso libre", inici):
        return False
    claus = ["promoción interna", "promoció interna", "movilidad", "mobilitat", "concurso de traslados",
             "concurs de trasllats", "provisión de puestos", "provisió de llocs", "libre designación",
             "lliure designació"]
    return any(c in inici for c in claus)


# ---------------------------------------------------------------------------
# Terminis
# ---------------------------------------------------------------------------
NOMBRES = {
    "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "quatre": 4, "cuatro": 4, "cinc": 5, "cinco": 5,
    "sis": 6, "seis": 6, "set": 7, "siete": 7, "vuit": 8, "ocho": 8, "nou": 9, "nueve": 9,
    "deu": 10, "diez": 10, "onze": 11, "once": 11, "dotze": 12, "doce": 12, "tretze": 13, "trece": 13,
    "catorze": 14, "catorce": 14, "quinze": 15, "quince": 15, "setze": 16, "dieciséis": 16, "dieciseis": 16,
    "disset": 17, "diecisiete": 17, "divuit": 18, "dieciocho": 18, "dinou": 19, "diecinueve": 19,
    "vint": 20, "veinte": 20, "trenta": 30, "treinta": 30,
}
RE_TERMINI = re.compile(
    r"(plazo|termini)[^.]{0,80}?\b(\d{1,2}|" + "|".join(sorted(NOMBRES, key=len, reverse=True)) +
    r")\b(?:\s*\(\d+\))?\s+(d[ií]as|dies)\s+(h[aàá]biles|h[aàá]bils|naturales|naturals)",
    re.IGNORECASE,
)
RE_DATA_FI = re.compile(
    r"(hasta el|fins al|fins el|hasta las [\d:]+ horas del)\s+(\d{1,2})\s+de\s+([a-zçé]+)\s+de\s+(\d{4})",
    re.IGNORECASE,
)
MESOS = {
    "enero": 1, "gener": 1, "febrero": 2, "febrer": 2, "marzo": 3, "març": 3, "marc": 3, "abril": 4,
    "mayo": 5, "maig": 5, "junio": 6, "juny": 6, "julio": 7, "juliol": 7, "agosto": 8, "agost": 8,
    "septiembre": 9, "setembre": 9, "octubre": 10, "noviembre": 11, "novembre": 11,
    "diciembre": 12, "desembre": 12,
}
# Festius nacionals fixos (no inclou festius autonòmics ni locals: per això el resultat és «estimat»)
FESTIUS_FIXOS = {(1, 1), (1, 6), (5, 1), (8, 15), (10, 12), (11, 1), (12, 6), (12, 8), (12, 25)}


def _habil(d: dt.date) -> bool:
    return d.weekday() < 5 and (d.month, d.day) not in FESTIUS_FIXOS


def calcula_termini(text: str, publicacio: dt.date) -> dict:
    """Busca el termini al text. Torna {'text':…, 'data_fi':'AAAA-MM-DD'|None, 'estimat':bool}."""
    t = normalitza(text)
    m = RE_DATA_FI.search(t)
    if m and m.group(3).lower() in MESOS:
        try:
            d = dt.date(int(m.group(4)), MESOS[m.group(3).lower()], int(m.group(2)))
            return {"text": m.group(0), "data_fi": d.isoformat(), "estimat": False}
        except ValueError:
            pass
    m = None
    for cand in RE_TERMINI.finditer(t):
        entorn = t[max(0, cand.start() - 150): cand.end()]
        if re.search(r"solicitud|sol·licitud|sollicitud|instancia|inst[aà]ncies|presentaci", entorn, re.IGNORECASE):
            m = cand
            break
    if not m:
        m = RE_TERMINI.search(t)  # cap menció de sol·licituds: el primer termini que hi haja
    if not m:
        return {"text": None, "data_fi": None, "estimat": True}
    n_txt = m.group(2).lower()
    n = int(n_txt) if n_txt.isdigit() else NOMBRES.get(n_txt, 0)
    habils = m.group(4).lower().startswith("h")
    d = publicacio
    if habils:
        compte = 0
        while compte < n:
            d += dt.timedelta(days=1)
            if _habil(d):
                compte += 1
    else:
        d += dt.timedelta(days=n)
        while not _habil(d):  # si acaba en dia inhàbil, passa al següent hàbil
            d += dt.timedelta(days=1)
    return {"text": m.group(0), "data_fi": d.isoformat(), "estimat": True}


# ---------------------------------------------------------------------------
# robots.txt: respectem el que diu cada web
# ---------------------------------------------------------------------------
_ROBOTS: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def permes(url: str) -> bool:
    host = urlparse(url)
    base = f"{host.scheme}://{host.netloc}"
    if base not in _ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = SESSIO.get(base + "/robots.txt", timeout=20)
            if r.status_code >= 400:
                _ROBOTS[base] = None  # sense robots.txt: permés
            else:
                rp.parse(r.text.splitlines())
                _ROBOTS[base] = rp
        except requests.RequestException:
            # No sabem què diu robots.txt: per prudència, no llegim res d'eixe servidor.
            rp.parse(["User-agent: *", "Disallow: /"])
            _ROBOTS[base] = rp
    rp = _ROBOTS[base]
    return True if rp is None else rp.can_fetch(USER_AGENT, url)


def obte(url: str, **kw) -> requests.Response:
    if not permes(url):
        raise PermissionError(f"robots.txt no permet llegir {url}")
    r = SESSIO.get(url, timeout=kw.pop("timeout", 40), **kw)
    r.raise_for_status()
    return r


# ---------------------------------------------------------------------------
# Eixida: JSON i RSS
# ---------------------------------------------------------------------------
def desa(nom: str, titol: str, descripcio: str, elements: list[dict], carpeta: Path, url_base: str = "") -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    ara = dt.datetime.now(dt.timezone.utc)
    elements = sorted(elements, key=lambda e: (e.get("data_fi") or "9999-12-31", e.get("titol", "")))
    dades = {
        "font": nom,
        "titol": titol,
        "descripcio": descripcio,
        "actualitzat": ara.isoformat(timespec="seconds"),
        "total": len(elements),
        "convocatories": elements,
    }
    (carpeta / f"{nom}.json").write_text(json.dumps(dades, ensure_ascii=False, indent=2), encoding="utf-8")

    items = []
    for e in elements:
        fi = e.get("data_fi")
        prefix = f"[FINS AL {fi}{' (estimat)' if e.get('termini_estimat') else ''}] " if fi else ""
        reservada = "🔒 " if e.get("reservada") else ""
        desc = (
            f"Organisme: {e.get('organisme') or '—'}<br/>"
            f"Publicació: {e.get('font_publicacio') or ''} {e.get('data_publicacio') or ''}<br/>"
            f"Termini: {e.get('termini_text') or 'no detectat; consulta les bases'}<br/>"
            f"Motiu de la selecció: {e.get('motiu') or ''}"
        )
        pub = e.get("data_publicacio")
        try:
            data_rss = format_datetime(dt.datetime.fromisoformat(pub).replace(tzinfo=dt.timezone.utc)) if pub else format_datetime(ara)
        except ValueError:
            data_rss = format_datetime(ara)
        items.append(
            "<item>"
            f"<title>{escape(reservada + prefix + e.get('titol', ''))}</title>"
            f"<link>{escape(e.get('enllac') or url_base)}</link>"
            f"<guid isPermaLink=\"false\">{escape(e.get('id') or e.get('enllac') or e.get('titol', ''))}</guid>"
            f"<pubDate>{data_rss}</pubDate>"
            f"<description>{escape(desc)}</description>"
            "</item>"
        )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
        f"<title>{escape(titol)}</title><link>{escape(url_base)}</link>"
        f"<description>{escape(descripcio)}</description><language>ca</language>"
        f"<lastBuildDate>{format_datetime(ara)}</lastBuildDate>"
        + "".join(items) + "</channel></rss>\n"
    )
    (carpeta / f"{nom}.xml").write_text(rss, encoding="utf-8")


def oberta(e: dict, avui: dt.date) -> bool:
    fi = e.get("data_fi")
    if not fi:
        return True  # sense termini detectat: es manté perquè ho revises
    try:
        return dt.date.fromisoformat(fi) >= avui
    except ValueError:
        return True

"""Proves dels filtres i del càlcul de terminis. Execució: python -m proves.prova_filtres"""
import datetime as dt

from fonts import comu
from fonts.boe import candidat, items_sumari

SI = [
    "1 plaça de Professor de català",
    "Borsa de treball de places de Tècnic superior d'edició i assessorament lingüístic",
    "1 plaça de Titulat superior en planificació lingüística a la Subdirecció General",
    "Denominación: Técnico de Normalización Lingüística. Escala: Administración Especial.",
    "convocatòria per a cobrir una plaça de tècnic/a de promoció del valencià",
    "Bases de la borsa de treball d'agent de promoció lingüística (SPV)",
    "Escala tècnica superior de lingüística, subescala d'assessorament en valencià",
    "Cuerpo de Profesores de Escuelas Oficiales de Idiomas, especialidad: Portugués",
    "Especialitat: Valencià: llengua i literatura",
    "plaza de Traductor-Intérprete de portugués",
    "lectorat de català a la Universitat de Lisboa",
]
NO = [
    "1 plaça de Tècnic mitjà professor de patronatge. Requisits: Nivell C1 de català",
    "Borsa de professor de piano. Requisit: certificat de nivell C1 de valencià",
    "1 plaça de Subaltern a l'Institut Català de Seguretat i Salut Laboral (Lleida)",
    "1 plaça de Consultor de l'Oficina de Comerç i Inversions de Catalunya a Istanbul",
    "Plaza de auxiliar administrativo del Ayuntamiento de València",
    "Plaça de tècnic de medi ambient de la Generalitat Valenciana",
]


def prova_paraules():
    errors = 0
    for t in SI:
        ok, motiu = comu.interessa(t)
        if not ok:
            errors += 1
            print("FALTA (hauria d'eixir):", t)
    for t in NO:
        ok, motiu = comu.interessa(t)
        if ok:
            errors += 1
            print("SOBRA (no hauria d'eixir):", t, "| motiu:", motiu)
    return errors


def prova_terminis():
    errors = 0
    pub = dt.date(2026, 11, 17)  # dimarts
    casos = [
        ("El plazo de presentación de solicitudes será de 10 días hábiles", "2026-12-01"),
        ("termini de vint dies naturals comptadors des de l'endemà", "2026-12-07"),  # 7/12 és dilluns
        ("El plazo será de veinte días naturales", "2026-12-07"),
        ("presentar solicitudes hasta el 15 de diciembre de 2026", "2026-12-15"),
    ]
    for text, esperat in casos:
        r = comu.calcula_termini(text, pub)
        if r["data_fi"] != esperat:
            errors += 1
            print("TERMINI MAL:", text, "→", r["data_fi"], "esperat", esperat)
    return errors


def prova_sumari_boe():
    """Sumari BOE amb l'estructura documentada (APIsumarioBOE.pdf)."""
    sumari = {"status": {"code": "200"}, "data": {"sumario": {
        "metadatos": {"publicacion": "BOE", "fecha_publicacion": "20261117"},
        "diario": [{"numero": "286", "seccion": [
            {"codigo": "1", "nombre": "I. Disposiciones generales", "departamento": []},
            {"codigo": "2B", "nombre": "II. Autoridades y personal. - B. Oposiciones y concursos", "departamento": [
                {"codigo": "1", "nombre": "UNIVERSIDADES", "epigrafe": [{"nombre": "Personal funcionario", "item": {
                    "identificador": "BOE-A-2026-24090",
                    "titulo": "Resolución de 2 de noviembre de 2026, de la Universitat de València, por la que se convoca proceso selectivo...",
                    "url_pdf": {"texto": "https://www.boe.es/boe/dias/2026/11/17/pdfs/BOE-A-2026-24090.pdf"},
                    "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-24090",
                    "url_xml": "https://www.boe.es/diario_boe/xml.php?id=BOE-A-2026-24090"}}]},
                {"codigo": "2", "nombre": "ADMINISTRACIÓN LOCAL", "epigrafe": [{"nombre": "Personal funcionario", "item": [
                    {"identificador": "BOE-A-2026-1", "titulo": "Resolución de 3 de noviembre de 2026, del Ayuntamiento de Torrent (Valencia), referente a la convocatoria para proveer una plaza.",
                     "url_xml": "x", "url_html": "y", "url_pdf": {"texto": "z"}},
                    {"identificador": "BOE-A-2026-2", "titulo": "Resolución de 3 de noviembre de 2026, del Ayuntamiento de Ourense (Ourense), referente a la convocatoria para proveer una plaza.",
                     "url_xml": "x", "url_html": "y", "url_pdf": {"texto": "z"}}]}]},
            ]},
        ]}]}}}
    its = items_sumari(sumari)
    ids = [i["id"] for i in its if candidat(i)]
    errors = 0
    if len(its) != 3:
        errors += 1
        print("SUMARI: s'esperaven 3 items i n'hi ha", len(its))
    if ids != ["BOE-A-2026-24090", "BOE-A-2026-1"]:
        errors += 1
        print("SUMARI: candidats incorrectes:", ids)
    return errors


if __name__ == "__main__":
    e = prova_paraules() + prova_terminis() + prova_sumari_boe()
    print("Errors:", e)
    raise SystemExit(1 if e else 0)

# Alertes ocupació filologia: API pròpies

Programa que cada dia llig fonts oficials, es queda amb les convocatòries de filologia catalana,
valencià, català i portuguès (tècnic lingüístic, professorat, traducció, correcció...) i publica
els resultats en fitxers JSON i RSS a GitHub Pages.

| Font | Fitxers | Mètode | Estat |
| --- | --- | --- | --- |
| BOE | `boe.json` · `boe.xml` | API oficial de sumaris + PDF oficial | Provat amb dades reals |
| CIDO (Catalunya: DOGC, BOE i BOP catalans) | `cido.json` · `cido.xml` | API oficial de la Diputació de Barcelona | Provat amb dades reals |
| BOP de València | `bop_valencia.json` · `bop_valencia.xml` | Lectura de la web amb un navegador sense pantalla | Experimental |
| Totes juntes | `totes.json` · `totes.xml` | — | — |

La guia completa, pas a pas, és a **GUIA.md**.

Ús local: `pip install -r requirements.txt && python principal.py` (o `--fonts boe,cido`).
Proves: `python -m proves.prova_filtres`.

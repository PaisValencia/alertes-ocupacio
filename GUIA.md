# Guia: les teues API d'ocupació (BOE, CIDO i BOP de València)

Esta guia explica, pas a pas i sense necessitat de saber informàtica, com posar en marxa les teues
pròpies «API»: uns fitxers que s'actualitzen sols cada matí amb les convocatòries de filologia
que tenen el termini obert. Després els pots usar per separat (al navegador, en una aplicació de
notícies RSS) i la tasca d'alertes els llegirà cada dia.

---

## 1. Què fa i què no fa

**Què fa.** Cada dia a les 6:00 (hora d'hivern; a les 7:00 a l'estiu), un ordinador gratuït de
GitHub executa el programa, que:

1. **BOE (API oficial).** Llig els sumaris dels últims 30 dies, secció II.B (oposicions i
   concursos). Es queda amb la Comunitat Valenciana, Catalunya, les Illes Balears, Aragó (per la
   Franja), les universitats d'eixos territoris, els ajuntaments i diputacions de les seues
   províncies i l'Estat. Llig el PDF oficial de cada convocatòria i hi busca paraules clau.
   *Per què és important:* quan un poble convoca una plaça de funcionari de carrera, l'extracte
   que obri el termini ix al BOE.
2. **CIDO (API oficial de la Diputació de Barcelona).** Recull tot Catalunya: DOGC, BOE i els
   quatre BOP catalans, incloses moltes borses.
3. **BOP de València (experimental).** Obri la web del BOP amb un navegador sense pantalla,
   recorre els anuncis del dia i hi busca paraules clau. Guarda un historial de 45 dies.

Després publica els resultats en una pàgina web teua.

**Què no fa (i per què).** Cada web diu en un fitxer anomenat *robots.txt* què es pot llegir
automàticament, i el programa ho respecta sempre:

| Font | Motiu | Com queda coberta |
| --- | --- | --- |
| DOGV | El seu robots.txt no ho permet | Les oposicions de la Generalitat i de les universitats solen eixir també al BOE |
| BOP de Castelló | El seu robots.txt no ho permet | Les oposicions de carrera dels pobles ixen al BOE |
| BOP d'Alacant | No té una consulta pública que es puga llegir automàticament | Ídem, via BOE |
| DOGC, ATRI i BOIB | El seu robots.txt no ho permet | DOGC i BOP catalans: CIDO. Balears: BOE i la tasca d'alertes (portal de l'opositor) |

El forat que queda són les **borses i interinatges** dels pobles valencians de les províncies
d'Alacant i Castelló, que només ixen al seu BOP. La tasca d'alertes continua buscant-les cada dia.

**Quines paraules clau s'usen.** Paraules «fortes» que sempre compten (normalització lingüística,
promoció del valencià, assessorament lingüístic, escala de lingüística, filologia catalana,
lectorat, traductor-intèrpret, Valencià: llengua i literatura, portuguès com a especialitat...)
i paraules «febles» (valencià, català, portuguès, lingüístic, traducció, filologia) que només
compten si apareixen just després de «denominació», «especialitat», «plaça de», «escala»... Així
no ix cada plaça que demana el C1 de valencià com a requisit, ni «Institut Català» o «València».

---

## 2. Què necessites

- Un compte de correu (pots usar ricardochulia123@gmail.com).
- La carpeta `api-ocupacio`, que trauràs del fitxer ZIP que t'he enviat. Per a descomprimir-lo,
  fes doble clic al fitxer (Mac) o botó dret → «Extrau-ho tot» (Windows).
- Uns 20 minuts.

---

## 3. Pas a pas

### Pas 1. Crear el compte de GitHub

1. Ves a <https://github.com/signup>.
2. Escriu el correu, una contrasenya i un nom d'usuari. **Apunta el nom d'usuari**: formarà part
   de l'adreça de les teues API. En esta guia l'anomenem `USUARI`.
3. Confirma el codi que t'arribarà per correu. El pla gratuït (*Free*) és suficient.

### Pas 2. Crear el repositori (la carpeta a GitHub)

1. A dalt a la dreta, prem **+** → **New repository**.
2. A *Repository name* escriu: `alertes-ocupacio`.
3. Marca **Public**. Cal que siga públic perquè la pàgina web siga gratuïta. Les dades són
   convocatòries públiques: no conté res personal.
4. **No** marques cap casella de *Add a README* ni altres opcions.
5. Prem **Create repository**.

### Pas 3. Pujar els fitxers

1. A la pàgina del repositori nou, prem l'enllaç **uploading an existing file**.
2. Obri la carpeta `api-ocupacio` de l'ordinador, selecciona **tot el que hi ha dins** i arrossega-ho
   a la finestra del navegador.
3. Baix de tot, prem **Commit changes**.

> **Compte amb la carpeta oculta `.github`.** Les carpetes que comencen per punt solen estar
> amagades i a vegades no es pugen. Comprova si al repositori apareix la carpeta `.github`.
> Si no hi és:
> 1. Prem **Add file** → **Create new file**.
> 2. Com a nom escriu exactament: `.github/workflows/actualitza.yml`
>    (quan escrigues cada barra, GitHub crearà la carpeta).
> 3. Obri amb el Bloc de notes (Windows) o TextEdit (Mac) el fitxer
>    `api-ocupacio/.github/workflows/actualitza.yml`, copia'n tot el text i apega'l a GitHub.
>    Si no veus la carpeta: a Mac, prem Cmd + Maj + . (punt) a la finestra del Finder;
>    a Windows, Explorador → Visualitza → Mostra → Elements amagats.
> 4. Prem **Commit changes**.

### Pas 4. Donar permís perquè el programa guarde els resultats

1. Al repositori, ves a **Settings** (Configuració, a dalt a la dreta).
2. Al menú de l'esquerra: **Actions** → **General**.
3. Baixa fins a *Workflow permissions* i marca **Read and write permissions**.
4. Prem **Save**.

### Pas 5. Activar la pàgina web (GitHub Pages)

1. A **Settings**, al menú de l'esquerra, prem **Pages**.
2. A *Source* tria **Deploy from a branch**.
3. A *Branch* tria **main** i, al costat, la carpeta **/docs**. Prem **Save**.
4. Al cap d'un o dos minuts, a dalt de la mateixa pàgina apareixerà l'adreça:
   `https://USUARI.github.io/alertes-ocupacio/`

### Pas 6. Executar-lo per primera vegada

1. Ves a la pestanya **Actions**. Si et demana activar els *workflows*, prem el botó verd
   **I understand my workflows, go ahead and enable them**.
2. A l'esquerra, prem **Actualitza les API d'ocupació**.
3. A la dreta, prem **Run workflow** → **Run workflow**.
4. Espera 5 o 10 minuts. Si ix un cercle verd amb ✓, tot ha anat bé. Si ix una ✗ roja, obri-la,
   copia el text de l'error i passa-me'l.

A partir d'ara s'executarà sol cada dia.

### Pas 7. Autoritzar l'adreça perquè la tasca d'alertes la llija

1. Obri claude.ai en un navegador.
2. Ves a **Configuració → Capacitats** (Settings → Capabilities).
3. En els dominis permesos, afig `USUARI.github.io` (amb el teu nom d'usuari) i guarda.
4. Digues-me l'adreça i afegiré estes API a la tasca «Alertes ocupació filologia».

---

## 4. Com usar cada API per separat

Quan ja funcione, tens estes adreces (canvia `USUARI` pel teu nom):

| Què | Dades (JSON) | Avisos (RSS) |
| --- | --- | --- |
| Pàgina principal | `https://USUARI.github.io/alertes-ocupacio/` | — |
| BOE | `…/boe.json` | `…/boe.xml` |
| CIDO (Catalunya) | `…/cido.json` | `…/cido.xml` |
| BOP de València | `…/bop_valencia.json` | `…/bop_valencia.xml` |
| Totes juntes | `…/totes.json` | `…/totes.xml` |
| Estat de cada font | `…/estat.json` | — |

**Al navegador.** Obri l'adreça JSON: Firefox i Chrome mostren la llista de convocatòries,
ordenada pel final del termini. Cada convocatòria porta:

- `titol`, `organisme`, `data_publicacio` i `font_publicacio`;
- `data_fi`: el final del termini;
- `termini_estimat`: `true` si el termini l'ha calculat el programa (sense festius locals);
  confirma-ho sempre en les bases;
- `termini_text`: la frase de les bases on es diu el termini;
- `reservada`: `true` si és de promoció interna, mobilitat o similar;
- `enllac` (i `pdf` o `inscripcio`, quan n'hi ha);
- `motiu`: les paraules que han fet que la convocatòria isca.

**Amb una aplicació RSS (avisos al mòbil).** L'RSS és el format de les «subscripcions de
notícies». Instal·la una aplicació de lectura RSS (per exemple Feedly, Inoreader o NetNewsWire,
o el gestor de correu Thunderbird). Busca l'opció «Afegir font» o «Subscriure's» i apega
l'adreça `.xml` que vulgues. Cada convocatòria nova t'apareixerà com una notícia, amb el termini
al principi del títol, i amb 🔒 si és reservada.

**Executar-ho a mà quan vulgues.** Pestanya **Actions** → **Actualitza les API d'ocupació** →
**Run workflow**.

---

## 5. Manteniment i problemes

- **Si una font falla,** les altres continuen. A `estat.json` i a la pàgina principal veuràs quina
  ha fallat i per què. La del BOP de València és experimental: si la web canvia, pot deixar de
  funcionar, i es continua publicant l'historial anterior.
- **Si GitHub deixa d'executar-lo:** GitHub pot desactivar les tasques programades d'un repositori
  que porta 60 dies sense activitat. El programa guarda resultats cada dia (això compta com a
  activitat), però si un dia veus que no s'actualitza, ves a **Actions** i torna a activar-lo.
- **Retards:** GitHub pot endarrerir uns minuts les execucions programades. És normal.
- **Canviar les paraules clau:** són al fitxer `fonts/comu.py`, en les llistes `FORTES` i `FEBLES`.
  Si vols canviar-ne alguna, digues-m'ho i et passe el fitxer corregit.

---

## 6. Proves fetes (18/11/2026)

- **BOE:** 25 sumaris i 141 convocatòries llegides, sense cap error. Han eixit 3 convocatòries,
  entre les quals la de la Universitat de València (escala tècnica superior de lingüística,
  subescala d'assessorament en valencià, torn lliure), amb el termini calculat fins a
  l'**1 de desembre de 2026**, que coincidix amb el càlcul fet a mà.
- **CIDO:** 4 convocatòries amb el termini obert, entre les quals una plaça de professor de
  català (Ajuntament del Papiol), una de titulat superior en planificació lingüística
  (Departament de Salut) i una borsa de tècnic superior d'edició i assessorament lingüístic
  (Àrea Metropolitana de Barcelona).
- **Filtres i terminis:** totes les proves automàtiques superades (`proves/prova_filtres.py`).
  Entre altres coses, comproven que «Nivell C1 de català», «Institut Català» o «València» no
  fan eixir convocatòries que no toquen.
- **BOP de València:** no s'ha pogut provar des d'ací, perquè la connexió amb eixa web estava
  bloquejada. Es provarà sol la primera vegada que s'execute a GitHub.

---

## Bibliografia

- Agencia Estatal BOE. *API para el acceso a los sumarios del Boletín Oficial del Estado*
  (document tècnic, 28/06/2024): <https://boe.es/datosabiertos/documentos/APIsumarioBOE.pdf>
- Agencia Estatal BOE. *API de datos abiertos: preguntas frecuentes*: <https://boe.es/datosabiertos/faq/boe.php>
- Agencia Estatal BOE. *robots.txt*: <https://www.boe.es/robots.txt>
- Diputació de Barcelona. *Documentació de l'API de dades obertes del CIDO*:
  <https://dadesobertes.diba.cat/sites/default/files/public/documentacio_api_cido.pdf>
- Diputació de València. *Butlletí Oficial de la Província de València*: <https://bop.dival.es>
- Generalitat Valenciana. *DOGV* i el seu *robots.txt*: <https://dogv.gva.es>
- Diputació d'Alacant. *Carta de Serveis del BOP*: <https://sede.diputacionalicante.es/wp-content/uploads/2025/11/Carta-de-Servicios-del-BOP.pdf>
- GitHub. *Documentació de GitHub Actions i GitHub Pages*: <https://docs.github.com>

## Resum de les indicacions

- Superar les limitacions de les alertes creant API pròpies per a les fonts que no en tenen
  (BOP de València, Alacant i Castelló, DOGV, ajuntaments).
- Fer-les «ací» i deixar-les preparades perquè les uses tu per separat.
- Fer la feina a les 3 de la matinada del 18/11/2026.
- Programa en Python, una peça per font i un programa principal, amb eixida en JSON i RSS,
  executat cada dia amb GitHub Actions i publicat a GitHub Pages.
- Guia pas a pas en valencià (normativa AVL), per a algú sense coneixements d'informàtica.
- Respectar les normes d'ús (robots.txt) de cada web.
- Afegir les API a la tasca «Alertes ocupació filologia» quan l'adreça estiga activa.

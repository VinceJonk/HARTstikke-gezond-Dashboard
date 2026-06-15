# 🫀 HARTstikke gezond

Streamlit-dashboard voor analyse van hartslag- en bewegingsdata. Visualiseert actieve minuten per dag op basis van de Nederlandse gezondheidsnorm, met een interactieve kaart van Amsterdamse stadsdelen en een buurtvergelijking van gezondheidsmetingen.

---

## Installatie

Volg de stappen hieronder. Je hebt geen technische kennis nodig — doe het gewoon stap voor stap.

---

### Stap 1 — Download de projectbestanden

Ga naar de GitHub-pagina van dit project en klik op de groene knop **Code**, dan op **Download ZIP**.

Pak het ZIP-bestand uit op een plek die je makkelijk terugvindt, bijvoorbeeld je bureaublad. Je krijgt dan een map zoals `hartstikke-gezond-main`. Je mag de map hernoemen naar `hartstikke-gezond`.

---

### Stap 2 — Installeer Python

Python is het programma waar het dashboard op draait. Controleer eerst of je het al hebt:

**Windows:**
1. Druk op de Windows-toets, typ `cmd` en open **Opdrachtprompt**.
2. Typ `python --version` en druk op Enter.
3. Zie je een versienummer zoals `Python 3.11.2`? Dan sla je deze stap over.
4. Zie je een foutmelding? Ga dan naar [python.org/downloads](https://www.python.org/downloads/) en download de nieuwste versie.
5. Voer het installatiebestand uit. **Belangrijk:** zet het vinkje aan bij _"Add Python to PATH"_ onderaan het installatiescherm, vóór je op Install klikt.

**Mac:**
1. Open de **Terminal** (zoek op "Terminal" via Spotlight met ⌘ + spatiebalk).
2. Typ `python3 --version` en druk op Enter.
3. Zie je een versienummer? Dan sla je deze stap over.
4. Zie je een foutmelding? Ga naar [python.org/downloads](https://www.python.org/downloads/) en download de nieuwste versie voor Mac. Volg de installatie.

---

### Stap 3 — Zet de data op de juiste plek

In de projectmap staan twee mappen waar je bestanden in moet zetten:

**`Bestanden/`** — Zet hier je CSV-bestanden van de hartslagmeter in. Dit zijn de meetbestanden die je in het dashboard kunt selecteren.

**`BuurtData/`** — Zet hier het bestand `anonieme_buurtbewoners_gezondheid.csv` in. Dit bestand bevat de gezondheidsgegevens per stadsdeel.

De mappenstructuur ziet er dan zo uit:
```
hartstikke-gezond/
├── app.py
├── requirements.txt
├── Bestanden/
│   └── jouw-meting.csv
└── BuurtData/
    └── anonieme_buurtbewoners_gezondheid.csv
```

---

### Stap 4 — Installeer de benodigde onderdelen

**Windows:**
1. Open de map `hartstikke-gezond` in Verkenner.
2. Klik in de adresbalk bovenaan, typ `cmd` en druk op Enter. Er opent een Opdrachtprompt in de juiste map.
3. Typ het volgende en druk op Enter:
   ```
   pip install -r requirements.txt
   ```
4. Wacht tot de installatie klaar is. Je ziet veel tekst voorbijkomen — dat is normaal.

**Mac:**
1. Open de **Terminal**.
2. Typ `cd ` (met een spatie erna), sleep dan de map `hartstikke-gezond` vanuit Finder naar het Terminal-venster, en druk op Enter.
3. Typ het volgende en druk op Enter:
   ```
   pip3 install -r requirements.txt
   ```
4. Wacht tot de installatie klaar is.

---

### Stap 5 — Start het dashboard

**Windows:**
Typ in diezelfde Opdrachtprompt:
```
streamlit run app.py
```
Druk op Enter.

**Mac:**
Typ in diezelfde Terminal:
```
streamlit run app.py
```
Druk op Enter.

Het dashboard opent automatisch in je browser. Lukt dat niet, ga dan zelf naar `http://localhost:8501`.

> De Opdrachtprompt of Terminal moet open blijven zolang je het dashboard gebruikt. Sluit je het venster, dan stopt het dashboard.

---

---

## Hoe werkt het dashboard?

### Stap 1 — Kies een bestand

In de **linkerzijbalk** zie je een lijst met beschikbare CSV-bestanden. Klik op het gewenste bestand om het te laden. Het dashboard verwerkt de data automatisch.

> De CSV-bestanden staan in de map `Bestanden/` en bevatten hartslagmetingen van een draagbare sensor.

---

### Stap 2 — Vul je leeftijd in

Vul in de zijbalk je **leeftijd** in. Dit is nodig om te berekenen wanneer je hartslag hoog genoeg is om als "actief" te tellen.

> Het dashboard gebruikt de formule `220 - leeftijd` om je maximale hartslag te schatten. Een minuut telt als actief wanneer je hartslag boven de 60% van dat maximum komt én je beweegt.

---

### Stap 3 — Bekijk de grafiek

De grafiek **Activiteit: BPM + Beweging** toont je hartslag (BPM = hartslagen per minuut) over de tijd van de meting.

- De **rode lijn** is je hartslag.
- **Groene vlakken** geven momenten aan waarop beweging werd gedetecteerd.

Hoe hoger de rode lijn en hoe meer groen, hoe actiever je was tijdens de meting.

---

### Stap 4 — Bekijk je actieve minuten

Rechts van de grafiek zie je het aantal **actieve minuten** uit de meting.

Een minuut telt als actief wanneer:
- je hartslag boven 60% van je maximale hartslag lag, én
- er beweging aanwezig was.

#### Optionele instelling: onafgebroken beweging

In de zijbalk kun je de **onafgebroken-regel** aanzetten. Dan tellen alleen aaneengesloten blokken van minimaal 10 minuten actief bewegen mee. Dit sluit korte uitschieters uit, zoals even opstaan van de bank.

> De Nederlandse beweegnorm adviseert 21–30 minuten matig intensieve beweging per dag.

---

### Stap 5 — Buurtvergelijking

Onder de grafiek vind je een tabel met gemiddelde gezondheidswaarden per Amsterdams stadsdeel. De kolommen zijn:

| Kolom | Wat betekent dit? |
|---|---|
| **Cholesterol** | Hoeveelheid cholesterol in het bloed (mmol/L). Lager is beter. Gezonde waarde: onder 5,0. |
| **Systolisch** | De bovendruk van de bloeddruk (mmHg). Lager is beter. Gezonde waarde: onder 120. |
| **Diastolisch** | De onderdruk van de bloeddruk (mmHg). Lager is beter. Gezonde waarde: onder 80. |
| **Bloedsuiker** | Hoeveelheid suiker in het bloed (mmol/L). Gezonde waarde: tussen 4,0 en 6,0. |
| **Actieve minuten per dag** | Gemiddeld aantal actieve minuten per dag in dit stadsdeel. |

Elke waarde heeft een gekleurde stip:
- 🟢 **Groen** — binnen de gezonde norm
- 🟡 **Geel** — net aan de grens
- 🔴 **Rood** — buiten de gezonde norm

Beweeg met je muis over een waarde voor een korte toelichting en een staafdiagram.

---

### Stap 6 — Kaart van Amsterdam

Klik onderaan op **📍 Naar kaart** om de kaartpagina te openen. De kaart kleurt de stadsdelen van Amsterdam in op basis van hun gemiddelde actieve minuten per dag:

- 🔴 **Rood** — minder dan 21 minuten per dag (onder de norm)
- 🔵 **Blauw** — 21 tot 30 minuten per dag (voldoet aan de norm)
- 🟢 **Groen** — meer dan 30 minuten per dag (boven de norm)

Onder de kaart staat een overzichtstabel met de exacte waarden per stadsdeel. Klik op **Terug naar dashboard** om terug te gaan.

---

## Bestandsformaat CSV

Het CSV-bestand moet de volgende kolommen bevatten:

| Kolom | Beschrijving |
|---|---|
| `time` of `time_ms` | Tijdstempel in milliseconden |
| `ECG` | Ruwe ECG-signaalwaarde |
| `accX`, `accY`, `accZ` | Versnellingsdata van de bewegingssensor (X, Y en Z-as) |

---

## Gezondheidswaarden — referentienormen

| Meting | Gezonde waarde | Bron |
|---|---|---|
| Cholesterol | < 5,0 mmol/L | Nederlande Hartstichting |
| Bloeddruk (systolisch) | < 120 mmHg | WHO |
| Bloeddruk (diastolisch) | < 80 mmHg | WHO |
| Bloedsuiker | 4,0 – 6,0 mmol/L | Diabetes Fonds |
| Actieve minuten | 21 – 30 min/dag | RIVM Beweegrichtlijnen |

---

## ENGLISH VERSION

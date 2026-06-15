# 🫀 HARTstikke gezond

Streamlit-dashboard voor analyse van hartslag- en bewegingsdata. Visualiseert actieve minuten per dag op basis van de Nederlandse gezondheidsnorm, met een interactieve kaart van Amsterdamse stadsdelen en een buurtvergelijking van gezondheidsmetingen.

---

## Vereisten

- Python 3.9 of hoger
- De volgende mappen in de projectmap:
  - `Bestanden/` — map met CSV-bestanden van de hartslagmeter
  - `BuurtData/` — map met het bestand `anonieme_buurtbewoners_gezondheid.csv`

## Installatie

```bash
git clone https://github.com/jouw-gebruikersnaam/hartstikke-gezond.git
cd hartstikke-gezond
pip install -r requirements.txt
streamlit run app.py
```

Het dashboard opent automatisch in je browser op `http://localhost:8501`.

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

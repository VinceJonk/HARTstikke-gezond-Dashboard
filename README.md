# 🫀 HARTstikke gezond

(↓ See English version below ↓)

Streamlit-dashboard voor analyse van hartslag- en bewegingsdata. Visualiseert actieve minuten per dag op basis van de Nederlandse gezondheidsnorm, met een interactieve kaart van Amsterdamse stadsdelen en een buurtvergelijking van gezondheidsmetingen.

---

## Installatie

Volg de stappen hieronder.

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

**`BuurtData/`** — Hier staat het bestand `anonieme_buurtbewoners_gezondheid.csv` in. Dit bestand bevat de gezondheidsgegevens per stadsdeel, deze kan aangepast worden als er metingen gedaan zijn.

De mappenstructuur ziet er dan zo uit:
```
hartstikke-gezond/
├── _pycache_/
├── Bestanden/
│   └── jouw-meting.csv <
├── BuurtData/
    └── anonieme_buurtbewoners_gezondheid.csv <
├── pages/
    └── kaart.py
├── app.py    <-- Hoofd app
├── data_utils.py
├── ecg_utils.py
├── health_utils.py
├── README.md
└── requirements.txt

```

---

### Stap 4 — Installeer de benodigde onderdelen

**Windows:**
1. Open de map `hartstikke-gezond` in Verkenner.
2. Klik in de adresbalk bovenaan, typ `powershell` en druk op Enter. Er opent een Opdrachtprompt in de juiste map.
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

Het dashboard opent automatisch in je browser. Lukt dat niet, probeer:
```text
python -m streamlit run app.py
```

of ga dan zelf naar `http://localhost:8501`.

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

## Geadvanceerde instellingen

### Dashboard automatisch opstarten bij inloggen (Windows)

Je kunt het dashboard automatisch laten starten zodra je inlogt op Windows, zodat je het niet handmatig hoeft op te starten.

> **Belangrijk:** Zet de projectmap op je bureaublad. Het pad naar je bureaublad is altijd hetzelfde patroon: `C:\Users\JOUWGEBRUIKERSNAAM\Desktop\HARTstikke-gezond-Dashboard-main`

**Stap 1 — Open de Taakplanner als administrator**
1. Druk op `Win + S`, zoek op **Taakplanner**
2. Klik rechts → **Als administrator uitvoeren**

**Stap 2 — Maak een nieuwe taak aan**
1. Klik rechts op **Taakplannerbibliotheek** → **Taak maken...**
2. Geef de taak een naam, bijv. `Start Dashboard`
3. Zorg dat onder **Security options** het volgende staat:
   - Gebruikersaccount: jouw eigen gebruikersnaam
   - **Run only when user is logged on** is aangevinkt
   - **Run with highest privileges** is aangevinkt

**Stap 3 — Stel de trigger in**
1. Ga naar het tabblad **Triggers** → klik op **New...**
2. Kies bij **Begin the task**: `At log on`
3. Klik op **OK**

**Stap 4 — Stel de actie in**
1. Ga naar het tabblad **Actions** → klik op **New...**
2. Vul in:
   - **Program/script:** `cmd.exe`
   - **Add arguments:** `/k "cd /d C:\Users\JOUWGEBRUIKERSNAAM\Desktop\HARTstikke-gezond-Dashboard-main && streamlit run app.py && timeout 3 && start chrome --start-fullscreen http://localhost:8501"`
3. Vervang `JOUWGEBRUIKERSNAAM` door jouw Windows-gebruikersnaam.
4. Klik op **OK**

**Stap 5 — Sla op en test**
1. Klik op **OK** om de taak op te slaan
2. Test door rechts te klikken op de taak → **Run**

> Het dashboard opent nu automatisch in Chrome in fullscreen zodra je inlogt. Als Chrome te snel opent voordat Streamlit klaar is, verhoog dan de `timeout 3` naar een hoger getal (bijv. `timeout 5`).

> Je bent klaar om te beginnen! Heb je vragen, neem dan contact op met een Biomedisch-technologie student/IT-specialist bij HARTstikke gezond of stuur een e-mail naar: vince.jonk@hva.nl
---

  
## ENGLISH VERSION 

A Streamlit dashboard for analyzing heart rate and movement data. Visualizes active minutes per day based on Dutch physical activity guidelines, with an interactive map of Amsterdam districts and a neighborhood comparison of health measurements.

---

## Installation

Follow the steps below. No technical knowledge is required — just follow them one by one.

---

### Step 1 — Download the project files

Go to the project's GitHub page and click the green **Code** button, then select **Download ZIP**.

Extract the ZIP file to an easy-to-find location, such as your desktop. You will get a folder named something like `hartstikke-gezond-main`. You may rename it to `hartstikke-gezond`.

---

### Step 2 — Install Python

Python is the software that runs the dashboard. First, check whether it is already installed:

#### Windows

1. Press the Windows key, type `cmd`, and open **Command Prompt**.
2. Type:

   ```bash
   python --version
   ```

3. Press Enter.
4. If you see a version number such as `Python 3.11.2`, you can skip this step.
5. If you see an error message, download Python from https://www.python.org/downloads/.
6. Run the installer.

> **Important:** Check the box **"Add Python to PATH"** before clicking Install.

#### Mac

1. Open **Terminal** (search for "Terminal" using Spotlight with ⌘ + Space).
2. Type:

   ```bash
   python3 --version
   ```

3. Press Enter.
4. If you see a version number, you can skip this step.
5. If you see an error message, download Python from https://www.python.org/downloads/ and follow the installation instructions.

---

### Step 3 — Place the data files in the correct folders

Inside the project folder, there are two folders where you need to place files:

**`Bestanden/`**  
Place your heart rate monitor CSV files here. These are the measurement files that can be selected in the dashboard.

**`BuurtData/`**  
The file `anonieme_buurtbewoners_gezondheid.csv` is placed here. This file contains health data for each district. when new measurements are done, this is where the're placed

The folder structure should look like this:

```text
hartstikke-gezond/
├── _pycache_/
├── Bestanden/
│   └── your-measurements.csv <
├── BuurtData/
    └── anonieme_buurtbewoners_gezondheid.csv <
├── pages/
    └── kaart.py
├── app.py    <-- Main app
├── data_utils.py
├── ecg_utils.py
├── health_utils.py
├── README.md
└── requirements.txt
```

---

### Step 4 — Install the required packages

#### Windows

1. Open the `hartstikke-gezond` folder in File Explorer.
2. Click the address bar, type `powershell`, and press Enter.
3. A Command Prompt window will open in the correct folder.
4. Run:

   ```bash
   pip install -r requirements.txt
   ```

5. Wait for the installation to finish.

#### Mac

1. Open **Terminal**.
2. Type `cd ` (including the space).
3. Drag the `hartstikke-gezond` folder into the Terminal window and press Enter.
4. Run:

   ```bash
   pip3 install -r requirements.txt
   ```

5. Wait for the installation to finish.

---

### Step 5 — Start the dashboard

#### Windows

Run:

```bash
streamlit run app.py
```

#### Mac

Run:

```bash
streamlit run app.py
```

The dashboard should open automatically in your browser.

If it does not try:
```text
python -m streamlit run app.py
```

or open:
```text
http://localhost:8501
```

> The Command Prompt or Terminal window must remain open while using the dashboard. If you close it, the dashboard will stop running.

---

## How does the dashboard work?

### Step 1 — Select a file

In the **left sidebar**, you will see a list of available CSV files.

Click the file you want to load. The dashboard processes the data automatically.

> The CSV files are stored in the `Bestanden/` folder and contain heart rate measurements from a wearable sensor.

---

### Step 2 — Enter your age

Enter your **age** in the sidebar.

This is required to calculate when your heart rate is high enough to count as "active".

> The dashboard uses the formula `220 - age` to estimate your maximum heart rate. A minute is considered active when your heart rate exceeds 60% of this maximum and movement is detected.

---

### Step 3 — View the graph

The **Activity: BPM + Movement** graph shows your heart rate over the duration of the recording.

- The **red line** represents your heart rate (BPM = beats per minute).
- **Green shaded areas** indicate periods where movement was detected.

The higher the red line and the more green areas you see, the more active you were during the recording.

---

### Step 4 — View your active minutes

To the right of the graph, you will see the number of **active minutes** recorded.

A minute counts as active when:

- Your heart rate was above 60% of your estimated maximum heart rate.
- Movement was detected.

#### Optional setting: Continuous activity requirement

In the sidebar, you can enable the **continuous activity rule**.

When enabled, only uninterrupted periods of active movement lasting at least 10 minutes will count. This filters out short bursts of activity, such as briefly standing up from a chair.

> Dutch physical activity guidelines recommend 21–30 minutes of moderate-intensity activity per day.

---

### Step 5 — Neighborhood comparison

Below the graph, you will find a table showing average health values for each Amsterdam district.

| Column | Meaning |
|----------|----------|
| **Cholesterol** | Amount of cholesterol in the blood (mmol/L). Lower is better. Healthy value: below 5.0. |
| **Systolic** | Upper blood pressure value (mmHg). Lower is better. Healthy value: below 120. |
| **Diastolic** | Lower blood pressure value (mmHg). Lower is better. Healthy value: below 80. |
| **Blood Glucose** | Amount of glucose in the blood (mmol/L). Healthy range: between 4.0 and 6.0. |
| **Active Minutes per Day** | Average number of active minutes per day in the district. |

Each value is accompanied by a colored indicator:

- 🟢 **Green** — within the healthy range
- 🟡 **Yellow** — close to the limit
- 🔴 **Red** — outside the healthy range

Hover over a value to see a short explanation and a bar chart.

---

### Step 6 — Amsterdam map

Click **📍 Go to map** at the bottom of the page to open the map view.

The map colors Amsterdam districts based on their average active minutes per day:

- 🔴 **Red** — fewer than 21 minutes per day (below the guideline)
- 🔵 **Blue** — 21–30 minutes per day (meets the guideline)
- 🟢 **Green** — more than 30 minutes per day (above the guideline)

Below the map is a table containing the exact values for each district.

Click **Back to dashboard** to return.

---

## CSV File Format

The CSV file must contain the following columns:

| Column | Description |
|----------|----------|
| `time` or `time_ms` | Timestamp in milliseconds |
| `ECG` | Raw ECG signal value |
| `accX`, `accY`, `accZ` | Accelerometer data from the motion sensor (X, Y, and Z axes) |

---

## Health values — reference standards

| Measurements | Healthy value | Source |
|---|---|---|
| Cholesterol | < 5,0 mmol/L | Nederlande Hartstichting |
| Bloodpressure (systolic) | < 120 mmHg | WHO |
| Bloodpressure (diastolic) | < 80 mmHg | WHO |
| Blood Glucose | 4,0 – 6,0 mmol/L | Diabetes Fonds |
| Active Minutes per Day | 21 – 30 min/day | RIVM Beweegrichtlijnen |

---

## Advanced Settings
### Automatically start the dashboard at login (Windows)
You can configure the dashboard to start automatically when you log in to Windows, so you do not have to launch it manually.
> **Important:** Place the project folder on your desktop. The path to your desktop always follows this pattern: `C:\Users\YOURUSERNAME\Desktop\HARTstikke-gezond-Dashboard-main`

**Step 1 — Open Task Scheduler as administrator**
1. Press `Win + S` and search for **Task Scheduler**
2. Right-click → **Run as administrator**

**Step 2 — Create a new task**
1. Right-click **Task Scheduler Library** → **Create Task...**
2. Give the task a name, for example `Start Dashboard`
3. Under **Security options**, make sure the following is set:
   - User account: your own username
   - **Run only when user is logged on** is selected
   - **Run with highest privileges** is checked

**Step 3 — Set the trigger**
1. Go to the **Triggers** tab → click **New...**
2. Set **Begin the task** to: `At log on`
3. Click **OK**

**Step 4 — Set the action**
1. Go to the **Actions** tab → click **New...**
2. Fill in:
   - **Program/script:** `cmd.exe`
   - **Add arguments:** `/k "cd /d C:\Users\YOURUSERNAME\Desktop\HARTstikke-gezond-Dashboard-main && streamlit run app.py && timeout 3 && start chrome --start-fullscreen http://localhost:8501"`
3. Replace `YOURUSERNAME` with your Windows username.
4. Click **OK**

**Step 5 — Save and test**
1. Click **OK** to save the task
2. Test it by right-clicking the task → **Run**

> The dashboard will now open automatically in Chrome in fullscreen whenever you log in. If Chrome opens too quickly before Streamlit is ready, increase `timeout 3` to a higher number (e.g. `timeout 5`).

> Your all set, if you have any questions, please contact an Biomedical-engineering student/IT-specialist at HARTstikke gezond or reach out via email: vince.jonk@hva.nl

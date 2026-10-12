# Scraping Real Estate BCN

## Overview
This project provides a Graphical User Interface (GUI) and an **Automated Batch Script** to scrape real estate listings (both **sale** and **rent**, for **new** and **used** properties, lands, chalets, etc.) from [Idealista](https://www.idealista.com), storing the results in CSV files inside the `output/` folder. 

It also includes an advanced suite of **Jupyter Notebooks** to explore, visualize, and compare the collected data across different cities and segments, generating standalone HTML Dashboards to share the insights.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MatiGrinberg/Scraping_Real_estate_BCN.git
   cd Scraping_Real_estate_BCN
   ```

2. **Install dependencies:**
   Make sure you have Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run the Scraper

### Option A: Using the GUI (Manual Scraping)
Run `python main.py` to open the interface.
1. Select the **Operation** (Rent or Buy).
2. Select the **Property Type** (New, Used, Land, Chalet, Reform).
3. Set your desired **Price** and **Area** ranges.
4. **(Optional) Custom Search Area (Shape):** Draw a custom area on Idealista, copy the **entire URL**, and paste it into the **"URL Base de Idealista"** text box.
5. **Custom Title:** Type a descriptive name in the **"Título Personalizado"** text box (e.g., `Ali_dentro`, `Bcn_afueras`). This text is crucial as it will be the exclusive name of your output CSV file (e.g., `Ali_dentro.csv`).
6. Click **"Iniciar Scraping"**. The system will open Chrome and begin saving the results in their respective `output/<parameters_and_title>/` folder.

### Option B: Automated Batch Scraping (Loop)
Run `python run_batch.py` to automatically scrape multiple zones sequentially.
- The script reads from `zonas.txt`, where each line is a custom title and an Idealista URL separated by a comma (e.g., `Val_dentro,https://www.idealista.com/...`).
- It applies pre-configured filters (e.g., Buy, New, 110k-320k) to all of them.
- It bypasses manual approval dialogs and extracts everything silently, waiting 10 seconds between zones to avoid bans.
- At the end, it generates a `urls_del_bucle.txt` containing all the exact URLs that were scraped.

---

## Data Analytics & HTML Dashboards

All scraped data is stored in the `output/` folder. You can analyze it using the provided Jupyter Notebooks in the `nb/` directory:

### 1. `Analytics.ipynb` (Single Market Analysis)
- Open it to analyze a single `.csv` file. 
- It cleans the data (automatically dropping properties >320k or <65m² that evade Idealista's filters) and calculates the Price/m² or Price/room.
- It generates Histograms, Scatter Plots, and Boxplots for that specific market.

### 2. `Compare_Searches.ipynb` (Multi-Market Comparison)
- Scans the entire `output/` folder to find properties matching your query (e.g., `buy_used`).
- Creates grouped comparative charts (e.g., Price vs Area scatter plots, and Distribution Histograms) for all your scraped cities/zones side-by-side.
- **Export Feature:** It embeds all generated graphics via Base64 into a standalone HTML file (e.g., `dashboard_comparativo_histogramas.html`) that you can double-click and view offline or share with anyone.

### 3. `Global_Comparison.ipynb` (Macro Market Overview)
- A powerful tool that consolidates ALL CSV files (New and Used) into a massive master dataset.
- Responds to specific analytical questions:
  - **City comparison**: Segmented Boxplots (e.g., Used-Centro across 5 cities).
  - **Internal City Dynamics**: Grouped Bar charts showing median prices with exact € numbers, calculating average % price variations (e.g., Centro vs Afueras, New vs Used).
  - **Global Market**: KDE density plots superimposing all the segments for the whole country.
- **Export Feature:** Generates a unified `reporte_global_independiente.html` dashboard holding all charts.

---

## Project Structure

- `main.py` / `run_batch.py`: Entry points for scraping (GUI and Batch).
- `zonas.txt`: Configuration file mapping zone titles to Idealista URLs for batch processing.
- `scripts/`: Internal scraping logic and Selenium drivers.
- `nb/`: Jupyter Notebooks for analytics.
- `output/`: Folder where the output `.csv` files and subfolders are stored.

## Optional details for Buy → Used

Individual listing visits also collect these optional CSV columns:

| Column | Value |
| --- | --- |
| `Useful area (m²)` | Numeric usable area, distinct from built area |
| `Orientation` | Reported orientation, such as `sur` or `sur, este` |
| `Construction year` | Construction year |
| `Energy rating` | Consumption rating A–G (not emissions) |
| `Energy consumption (kWh/m² year)` | Numeric energy consumption |
| `No heating` | True when explicitly absent, False when explicitly present, blank if unknown |

Missing details are saved as blank fields. This extraction is enabled only for Buy → Used,
and reuses the individual visit used to collect the location. Old CSVs remain readable;
these columns are treated as unknown when absent. Existing CSVs are not enriched retroactively.

In `nb/Analytics.ipynb`, initial cleaning checks missing values only in the original five
columns. Optional missing values never cause a row to be discarded during this step.
The final `filter_buy_rows` call exposes these parameters, all set to `None` by default:

```python
useful_area=None,         # e.g. ('>=', 80)
orientation=None,         # e.g. ['sur', 'sur, este']; full value, case-insensitive
construction_year=None,   # e.g. ('>=', 1980)
energy_rating=None,       # e.g. ['A', 'B', 'C', 'D', 'E']
energy_consumption=None,  # e.g. ('<', 80)
no_heating=None           # True: no heating; False: heating explicitly present
```

Numeric filters support `<`, `<=`, `>`, `>=`, `==`, and `!=`.
Each active optional filter accepts unknown values as well as matching values.
For example, `energy_consumption=('<', 80)` excludes known values of 80 or more,
but keeps missing consumption values. All existing price, area, room and location
filters still apply. Re-run the cleaning and function-definition cells before the final filter.

Local checks (without scraping):

```bash
python -B -m unittest discover -s tests -v
```

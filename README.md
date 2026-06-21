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

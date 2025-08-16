# Scraping_Real_estate_BCN

## Overview
This project scrapes real estate listings (both **sale** and **rent**, for **new** and **old** properties) from [Idealista](https://www.idealista.com), stores the results in CSV files, and provides analysis tools to explore the collected data.

---

## Project Structure

📂 project_root
│── Dependencies.py # Common imports, utility functions, Selenium driver setup
│── Rent_scraper.py # Scrapes rental properties (old and new)
│── Buy_scraper.py # Scrapes sale properties (old and new)
│── Rent_Analyze.py # Loads and analyzes scraped rental data
│── Buy_Analyze.py # Loads and analyzes scraped sale data


---

## How It Works

### **1. Scraping**
- **Rent_scraper.py** → Scrapes both **old** and **new** rental properties.
- **Buy_scraper.py** → Scrapes both **old** and **new** properties for sale.
- Both scripts:
  - Use **Selenium** to load pages dynamically.
  - Handle pagination to scrape all available listings.
  - Store extracted data (links, price, area, rooms, etc.) into CSV files.
 
- **Each file has 2 different functions (for NEW & OLD prop) that rely on helper functions from Dependencies.py** → you pass certain parameters like min/max price, size (sqM), location as area in a map, etc. → it returns a Csv file where each row is a property scraped according to your criteria (parameters passed into the function), with names of such files including the price range & type of property

---

### **2. Analysis**
- **Rent_Analyze.py** 
- **Buy_Analyze.py**

- **Each file has a dictionary with the possible Csv files so you can decide which one to import into a dataframe and start analyzing** → once you load any df, you use some of the functions imported from Dependencies.py to do data manipulation (e.g. calculating new columns), descriptive statistics (e.g. of the whole dataset/group of properties), and filtering to find the property you're looking for.


---

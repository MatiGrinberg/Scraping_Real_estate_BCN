import time
import random
import re
import pandas as pd
import json
import numpy as np
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

def load_config(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def initialize_driver():
    config = load_config()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-agent={random.choice(config['user_agents'])}")
    driver = uc.Chrome(options=chrome_options, version_main=149)
    return driver

def extract_shape_from_url(url):
    """Extrae el parámetro shape o barrio de una URL completa de Idealista."""
    if not url:
        return ""
    
    # Check for shape parameter
    shape_match = re.search(r"shape=([^&]+)", url)
    if shape_match:
        return shape_match.group(1)
    
    return ""

def prepare_data(df, max_pr=3000, price_col='Price', size_col='Area', price_per_sqm_col='Price/SqM', hab_col='Hab', kind="Property"):
    # Ensure column names match before processing
    if 'Price (€)' in df.columns:
        df = df.rename(columns={'Price (€)': price_col})
    if 'Area (m²)' in df.columns:
        df = df.rename(columns={'Area (m²)': size_col})
        
    if kind.lower() == "land":
        df[size_col] = df[hab_col].astype(str).str.replace("m²", "", regex=False).str.strip()
        df[hab_col] = 1
        
    df[size_col] = pd.to_numeric(df[size_col], errors='coerce')
    df = df.dropna(subset=[size_col])
    
    # Handle price cleaning if it's strings
    if df[price_col].dtype == object:
        df[price_col] = df[price_col].str.replace(".", "").str.replace("€", "").str.replace("/mes", "").str.strip()
    
    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
    df[price_col] = (df[price_col] / 1000).round(1) # In thousands for easier reading
    
    df[size_col] = df[size_col].astype(int)
    df[price_per_sqm_col] = (df[price_col] / df[size_col]).round(1)
    
    df = df[df[hab_col] != '-']
    # Replace non-numeric with NaN to drop or fill
    df[hab_col] = pd.to_numeric(df[hab_col], errors='coerce').fillna(1)
    df[hab_col] = df[hab_col].astype(int)
    
    df['Price/room'] = (df[price_col] / df[hab_col]).round(1)
    df = df[df[price_col] <= max_pr]
    
    df = df.drop_duplicates().reset_index(drop=True)
    if 'Location' in df.columns:
        df['Location'] = df['Location'].apply(lambda x: str(x).split(',')[1].strip() if ',' in str(x) else str(x))
        
    return df

def filter_by_string(d, c, tx):
    return d[d[c].str.contains(tx, na=False)]

def filter_per_loc(d, l):
    if isinstance(l, list) or isinstance(l, pd.Index):
        return d[d['Location'].isin(l)]
    return d[d['Location'] == l]

def filter_rent_rows(df, mx_pr_1h=1.2, mx_pr_room=0.8, min_area_1h=60, min_area_2h=75, min_area_3h=100, include=None, exclude=None):
    hab1 = (df['Hab'] == 1) & (df['Price'] <= mx_pr_1h) & (df['Area'] >= min_area_1h)
    hab2 = (df['Hab'] == 2) & (df['Price/room'] <= mx_pr_room) & (df['Area'] >= min_area_2h)
    hab3 = (df['Hab'] >= 3) & (df['Price/room'] <= mx_pr_room) & (df['Area'] >= min_area_3h)
    res = pd.concat([df[hab1], df[hab2], df[hab3]])
    
    if exclude:
        res = res[~res['Location'].isin(exclude)]
    if include:
        res = res[res['Location'].isin(include)]
    return res

def filter_buy_rows(df, min_h=2, min_price_sqm=1.5, max_price_sqm=3, min_area_any=60, min_area_large=100, min_hab_large=3, max_size=200, exclude=None):
    base = (df['Price/SqM'] <= max_price_sqm) & (df['Price/SqM'] >= min_price_sqm) & (df['Area'] >= min_area_any) & (df['Hab'] >= min_h) & (df['Area'] <= max_size)
    large_area_rule = (df['Area'] < min_area_large) | ((df['Area'] >= min_area_large) & (df['Hab'] >= min_hab_large))
    res = df[base & large_area_rule]
    
    if exclude:
        res = res[~res['Location'].isin(exclude)]
    return res

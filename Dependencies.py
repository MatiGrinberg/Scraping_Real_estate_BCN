import time
import random
import pandas as pd
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
plt.ion()
import seaborn as sns
import re
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

csv_map={"Buy_Reform": "60000-200000venta-viviendas__reform.csv","Rent_New": "alquiler-obranueva.csv","Buy_New": "venta-obranueva.csv","Buy_Chalet": "100000-300000venta-viviendas__chalets.csv","Buy_Old": "venta-viviendas.csv","Rent_Old":"alquiler-viviendas.csv","Land":"0-90000venta-terrenos_land.csv"}
csv_map=dict(sorted(csv_map.items()))
pd.set_option('display.max_colwidth', None)
timeout = 10 
USER_AGENTS=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36","Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"]

def initialize_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    driver = uc.Chrome(options=chrome_options)
    return driver

def scrape_page(url, collected_links, max_retries=3):
    retries = 0
    while retries < max_retries:
        driver = None
        try:
            driver = initialize_driver()
            driver.get(url)
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.items-container.items-list')))
            time.sleep(random.uniform(4, 8))
            for _ in range(random.randint(5, 15)):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(1, 3))
            section = driver.find_element(By.CSS_SELECTOR, 'section.items-container.items-list')
            articles = section.find_elements(By.CSS_SELECTOR, 'article.item')
            if not articles:
                raise ValueError("No articles found on page.")
            for article in articles:
                anchors = article.find_elements(By.CSS_SELECTOR, 'a[href^="/obra-nueva"]')
                for anchor in anchors:
                    collected_links.append(anchor.get_attribute('href'))
            print(f"Collected {len(collected_links)} links so far")
            print(f"Last_Link {collected_links[-1]}\n")
            return True  
        except Exception as e:
            retries += 1
            print(f"Error occurred on {url} (attempt {retries}/{max_retries}): {e}")
            if retries >= max_retries:
                print(f"Failed to scrape {url} after {max_retries} attempts.")
                return False
            time.sleep(random.uniform(5, 10))
        finally:
            if driver:
                driver.quit()

def scrape_page_v2(data, url, max_retries=3):
    attempts = 0
    while attempts < max_retries:
        attempts += 1
        driver = None
        try:
            driver = initialize_driver()
            driver.get(url)
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.items-container.items-list')))            
            for _ in range(random.randint(8, 20)):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(1, 4))            
            section = driver.find_element(By.CSS_SELECTOR, 'section.items-container.items-list')
            articles = section.find_elements(By.CSS_SELECTOR, 'article.item')
            if not articles:
                print(f"[Attempt {attempts}] No properties found on {url}. Retrying...")
                continue             
            print(f"Properties found on attempt {attempts}: {len(articles)}")
            for article in articles:
                try:
                    anchor = article.find_element(By.CSS_SELECTOR, 'a[href^="/inmueble/"]')
                    link = anchor.get_attribute('href')
                    price_element = article.find_element(By.CSS_SELECTOR, 'span.item-price')
                    price = price_element.text.strip().replace("€", "").replace("/mes", "").replace(".", "").strip()
                    details_div = article.find_element(By.CSS_SELECTOR, 'div.item-detail-char')
                    detail_spans = details_div.find_elements(By.CSS_SELECTOR, 'span.item-detail')
                    hab = detail_spans[0].text.replace("hab.", "").strip() if len(detail_spans) > 0 else "N/A"
                    area = detail_spans[1].text.replace("m²", "").strip() if len(detail_spans) > 1 else "N/A"
                    data.append({"Link": link, "Price (€)": price, "Area (m²)": area, "Hab": hab})
                except Exception as e:
                    print(f"Error processing an article: {e}")
                    continue
            print(f"Last link added: {data[-1]['Link']}\n")            
            time.sleep(random.uniform(timeout / 2, timeout))
            return True 
        except Exception as e:
            print(f"[Attempt {attempts}] Error occurred on {url}: {e}")
            time.sleep(random.uniform(10, 30))  
        finally:
            if driver:
                driver.quit()    
    print(f"Failed to scrape {url} after {max_retries} attempts.")
    return False


def scrape_link(link):
    data = [] 
    try:
        driver = initialize_driver()
        driver.get(link)
        wait = 3
        location = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.main-info__title-minor"))).text.strip()
        table = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table")))
        all_rows = table.find_elements(By.CSS_SELECTOR, "a.table__row")
        rows = [row for row in all_rows if row.get_attribute("class") == "table__row"]
        print(f"Link: {link} Total rows found: {len(rows)}")
        for i, row in enumerate(rows, start=1):
            try:
                row_href = row.get_attribute("href")
                strong_element = row.find_element(By.CSS_SELECTOR, "span strong")
                price = strong_element.text.strip().replace(".", "").replace("€", "")
                span_elements = row.find_elements(By.CSS_SELECTOR, "span.table__cell")
                if len(span_elements) > 2:
                    dorm = span_elements[1].text.strip().replace("dorm", "")
                    area = span_elements[2].text.strip().replace("m²", "")
                else:
                    area = "N/A"  
                    dorm= "N/A"
                data.append({"Location": location,"Link": row_href,"Price (€)": price,"Area (m²)": area,"Hab": dorm})
            except Exception as e:
                print(f"Error processing row {i}: {e}")
    except Exception as e:
        print(f"Error while scraping {link}: {e}")
    finally:
        driver.quit()
    return data

def scrape_link_v2(link):
    data = []
    try:
        driver = initialize_driver()
        driver.get(link)
        wait = 3
        location = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.main-info__title-minor"))).text.strip()
        table = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table")))
        all_rows = table.find_elements(By.CSS_SELECTOR, "a.table__row")
        rows = [row for row in all_rows if row.get_attribute("class") == "table__row"]
        print(f"\nLink: {link} Total rows found: {len(rows)}")
        for i, row in enumerate(rows, start=1):
            try:
                strong_element = row.find_element(By.CSS_SELECTOR, "span strong")
                price = strong_element.text.strip().replace(".", "").replace("€/Mes", "")
                span_elements = row.find_elements(By.CSS_SELECTOR, "span.table__cell")
                row_href = row.get_attribute("href")
                if len(span_elements) > 2:
                    dorm = span_elements[1].text.strip().replace("dorm", "")
                    area = span_elements[2].text.strip().replace("m²", "")
                else:
                    area = "N/A"  
                    dorm= "N/A"
                data.append({"Location": location,"Link": row_href,"Price (€)": price,"Area (m²)": area,"Hab": dorm})
            except Exception as e:
                print(f"Error processing row {i}: {e}")
    except Exception as e:
        print(f"Error while scraping {link}: {e}")
    finally:
        driver.quit() 
    return data

def scrape_all_links(links):
    all_data = []
    for link in links:
        link_data = scrape_link(link) 
        all_data.extend(link_data)  
    df=pd.DataFrame(all_data)
    return df

def scrape_all_links_v2(links):
    all_data = []
    for link in links:
        link_data = scrape_link_v2(link)
        all_data.extend(link_data)
    return pd.DataFrame(all_data)

def scrape_location(links, max_retries=2):
    locations = []
    for idx, link in enumerate(links, start=1):
        attempt,location = 0,"Unknown"
        while attempt < max_retries:
            try:
                driver = initialize_driver()
                driver.get(link)
                location_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.main-info__title-minor')))
                location = location_element.text.strip()
                break 
            except Exception as e:
                attempt += 1
                print(f"Error scraping {link} (Attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    print("Retrying...")
                    time.sleep(random.uniform(2, 5))  # short pause before retry
            finally:
                driver.quit()        
        locations.append(location)
        print(f"Processed link {idx}/{len(links)}: {location}")    
    print("Scraping process is complete.")
    return locations

def count_per_loc(d,gr):
    print("Q ("+gr+") Prop per location:\n", d['Location'].value_counts())
    
def mean_by_location(df, col):
    df_gr = df.groupby('Location')[col].agg(['mean','count']).assign(mean=lambda x: x['mean'].round(1)).sort_values('mean')
    print(df_gr)
    return df_gr.index
def filter_by_string(d,c,tx):
    return d[d[c].str.contains(tx, na=False)]
    
def filter_per_loc(d,l):
    return d[d['Location'].isin(l)]

def dupli_row(d,so):
    d[d.duplicated(keep=False)].sort_values(so)

def prepare_data(df,max_pr=300,price_col='Price (€)',size_col='Area (m²)',price_per_sqm_col='Price/SqM',hab_col='Hab',kind="Property"):
    if kind.lower()=="land":
        df[size_col] = df[hab_col].str.replace("m²", "", regex=False).str.strip()
        df[hab_col]=1
    df[size_col] = pd.to_numeric(df[size_col], errors='coerce')
    print("Null_Rows {}".format(len(df[df[size_col].isnull()])))
    df = df.dropna(subset=[size_col])
    df[price_col] = (df[price_col].astype(float) / 1000).round(1)
    df[size_col] = df[size_col].astype(int)
    df[price_per_sqm_col] = (df[price_col] / df[size_col]).round(1)
    df=df[df[hab_col]!='-']
    df[hab_col] = df[hab_col].astype(int)
    df['Price/room'] = (df[price_col] / df[hab_col]).round(1)
    df = df[df[price_col] <= max_pr]
    print('Duplicates ',df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    df['Location']=df['Location'].apply(lambda x: x.split(',')[1].strip() if ',' in x else x)
    df = df.rename(columns={'Price (€)': 'Price', 'Area (m²)': 'Area'})
    return df

def print_by_group(d,col):
    gr=d.groupby(col,sort=False)
    for c, g in gr:
        print(f"\n--- {c} ---")
        print(g)
        
def filter_rent_rows(df, mx_pr_1h=1.2, mx_pr_room=0.8, min_area_1h=60,min_area_2h=75,min_area_3h=100,include=None,exclude=None):
    hab1 = (df['Hab'] == 1) & (df['Price'] <= mx_pr_1h)& (df['Area'] >= min_area_1h)
    hab2 = (df['Hab'] == 2) & (df['Price/room'] <= mx_pr_room) & (df['Area'] >= min_area_2h)
    hab3 = (df['Hab'] >= 3) & (df['Price/room'] <= mx_pr_room) & (df['Area'] >= min_area_3h)
    res=pd.concat([df[hab1],df[hab2],df[hab3]])
    if exclude:
        res = res[~res['Location'].isin(exclude)]
    if include:
        res = res[res['Location'].isin(include)]
    return res



def filter_buy_rows(df,min_h=2,min_price_sqm=1.5,max_price_sqm=3,min_area_any=60,min_area_large=100,min_hab_large=3,max_size=200,exclude=None):
    base = (df['Price/SqM'] <= max_price_sqm)&(df['Price/SqM'] >= min_price_sqm) & (df['Area'] >= min_area_any)&(df['Hab'] >= min_h)&(df['Area']<=max_size)
    large_area_rule = (df['Area'] < min_area_large) | ((df['Area'] >= min_area_large) & (df['Hab'] >= min_hab_large))
    res=df[base&large_area_rule]
    if exclude:
        res=res[~res['Location'].isin(exclude)]
    return res

def print_numeric_columns_value_counts(df):
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        print(df[col].value_counts(dropna=False).sort_index())
        print('\n')
        
def plot_price_vs_size(df, title, price_col, size_col):
    plt.figure(figsize=(10, 6))
    plt.scatter(df[size_col], df[price_col], alpha=0.7, edgecolor='k')
    plt.title(title)
    plt.xlabel(size_col)
    plt.ylabel(price_col)
    plt.grid(True)
    plt.show()
    
def plot_histogram(df,t,c):
    plt.figure(figsize=(10, 6))
    sns.histplot(df[c], kde=True, bins=30)
    plt.title('Histogram '+t)
    plt.xlabel(c)
    plt.ylabel('Frequency')
    plt.show()

def plot_correlation_heatmap(df, cols, title):
    plt.figure(figsize=(8, 6))
    correlation_matrix = df[cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
    plt.title(title+' - Corr b/ Var', fontsize=16)
    plt.show()

def print_df_by_var(df,var,dfname):
    for v in var:
        print('\n'+dfname+"_"+v)
        print(sorted(df[v]))

def plot_boxplot(df, x_col, y_col, locations, group_num=None, char=10):
    df_filtered = df[df[x_col].isin(locations)]
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_filtered, x=x_col, y=y_col)
    title = f'{y_col} by {x_col} (group {group_num})'
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    labels = [label.get_text()[:char] for label in plt.gca().get_xticklabels()]
    plt.gca().set_xticklabels(labels)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def boxplot_location_groups(df, y_col='Price/SqM', n_groups=4):
    locations = df['Location'].unique()
    group_size = len(locations) // n_groups
    location_groups = [locations[i*group_size:(i+1)*group_size] for i in range(n_groups)]
    if len(locations) % n_groups != 0:
        location_groups[-1] = np.append(location_groups[-1], locations[n_groups*group_size:])
    for i, group in enumerate(location_groups, 1):
        plot_boxplot(df, 'Location', y_col, group, group_num=i, char=10)
    plt.ioff()
    plt.show()

def inspect_dataframe(df):
    print(f"Shape: {df.shape}\n")
    print("Column Data Types:")
    print(df.dtypes, "\n")
    print("Null Values per Column:")
    print(df.isnull().sum(), "\n")
    print("Rows with Null Values:")
    print(df[df.isnull().any(axis=1)])
    print("\n")
    print(f"Duplicate Rows sorted by 'Location':")
    print(df[df.duplicated(keep=False)].sort_values(by='Location', ascending=True))
    print("\n")
    print("Unique Values per Column (sorted):")
    for col in df.columns:
        unique_vals = sorted(df[col].dropna().unique())
        print(f"{col} ({len(unique_vals)} unique): {unique_vals}")
    print("\n")

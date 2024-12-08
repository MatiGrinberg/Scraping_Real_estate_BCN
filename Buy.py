import undetected_chromedriver as uc
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# En Construccion
typ,min_p,max_p = "obranueva",80000,240000
#url = f"https://www.idealista.com/areas/venta-obranueva/con-precio-hasta_300000,precio-desde_60000,1-dormitorio,2-dormitorios/mapa-google?shape=%28%28cbg%7BFijdI%7Ba_Aa%7C%7BCrsOmgUtyl%40zcgAjqUl_d%40nEzrp%40idThkS%29%29"
url = "https://www.idealista.com/areas/venta-obranueva/con-precio-hasta_300000,precio-desde_60000,1-dormitorio,2-dormitorios/mapa-google?shape=%28%28cbg%7BFijdI%7Ba_Aa%7C%7BCrsOmgUtyl%40zcgAjqUl_d%40nEzrp%40idThkS%29%29"
url = "https://www.idealista.com/areas/venta-obranueva/con-precio-hasta_300000,precio-desde_60000,1-dormitorio,2-dormitorios/?shape=%28%28cbg%7BFijdI%7Ba_Aa%7C%7BCrsOmgUtyl%40zcgAjqUl_d%40nEzrp%40idThkS%29%29"

timeout = 10  # Increase this timeout for page elements to load
collected_links = []
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

def initialize_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    driver = uc.Chrome(options=chrome_options)
    return driver


def scrape_page():
    global url
    try:
        driver = initialize_driver()
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section.items-container.items-list'))
        )
        time.sleep(random.uniform(5, 10))
        for _ in range(random.randint(5, 15)):
            driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(random.uniform(2, 5))
        section = driver.find_element(By.CSS_SELECTOR, 'section.items-container.items-list')
        articles = section.find_elements(By.CSS_SELECTOR, 'article.item')
        for article in articles:
            anchors = article.find_elements(By.CSS_SELECTOR, 'a[href^="/obra-nueva"]')
            for anchor in anchors:
                collected_links.append(anchor.get_attribute('href'))
        print(len(collected_links))
        try:
            next_button = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li.next a'))
            )
            next_page_url = next_button.get_attribute('href')
            print(f"Going to next page: {next_page_url}")
            url = next_page_url
        except (TimeoutException, WebDriverException):
            print("Last page reached or error in pagination. Stopping.")
            return False  
        return True  # Continue scraping
    except Exception as e:
        print(f"Error occurred on {url}: {e}")
        return False  # Stop scraping if an error happens
    driver.quit()
    
# Loop to scrape multiple pages until the last page is reached
while True:
    page_scraped = scrape_page()
    if not page_scraped:
        break  # Exit the loop if scraping fails or we reach the last page
    print(f"Scraping completed. Collected {len(collected_links)} links.")


    
#######   Scrape Individual Links ########


def scrape_link(link):
    data = []  # List to store extracted data for this specific link
    try:
        driver = initialize_driver()
        driver.get(link)
        wait = 3
        # Wait for location element to load
        location = WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.main-info__title-minor"))
        ).text.strip()
        # Wait for the table element to load
        table = WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.table"))
        )
        all_rows = table.find_elements(By.CSS_SELECTOR, "a.table__row")
        # Filter rows that have only the class "table__row"
        rows = [row for row in all_rows if row.get_attribute("class") == "table__row"]
        print(f"\nLink: {link} Total rows found: {len(rows)}")
        # Extract and append details for each row
        for i, row in enumerate(rows, start=1):
            try:
                # Extract price (text inside <strong>)
                strong_element = row.find_element(By.CSS_SELECTOR, "span strong")
                price = strong_element.text.strip().replace(".", "").replace("€", "")
                # Extract area (text inside the third <span>)
                span_elements = row.find_elements(By.CSS_SELECTOR, "span.table__cell")
                if len(span_elements) > 2:
                    area = span_elements[2].text.strip().replace("m²", "")
                else:
                    area = "N/A"  # Handle missing area
                data.append({
                    "Location": location,
                    "Link": link,
                    "Price (€)": price,
                    "Area (m²)": area
                })
                #print(f"Row {i}:  Location: {location}  Price: {price} €  Area: {area} m²")
            except Exception as e:
                print(f"Error processing row {i}: {e}")
    except Exception as e:
        print(f"Error while scraping {link}: {e}")
    finally:
        driver.quit()  # Ensure the driver is closed
    return data

def scrape_all_links(links):
    all_data = []
    for link in links:
        #print(f"Scraping link: {link}")
        link_data = scrape_link(link) 
        all_data.extend(link_data)  
    df = pd.DataFrame(all_data)
    return df


# Scrape data from all the links and store it in a DataFrame
new = scrape_all_links(collected_links)
print(len(new.Link.unique()))
new.to_csv(typ+".csv", index=False)



#################     Usadas  #################    #################    

typ, min_m, max_m = "viviendas", 70, 260
#url = f"https://www.idealista.com/areas/venta-viviendas/con-precio-hasta_240000,precio-desde_60000,metros-cuadrados-mas-de_70,metros-cuadrados-menos-de_260,de-un-dormitorio,de-dos-dormitorios,balcon-y-terraza,obra-nueva,buen-estado/mapa-google?shape=%28%28yoq%7BF_kpJswa%40gtcAmmQeyd%40tfNasZjyk%40%60%7C_AtvQb%7Db%40xXf%7DWokY%60iG%29%29"
#url = "https://www.idealista.com/areas/venta-viviendas/con-precio-hasta_240000,precio-desde_60000,metros-cuadrados-mas-de_70,metros-cuadrados-menos-de_260,de-un-dormitorio,de-dos-dormitorios,balcon-y-terraza,obra-nueva,buen-estado/mapa-google?shape=%28%28_io%7BFe%60dJ_mx%40ey%60CfmPsfQryl%40dfhAlvPpxUsr%40%7Ckb%40u%7DTbsO%29%29"
url ="https://www.idealista.com/areas/venta-viviendas/con-precio-hasta_240000,precio-desde_60000,metros-cuadrados-mas-de_70,metros-cuadrados-menos-de_260,de-un-dormitorio,de-dos-dormitorios,balcon-y-terraza,obra-nueva,buen-estado/?shape=%28%28_io%7BFe%60dJ_mx%40ey%60CfmPsfQryl%40dfhAlvPpxUsr%40%7Ckb%40u%7DTbsO%29%29"
data = []

def scrape_page():
    global url
    try:
        driver = initialize_driver()
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section.items-container.items-list'))
        )
        scrolls = random.randint(8, 20)
        for _ in range(scrolls):
            driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(random.uniform(1, 4))
        # Locate all articles within the section
        section = driver.find_element(By.CSS_SELECTOR, 'section.items-container.items-list')
        articles = section.find_elements(By.CSS_SELECTOR, 'article.item')
        print(len(articles))
        for article in articles:
            try:
                # Extract the link
                anchor = article.find_element(By.CSS_SELECTOR, 'a[href^="/inmueble/"]')
                link = anchor.get_attribute('href')
                
                # Extract the price
                price_element = article.find_element(By.CSS_SELECTOR, 'span.item-price')
                price = price_element.text.strip().replace("€", "").replace(".", "").strip()
                
                # Extract details (number of rooms and area)
                details_div = article.find_element(By.CSS_SELECTOR, 'div.item-detail-char')
                detail_spans = details_div.find_elements(By.CSS_SELECTOR, 'span.item-detail')
                hab = detail_spans[0].text.replace("hab.", "").strip() if len(detail_spans) > 0 else "N/A"
                area = (
                    detail_spans[1].text.replace("m²", "").strip() if len(detail_spans) > 1 else "N/A"
                )
                
                # Append to the data list
                data.append({
                    "Link": link,
                    "Price (€)": price,
                    "Area (m²)": area,
                    "Hab": hab
                })
            except Exception as e:
                print(f"Error processing an article: {e}")
                continue
        # Pagination: Find the "next" button and get its URL
        try:
            next_button = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li.next a'))
            )
            next_page_url = next_button.get_attribute('href')
            print(f"Going to next page: {next_page_url}")
            url = next_page_url
        except (TimeoutException, WebDriverException):
            print("Last page reached or error in pagination. Stopping.")
            return False  # Stop scraping
        # Random delay to avoid blocking
        time.sleep(random.uniform(timeout / 2, timeout))
        return True  # Continue scraping
    except Exception as e:
        print(f"Error occurred on {url}: {e}")
        time.sleep(random.uniform(30, 60))  # Longer delay on error
        return False  # Stop scraping if an error happens


# Loop to scrape multiple pages until the last page is reached
while True:
    page_scraped = scrape_page()
    if not page_scraped:
        break  # Exit the loop if scraping fails or we reach the last page


# Create a DataFrame from the collected data
old = pd.DataFrame(data)
print(f"Scraping completed. Collected {len(data)} rows.")

def scrape_location(links):
    locations = []
    for idx, link in enumerate(links, start=1):
        try:
            driver = initialize_driver()
            driver.get(link)
            location_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span.main-info__title-minor'))
            )
            location = location_element.text.strip()
            locations.append(location)
        except Exception as e:
            print(f"Error scraping {link}: {e}")
            locations.append("Unknown")  # Append a placeholder for failed cases
        finally:
            driver.quit()
            print(f"Processed link {idx}/{len(links)}.")
    print("Scraping process is complete.")
    return locations

# Apply the function to scrape locations for all links
locations= scrape_location(old['Link'].tolist())

old['Location'] = locations
#old['Location'] = old['Link'].apply(scrape_location)
print("Links: {} Locations: {}".format(len(old.Link.unique()),len(locations)))

old.to_csv(typ+".csv", index=False)




####### analsyis DF individually ######

new = pd.read_csv('obranueva.csv')
old = pd.read_csv('viviendas.csv')

def prepare_data(df, price_col='Price (€)', size_col='Area (m²)', price_per_sqm_col='Price/SqM'):
    null_rows = df[df['Area (m²)'].isnull()]
    print("Null_Rows {}".format(len(null_rows)))
    df = df.dropna(subset=[size_col])
    df[price_col] = (df[price_col].astype(float) / 1000).round(0).astype(int)
    df[size_col] = df[size_col].astype(int)
    df[price_per_sqm_col] = (df[price_col] / df[size_col]).round(1)
    df=df[df['Price (€)']<=300]
    df = df.drop_duplicates().reset_index(drop=True)
    return df

new = prepare_data(new)
old = prepare_data(old)

def plot_price_vs_size(df, title, price_col, size_col):
    plt.figure(figsize=(10, 6))
    plt.scatter(df[size_col], df[price_col], alpha=0.7, edgecolor='k')
    plt.title(title)
    plt.xlabel('Area (m²)')
    plt.ylabel('Price (€)')
    plt.grid(True)
    plt.show()
    
    
def plot_price_per_sqm_histogram(df, t, price_per_sqm_col='Price/SqM'):
    plt.figure(figsize=(10, 6))
    sns.histplot(df[price_per_sqm_col], kde=True, bins=30)
    plt.title('Distribution of Price Per Square Meter '+t)
    plt.xlabel('Price Per Square Meter (€)')
    plt.ylabel('Frequency')
    plt.show()


def plot_boxplot(df, x_col, y_col, title, xlabel, ylabel, locations,char):
    df_filtered = df[df[x_col].isin(locations)]
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_filtered, x=x_col, y=y_col)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    labels = [label.get_text()[:char] for label in plt.gca().get_xticklabels()]
    plt.gca().set_xticklabels(labels)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
    


for d in [old, new]:
    locations = d['Location'].unique()
    mid_index = len(locations) // 4
    location_groups = [
        locations[:mid_index],  # Group 1
        locations[mid_index: 2 * mid_index],  # Group 2
        locations[2 * mid_index: 3 * mid_index],  # Group 3
        locations[3 * mid_index:]  # Group 4
    ]
    for i, locations_group in enumerate(location_groups, 1):
        plot_boxplot(d, 'Location', 'Price/SqM', 
                     f'Price Per Square Meter by Location (group {i})', 
                     'Location', 'Price Per Square Meter (€)', 
                     locations_group,10)
        

def plot_correlation_heatmap(df, cols, title):
    plt.figure(figsize=(8, 6))
    correlation_matrix = df[cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
    plt.title(title, fontsize=16)
    plt.show()


def print_df_by_var(df,var,dfname):
    for v in var:
        print('\n'+dfname+v)
        print(sorted(df[v]))


############### PLOTS 
#print_df_by_var(new,['Price (€)', 'Area (m²)', 'Price/SqM'],'New ')
#print_df_by_var(old,['Price (€)', 'Area (m²)', 'Price/SqM'],'Old ')

plot_price_vs_size(old,'OLD => Price vs Size','Price (€)','Area (m²)')
plot_price_vs_size(old,'OLD => Price/Sqm vs Size','Price/SqM','Area (m²)')

plot_price_vs_size(new,'NEW => Price vs Size','Price (€)','Area (m²)')
plot_price_vs_size(new,'NEW => Price/Sqm vs Size','Price/SqM','Area (m²)')

#plot_price_per_sqm_histogram(old,'(old)')
#plot_price_per_sqm_histogram(new,'(new)')

#plot_correlation_heatmap(new, ['Price (€)', 'Area (m²)', 'Price/SqM'], 'NEW: Correlation Between Variables')
#plot_correlation_heatmap(old, ['Price (€)', 'Area (m²)', 'Price/SqM'], 'OLD: Correlation Between Variables')

# Filtered Rows
rows_old_price_vs_size = old[(old['Area (m²)'] >= 70) & (old['Price (€)'] < 175)].index
rows_old_price_sqm = old[(old['Price/SqM'] > 1.2)&(old['Price/SqM'] <= 2.1)].index
rows_new_price_vs_size = new[(new['Area (m²)'] >= 59) & (new['Price (€)'] <= 250)].index
rows_new_price_sqm = new[new['Price/SqM'] <= 2.6].index

print(f"Length of rows_old_price_vs_size: {len(rows_old_price_vs_size)}")
print(f"Length of rows_new_price_vs_size: {len(rows_new_price_vs_size)}")
print(f"Length of rows_old_price_sqm: {len(rows_old_price_sqm)}")
print(f"Length of rows_new_price_sqm: {len(rows_new_price_sqm)}")

intersection_old = list(set(rows_old_price_vs_size).intersection(rows_old_price_sqm))
intersection_new = list(set(rows_new_price_vs_size).intersection(rows_new_price_sqm))

print(f"Intersection of old indices: {len(intersection_old)}")
print(f"Intersection of new indices: {len(intersection_new)}")

old=old.loc[intersection_old,:].sort_values('Price (€)')
new=new.loc[intersection_new,:].sort_values('Price/SqM')





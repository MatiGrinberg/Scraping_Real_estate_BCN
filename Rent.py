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

url='https://www.idealista.com/areas/alquiler-obranueva/con-precio-hasta_1700,precio-desde_600,1-dormitorio,2-dormitorios,3-dormitorios/?shape=%28%28mpc%7BFuvvJapSqcLq%60H%60%7B%40wyF_bOmmLsia%40%7B_HqqRbyDkmu%40nrj%40zqmArqWn%7CSsyBtw%5C%7DgI%7ElE%29%29'

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
    
while True:
    page_scraped = scrape_page()
    if not page_scraped:
        break  # Exit the loop if scraping fails or we reach the last page
    print(f"Scraping completed. Collected {len(collected_links)} links.")


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
                price = strong_element.text.strip().replace(".", "").replace("€/Mes", "")
                # Extract area (text inside the third <span>)
                span_elements = row.find_elements(By.CSS_SELECTOR, "span.table__cell")
                if len(span_elements) > 2:
                    dorm = span_elements[1].text.strip().replace("dorm", "")
                    area = span_elements[2].text.strip().replace("m²", "")
                else:
                    area = "N/A"  # Handle missing area
                    dorm= "N/A"
                data.append({
                    "Location": location,
                    "Link": link,
                    "Price (€)": price,
                    "Area (m²)": area,
                    "Hab": dorm
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
new.to_csv("rent_new.csv", index=False)


# Usadas
url='https://www.idealista.com/areas/alquiler-viviendas/con-precio-hasta_1300,precio-desde_350,metros-cuadrados-mas-de_50,metros-cuadrados-menos-de_120,de-un-dormitorio,de-dos-dormitorios,de-tres-dormitorios,amueblado_amueblados,balcon-y-terraza,alquiler-de-larga-temporada/?shape=%28%28mpc%7BFuvvJapSqcLq%60H%60%7B%40wyF_bOmmLsia%40%7B_HqqRbyDkmu%40nrj%40zqmArqWn%7CSsyBtw%5C%7DgI%7ElE%29%29'
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

old.to_csv("rent_old.csv", index=False)



######## ANALYSIS   #############

new = pd.read_csv('rent_new.csv')
old = pd.read_csv('rent_old.csv')

def prepare_data(df, price_col='Price (€)', size_col='Area (m²)', price_per_sqm_col='Price/SqM'):
    null_rows = df[df['Area (m²)'].isnull()]
    print("Null_Rows {}".format(len(null_rows)))
    df = df.dropna(subset=[size_col])
    df[price_col] = (df[price_col].astype(str).str.replace('/mes', '', regex=True).astype(float).round(0).astype(int))
    df[size_col] = df[size_col].astype(int)
    df[price_per_sqm_col] = (df[price_col] / df[size_col]).round(1)
    df['Price/room'] = (df[price_col] / df['Hab']).round(1)
    df = df.drop_duplicates().reset_index(drop=True)
    return df

new = prepare_data(new)
old = prepare_data(old)

def plot_price_vs_size(df, title, price_col, size_col):
    plt.figure(figsize=(10, 6))
    plt.scatter(df[size_col], df[price_col], alpha=0.7, edgecolor='k')
    plt.title(title)
    plt.xlabel(size_col)
    plt.ylabel(price_col)
    plt.grid(True)
    plt.show()
    
    
def plot_price_per_sqm_histogram(df, t, c='Price/SqM'):
    plt.figure(figsize=(10, 6))
    sns.histplot(df[c], kde=True, bins=30)
    plt.title('Distribution of '+c+t)
    plt.xlabel(c)
    plt.ylabel('Frequency')
    plt.show()


def plot_boxplot(df, x_col, y_col, title, xlabel, ylabel,locations,char):
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
    all_locations = d['Location'].unique()
    plot_boxplot(d,'Location','Price/SqM','Price Per Square Meter by Location','Location','Price Per Square Meter (€)',all_locations,10)
        

def plot_correlation_heatmap(df, title):
    plt.figure(figsize=(8, 6))
    correlation_matrix = df.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
    plt.title(title, fontsize=16)
    plt.show()


def print_df_by_var(df,var,dfname):
    for v in var:
        print('\n'+dfname+v)
        print(sorted(df[v]))


############### PLOTS 
plot_price_vs_size(old,'OLD => Price vs Size','Price (€)','Area (m²)')
plot_price_vs_size(old,'OLD => Price/room vs Hab','Price/room','Hab')
plot_price_vs_size(old,'OLD => Price/Sqm vs Size','Price/SqM','Area (m²)')
plot_price_vs_size(old,'OLD => Price/room vs Size','Price/room','Area (m²)')

plot_price_vs_size(new,'new => Price vs Size','Price (€)','Area (m²)')
plot_price_vs_size(new,'OLD => Price/room vs Hab','Price/room','Hab')
plot_price_vs_size(new,'new => Price/Sqm vs Size','Price/SqM','Area (m²)')
plot_price_vs_size(new,'new => Price/room vs Size','Price/room','Area (m²)')

plot_price_per_sqm_histogram(old,' (old)',c='Price/SqM')
plot_price_per_sqm_histogram(new,' (new)',c='Price/SqM')

plot_price_per_sqm_histogram(old,' (old)',c='Price/room')
plot_price_per_sqm_histogram(new,' (new)',c='Price/room')

plot_price_per_sqm_histogram(old,' (old)',c='Price (€)')
plot_price_per_sqm_histogram(new,' (new)',c='Price (€)')

plot_price_per_sqm_histogram(old,' (old)',c='Area (m²)')
plot_price_per_sqm_histogram(new,' (new)',c='Area (m²)')


plot_correlation_heatmap(new.drop(['Location','Link'],axis=1), 'NEW: Correlation Between Variables')
plot_correlation_heatmap(old.drop(['Location','Link'],axis=1), 'OLD: Correlation Between Variables')

# Filtered Rows
rows_old_filtered = old[(old['Area (m²)'] > 60) &(old['Price/room'] <= 1000)&(old['Price/SqM'] <= 20)&(old['Price (€)'] < 1300)].index
#rows_new_filtered = new[(new['Price (€)'] <= 250)&(new['Price/SqM'] <= 2.6)].index

print(f"Length of rows_old: {len(rows_old_filtered)}")
#print(f"Length of rows_new: {len(rows_new_filtered)}")

old=old.loc[rows_old_filtered,:].sort_values('Price (€)')
#new=new.loc[rows_new_filtered,:].sort_values('Price/SqM')
old[['Link','Hab','Area (m²)','Price/room','Price (€)']]







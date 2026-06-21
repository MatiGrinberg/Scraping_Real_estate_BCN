import time
import random
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scripts.utils import initialize_driver, extract_shape_from_url

TIMEOUT = 10

def scrape_links_from_page(url, collected_links, max_retries=3):
    """Scrapes only the property links from a listing page (used for New Properties)."""
    retries = 0
    while retries < max_retries:
        driver = None
        try:
            driver = initialize_driver()
            driver.get(url)
            WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.items-container.items-list')))
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
            return True
        except Exception as e:
            retries += 1
            print(f"Error on {url} (attempt {retries}/{max_retries}): {e}")
            if retries >= max_retries:
                return False
            time.sleep(random.uniform(5, 10))
        finally:
            if driver:
                driver.quit()

def scrape_list_page_details(data, url, max_retries=3):
    """Scrapes property details directly from the list page (used for Used Properties/Land)."""
    attempts = 0
    while attempts < max_retries:
        attempts += 1
        driver = None
        try:
            driver = initialize_driver()
            driver.get(url)
            WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.items-container.items-list')))            
            for _ in range(random.randint(8, 20)):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(1, 4))            
            
            section = driver.find_element(By.CSS_SELECTOR, 'section.items-container.items-list')
            articles = section.find_elements(By.CSS_SELECTOR, 'article.item')
            if not articles:
                print(f"[Attempt {attempts}] No properties found on {url}. Retrying...")
                continue             
            
            for article in articles:
                try:
                    anchor = article.find_element(By.CSS_SELECTOR, 'a[href^="/inmueble/"]')
                    link = anchor.get_attribute('href')
                    price_element = article.find_element(By.CSS_SELECTOR, 'span.item-price')
                    price = price_element.text.strip().replace("€", "").replace("/mes", "").replace(".", "").strip()
                    
                    details_div = article.find_element(By.CSS_SELECTOR, 'div.item-detail-char')
                    detail_spans = details_div.find_elements(By.CSS_SELECTOR, 'span.item-detail')
                    
                    hab = "N/A"
                    area = "N/A"
                    for span in detail_spans:
                        text = span.text.lower()
                        if "m²" in text:
                            # Keep original text to retain formatting if needed, but remove 'm²'
                            area = span.text.replace("m²", "").strip()
                        elif "hab." in text:
                            hab = span.text.replace("hab.", "").strip()
                    
                    data.append({"Link": link, "Price (€)": price, "Area (m²)": area, "Hab": hab})
                except Exception as e:
                    continue
                    
            time.sleep(random.uniform(TIMEOUT / 2, TIMEOUT))
            return True 
        except Exception as e:
            print(f"[Attempt {attempts}] Error occurred on {url}: {e}")
            time.sleep(random.uniform(10, 30))  
        finally:
            if driver:
                driver.quit()    
    return False

def scrape_new_property_details(link, is_rent=False):
    """Visits a specific new property page and extracts data from the table rows."""
    data = []
    try:
        driver = initialize_driver()
        driver.get(link)
        wait = 3
        location = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.main-info__title-minor"))).text.strip()
        table = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table")))
        all_rows = table.find_elements(By.CSS_SELECTOR, "a.table__row")
        rows = [row for row in all_rows if row.get_attribute("class") == "table__row"]
        
        for i, row in enumerate(rows, start=1):
            try:
                row_href = row.get_attribute("href")
                strong_element = row.find_element(By.CSS_SELECTOR, "span strong")
                
                price = strong_element.text.strip().replace(".", "").replace("€", "")
                if is_rent:
                    price = price.replace("/Mes", "").replace("/mes", "")
                    
                span_elements = row.find_elements(By.CSS_SELECTOR, "span.table__cell")
                if len(span_elements) > 2:
                    dorm = span_elements[1].text.strip().replace("dorm", "")
                    area = span_elements[2].text.strip().replace("m²", "")
                else:
                    area = "N/A"  
                    dorm= "N/A"
                data.append({"Location": location, "Link": row_href, "Price (€)": price, "Area (m²)": area, "Hab": dorm})
            except Exception as e:
                pass
    except Exception as e:
        print(f"Error scraping {link}: {e}")
    finally:
        driver.quit()
    return data

def get_location_for_links(links, max_retries=2, log_callback=None):
    """Visits a list of links just to extract the location (used for old properties)."""
    locations = []
    visited_count = 0
    for idx, link in enumerate(links, start=1):
        if log_callback:
            log_callback(f"[{idx}/{len(links)}] Obteniendo ubicación de: {link}")
        visited_count += 1
        attempt, location = 0, "Unknown"
        while attempt < max_retries:
            try:
                driver = initialize_driver()
                driver.get(link)
                location_element = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.main-info__title-minor')))
                location = location_element.text.strip()
                break 
            except Exception as e:
                attempt += 1
                if attempt < max_retries:
                    time.sleep(random.uniform(2, 5))
            finally:
                driver.quit()        
        locations.append(location)
    return locations, visited_count

# Main runner functions
def run_scraper(operation, property_type, min_price, max_price, min_area, max_area, shape_url, output_filename, log_callback=print, confirm_callback=None):
    """Main execution entry point for the GUI."""
    import os
    shape_param = extract_shape_from_url(shape_url)
    
    # Definir la subcarpeta específica para la búsqueda
    subfolder = output_filename
    output_dir = os.path.join("output", subfolder)
    parts = subfolder.split("_", 3)
    custom_name = parts[3] if len(parts) >= 4 else subfolder
    output_path = os.path.join(output_dir, f"{custom_name}.csv")
    
    base_url = "https://www.idealista.com/areas"
    
    # Logic to build the URL based on operation and type
    if operation == "Rent":
        if property_type == "New":
            # Rent New
            log_callback("Filtros fijos aplicados: 1, 2 o 3 dormitorios.")
            url_filter = f"/alquiler-obranueva/con-precio-hasta_{max_price},precio-desde_{min_price},1-dormitorio,2-dormitorios,3-dormitorios/"
            if shape_param:
                url_filter += f"?shape={shape_param}"
                
            full_url = base_url + url_filter
            return _scrape_new_runner(full_url, output_path, is_rent=True, log_callback=log_callback, confirm_callback=confirm_callback)
            
        else:
            # Rent Old
            log_callback("Filtros fijos aplicados: 1, 2 o 3 dormitorios, amueblado, balcón/terraza, buen estado/obra nueva, larga temporada.")
            url_filter = f"/alquiler-viviendas/con-precio-hasta_{max_price},precio-desde_{min_price},metros-cuadrados-mas-de_{min_area},metros-cuadrados-menos-de_{max_area},de-un-dormitorio,de-dos-dormitorios,de-tres-dormitorios,amueblado_amueblados,balcon-y-terraza,obra-nueva,buen-estado,alquiler-de-larga-temporada/"
            if shape_param:
                url_filter += f"?shape={shape_param}"
            full_url = base_url + url_filter
            return _scrape_old_runner(full_url, output_path, log_callback=log_callback, confirm_callback=confirm_callback)
            
    elif operation == "Buy":
        if property_type == "New":
            url_filter = f"/venta-obranueva/con-precio-hasta_{max_price},precio-desde_{min_price},1-dormitorio,2-dormitorios,3-dormitorios/"
            if shape_param:
                url_filter += f"?shape={shape_param}&ordenado-por=precios-asc"
            full_url = base_url + url_filter
            return _scrape_new_runner(full_url, output_path, is_rent=False, log_callback=log_callback, confirm_callback=confirm_callback)
            
        else:
            if property_type == "Land":
                prop_path = "venta-terrenos"
                url_filter = f"con-precio-hasta_{max_price},metros-cuadrados-mas-de_{min_area},metros-cuadrados-menos-de_{max_area},terrenos-urbanos"
            else:
                prop_path = "venta-viviendas"
                
                condition = "obra-nueva,buen-estado,"
                extra_filters = ""
                if property_type == "Reform":
                    condition = "para-reformar,"
                elif property_type == "Chalet":
                    extra_filters = "chalets,"
                    
                url_filter = f"con-precio-hasta_{max_price},precio-desde_{min_price},metros-cuadrados-mas-de_{min_area},metros-cuadrados-menos-de_{max_area},{extra_filters}de-dos-dormitorios,de-tres-dormitorios,de-cuatro-cinco-habitaciones-o-mas,balcon-y-terraza,{condition}sin-inquilinos"
            
            full_url = f"{base_url}/{prop_path}/{url_filter}/"
            if shape_param:
                full_url += f"?shape={shape_param}&ordenado-por=precios-asc"
                
            return _scrape_old_runner(full_url, output_path, log_callback=log_callback, confirm_callback=confirm_callback)

def _get_search_metadata(url):
    driver = initialize_driver()
    driver.get(url)
    last_page_num = 1
    total_props = "Desconocido"
    try:
        try:
            h1_el = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'h1-container__text')))
            match = re.search(r'^([\d\.]+)\s+', h1_el.text.strip())
            if match:
                total_props = match.group(1)
        except:
            pass
            
        try:
            pagination_ul = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pagination ul')))
            li_elements = pagination_ul.find_elements(By.TAG_NAME, 'li')
            if len(li_elements) >= 2:
                last_page_num = int(li_elements[-2].text.strip())
        except:
            pass
    finally:
        driver.quit()
    return last_page_num, total_props

def _scrape_new_runner(base_url, output_path, is_rent, log_callback, confirm_callback=None):
    log_callback(f"Buscando el número total de páginas en: {base_url}")
    last_page_num, total_props = _get_search_metadata(base_url)
    log_callback(f"Total de páginas: {last_page_num} | Propiedades: {total_props}")
    
    if confirm_callback:
        if not confirm_callback(base_url, last_page_num, total_props):
            log_callback("Proceso cancelado por el usuario.")
            return "Operación cancelada. No se realizó el scraping."
    
    collected_links = []
    
    for page_num in range(1, last_page_num + 1):
        if page_num == 1:
            page_url = base_url
        else:
            if "?" in base_url:
                prefix, query = base_url.split("?", 1)
                page_url = f"{prefix.rstrip('/')}/pagina-{page_num}?{query}"
            else:
                page_url = f"{base_url.rstrip('/')}/pagina-{page_num}"
                
        scrape_links_from_page(page_url, collected_links)
        log_callback(f"Enlaces recolectados hasta ahora: {len(collected_links)}")
        
    all_data = []
    log_callback("Extrayendo detalles de cada propiedad nueva...")
    visited_count = 0
    for idx, link in enumerate(collected_links, start=1):
        log_callback(f"[{idx}/{len(collected_links)}] Obteniendo detalles de: {link}")
        link_data = scrape_new_property_details(link, is_rent=is_rent)
        visited_count += 1
        all_data.extend(link_data)
        
    df = pd.DataFrame(all_data)
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    total_accumulated = len(collected_links)
    return (f"Terminado. Total recolectado: {len(df)} propiedades. Guardado en {output_path}\n"
            f"[Check Consistencia: Links acumulados al inicio: {total_accumulated} | Links procesados individualmente: {visited_count}]")

def _scrape_old_runner(base_url, output_path, log_callback, confirm_callback=None):
    log_callback(f"Buscando el número total de páginas en: {base_url}")
    last_page_num, total_props = _get_search_metadata(base_url)
    log_callback(f"Total de páginas: {last_page_num} | Propiedades: {total_props}")
    
    if confirm_callback:
        if not confirm_callback(base_url, last_page_num, total_props):
            log_callback("Proceso cancelado por el usuario.")
            return "Operación cancelada. No se realizó el scraping."
    
    data = []
    
    for page_num in range(1, last_page_num + 1):
        if page_num == 1:
            page_url = base_url
        else:
            if "?" in base_url:
                prefix, query = base_url.split("?", 1)
                page_url = f"{prefix.rstrip('/')}/pagina-{page_num}?{query}"
            else:
                page_url = f"{base_url.rstrip('/')}/pagina-{page_num}"
                
        if not scrape_list_page_details(data, page_url):
            log_callback(f"Falló al scrapear la página {page_num}.")
            break
        log_callback(f"Propiedades recolectadas hasta ahora: {len(data)}")
            
    visited_count = 0
    df = pd.DataFrame(data)
    if not df.empty and 'Link' in df.columns:
        log_callback("Extrayendo ubicación de los enlaces de las propiedades...")
        locations, visited_count = get_location_for_links(df['Link'].tolist(), log_callback=log_callback)
        df['Location'] = locations
        
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    total_accumulated = len(df)
    return (f"Terminado. Total recolectado: {len(df)} propiedades. Guardado en {output_path}\n"
            f"[Check Consistencia: Links acumulados al inicio: {total_accumulated} | Links procesados individualmente: {visited_count}]")

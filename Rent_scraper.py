from Dependencies import *

# NEW
def scrape_new_properties(typ, max_price, min_price, shape):
    base_url = (f"https://www.idealista.com/areas/{typ}/con-precio-hasta_{max_price},"f"precio-desde_{min_price},1-dormitorio,2-dormitorios,3-dormitorios/"f"?shape={shape}")
    print(base_url)
    collected_links = []
    driver = initialize_driver()
    driver.get(base_url)
    try:
        pagination_ul = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pagination ul')))
        li_elements = pagination_ul.find_elements(By.TAG_NAME, 'li')
        if len(li_elements) > 1:
            last_page_li = li_elements[-2]
            last_page_num = int(last_page_li.text)
        else:
            last_page_num = 1
    except TimeoutException:
        last_page_num = 1
    driver.quit()
    for page_num in range(1, last_page_num + 1):
        if page_num == 1:
            url = base_url
        else:
            url = base_url + f"pagina-{page_num}/"
        print(f"Scraping page {page_num}: {url}")
        page_scraped = scrape_page(url, collected_links)
        if not page_scraped:
            break
    print(f"Scraping completed. Collected {len(collected_links)} links.")
    new_df = scrape_all_links_v2(collected_links)
    print(f"Unique links collected: {len(new_df.Link.unique())}")
    new_df.to_csv(str(min_price)+"-"+str(max_price)+typ+".csv", index=False)
    return new_df


# OLD
def scrape_used_properties(typ, max_price, min_price, min_area, max_area, shape):
    base_url = (f"https://www.idealista.com/areas/{typ}/con-precio-hasta_{max_price},"f"precio-desde_{min_price},metros-cuadrados-mas-de_{min_area},"f"metros-cuadrados-menos-de_{max_area},de-un-dormitorio,de-dos-dormitorios,"f"de-tres-dormitorios,amueblado_amueblados,balcon-y-terraza,obra-nueva,"f"buen-estado,alquiler-de-larga-temporada/?shape={shape}")
    print(base_url)
    driver = initialize_driver()
    driver.get(base_url)
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pagination ul')))
    pagination_ul = driver.find_element(By.CSS_SELECTOR, 'div.pagination ul')
    li_items = pagination_ul.find_elements(By.TAG_NAME, 'li')
    last_page_num = 1
    if len(li_items) >= 2:
        second_last_li = li_items[-2]
        try:
            last_page_num = int(second_last_li.text.strip())
        except ValueError:
            print(f"Could not convert last page number text '{second_last_li.text}' to int. Defaulting to 1.")
    driver.quit()
    print(f"Total pages found: {last_page_num}")
    data = []
    for page_num in range(1, last_page_num + 1):
        if page_num == 1:
            url = base_url
        else:
            url = base_url.replace("/?", f"/pagina-{page_num}?")
        if not scrape_page_v2(data, url):
            break
    old_df = pd.DataFrame(data)
    print(f"Scraping completed. Collected {len(data)} rows.")
    locations = scrape_location(old_df['Link'].tolist())
    old_df['Location'] = locations
    print(f"Links: {len(old_df.Link.unique())} Locations: {len(locations)}")
    old_df.to_csv(str(min_price)+"-"+str(max_price)+typ+".csv", index=False)
    return old_df


shape="%28%28u%7Em%7BFwg%60Im%7Eb%40w%7Dq%40qfJuia%40kyHowr%40%7Bk%40az%5D%60mNstWdsm%40fm%60Ax%60_%40prqAh_%40n_d%40shJ%60bDokXflA%29%29&ordenado-por=precios-asc"
new_data=scrape_new_properties("alquiler-obranueva",2100,600,shape)
used_data=scrape_used_properties("alquiler-viviendas", 1800,500,65,160,shape)

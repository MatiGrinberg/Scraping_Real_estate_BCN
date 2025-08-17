from Dependencies import *

# NEW
def scrape_new_properties(shape, max_p=300000, min_p=60000):
    typ,f_t = "venta-obranueva",str(min_p)+"-"+str(max_p)
    base_url = (f"https://www.idealista.com/areas/{typ}/"f"con-precio-hasta_{max_p},precio-desde_{min_p},"f"1-dormitorio,2-dormitorios,3-dormitorios/"f"?shape=%28%28{shape}%29%29&ordenado-por=precios-asc")
    print("Base URL:", base_url)
    collected_links = []
    driver = initialize_driver()
    driver.get(base_url)
    try:
        pagination_ul = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.pagination ul")))
        li_elements = pagination_ul.find_elements(By.TAG_NAME, "li")
        last_page_num = int(li_elements[-2].text.strip()) if len(li_elements) >= 2 else 1
        h1_text = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'h1-container'))).text
        total_properties = int(re.search(r'\d+', h1_text.replace('.', '')).group())
    except TimeoutException:
        print("No pagination found or timeout. Assuming only 1 page.")
        last_page_num = 1
        total_properties=0
    finally:
        driver.quit()
    print(f"Total pages found: {last_page_num}")
    print(f"Total properties found: {total_properties}")
    for page_num in range(1, last_page_num + 1):
        if page_num == 1:
            page_url = base_url
        else:
            if "?" in base_url:
                prefix, query = base_url.split("?", 1)
                page_url = f"{prefix.rstrip('/')}/pagina-{page_num}?{query}"
            else:
                page_url = f"{base_url.rstrip('/')}/pagina-{page_num}"
        print(f"Scraping page {page_num}/{last_page_num}")
        scrape_page(page_url, collected_links)
    print(f"Scraping completed. Total collected links: {len(collected_links)}")
    df = scrape_all_links(collected_links)
    print(f"Final unique links: {len(df.Link.unique())}")
    df.to_csv(f"{f_t}{typ}.csv", index=False)
    return df

# OLD
def scrape_old_properties(shape,max_p=500000,min_p=200000,min_m=70,max_m=250,condition="obra-nueva,buen-estado,",t="",extra_filters=""):
    typ, f_t = "venta-viviendas",str(min_p)+"-"+str(max_p)
    filters = (f"con-precio-hasta_{max_p},"f"precio-desde_{min_p},"f"metros-cuadrados-mas-de_{min_m},"f"metros-cuadrados-menos-de_{max_m},"f"{extra_filters}""de-dos-dormitorios,""de-tres-dormitorios,""de-cuatro-cinco-habitaciones-o-mas,""balcon-y-terraza,"f"{condition}""sin-inquilinos/")
    base_url = (f"https://www.idealista.com/areas/{typ}/"f"{filters}"f"?shape=%28%28{shape}%29%29&ordenado-por=precios-asc")
    print("Base URL:", base_url)
    driver = initialize_driver()
    driver.get(base_url)
    try:
        pagination_ul = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pagination ul')))
        li_items = pagination_ul.find_elements(By.TAG_NAME, 'li')
        last_page_num = int(li_items[-2].text.strip()) if len(li_items) >= 2 else 1
        h1_text = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'h1-container'))).text
        total_properties = int(re.search(r'\d+', h1_text.replace('.', '')).group())
    except TimeoutException:
        print("No pagination found or timeout reached. Assuming only 1 page.")
        last_page_num = 1
        total_properties = 0
    finally:
        driver.quit()
    print(f"Total pages found: {last_page_num}")
    print(f"Total properties found: {total_properties}")
    data = []
    for page_num in range(1, last_page_num + 1):
        if page_num == 1:
            url = base_url
        else:
            if "?" in base_url:
                prefix, query = base_url.split("?", 1)
                url = f"{prefix.rstrip('/')}/pagina-{page_num}?{query}"
            else:
                url = f"{base_url.rstrip('/')}/pagina-{page_num}"
        print(f"Scraping page {page_num}/{last_page_num}: {url}\n")
        scrape_page_v2(data, url)
    df = pd.DataFrame(data)
    print(f"Scraping completed. Collected {len(df)} rows.")
    locations = scrape_location(df['Link'].tolist())
    df['Location'] = locations
    print(f"Links: {len(df.Link.unique())} | Locations: {len(locations)}")
    chal = extra_filters.strip(',/').replace(',', '_')
    df.to_csv(f"{f_t}{typ}{'_'+t if t else ''}.csv", index=False)
    return df

shape_new_dep="gif%7BFgpeI%7D_CujDibPk_o%40iaNupYa%60GqxUifHgaKc_%40idPteBgzGf%60J_bOb%7Cr%40%60yz%40hnHvgeAidThyY"
shape_old_dep="cq%7CzFsbvJ%7BgI%7BeMgzFhhC%7D%60Ija%40w_CucAmsFgvTgsF%7BlPtXaz%5DpyEoyCrlc%40xza%40btF%60og%40ofCtmI"
shape_old_chalet="kdr%7BF%7BkmJanKkkHafC%7DeMoyDeoQyeBo%60Gw_EwtLolEe%7EEyeCkyN%3FivIjmMufQn_CbiGpgk%40nwr%40hzExae%40geZzlP"
shape_old_reform="_%60xzF%7BrwJyaJia%40ohMsqG_tH%3FcsD%60%7B%40m_BuqGelA%7DaOyyGwiVyKyiKdsFcaV%7ClFpnBltg%40t~_%40%7BK%7Cuu%40"
new_df=scrape_new_properties(shape_new_dep,max_p=360000,min_p=150000)
old_df=scrape_old_properties(shape_old_dep,max_p=240000,min_p=160000,min_m=80,max_m=160,condition="obra-nueva,buen-estado,",t='depto') 
old_chal=scrape_old_properties(shape_old_chalet,max_p=300000,min_p=100000,min_m=80,max_m=200,extra_filters="chalets,",condition="obra-nueva,buen-estado,",t="chalets")
old_reform = scrape_old_properties(shape=shape_old_reform,max_p=200000,min_p=60000,min_m=80,max_m=160,condition="para-reformar,",t="reform")




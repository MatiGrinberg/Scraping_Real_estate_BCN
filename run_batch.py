import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.scrapers import run_scraper

def parse_zonas(filepath):
    zonas = []
    current_name = None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                current_name = line[1:].strip()
            elif line.startswith("http"):
                if current_name:
                    zonas.append({"name": current_name, "url": line})
                    current_name = None
    return zonas

def main():
    filepath = "zonas.txt"
    if not os.path.exists(filepath):
        print(f"No se encontró {filepath}")
        return

    zonas = parse_zonas(filepath)
    
    op = "Buy"
    prop = "New"
    min_price = 110000
    max_price = 320000
    min_area = 70
    max_area = 150

    urls_used = []

    print(f"Iniciando scrapeo en bucle para {len(zonas)} zonas.")
    
    # Auto-approve callback
    auto_approve = lambda url, pages, props: True

    for i, z in enumerate(zonas, 1):
        name = z["name"]
        shape_url = z["url"]
        
        # Guardamos la info de la zona y la URL en nuestra lista
        urls_used.append(f"{name}: {shape_url}")

        print("-" * 50)
        print(f"[{i}/{len(zonas)}] Ejecutando {name}...")
        
        subfolder_name = f"{min_price}-{max_price}_{op.lower()}_{prop.lower()}_{name}"
        
        try:
            run_scraper(
                operation=op,
                property_type=prop,
                min_price=min_price,
                max_price=max_price,
                min_area=min_area,
                max_area=max_area,
                shape_url=shape_url,
                output_filename=subfolder_name,
                log_callback=print,
                confirm_callback=auto_approve
            )
            print(f"Éxito con {name}")
        except Exception as e:
            print(f"Error en {name}: {e}")
            
        # Pequeña pausa entre zonas para ser amable con el servidor de Idealista
        print("Pausando 10 segundos antes de la siguiente zona...")
        time.sleep(10)

    # Al finalizar el bucle, guardamos las URLs originales
    out_file = os.path.join("output", "urls_del_bucle.txt")
    os.makedirs("output", exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("URLs Originales utilizadas en el Bucle de Búsqueda\\n")
        f.write("="*50 + "\\n")
        for u in urls_used:
            f.write(u + "\\n\\n")
            
    print(f"\\n¡Bucle finalizado! Las URLs se han guardado en {out_file}")

if __name__ == "__main__":
    main()

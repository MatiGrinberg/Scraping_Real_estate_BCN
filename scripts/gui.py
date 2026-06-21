import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
from scripts.scrapers import run_scraper

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Idealista Scraper BCN")
        self.root.geometry("600x750")
        self.root.configure(padx=20, pady=20)
        
        self.log_queue = queue.Queue()
        self.create_widgets()
        self.process_queue()
        
        # Enlazamos el evento de cierre de ventana para abortar todo inmediatamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Buscador de Propiedades", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Frame
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", expand=False)
        
        # Operation
        ttk.Label(frame, text="Operación:").grid(row=0, column=0, sticky="w", pady=5)
        self.op_var = tk.StringVar(value="Buy")
        self.op_combo = ttk.Combobox(frame, textvariable=self.op_var, values=["Rent", "Buy"], state="readonly")
        self.op_combo.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.op_combo.bind("<<ComboboxSelected>>", self.update_types)
        
        # Type
        ttk.Label(frame, text="Tipo de Propiedad:").grid(row=1, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="Used")
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, state="readonly")
        self.type_combo.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        
        self.update_types() # Initial population
        
        # Prices
        ttk.Label(frame, text="Precio Mínimo (€):").grid(row=2, column=0, sticky="w", pady=5)
        self.min_price = ttk.Entry(frame)
        self.min_price.insert(0, "100000")
        self.min_price.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Label(frame, text="Precio Máximo (€):").grid(row=3, column=0, sticky="w", pady=5)
        self.max_price = ttk.Entry(frame)
        self.max_price.insert(0, "300000")
        self.max_price.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
        
        # Areas
        ttk.Label(frame, text="Área Mínima (m²):").grid(row=4, column=0, sticky="w", pady=5)
        self.min_area = ttk.Entry(frame)
        self.min_area.insert(0, "60")
        self.min_area.grid(row=4, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Label(frame, text="Área Máxima (m²):").grid(row=5, column=0, sticky="w", pady=5)
        self.max_area = ttk.Entry(frame)
        self.max_area.insert(0, "150")
        self.max_area.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        
        # Shape / URL
        ttk.Label(frame, text="URL Base de Idealista\n(Opcional, para extraer zona):").grid(row=6, column=0, sticky="w", pady=15)
        self.url_entry = ttk.Entry(frame)
        self.url_entry.grid(row=6, column=1, sticky="ew", pady=15, padx=5)
        
        # Custom Title
        ttk.Label(frame, text="Título Personalizado\n(Se añadirá al CSV. Opcional):").grid(row=7, column=0, sticky="w", pady=5)
        self.title_entry = ttk.Entry(frame)
        self.title_entry.grid(row=7, column=1, sticky="ew", pady=5, padx=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Execute Button
        self.run_btn = ttk.Button(self.root, text="Iniciar Scraping", command=self.start_scraping)
        self.run_btn.pack(pady=10, fill="x")
        
        # Log Text Area
        ttk.Label(self.root, text="Progreso:").pack(anchor="w", pady=(10,0))
        self.log_text = tk.Text(self.root, height=12, state="disabled", wrap="word", bg="#f0f0f0")
        self.log_text.pack(fill="both", expand=True, pady=5)
        
    def log(self, message):
        self.log_queue.put(message)
        
    def process_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if msg == "___FINISHED___":
                    self.run_btn.config(state="normal")
                    messagebox.showinfo("Proceso Terminado", "El scraping ha finalizado.")
                elif msg.startswith("___ERROR___"):
                    self.run_btn.config(state="normal")
                    messagebox.showerror("Error", msg.replace("___ERROR___", ""))
                else:
                    self.log_text.config(state="normal")
                    self.log_text.insert("end", msg + "\n")
                    self.log_text.see("end")
                    self.log_text.config(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
        
    def update_types(self, event=None):
        op = self.op_var.get()
        if op == "Rent":
            self.type_combo['values'] = ["New", "Used"]
        else:
            self.type_combo['values'] = ["New", "Used", "Land", "Chalet", "Reform"]
        self.type_combo.current(1) # Default to Used
            
    def start_scraping(self):
        op = self.op_var.get()
        prop_type = self.type_var.get()
        min_p = self.min_price.get()
        max_p = self.max_price.get()
        min_a = self.min_area.get()
        max_a = self.max_area.get()
        url = self.url_entry.get()
        custom_title = self.title_entry.get().strip()
        
        # Basic validation
        if not all([min_p, max_p, min_a, max_a]):
            messagebox.showerror("Error", "Por favor completa todos los campos numéricos.")
            return
            
        base_filename = f"{min_p}-{max_p}_{op.lower()}_{prop_type.lower()}"
        filename = f"{base_filename}_{custom_title}" if custom_title else base_filename
        
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        
        self.log("Scrapeando... Por favor, no cierres la ventana. Chrome se abrirá automáticamente.")
        self.run_btn.config(state="disabled")
        
        # Run in thread to not freeze GUI, set as daemon to kill it if app closes
        thread = threading.Thread(target=self.execute_scraper, args=(op, prop_type, min_p, max_p, min_a, max_a, url, filename))
        thread.daemon = True
        thread.start()
        
    def execute_scraper(self, op, prop_type, min_p, max_p, min_a, max_a, url, filename):
        try:
            result = run_scraper(op, prop_type, min_p, max_p, min_a, max_a, url, filename, self.log, self.confirm_scrape)
            self.log(result)
            self.log_queue.put("___FINISHED___")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.log_queue.put(f"___ERROR___Ocurrió un error: {str(e)}")

    def confirm_scrape(self, base_url, last_page_num, total_props="Desconocido"):
        self.root.update_idletasks()
        
        comp_str = ""
        try:
            if total_props != "Desconocido":
                tot_int = int(total_props.replace(".", ""))
                if tot_int > 180:
                    comp_str = f" (> 180, Idealista limitará a 180)"
                else:
                    comp_str = f" (<= 180, todo dentro del límite)"
        except:
            pass
            
        ans = messagebox.askyesno(
            "Confirmar Scraping",
            f"Se han encontrado {last_page_num} páginas para scrapear.\n"
            f"El sitio reporta {total_props} propiedades{comp_str}.\n\n"
            f"URL de búsqueda:\n{base_url}\n\n"
            f"¿Deseas proceder con la extracción de datos?"
        )
        return ans

    def on_close(self):
        # Matamos todo el proceso de Python y liberamos la terminal al cerrar la GUI
        import os
        os._exit(0)

def launch_gui():
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()

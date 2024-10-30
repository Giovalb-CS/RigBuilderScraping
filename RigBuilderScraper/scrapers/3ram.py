# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part,Query
import csv
import os

# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_ram(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'memory':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati, immagini

# Funzione di ricerca "LIKE" nel nome della RAM
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'

# Funzione per salvare le informazioni delle RAM nel file CSV
def salva_ram_csv(file_path, ram_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=ram_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(ram_data)

# Funzione principale per raccogliere le informazioni delle RAM
def info_loop_ram(p_list, images, existing_names):
    print("Starting data collection...")
    ram_data = []

    for part in p_list:
        specs = part.advanced_specs()
        name = part.name()

        # Se il nome è nullo o già esistente, salta l'iterazione
        if not name or name.strip() in existing_names:
            continue

        # Estrarre il numero di moduli dal campo 'Modules'
        modules_info = specs.get('Modules', '').strip()
        tdp = 1  # Default per un singolo modulo
        if 'x' in modules_info:
            try:
                tdp = int(modules_info.split('x')[0].strip())
            except ValueError:
                tdp = 1  # Se non si riesce a interpretare il numero, si usa 1 come default

        # Estrarre il tipo di memoria (DDR3, DDR4, DDR5) dal campo 'Form Factor'
        form_factor_info = specs.get('Form Factor', '').strip()
        ram_type = "N/A"  # Default value
        if '(' in form_factor_info and ')' in form_factor_info:
            ram_type = form_factor_info.split('(')[-1].replace(')', '').strip()

        # Estrarre solo la parte numerica della velocità di memoria
        speed_info = specs.get('Speed', '').strip()
        speed = ''.join(filter(str.isdigit, speed_info)) if speed_info else "N/A"

        # Costruzione del dizionario di informazioni per la RAM
        ram_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else "N/A",
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'tdp': tdp,
            'type': ram_type,
            'speed': speed
        }
        print(f"Collected {len(ram_data)} RAM entries.")
        ram_data.append(ram_entry)

    return ram_data

# Caricamento degli URL e delle immagini dal file CSV
dati_ram, images = carica_dati_ram('../src/data/Memory.csv')

# Creazione della lista di oggetti Part
ram_parts_list = [Part(url) for url in dati_ram]

# Percorso del file di esportazione
export_path = '../export/RAMs.csv'

# Carica i nomi esistenti dal file di esportazione
existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

# Raccoglie e salva i dati delle RAM nel CSV
ram_data = info_loop_ram(ram_parts_list, images, existing_names)
if ram_data:
    salva_ram_csv(export_path, ram_data)
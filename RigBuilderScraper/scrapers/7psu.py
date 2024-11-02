# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part,Query
import csv
import os

# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_psu(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'psu':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati, immagini

# Funzione di ricerca "LIKE" nel nome del PSU
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'

# Funzione per salvare le informazioni dei PSU nel file CSV
def salva_psu_csv(file_path, psu_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=psu_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(psu_data)

# Funzione principale per raccogliere le informazioni dei PSU
def info_loop_psu(p_list, images, existing_names):
    psu_data = []

    for part in p_list:
        specs = part.advanced_specs()
        name = part.name()

        if not name or name.strip() in existing_names:
            continue  # Skip se nome è nullo o già presente

        # Funzione per formattare il tipo di alimentatore
        def format_modular(modular_str):
            if "Full" in modular_str:
                return "Fully Modular"
            elif "Semi" in modular_str:
                return "Semi Modular"
            elif "No" in modular_str:
                return "Non Modular"
            return "N/A"

        # Crea la voce per il PSU
        psu_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else "N/A",
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'type': format_modular(specs.get('Modular', 'N/A')),
            'efficiency': specs.get('Efficiency Rating', 'N/A').strip(),
            'wattage': specs.get('Wattage', 'N/A').replace(" W", "").strip(),
            'length': specs.get('Length', 'N/A').replace(" mm", "").strip(),
        }

        # Aggiungi PSU alla lista da salvare
        psu_data.append(psu_entry)

    return psu_data


# Caricamento degli URL e delle immagini dal file CSV
dati_psu, images = carica_dati_psu('../src/data/PSU.csv')

# Creazione della lista di oggetti Part
psu_parts_list = [Part(url) for url in dati_psu]

# Percorso del file di esportazione
export_path = '../export/PSUs.csv'

# Carica i nomi esistenti dal file di esportazione
existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

# Raccoglie e salva i dati dei PSU nel CSV
psu_data = info_loop_psu(psu_parts_list, images, existing_names)
if psu_data:
    salva_psu_csv(export_path, psu_data)

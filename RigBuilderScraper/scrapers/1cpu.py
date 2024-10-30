# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part, Query
import csv
import os


# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_cpu(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'cpu':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati, immagini


# Funzione di ricerca "LIKE" nel nome della CPU
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'


# Funzione per determinare la memoria supportata
def determina_memoria_supportata(socket):
    return "DDR5" if socket in ["LGA 1700", "LGA 1851", "AM5"] else "DDR4"


# Funzione per salvare le informazioni delle CPU nel file CSV
def salva_cpu_csv(file_path, cpu_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=cpu_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(cpu_data)


# Funzione principale per raccogliere le informazioni delle CPU
def info_loop_cpu(p_list, images, existing_names):
    cpu_data = []

    for part in p_list:
        specs = part.advanced_specs()
        name = part.name()

        if not name or name.strip() in existing_names:
            continue  # Skip se nome è nullo o già presente

        cpu_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else "N/A",
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'tdp': specs.get('TDP', 'N/A').strip().replace(" W", ""),
            'socket': specs.get('Socket', 'N/A').strip().replace("LGA", "LGA "),
            'supported_memory': determina_memoria_supportata(specs.get('Socket', '').strip()),
            'core_count': specs.get('Core Count', 'N/A').strip(),
            'thread_count': specs.get('Thread Count', 'N/A').strip(),
            'performance_core_clock': specs.get('Performance Core Clock', 'N/A').strip().replace(" GHz", ""),
            'boost_clock': specs.get('Performance Core Boost Clock', 'N/A').strip().replace(" GHz", ""),
            'cache': specs.get('L3 Cache', 'N/A').strip().replace(" MB", ""),
            'lithography': specs.get('Lithography', 'N/A').strip().replace(" nm", ""),
            'generation': f"{specs.get('Manufacturer', 'N/A').strip()} {specs.get('Microarchitecture', 'N/A').strip()}"
        }

        # Aggiungi CPU alla lista da salvare
        cpu_data.append(cpu_entry)

    return cpu_data


# Caricamento degli URL e delle immagini dal file CSV
dati_cpu, images = carica_dati_cpu('../src/data/CPU.csv')

# Creazione della lista di oggetti Part
cpu_parts_list = [Part(url) for url in dati_cpu]

# Percorso del file di esportazione
export_path = '../export/CPUs.csv'

# Carica i nomi esistenti dal file di esportazione
existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

# Raccoglie e salva i dati delle CPU nel CSV
cpu_data = info_loop_cpu(cpu_parts_list, images, existing_names)
if cpu_data:
    salva_cpu_csv(export_path, cpu_data)

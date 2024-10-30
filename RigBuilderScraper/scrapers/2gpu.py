# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part,Query

import csv
import os

# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_gpu(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'gpu':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati , immagini

# Funzione di ricerca "LIKE" nel nome della GPU
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'

# Funzione per salvare le informazioni delle GPU nel file CSV
def salva_gpu_csv(file_path, gpu_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=gpu_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(gpu_data)

# Funzione principale per raccogliere le informazioni delle CPU
def info_loop_gpu(p_list, images, existing_names):
    gpu_data = []

    for part in p_list:
        specs = part.advanced_specs()
        name = part.name()

        if not name or name.strip() in existing_names:
            continue

        gpu_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else 'N/A',
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'tdp': specs.get('TDP', 'N/A').strip().replace(" W", ""),
            'memory': f"{specs.get('Memory', 'N/A').strip().replace(" ", "")} {specs.get('Memory Type', 'N/A').strip()}",
            'effective memory clock': specs.get('Effective Memory Clock', 'N/A').strip().replace(" MHz", ""),
            'core clock': specs.get('Core Clock', 'N/A').strip().replace(" MHz", ""),
            'boost clock': specs.get('Boost Clock', 'N/A').strip().replace(" MHz", ""),
            'length': specs.get('Length', 'N/A').strip().replace(" mm", ""),
            'case expansion slot width': specs.get('Case Expansion Slot Width', 'N/A').strip(),
            'external power': specs.get('External Power', 'N/A').strip().replace(" PCIe", "x")
        }

        gpu_data.append(gpu_entry)

    return gpu_data

dati_gpu, images = carica_dati_gpu('../src/data/GPU.csv')

gpu_parts_list = [Part(url) for url in dati_gpu]

export_path = '../export/GPUs.csv'

existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

gpu_data = info_loop_gpu(gpu_parts_list, images, existing_names)
if gpu_data:
    salva_gpu_csv(export_path, gpu_data)
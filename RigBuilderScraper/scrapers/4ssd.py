# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part,Query
import csv
import os

# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_ssd(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'storage':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati, immagini

# Funzione di ricerca "LIKE" nel nome del SSD
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'

# Funzione per salvare le informazioni degli SSD nel file CSV
def salva_ssd_csv(file_path, ssd_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=ssd_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(ssd_data)

# Funzione principale per raccogliere le informazioni degli SSD
def info_loop_ssd(p_list, images, existing_names):
    ssd_data = []

    for part in p_list:
        specs = part.advanced_specs()
        name = part.name()

        # Skip se il nome è nullo o già presente nella lista esistente
        if not name or name.strip() in existing_names:
            continue

            # Estrai e formatta i campi richiesti
        interface = specs.get('Interface', 'N/A')
        capacity = specs.get('Capacity', 'N/A')

        # Estrai PCIe generazione e numero corsie
        if 'PCIe' in interface:
            pcie_gen_raw = interface.split('PCIe')[1].strip().split()[0]  # Es. '3.0'
            pcie_gen = pcie_gen_raw.split('.')[0]  # Prendi solo la parte intera prima del punto
            lanes = interface.split('X')[1].strip() if 'X' in interface else 'N/A'  # Es. '4'
            pcie_gen = f"{pcie_gen}x{lanes}"
        else:
            pcie_gen = "N/A"

        # Estrai le velocità di lettura e scrittura sequenziali
        speed_read = specs.get('Sequential Read Throughput (Disk 50% Full)', 'N/A').split()[0]
        speed_write = specs.get('Sequential Write Throughput (Disk 50% Full)', 'N/A').split()[0]

        # Popola la voce SSD con i campi estratti
        ssd_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else "N/A",
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'tdp': 10,
            'pcie_gen': pcie_gen,
            'capacity': capacity.strip(),
            'speed_read': speed_read,
            'speed_write': speed_write
        }

        # Aggiungi SSD alla lista dei dati da salvare
        ssd_data.append(ssd_entry)

    return ssd_data

# Caricamento degli URL e delle immagini dal file CSV
dati_ssd, images = carica_dati_ssd('../src/data/Storage.csv')

# Creazione della lista di oggetti Part
ssd_parts_list = [Part(url) for url in dati_ssd]

# Percorso del file di esportazione
export_path = '../export/SSDs.csv'

# Carica i nomi esistenti dal file di esportazione
existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

# Raccoglie e salva i dati degli SSD nel CSV
ssd_data = info_loop_ssd(ssd_parts_list, images, existing_names)
if ssd_data:
    salva_ssd_csv(export_path, ssd_data)

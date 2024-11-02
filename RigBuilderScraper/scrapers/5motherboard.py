# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part, Query
import csv
import os

# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_mobo(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'motherboard':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati, immagini

# Funzione di ricerca "LIKE" nel nome della MOBO
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'

# Funzione per salvare le informazioni delle MOBO nel file CSV
def salva_mobo_csv(file_path, mobo_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=mobo_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(mobo_data)

# id, name, rating, price, shop_URL, image_URL, TDP, socket, chipset, RAM_type, RAM_max_speed, RAM_slot, RAM_max, PCIe_x16_slot, PCIe_x1_slot, M2_slot, SATA_slot, LAN, WIFI, form_factor
def info_loop_mobo(p_list, images, existing_names):
    mobo_data = []

    for part in p_list:
        specs = part.advanced_specs()
        name = part.name()

        if not name or name.strip() in existing_names:
            continue  # Skip se nome è nullo o già presente

        # Funzione per ottenere la massima velocità di memoria
        def get_max_speed(memory_speed):
            speeds = [int(s) for s in memory_speed.replace("DDR4", "").replace("DDR5", "").split("DDR") if s.isdigit()]
            return max(speeds) if speeds else 0  # Modificato per restituire 0 invece di "N/A"

        # Calcola il numero di slot M.2
        def count_m2_slots(m2_slots_str):
            return m2_slots_str.count('M-key') if m2_slots_str else 0

        # Formatta la connessione LAN
        def format_lan(lan_str):
            if not lan_str or 'N/A' in lan_str:
                return "No"
            # Rimuove le informazioni tra parentesi e crea la stringa desiderata
            lan_components = []
            for item in lan_str.split(","):
                clean_item = item.split("(")[0].strip()  # Rimuove tutto ciò che è tra parentesi
                if "Gb/s" in clean_item:  # Assicurati che contenga "Gb/s"
                    clean_item = clean_item.replace(" ", "")  # Rimuove spazi
                    lan_components.append(clean_item)
            return " + ".join(lan_components)

        # Estrarre Wi-Fi o restituire "No"
        def format_wifi(wifi_str):
            return wifi_str.strip() if wifi_str and wifi_str.lower() != 'none' else "No"

        # Formatta il valore del form factor
        def format_form_factor(form_factor):
            return form_factor.replace(" ", "-")

        # Inserire i dati nella voce della scheda madre
        mobo_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else "N/A",
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'tdp': 80,  # valore fisso per TDP
            'socket': specs.get('Socket / CPU', 'N/A').strip(),
            'chipset': specs.get('Chipset', 'N/A').strip(),
            'ram_type': specs.get('Memory Type', 'N/A').strip(),
            'ram_max_speed': get_max_speed(specs.get('Memory Speed', '')),
            'ram_slot': specs.get('Memory Slots', 'N/A').strip(),
            'ram_max': specs.get('Memory Max', 'N/A').strip().replace(" GB", ""),  # Solo numeri, senza "GB"
            'pcie_x16_slot': specs.get('PCIe x16 Slots', 'N/A').strip(),
            'pcie_x1_slot': specs.get('PCIe x1 Slots', 'N/A').strip(),
            'm2_slot': count_m2_slots(specs.get('M.2 Slots', '')),
            'sata_slot': specs.get('SATA 6.0 Gb/s', 'N/A').strip(),
            'lan': format_lan(specs.get('Onboard Ethernet', 'N/A')),
            'wifi': format_wifi(specs.get('Wireless Networking', 'None')),
            'form_factor': format_form_factor(specs.get('Form Factor', 'N/A').strip()),
        }

        # Aggiungi la voce alla lista di schede madri
        mobo_data.append(mobo_entry)

    return mobo_data

# Caricamento degli URL e delle immagini dal file CSV
dati_mobo, images = carica_dati_mobo('../src/data/Motherboard.csv')

# Creazione della lista di oggetti Part
mobo_parts_list = [Part(url) for url in dati_mobo]

# Percorso del file di esportazione
export_path = '../export/MOBOs.csv'

# Carica i nomi esistenti dal file di esportazione
existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

# Raccoglie e salva i dati delle MOBO nel CSV
mobo_data = info_loop_mobo(mobo_parts_list, images, existing_names)
if mobo_data:
    salva_mobo_csv(export_path, mobo_data)
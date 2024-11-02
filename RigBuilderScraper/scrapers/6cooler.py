# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part,Query
import csv
import os

# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_cooler(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'cooler':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati, immagini

# Funzione di ricerca "LIKE" nel nome del Cooler
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'

# Funzione per salvare le informazioni dei cooler nel file CSV
def salva_cooler_csv(file_path, cooler_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=cooler_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(cooler_data)

# Funzione principale per raccogliere le informazioni dei Cooler
# Water: {'Manufacturer': 'Cooler Master', 'Model': 'MASTERLIQUID ML240L RGB V2', 'Part #': 'MLW-D24M-A18PC-R2', 'Fan RPM': '650 - 1800 RPM', 'Noise Level': '6 - 27 dB', 'Color': 'Black', 'CPU Socket': 'AM2AM2+AM3AM3+AM4AM5FM1FM2FM2+LGA1150LGA1151LGA1155LGA1156LGA1200LGA1366LGA1700LGA1851LGA2011LGA2011-3LGA2066', 'Water Cooled': 'Yes - 240 mm', 'Fanless': 'No'}
# Air: {'Manufacturer': 'Scythe', 'Model': 'Big Shuriken 3', 'Part #': 'SCBSK-3000', 'Fan RPM': '300 - 1800 RPM', 'Noise Level': '2.7 - 30.4 dB', 'Color': 'Black / Silver', 'Height': '69 mm', 'CPU Socket': 'AM2AM2+AM3AM3+AM4AM5FM1FM2FM2+LGA775LGA1150LGA1151LGA1155LGA1156LGA1200LGA1366LGA1700LGA1851LGA2011LGA2011-3LGA2066', 'Water Cooled': 'No', 'Fanless': 'No'}
def info_loop_cooler(p_list, images, existing_names):
    cooler_data = []

    for part in p_list:
        specs = part.advanced_specs()
        name = part.name()

        if not name or name.strip() in existing_names:
            continue  # Skip se nome è nullo o già presente

        # Estrae l'RPM massimo
        def get_max_rpm(rpm_str):
            if rpm_str:
                return max(int(r) for r in rpm_str.replace(" RPM", "").split(" - ") if r.isdigit())
            return "N/A"

        def get_max_noise(noise_str):
            if noise_str:
                # Rimuovi l'unità di misura e prova a estrarre i numeri
                numbers = [int(n) for n in noise_str.replace(" dB", "").split(" - ") if n.isdigit()]
                return max(numbers) if numbers else "N/A"  # Se non ci sono numeri, restituisci "N/A"
            return "N/A"

        # Estrae la dimensione del radiatore
        def get_radiator_size(water_cooled_str):
            if "Yes" in water_cooled_str:
                return int(water_cooled_str.split('-')[1].strip().replace(" mm", ""))
            return 0

        # Imposta l'altezza del cooler
        def get_cooler_height(water_cooled_str, height_str):
            if "Yes" in water_cooled_str:
                return 0
            elif height_str:
                return int(height_str.replace(" mm", ""))
            return "N/A"

        def format_socket(socket_str):
            import re
            # Trova tutte le socket AMD e LGA
            amd_sockets = re.findall(r'(AM\d+(\+)?|FM\d+(\+)?|sTR[4,5]|\sTRX[4]|TR[4]|sWRX8)', socket_str)
            lga_sockets = re.findall(r'(LGA\d+(-\d+)?)', socket_str)

            # Combina e formatta le socket
            formatted_sockets = []

            if amd_sockets:
                formatted_sockets.extend([s[0] for s in amd_sockets])

            if lga_sockets:
                formatted_sockets.extend([s[0] for s in lga_sockets])

            # Unisce le socket con "/" e formatta le LGA
            formatted_sockets = [
                socket if not socket.startswith("LGA") else socket.replace("LGA", "LGA ")
                for socket in formatted_sockets
            ]

            return '/'.join(formatted_sockets)

        # Crea la voce per il cooler
        cooler_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else "N/A",
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'tdp': 25 if "Yes" in specs.get('Water Cooled', 'No') else 15,  # Imposta il TDP
            'socket': format_socket(specs.get('CPU Socket', 'N/A')),
            'rpm': get_max_rpm(specs.get('Fan RPM', 'N/A')),
            'noise_level': get_max_noise(specs.get('Noise Level', 'N/A')),
            'radiator_size': get_radiator_size(specs.get('Water Cooled', 'No')),
            'cooler_height': get_cooler_height(specs.get('Water Cooled', 'No'), specs.get('Height', '0 mm')),
        }

        # Aggiungi Cooler alla lista da salvare
        cooler_data.append(cooler_entry)

    return cooler_data

# Caricamento degli URL e delle immagini dal file CSV
dati_cooler, images = carica_dati_cooler('../src/data/Cooler.csv')

# Creazione della lista di oggetti Part
cooler_parts_list = [Part(url) for url in dati_cooler]

# Percorso del file di esportazione
export_path = '../export/Coolers.csv'

# Carica i nomi esistenti dal file di esportazione
existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

# Raccoglie e salva i dati dei Cooler nel CSV
cooler_data = info_loop_cooler(cooler_parts_list, images, existing_names)
if cooler_data:
    salva_cooler_csv(export_path, cooler_data)
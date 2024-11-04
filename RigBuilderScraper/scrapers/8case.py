# https://github.com/Jeet-Chugh/pcpartscraper?tab=readme-ov-file
from pcpartscraper.scraper import Part,Query
import csv
import os

# Funzione per caricare le immagini e gli URL dal CSV
def carica_dati_case(percorso_csv):
    dati = []
    immagini = {}
    with open(percorso_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['partType'].strip().lower() == 'case':
                immagini[row['name'].strip()] = row['image'].strip()
                url_relativo = row['url'].replace("https://pcpartpicker.com", "").strip()
                dati.append(url_relativo)
    return dati, immagini

# Funzione di ricerca "LIKE" nel nome del Case
def trova_immagine_simile(name, image):
    keywords = name.split()
    for nome, link_immagine in image.items():
        if all(keyword.lower() in nome.lower() for keyword in keywords):
            return link_immagine
    return 'null'

# Funzione per salvare le informazioni dei Case nel file CSV
def salva_case_csv(file_path, case_data):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=case_data[0].keys())

        # Scrivi l'intestazione se il file non esiste
        if not file_exists:
            writer.writeheader()

        # Scrivi le righe per ciascun dato
        writer.writerows(case_data)

# Funzione principale per raccogliere le informazioni dei Case
# {'Manufacturer': 'NZXT', 'Part #': 'CC-H51FB-01', 'Type': 'ATX Mid Tower', 'Color': 'Black', 'Power Supply': 'None', 'Side Panel': 'Tempered Glass', 'Power Supply Shroud': 'Yes', 'Front Panel USB': 'USB 3.2 Gen 2 Type-CUSB 3.2 Gen 1 Type-A', 'Motherboard Form Factor': 'ATXEATXMicro ATXMini ITX', 'Maximum Video Card Length': '365 mm / 14.37"', 'Drive Bays': '1 x Internal 3.5"1 x Internal 2.5"', 'Expansion Slots': '7 x Full-Height', 'Dimensions': '446 mm x 227 mm x 464 mm17.559" x 8.937" x 18.268"', 'Volume': '46.976 L1.659 ft³'}
# {'Manufacturer': 'Deepcool', 'Part #': 'R-CC560-BKGAA4-G-1CC560', 'Type': 'ATX Mid Tower', 'Color': 'Black', 'Power Supply': 'None', 'Side Panel': 'Tempered Glass', 'Power Supply Shroud': 'Yes', 'Front Panel USB': 'USB 3.2 Gen 1 Type-AUSB 2.0 Type-A', 'Motherboard Form Factor': 'ATXMicro ATXMini ITX', 'Maximum Video Card Length': '370 mm / 14.567"', 'Drive Bays': '2 x Internal 3.5"2 x Internal 2.5"', 'Expansion Slots': '7 x Full-Height', 'Dimensions': '416 mm x 210 mm x 477 mm16.378" x 8.268" x 18.78"', 'Volume': '41.671 L1.472 ft³'}
def info_loop_case(p_list, images, existing_names):
    case_data = []

    for part in p_list:
        specs = part.advanced_specs()
        print(specs)
        name = part.name()

        if not name or name.strip() in existing_names:
            continue  # Skip se nome è nullo o già presente

        # Estrai solo il numero per la lunghezza massima della GPU
        def get_gpu_length(length_str):
            return length_str.split(" ")[0] if length_str else "0"

        # Formatta il form factor della scheda madre con "/" e sostituisce spazi con "-"
        def format_form_factor(form_factor_str):
            form_factors = form_factor_str.split("\n")  # Separa su nuove righe o altri delimitatori
            return "/".join(item.replace(" ", "-") for item in form_factors) if form_factors else "N/A"

        # Estrai solo il numero dagli slot di espansione
        def get_pcie_slots(expansion_str):
            return expansion_str.split(" x")[0] if expansion_str else "0"

        # Crea la voce per il case
        case_entry = {
            'name': name.strip(),
            'rating': part.rating() if part.rating() is not None else "N/A",
            'price': part.price() if part.price() else "N/A",
            'amazon_link': part.amazon_link().strip() if part.amazon_link() else "N/A",
            'image_link': trova_immagine_simile(name.strip(), images),
            'max_cooler_height': 0,  # valore fisso come specificato
            'radiator_size': 0,  # valore fisso come specificato
            'gpu_length': get_gpu_length(specs.get('Maximum Video Card Length', '')),
            'form_factor': format_form_factor(specs.get('Motherboard Form Factor', '')),
            'psu_length': 0,  # valore fisso come specificato
            'pcie_slots': get_pcie_slots(specs.get('Expansion Slots', ''))
        }

        # Aggiungi Case alla lista da salvare
        case_data.append(case_entry)

    return case_data


# Caricamento degli URL e delle immagini dal file CSV
dati_case, images = carica_dati_case('../src/data/Case.csv')

# Creazione della lista di oggetti Part
case_parts_list = [Part(url) for url in dati_case]

# Percorso del file di esportazione
export_path = '../export/Cases_todelete.csv'

# Carica i nomi esistenti dal file di esportazione
existing_names = set()
if os.path.exists(export_path):
    with open(export_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_names = {row['name'].strip() for row in reader}

# Raccoglie e salva i dati dei Case nel CSV
case_data = info_loop_case(case_parts_list, images, existing_names)
if case_data:
    salva_case_csv(export_path, case_data)

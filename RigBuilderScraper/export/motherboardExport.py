import pandas as pd

# Carica il CSV originale
df = pd.read_csv('../export/MOBOs.csv')

# Mappa dei nomi delle colonne nel CSV ai nomi della tabella MySQL
column_mapping = {
    'name': 'name',
    'rating': 'rating',
    'price': 'price',
    'amazon_link': 'shop_url',
    'image_link': 'image_url',
    'tdp': 'tdp',
    'socket': 'socket',
    'chipset': 'chipset',
    'ram_type': 'ram_type',
    'ram_max_speed': 'ram_max_speed',
    'ram_slot': 'ram_slot',
    'ram_max': 'ram_max',
    'pcie_x16_slot': 'pcie_x16_slot',
    'pcie_x1_slot': 'pcie_x1_slot',
    'm2_slot': 'm2_slot',
    'sata_slot': 'sata_slot',
    'lan': 'lan',
    'wifi': 'wifi',
    'form_factor': 'form_factor'
}

# Rinomina le colonne
df.rename(columns=column_mapping, inplace=True)

# Rimuovi spazi bianchi dalle stringhe
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Sostituisci 'N/A', spazi vuoti e valori nulli nei campi numerici con 0
# Converti le colonne numeriche in float prima della sostituzione
numeric_columns = ['rating', 'price', 'tdp', 'ram_max_speed', 'ram_slot', 'ram_max', 'pcie_x16_slot', 'pcie_x1_slot', 'm2_slot', 'sata_slot']

# Sostituisci 'N/A', spazi vuoti e valori nulli
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col].replace({'N/A': 0, '': 0, None: 0, ' ': 0}), errors='coerce').fillna(0)

# Sostituisci 'N/A' e valori nulli nei campi di testo con 'unknown'
df.fillna({'shop_url': 'unknown', 'image_url': 'unknown', 'socket': 'unknown', 'chipset': 'unknown', 'ram_type': 'unknown', 'lan': 'unknown', 'wifi': 'unknown', 'form_factor': 'unknown'}, inplace=True)

# Salva il nuovo CSV
df.to_csv('../export/Motherboards_for_import.csv', index=False)

import pandas as pd

# Carica il CSV originale
df = pd.read_csv('../export/Coolers.csv')

# Mappa dei nomi delle colonne nel CSV ai nomi della tabella MySQL
# ,,,
column_mapping = {
    'name': 'name',
    'rating': 'rating',
    'price': 'price',
    'amazon_link': 'shop_url',
    'image_link': 'image_url',
    'tdp': 'tdp',
    'socket': 'socket',
    'rpm': 'rpm',
    'noise_level': 'noise_level',
    'radiator_size': 'radiator_size',
    'cooler_height': 'cooler_height'
}

# Rinomina le colonne
df.rename(columns=column_mapping, inplace=True)

# Rimuovi spazi bianchi dalle stringhe
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Sostituisci 'N/A', spazi vuoti e valori nulli nei campi numerici con 0
# Converti le colonne numeriche in float prima della sostituzione
numeric_columns = ['rating', 'price', 'tdp', 'rpm', 'noise_level', 'radiator_size', 'cooler_height']

# Sostituisci 'N/A', spazi vuoti e valori nulli
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col].replace({'N/A': 0, '': 0, None: 0, ' ': 0}), errors='coerce').fillna(0)

# Sostituisci 'N/A' e valori nulli nei campi di testo con 'unknown'
df.fillna({'shop_url': 'unknown', 'image_url': 'unknown', 'socket': 'unknown'}, inplace=True)

# Salva il nuovo CSV
df.to_csv('../export/Coolers_for_import.csv', index=False)

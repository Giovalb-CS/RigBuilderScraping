import pandas as pd

# Carica il CSV originale
df = pd.read_csv('../export/GPUs.csv')

# Stampa i nomi delle colonne per il debug
print("Colonne nel CSV originale:", df.columns)

# Mappa dei nomi delle colonne nel CSV ai nomi della tabella MySQL
column_mapping = {
    'name': 'name',
    'rating': 'rating',
    'price': 'price',
    'amazon_link': 'shop_url',
    'image_link': 'image_url',
    'tdp': 'tdp',
    'memory': 'memory',
    'effective memory clock': 'memory_clock',
    'core clock': 'core_clock',
    'boost clock': 'boost_clock',
    'length': 'lenght',
    'case expansion slot width': 'slot_width',
    'external power': 'power_cable'
}

# Rinomina le colonne
df.rename(columns=column_mapping, inplace=True)

# Rimuovi spazi bianchi dalle stringhe
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Sostituisci 'N/A', spazi vuoti e valori nulli nei campi numerici con 0
# Converti le colonne numeriche in float prima della sostituzione
numeric_columns = ['rating', 'price', 'tdp', 'memory_clock', 'core_clock', 'boost_clock', 'lenght', 'slot_width']

# Sostituisci 'N/A', spazi vuoti e valori nulli
for col in numeric_columns:
    if col in df.columns:  # Controlla se la colonna esiste
        df[col] = pd.to_numeric(df[col].replace({'N/A': 0, '': 0, None: 0, ' ': 0}), errors='coerce').fillna(0)
    else:
        print(f"Warning: '{col}' not found in DataFrame columns.")

# Sostituisci 'N/A' e valori nulli nei campi di testo con 'unknown'
df.fillna({'shop_url': 'unknown', 'image_url': 'unknown', 'memory': 'unknown', 'power_cable': 'unknown'}, inplace=True)

# Salva il nuovo CSV
df.to_csv('../export/GPUs_for_import.csv', index=False)

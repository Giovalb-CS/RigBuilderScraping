import pandas as pd

# Carica il CSV originale
df = pd.read_csv('../export/CPUs.csv')

# Mappa dei nomi delle colonne nel CSV ai nomi della tabella MySQL
column_mapping = {
    'name': 'name',
    'rating': 'rating',
    'price': 'price',
    'amazon_link': 'shop_url',
    'image_link': 'image_url',
    'tdp': 'tdp',
    'socket': 'socket',
    'supported_memory': 'ram_type',
    'core_count': 'core',
    'thread_count': 'thread',
    'performance_core_clock': 'clock_base',
    'boost_clock': 'clock_boost',
    'cache': 'cache',
    'lithography': 'scale',
    'generation': 'generation'
}

# Rinomina le colonne
df.rename(columns=column_mapping, inplace=True)

# Rimuovi spazi bianchi dalle stringhe
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Sostituisci 'N/A', spazi vuoti e valori nulli nei campi numerici con 0
# Converti le colonne numeriche in float prima della sostituzione
numeric_columns = ['rating', 'price', 'tdp', 'core', 'thread', 'clock_base', 'clock_boost', 'cache', 'scale']

# Sostituisci 'N/A', spazi vuoti e valori nulli
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col].replace({'N/A': 0, '': 0, None: 0, ' ': 0}), errors='coerce').fillna(0)

# Sostituisci 'N/A' e valori nulli nei campi di testo con 'unknown'
df.fillna({'shop_url': 'unknown', 'image_url': 'unknown', 'socket': 'unknown', 'ram_type': 'unknown', 'generation': 'unknown'}, inplace=True)

# Salva il nuovo CSV
df.to_csv('../export/CPUs_for_import.csv', index=False)

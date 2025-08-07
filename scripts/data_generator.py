import pandas as pd
import numpy as np
from faker import Faker
import os
from datetime import datetime, timedelta

# Inicializar Faker para datos ficticios
fake = Faker()

# --- Parámetros de Generación ---
NUM_PRODUCTS = 10000
NUM_SALES = 1000000
START_DATE = datetime(2018, 1, 1)
END_DATE = datetime.now()
OUTPUT_DIR = 'data'

# --- 1. Generar Tabla de Productos (OITM) ---
def generate_products(n):
    print(f"Generando {n} productos...")
    items = []
    for i in range(n):
        items.append({
            'ItemCode': f'SKU-{i:05}',  # Código del producto
            'ItemName': fake.word().capitalize() + ' ' + fake.word() + ' Part',
            'Brand': fake.company(),
            'Category': fake.bs().split(' ')[0], # Categoría del producto
            'CreateDate': fake.date_time_between(start_date='-10y', end_date='-6y')
        })
    df_oitm = pd.DataFrame(items)
    print("Tabla de productos (OITM) generada.")
    return df_oitm

# --- 2. Generar Tabla de Ventas (INV1) ---
def generate_sales(n, products_df):
    print(f"Generando {n} registros de ventas...")
    sales = []
    product_codes = products_df['ItemCode'].tolist()
    date_range = (END_DATE - START_DATE).days

    for _ in range(n):
        doc_date = START_DATE + timedelta(days=np.random.randint(0, date_range))
        sales.append({
            'DocEntry': _ + 1, # ID de la transacción
            'DocDate': doc_date,
            'CardCode': f'C{np.random.randint(1, 2000):04}', # ID del cliente
            'ItemCode': np.random.choice(product_codes),
            'Quantity': np.random.randint(1, 15),
            'Price': round(np.random.uniform(5.0, 500.0), 2)
        })
    df_inv1 = pd.DataFrame(sales)
    df_inv1['LineTotal'] = df_inv1['Quantity'] * df_inv1['Price']
    print("Tabla de ventas (INV1) generada.")
    return df_inv1

# --- 3. Generar Tabla de Inventario (OINM) ---
def generate_inventory(sales_df, products_df):
    print("Generando transacciones de inventario...")
    inventory = []
    product_codes = products_df['ItemCode'].tolist()

    # Simular transacciones de salida por ventas
    for _, row in sales_df.iterrows():
        inventory.append({
            'TransNum': len(inventory) + 1,
            'TransType': 'OUT', # Salida de inventario
            'DocDate': row['DocDate'],
            'ItemCode': row['ItemCode'],
            'OutQty': row['Quantity'],
            'InQty': 0,
            'Price': row['Price']
        })

    # Simular transacciones de entrada (reposición de stock)
    num_restocks = len(sales_df) // 10 # Asumimos una reposición por cada 10 ventas
    date_range = (END_DATE - START_DATE).days

    for _ in range(num_restocks):
        doc_date = START_DATE + timedelta(days=np.random.randint(0, date_range))
        inventory.append({
            'TransNum': len(inventory) + 1,
            'TransType': 'IN', # Entrada de inventario
            'DocDate': doc_date,
            'ItemCode': np.random.choice(product_codes),
            'OutQty': 0,
            'InQty': np.random.randint(50, 200),
            'Price': round(np.random.uniform(4.0, 450.0), 2) # Costo de compra
        })
    
    df_oinm = pd.DataFrame(inventory)
    df_oinm = df_oinm.sort_values(by='DocDate').reset_index(drop=True)
    print("Tabla de inventario (OINM) generada.")
    return df_oinm

# --- Función Principal ---
def main():
    # Crear directorio de salida si no existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio '{OUTPUT_DIR}' creado.")

    # Generar datos
    df_oitm = generate_products(NUM_PRODUCTS)
    df_inv1 = generate_sales(NUM_SALES, df_oitm)
    df_oinm = generate_inventory(df_inv1, df_oitm)

    # Guardar a Parquet
    print("\nGuardando tablas en formato Parquet...")
    df_oitm.to_parquet(os.path.join(OUTPUT_DIR, 'oitm.parquet'), index=False)
    df_inv1.to_parquet(os.path.join(OUTPUT_DIR, 'inv1.parquet'), index=False)
    df_oinm.to_parquet(os.path.join(OUTPUT_DIR, 'oinm.parquet'), index=False)
    print(f"Archivos guardados en el directorio '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()

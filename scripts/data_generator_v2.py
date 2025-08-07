# %%
import pandas as pd
import numpy as np
from faker import Faker
import os
from datetime import datetime, timedelta

# %%
# Inicializar Faker para datos ficticios
fake = Faker()

# --- Parámetros de Generación ---
NUM_PRODUCTS = 10000
NUM_SALES = 1000000
START_DATE = datetime(2018, 1, 1)
END_DATE = datetime.now()
OUTPUT_DIR = 'data'

# %% [markdown]
# # Generacion de tabla OITM

# %%
# # --- 1. Generar Tabla de Productos (OITM) ---
# def generate_products(n):
#     print(f"Generando {n} productos...")
#     items = []
#     for i in range(n):
#         items.append({
#             'ItemCode': f'SKU-{i:05}',  # Código del producto
#             'ItemName': fake.word().capitalize() + ' ' + fake.word() + ' Part',
#             'Brand': fake.company(),
#             'Category': fake.bs().split(' ')[0], # Categoría del producto
#             'CreateDate': fake.date_time_between(start_date='-10y', end_date='-6y')
#         })
#     df_oitm = pd.DataFrame(items)
#     print("Tabla de productos (OITM) generada.")
#     return df_oitm

# %%
def generate_products(n):
    print(f"Generando {n} productos...")
    items = []
    
    # Predefined groups
    groups = [101, 202, 303, 124, 405, 506, 607, 708, 809, 447]
    
    for i in range(n):
        # Determine if item is active (N) or inactive (Y)
        frozen_for = 'Y' if i < 500 else 'N'  # First 500 items will be inactive
        
        # Assign item group
        if i < 250:  # First 250 items in group 447 (Liquidación)
            item_grp = 447
        elif i < 750:  # Next 500 items in group 124 (Discontinuados)
            item_grp = 124
        else:
            # Randomly assign to remaining groups (excluding 124 and 447)
            item_grp = np.random.choice([g for g in groups if g not in [124, 447]])
        
        items.append({
            'ItemCode': f'SKU-{i:05}',  # Código del producto
            'ItemName': fake.word().capitalize() + ' ' + fake.word() + ' Part',
            'Brand': fake.company(),
            'Category': fake.bs().split(' ')[0],  # Categoría del producto
            'CreateDate': fake.date_time_between(start_date='-10y', end_date='-6y'),
            'FrozenFor': frozen_for,  # 'Y' for inactive, 'N' for active
            'ItemGrp': item_grp  # Group assignment
        })
    
    df_oitm = pd.DataFrame(items)
    
    # Verify the distribution
    frozen_dist = df_oitm['FrozenFor'].value_counts()
    group_dist = df_oitm['ItemGrp'].value_counts()
    
    print("\nDistribución de productos:")
    print(f"Activos (N): {frozen_dist.get('N', 0)}")
    print(f"Inactivos (Y): {frozen_dist.get('Y', 0)}")
    print("\nDistribución por grupo:")
    print(group_dist)
    
    print("\nTabla de productos (OITM) generada.")
    return df_oitm

# %% [markdown]
# # Generacion de tabla INV1

# %%
# # --- 2. Generar Tabla de Ventas (INV1) ---
# def generate_sales(n, products_df):
#     print(f"Generando {n} registros de ventas...")
#     sales = []
#     product_codes = products_df['ItemCode'].tolist()
#     date_range = (END_DATE - START_DATE).days

#     for _ in range(n):
#         doc_date = START_DATE + timedelta(days=np.random.randint(0, date_range))
#         sales.append({
#             'DocEntry': _ + 1, # ID de la transacción
#             'DocDate': doc_date,
#             'CardCode': f'C{np.random.randint(1, 2000):04}', # ID del cliente
#             'ItemCode': np.random.choice(product_codes),
#             'Quantity': np.random.randint(1, 15),
#             'Price': round(np.random.uniform(5.0, 500.0), 2)
#         })
#     df_inv1 = pd.DataFrame(sales)
#     df_inv1['LineTotal'] = df_inv1['Quantity'] * df_inv1['Price']
#     print("Tabla de ventas (INV1) generada.")
#     return df_inv1

# %%
def generate_sales(n, products_df):
    print(f"Generando {n} registros de ventas...")
    
    # Assign demand patterns to items
    unique_items = products_df['ItemCode'].unique()
    n_items = len(unique_items)
    
    # Assign demand patterns according to specified distribution
    np.random.shuffle(unique_items)
    n_smooth = int(n_items * 0.4)      # 40% Smooth
    n_erractic = int(n_items * 0.2)    # 20% Erratic
    n_intermittent = int(n_items * 0.3) # 30% Intermittent
    n_lumpy = n_items - n_smooth - n_erractic - n_intermittent  # Remainder to Lumpy
    
    demand_patterns = {}
    demand_patterns.update({item: 'Smooth' for item in unique_items[:n_smooth]})
    demand_patterns.update({item: 'Erratic' for item in unique_items[n_smooth:n_smooth+n_erractic]})
    demand_patterns.update({item: 'Intermittent' for item in unique_items[n_smooth+n_erractic:n_smooth+n_erractic+n_intermittent]})
    demand_patterns.update({item: 'Lumpy' for item in unique_items[n_smooth+n_erractic+n_intermittent:]})
    
    # Create a dictionary to track item sales patterns
    item_sales_patterns = {item: [] for item in unique_items}
    
    # Generate time series for each item based on its demand pattern
    date_range = (END_DATE - START_DATE).days
    all_sales = []
    doc_entry = 1
    
    for item_code in unique_items:
        pattern = demand_patterns[item_code]
        current_date = START_DATE
        last_sale_date = None
        
        while current_date <= END_DATE:
            # Generate demand based on pattern
            if pattern == 'Smooth':
                # Regular, low variability
                if np.random.random() > 0.9:  # 90% chance of sale on any given day
                    quantity = max(1, int(np.random.normal(8, 2)))
                    price = round(np.random.uniform(10.0, 500.0), 2)
                    all_sales.append({
                        'DocEntry': doc_entry,
                        'DocDate': current_date,
                        'CardCode': f'C{np.random.randint(1, 2000):04}',
                        'ItemCode': item_code,
                        'Quantity': quantity,
                        'Price': price,
                        'DemandPattern': pattern
                    })
                    doc_entry += 1
                    last_sale_date = current_date
            
            elif pattern == 'Erratic':
                # Frequent but highly variable quantities
                if np.random.random() > 0.3:  # 70% chance of sale
                    quantity = max(1, int(np.random.gamma(2, 3)))  # Right-skewed distribution
                    price = round(np.random.uniform(10.0, 500.0), 2)
                    all_sales.append({
                        'DocEntry': doc_entry,
                        'DocDate': current_date,
                        'CardCode': f'C{np.random.randint(1, 2000):04}',
                        'ItemCode': item_code,
                        'Quantity': quantity,
                        'Price': price,
                        'DemandPattern': pattern
                    })
                    doc_entry += 1
                    last_sale_date = current_date
            
            elif pattern == 'Intermittent':
                # Long periods of zero demand with occasional sales
                if (current_date - (last_sale_date or current_date)).days > np.random.randint(5, 30):
                    quantity = np.random.randint(1, 20)
                    price = round(np.random.uniform(10.0, 500.0), 2)
                    all_sales.append({
                        'DocEntry': doc_entry,
                        'DocDate': current_date,
                        'CardCode': f'C{np.random.randint(1, 2000):04}',
                        'ItemCode': item_code,
                        'Quantity': quantity,
                        'Price': price,
                        'DemandPattern': pattern
                    })
                    doc_entry += 1
                    last_sale_date = current_date
            
            elif pattern == 'Lumpy':
                # Occasional large orders with many zeros
                if np.random.random() > 0.9:  # 10% chance of sale
                    if np.random.random() > 0.7:  # 30% chance of large order
                        quantity = np.random.randint(20, 100)
                    else:
                        quantity = np.random.randint(1, 10)
                    price = round(np.random.uniform(10.0, 500.0), 2)
                    all_sales.append({
                        'DocEntry': doc_entry,
                        'DocDate': current_date,
                        'CardCode': f'C{np.random.randint(1, 2000):04}',
                        'ItemCode': item_code,
                        'Quantity': quantity,
                        'Price': price,
                        'DemandPattern': pattern
                    })
                    doc_entry += 1
                    last_sale_date = current_date
            
            current_date += timedelta(days=1)
    
    # Convert to DataFrame and sample to get desired number of sales
    df_inv1 = pd.DataFrame(all_sales)
    if len(df_inv1) > n:
        df_inv1 = df_inv1.sample(n=n, replace=False)
    
    df_inv1 = df_inv1.sort_values('DocDate').reset_index(drop=True)
    df_inv1['LineTotal'] = df_inv1['Quantity'] * df_inv1['Price']
    
    # Print demand pattern distribution
    print("\nDistribución de patrones de demanda en las ventas generadas:")
    print(df_inv1['DemandPattern'].value_counts(normalize=True).mul(100).round(1).astype(str) + '%')
    
    print("Tabla de ventas (INV1) generada.")
    return df_inv1

# %% [markdown]
# # Generacion de tabla OINM

# %%
# # --- 3. Generar Tabla de Inventario (OINM) ---
# def generate_inventory(sales_df, products_df):
#     print("Generando transacciones de inventario...")
#     inventory = []
#     product_codes = products_df['ItemCode'].tolist()

#     # Simular transacciones de salida por ventas
#     for _, row in sales_df.iterrows():
#         inventory.append({
#             'TransNum': len(inventory) + 1,
#             'TransType': 'OUT', # Salida de inventario
#             'DocDate': row['DocDate'],
#             'ItemCode': row['ItemCode'],
#             'OutQty': row['Quantity'],
#             'InQty': 0,
#             'Price': row['Price']
#         })

#     # Simular transacciones de entrada (reposición de stock)
#     num_restocks = len(sales_df) // 10 # Asumimos una reposición por cada 10 ventas
#     date_range = (END_DATE - START_DATE).days

#     for _ in range(num_restocks):
#         doc_date = START_DATE + timedelta(days=np.random.randint(0, date_range))
#         inventory.append({
#             'TransNum': len(inventory) + 1,
#             'TransType': 'IN', # Entrada de inventario
#             'DocDate': doc_date,
#             'ItemCode': np.random.choice(product_codes),
#             'OutQty': 0,
#             'InQty': np.random.randint(50, 200),
#             'Price': round(np.random.uniform(4.0, 450.0), 2) # Costo de compra
#         })
    
#     df_oinm = pd.DataFrame(inventory)
#     df_oinm = df_oinm.sort_values(by='DocDate').reset_index(drop=True)
#     print("Tabla de inventario (OINM) generada.")
#     return df_oinm

# %%
def generate_inventory(sales_df, products_df):
    print("Generando transacciones de inventario...")
    inventory = []
    product_codes = products_df['ItemCode'].unique()
    
    # Calculate stock requirements based on sales patterns
    sales_by_item = sales_df.groupby('ItemCode')
    inventory_events = []
    
    # Create inventory events from sales
    for item_code, group in sales_by_item:
        stock_level = np.random.randint(50, 200)  # Initial stock level
        
        for _, sale in group.sort_values('DocDate').iterrows():
            # Check if we have enough stock
            if stock_level >= sale['Quantity']:
                stock_level -= sale['Quantity']
                out_qty = sale['Quantity']
            else:
                out_qty = stock_level
                stock_level = 0
                
            # Add sale to inventory
            inventory_events.append({
                'Timestamp': sale['DocDate'],
                'ItemCode': item_code,
                'OutQty': out_qty,
                'InQty': 0,
                'Price': sale['Price'],
                'IsStockout': 1 if out_qty < sale['Quantity'] else 0
            })
            
            # Trigger restock if stock is low
            if stock_level < 10 and np.random.random() > 0.7:  # 30% chance to restock when low
                restock_qty = np.random.randint(50, 200)
                inventory_events.append({
                    'Timestamp': sale['DocDate'] + timedelta(days=1),
                    'ItemCode': item_code,
                    'OutQty': 0,
                    'InQty': restock_qty,
                    'Price': sale['Price'] * 0.8,  # 80% of sale price as cost
                    'IsStockout': 0
                })
                stock_level += restock_qty
    
    # Add periodic restocks for items with no recent activity
    for item_code in product_codes:
        if item_code not in sales_by_item.groups:
            # Add initial stock
            inventory_events.append({
                'Timestamp': START_DATE,
                'ItemCode': item_code,
                'OutQty': 0,
                'InQty': np.random.randint(50, 200),
                'Price': round(np.random.uniform(4.0, 450.0), 2),
                'IsStockout': 0
            })
    
    # Sort all events by timestamp
    inventory_events.sort(key=lambda x: x['Timestamp'])
    
    # Create final inventory DataFrame
    for i, event in enumerate(inventory_events, 1):
        inventory.append({
            'TransNum': i,
            'TransType': 'IN' if event['InQty'] > 0 else 'OUT',
            'DocDate': event['Timestamp'],
            'ItemCode': event['ItemCode'],
            'OutQty': event['OutQty'],
            'InQty': event['InQty'],
            'Price': event['Price'],
            'IsStockout': event.get('IsStockout', 0)
        })
    
    df_oinm = pd.DataFrame(inventory)
    df_oinm = df_oinm.sort_values(by='DocDate').reset_index(drop=True)
    
    # Print inventory statistics
    print("\nEstadísticas de inventario:")
    print(f"Total de transacciones: {len(df_oinm)}")
    print(f"Entradas de inventario: {len(df_oinm[df_oinm['TransType'] == 'IN'])}")
    print(f"Salidas de inventario: {len(df_oinm[df_oinm['TransType'] == 'OUT'])}")
    print(f"Stockouts registrados: {df_oinm['IsStockout'].sum()}")
    
    print("Tabla de inventario (OINM) generada.")
    return df_oinm

# %% [markdown]
# # Ejecucion de la funcion

# %%
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



"""
# Cell 1: Título y descripción
# # Generador de Datos para Análisis de Repuestos Automotrices

# Este notebook genera datos sintéticos para un análisis de ventas e inventario de repuestos automotrices.
"""

"""
# Cell 2: Importación de bibliotecas
import pandas as pd
import numpy as np
from faker import Faker
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilo para gráficos
%matplotlib inline
sns.set_theme(style="whitegrid")

# Inicializar Faker para datos ficticios
fake = Faker('es_ES')  # Usamos español para nombres de empresas y categorías
"""

"""
# Cell 3: Configuración de parámetros
# --- Parámetros de Generación ---
NUM_PRODUCTS = 10000
NUM_SALES = 100000
START_DATE = datetime(2018, 1, 1)
END_DATE = datetime.now()
OUTPUT_DIR = '../data'

print(f"Se generarán {NUM_PRODUCTS} productos y {NUM_SALES} ventas desde {START_DATE.strftime('%Y-%m-%d')} hasta {END_DATE.strftime('%Y-%m-%d')}")
"""

"""
# Cell 4: Función para generar productos
def generate_products(n):
    print(f"Generando {n} productos...")
    items = []
    for i in range(n):
        items.append({
            'ItemCode': f'SKU-{i:05}',  # Código del producto
            'ItemName': fake.word().capitalize() + ' ' + fake.word() + ' Part',
            'Brand': fake.company(),
            'Category': fake.bs().split(' ')[0],  # Categoría del producto
            'CreateDate': fake.date_time_between(start_date='-10y', end_date='-6y'),
            'Price': round(np.random.uniform(5.0, 500.0), 2)  # Precio del producto
        })
    df_products = pd.DataFrame(items)
    print("Tabla de productos generada con éxito.")
    return df_products
"""

"""
# Cell 5: Generar y mostrar productos
df_products = generate_products(NUM_PRODUCTS)
display(df_products.head())
print("\nResumen estadístico:")
display(df_products.describe(include='all').T)
"""

"""
# Cell 6: Función para generar ventas
def generate_sales(n, products_df):
    print(f"Generando {n} registros de ventas...")
    sales = []
    product_codes = products_df['ItemCode'].tolist()
    date_range = (END_DATE - START_DATE).days

    for _ in range(n):
        doc_date = START_DATE + timedelta(days=np.random.randint(0, date_range))
        sales.append({
            'DocEntry': _ + 1,  # ID de la transacción
            'DocDate': doc_date,
            'CardCode': f'C{np.random.randint(1, 2000):04}',  # ID del cliente
            'ItemCode': np.random.choice(product_codes),
            'Quantity': np.random.randint(1, 15),
            'Price': round(np.random.uniform(5.0, 500.0), 2)
        })
    df_sales = pd.DataFrame(sales)
    df_sales['LineTotal'] = df_sales['Quantity'] * df_sales['Price']
    print("Tabla de ventas generada con éxito.")
    return df_sales
"""

"""
# Cell 7: Generar y mostrar ventas
df_sales = generate_sales(NUM_SALES, df_products)
display(df_sales.head())
print("\nResumen estadístico:")
display(df_sales.describe().T)
"""

"""
# Cell 8: Función para generar inventario
def generate_inventory(sales_df, products_df):
    print("Generando transacciones de inventario...")
    inventory = []
    product_codes = products_df['ItemCode'].tolist()

    # Simular transacciones de salida por ventas
    for _, row in sales_df.iterrows():
        inventory.append({
            'TransNum': len(inventory) + 1,
            'TransType': 'OUT',  # Salida de inventario
            'DocDate': row['DocDate'],
            'ItemCode': row['ItemCode'],
            'OutQty': row['Quantity'],
            'InQty': 0,
            'Price': row['Price']
        })

    # Simular transacciones de entrada (reposición de stock)
    num_restocks = len(sales_df) // 10  # Asumimos una reposición por cada 10 ventas
    date_range = (END_DATE - START_DATE).days

    for _ in range(num_restocks):
        doc_date = START_DATE + timedelta(days=np.random.randint(0, date_range))
        inventory.append({
            'TransNum': len(inventory) + 1,
            'TransType': 'IN',  # Entrada de inventario
            'DocDate': doc_date,
            'ItemCode': np.random.choice(product_codes),
            'OutQty': 0,
            'InQty': np.random.randint(50, 200),
            'Price': round(np.random.uniform(4.0, 450.0), 2)  # Costo de compra
        })
    
    df_inventory = pd.DataFrame(inventory)
    df_inventory = df_inventory.sort_values(by='DocDate').reset_index(drop=True)
    print("Tabla de inventario generada con éxito.")
    return df_inventory
"""

"""
# Cell 9: Generar y mostrar inventario
df_inventory = generate_inventory(df_sales, df_products)
display(df_inventory.head())
print("\nResumen estadístico:")
display(df_inventory.describe().T)
"""

"""
# Cell 10: Visualización de datos - Configuración
plt.figure(figsize=(15, 10))

# Gráfico 1: Distribución de precios de productos
plt.subplot(2, 2, 1)
sns.histplot(df_products['Price'], bins=50, kde=True)
plt.title('Distribución de Precios de Productos')
plt.xlabel('Precio')
plt.ylabel('Frecuencia')

# Gráfico 2: Ventas por mes
plt.subplot(2, 2, 2)
df_sales['Month'] = df_sales['DocDate'].dt.to_period('M')
sales_by_month = df_sales.groupby('Month')['LineTotal'].sum().reset_index()
sns.lineplot(data=sales_by_month, x='Month', y='LineTotal')
plt.title('Ventas Mensuales')
plt.xticks(rotation=45)
plt.tight_layout()

# Gráfico 3: Top 10 productos más vendidos
plt.subplot(2, 2, 3)
top_products = df_sales['ItemCode'].value_counts().head(10)
sns.barplot(x=top_products.index, y=top_products.values)
plt.title('Top 10 Productos Más Vendidos')
plt.xticks(rotation=90)

# Gráfico 4: Distribución de cantidades vendidas
plt.subplot(2, 2, 4)
sns.boxplot(x=df_sales['Quantity'])
plt.title('Distribución de Cantidades por Venta')

plt.tight_layout()
plt.show()
"""

"""
# Cell 11: Guardar datos
# Crear directorio de salida si no existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Directorio '{OUTPUT_DIR}' creado.")

# Guardar a Parquet
print("\nGuardando tablas en formato Parquet...")
df_products.to_parquet(os.path.join(OUTPUT_DIR, 'products.parquet'), index=False)
df_sales.to_parquet(os.path.join(OUTPUT_DIR, 'sales.parquet'), index=False)
df_inventory.to_parquet(os.path.join(OUTPUT_DIR, 'inventory.parquet'), index=False)
print(f"Archivos guardados en el directorio '{OUTPUT_DIR}'.")
"""

"""
# Cell 12: Análisis adicional (opcional)
# Aquí puedes agregar más análisis según sea necesario
print("\nResumen de datos generados:")
print(f"- Número de productos: {len(df_products)}")
print(f"- Número de ventas: {len(df_sales)}")
print(f"- Número de transacciones de inventario: {len(df_inventory)}")
print(f"- Período cubierto: {df_sales['DocDate'].min().date()} a {df_sales['DocDate'].max().date()}")
"""

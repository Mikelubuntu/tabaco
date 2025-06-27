import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear tabla productos
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    descripcion TEXT,
    ean TEXT,
    ean2 TEXT,
    cod_barras TEXT
)
''')

# Crear tabla conteos_fisicos
cursor.execute('''
CREATE TABLE IF NOT EXISTS conteos_fisicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tienda TEXT,
    codigo TEXT,
    descripcion TEXT,
    ean TEXT,
    ean2 TEXT,
    stock_fisico INTEGER,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    autor TEXT,
    eliminado INTEGER,
    motivo_eliminacion TEXT
)
''')

# Crear tabla inventario_historico
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventario_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    autor TEXT,
    tienda TEXT,
    productos_json TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("✅ Base de datos creada correctamente como 'database.db'")

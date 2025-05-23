import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cod_barras TEXT NOT NULL
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS conteos_fisicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tienda TEXT NOT NULL,
    codigo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cod_barras TEXT NOT NULL,
    stock_fisico INTEGER,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    autor TEXT,
    eliminado INTEGER DEFAULT 0,
    motivo_eliminacion TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS inventario_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    autor TEXT NOT NULL,
    tienda TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    productos_json TEXT NOT NULL
)
''')

conn.commit()
conn.close()
print("¡Base de datos creada correctamente!")

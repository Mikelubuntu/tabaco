import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    marca TEXT NOT NULL,
    presentacion TEXT NOT NULL,
    precio_compra REAL NOT NULL,
    precio_venta REAL NOT NULL,
    stock INTEGER NOT NULL
)
''')

conn.commit()
conn.close()

print("Base de datos y tabla de productos creada exitosamente.")

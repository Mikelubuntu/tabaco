<<<<<<< HEAD
import sqlite3

# Conectar a tu base de datos (database.db)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conteos_fisicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tienda TEXT,
        codigo TEXT,
        descripcion TEXT,
        cod_barras TEXT,
        stock_fisico INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()

print("Tabla 'conteos_fisicos' creada correctamente.")
=======
import sqlite3

# Conectar a tu base de datos (database.db)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conteos_fisicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tienda TEXT,
        codigo TEXT,
        descripcion TEXT,
        cod_barras TEXT,
        stock_fisico INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()

print("Tabla 'conteos_fisicos' creada correctamente.")
>>>>>>> b941901bcb68c5523b74da7ad06e59dbd1a0516a

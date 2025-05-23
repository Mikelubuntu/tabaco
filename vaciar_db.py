import sqlite3

conn = sqlite3.connect('database.db')
conn.execute('DELETE FROM productos')
conn.execute('DELETE FROM conteos_fisicos')
conn.execute('DELETE FROM inventario_historico')
conn.commit()
conn.close()

print("¡Base de datos vaciada correctamente!")

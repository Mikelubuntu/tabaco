import sqlite3

conn = sqlite3.connect('database.db')
conn.execute('DELETE FROM productos')
conn.execute('DELETE FROM conteos_fisicos')
conn.execute('DELETE FROM inventario_historico')
# Ahora resetea el contador de cada tabla:
conn.execute("DELETE FROM sqlite_sequence WHERE name='productos'")
conn.execute("DELETE FROM sqlite_sequence WHERE name='conteos_fisicos'")
conn.execute("DELETE FROM sqlite_sequence WHERE name='inventario_historico'")
conn.commit()
conn.close()

print("¡Base de datos vaciada y IDs reiniciados correctamente!")

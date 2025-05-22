-- Elimina todas las tablas si existen (por seguridad)
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS productos_old;
DROP TABLE IF EXISTS conteos_fisicos;
DROP TABLE IF EXISTS historico_inventarios;
DROP TABLE IF EXISTS inventario_historico;

-- Crea la tabla principal de productos
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cod_barras TEXT,
    tienda TEXT NOT NULL
);

-- Crea la tabla de conteos físicos
CREATE TABLE conteos_fisicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tienda TEXT NOT NULL,
    codigo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cod_barras TEXT,
    stock_fisico INTEGER,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Crea la tabla de históricos
CREATE TABLE inventario_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    autor TEXT NOT NULL,
    tienda TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    productos_json TEXT NOT NULL
);

ALTER TABLE conteos_fisicos ADD COLUMN autor TEXT;
def get_productos_de_tienda_y_fecha(tienda, fecha):
    if fecha:
        cursor.execute("SELECT * FROM inventario WHERE tienda=%s AND fecha=%s", (tienda, fecha))
    else:
        cursor.execute("SELECT * FROM inventario WHERE tienda=%s", (tienda,))
    return cursor.fetchall()
ALTER TABLE productos RENAME TO productos_old;

CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cod_barras TEXT NOT NULL
    -- NO añadas tienda aquí
);

INSERT INTO productos (id, codigo, descripcion, cod_barras)
SELECT id, codigo, descripcion, cod_barras FROM productos_old;

DROP TABLE productos_old;

DELETE FROM conteos_fisicos;
DELETE FROM inventario_historico WHERE tienda = 'Las Canteras';



-- Tabla de productos (sin tienda)
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cod_barras TEXT NOT NULL
);

-- Tabla de conteos físicos (CON tienda, para diferenciar los conteos por tienda y fecha)
CREATE TABLE conteos_fisicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tienda TEXT NOT NULL,
    codigo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    cod_barras TEXT NOT NULL,
    stock_fisico INTEGER,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    autor TEXT
);

-- Tabla de históricos de inventario físico
CREATE TABLE inventario_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    autor TEXT NOT NULL,
    tienda TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    productos_json TEXT NOT NULL
);

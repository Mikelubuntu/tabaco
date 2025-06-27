from flask import Flask, render_template, request, redirect, url_for, send_file, make_response, session, flash
from functools import wraps
import sqlite3
import pandas as pd
from io import BytesIO
from xhtml2pdf import pisa
import io
import os
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch




app = Flask(__name__)
app.secret_key = '0022'
os.makedirs('static/temp', exist_ok=True)

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_requerido
def index():
    return render_template('base.html')

import secrets

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        password = request.form['password']
        if password == '0022':
            session['logueado'] = True
            # Aquí creas el token aleatorio
            session['token'] = secrets.token_hex(32)
            return redirect(url_for('index'))
        else:
            error = 'Contraseña incorrecta'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------ Lista de productos ------------
import json

with open('productos.json', 'r', encoding='utf-8') as f:
    productos = json.load(f)

  # ------------ Lista de tiendas ------------
tiendas = [
    "Mesa y Lopez",
    "Las Canteras",
    "Triana",
    "Mercado Central",
    "Castillo 20",
    "Castillo 53",
    "Los Cristianos",
    "Campanario"
    ]

# ------------ Conexión SQLite -------------
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_productos_de_tienda_y_fecha(tienda, fecha):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tienda and fecha:
        cursor.execute(
            "SELECT * FROM conteos_fisicos WHERE tienda=? AND DATE(fecha)=?",
            (tienda, fecha)
        )
    elif tienda:
        cursor.execute(
            "SELECT * FROM conteos_fisicos WHERE tienda=?",
            (tienda,)
        )
    elif fecha:
        cursor.execute(
            "SELECT * FROM conteos_fisicos WHERE DATE(fecha)=?",
            (fecha,)
        )
    else:
        cursor.execute(
            "SELECT * FROM conteos_fisicos"
        )
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def productos_sql_a_dict(productos_sql):
    def limpiar(valor):
        return str(valor).strip() if valor not in [None, "", 0, "0"] else ""

    return [
        {
            "codigo": p["codigo"],
            "descripcion": p["descripcion"],
            "ean": limpiar(p["ean"]),
            "ean2": limpiar(p["ean2"]),
            "cod_barras": limpiar(p["ean"])
        }
        for p in productos_sql
    ]

# ------------ Rutas principales -----------

@app.route('/inventario')
@login_requerido
def inventario():
    conn = get_db_connection()
    productos_sql = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()
    return render_template(
        'inventario.html',
        productos=productos_sql
    )

    return render_template(
        'inventario.html',
        productos=productos_sql,
        tiendas=tiendas,
        tienda_seleccionada=tienda,
        fecha_seleccionada=fecha
    )

@app.route('/agregar_producto', methods=('GET', 'POST'))
@login_requerido
def agregar_producto():
    mensaje = ""
    if request.method == 'POST':
        codigo = request.form['codigo']
        descripcion = request.form['descripcion']
        ean = request.form.get('ean', '').strip()
        ean2 = request.form.get('ean2', '').strip()

        conn = get_db_connection()
        existe = conn.execute(
            "SELECT * FROM productos WHERE codigo = ?",
            (codigo,)
        ).fetchone()
        if existe:
            mensaje = "¡Ya existe un producto con ese código!"
            conn.close()
            return render_template('agregar_producto.html', mensaje=mensaje)
        else:
            conn.execute(
                'INSERT INTO productos (codigo, descripcion, ean, ean2) VALUES (?, ?, ?, ?)',
                (codigo, descripcion, ean, ean2)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('inventario'))

    return render_template('agregar_producto.html', mensaje=mensaje)

# ------------ App Exportar ------------

@app.route('/exportar_conteos_excel')
@login_requerido
def exportar_conteos_excel():
    tienda = request.args.get('tienda', '')
    conn = get_db_connection()
    if tienda:
        df = pd.read_sql_query(
            "SELECT * FROM conteos_fisicos WHERE (eliminado IS NULL OR eliminado = 0) AND tienda = ? ORDER BY fecha DESC",
            conn, params=(tienda,)
        )
    else:
        df = pd.read_sql_query(
            "SELECT * FROM conteos_fisicos WHERE eliminado IS NULL OR eliminado = 0 ORDER BY fecha DESC",
            conn
        )
    conn.close()
    
    print("Columnas reales:", df.columns.tolist())

    # Renombra y reordena las columnas
    df = df.rename(columns={
    'id': 'id',
    'ean': 'EAN',
    'ean2': 'EAN2',
    'codigo': 'Código artículo',
    'descripcion': 'Descripción artículo',
    'tienda': 'Nombre almacén',
    'stock_fisico': 'Stock',
    'cod_barras': 'COD.BARRAS'
})

    columnas_finales = ['id', 'EAN', 'EAN2', 'Código artículo', 'Descripción artículo', 'Nombre almacén', 'COD.BARRAS', 'Stock', 'fecha']

    # Sólo usa columnas que existen realmente en el df (puedes avisar si falta alguna)
    columnas_existentes = [col for col in columnas_finales if col in df.columns]
    df = df[columnas_existentes]

    # Si falta alguna columna, puedes avisar
    if len(columnas_existentes) < len(columnas_finales):
        faltan = set(columnas_finales) - set(columnas_existentes)
        print("FALTAN COLUMNAS en exportar_conteos_excel:", faltan)

    from openpyxl.styles import numbers

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Conteos')
        workbook = writer.book
        worksheet = writer.sheets['Conteos']
    
    # Aplicar formato de texto a columnas específicas (EAN, EAN2, COD.BARRAS)
        for idx, col_name in enumerate(df.columns):
            if col_name in ['EAN', 'EAN2', 'COD.BARRAS']:
                col_letter = chr(65 + idx)  # A, B, C, etc.
                for cell in worksheet[f"{col_letter}2":f"{col_letter}{len(df)+1}"]:
                    for c in cell:
                        c.number_format = numbers.FORMAT_TEXT

    output.seek(0)
    return send_file(
    output,
    download_name="conteos_fisicos.xlsx",
    as_attachment=True,
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

from flask import make_response


@app.route('/exportar_conteos_pdf')
@login_requerido
def exportar_conteos_pdf():
    tienda = request.args.get('tienda', '')
    conn = get_db_connection()
    if tienda:
        conteos = conn.execute("SELECT * FROM conteos_fisicos WHERE tienda = ? ORDER BY fecha DESC", (tienda,)).fetchall()
    else:
        conteos = conn.execute("SELECT * FROM conteos_fisicos ORDER BY fecha DESC").fetchall()
    conn.close()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2.0, height - 40, f"Conteos en Tienda - {tienda or 'Todas'}")

    headers = ["ID", "Tienda", "EAN", "EAN2", "Código", "Descripción", "Cantidad", "Fecha"]
    col_widths = [50, 70, 80, 80, 60, 150, 50, 100]
    total_table_width = sum(col_widths)
    left_margin = (width - total_table_width) / 2  # Centrado en la página
    y = height - 70  # Posición inicial vertical

    # Dibujar encabezados
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        x = sum(col_widths[:i]) + left_margin
        c.drawString(x, y, h)

    # Dibujar datos
    c.setFont("Helvetica", 8)
    y -= 15
    for row in conteos:
        datos = [
            row['id'],
            row['tienda'],
            str(row['ean']),
            str(row['ean2']),
            row['codigo'],
            row['descripcion'][:40],  # limitar descripción
            row['stock_fisico'],
            row['fecha']
        ]
        for i, dato in enumerate(datos):
            x = sum(col_widths[:i]) + left_margin
            c.drawString(x, y, str(dato))
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 8)

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="conteos_fisicos.pdf", mimetype='application/pdf')


# ------------ Inventario físico por tienda, guay! ------------
import json

@app.route('/inventario_fisico', methods=['GET', 'POST'])
@login_requerido
def inventario_fisico():
    mensaje = ''
    conn = get_db_connection()
    productos_sql = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()

    productos_db = productos_sql_a_dict(productos_sql)

    # ✅ Función bien indentada dentro de la función principal
    def transformar_json(producto):
        def limpiar(valor):
            return str(valor).strip() if valor not in [None, "", 0, "0"] else ""

        return {
        "codigo": producto.get("Código artículo", "").strip(),
        "descripcion": producto.get("Descripción artículo", "").strip(),
        "ean": limpiar(producto.get("EAN")),
        "ean2": limpiar(producto.get("EAN2")),
        "cod_barras": limpiar(producto.get("EAN"))
    }


    # ✅ Unir productos priorizando los del JSON
    productos_json_transformados = [transformar_json(p) for p in productos]
    productos_dict = {p["codigo"]: p for p in productos_db}
    productos_dict.update({p["codigo"]: p for p in productos_json_transformados})
    productos_unidos = list(productos_dict.values())

    productos_unidos.sort(key=lambda x: (
        str(x.get('ean', '')),
        str(x.get('ean2', '')),
        x.get('codigo', ''),
        x.get('descripcion', '')
    ))

    if request.method == 'POST':
        tienda = request.form['tienda']
        autor = request.form.get('autor', '').strip()
        productos_modificados = 0
        inventario_actual = []
        conn = get_db_connection()

        for producto in productos_unidos:
            cantidad = request.form.get(f"stock_{producto['codigo']}")
            try:
                cantidad_num = int(cantidad)
            except Exception:
                cantidad_num = 0
            if cantidad_num > 0:
                conn.execute(
                    'INSERT INTO conteos_fisicos (tienda, codigo, descripcion, ean, ean2, stock_fisico, fecha, autor) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)',
                    (tienda, producto['codigo'], producto['descripcion'], producto['ean'], producto['ean2'], cantidad_num, autor)
                )
                productos_modificados += 1
                inventario_actual.append({
                    "codigo": producto['codigo'],
                    "descripcion": producto['descripcion'],
                    "cod_barras": producto['cod_barras'],
                    "ean": producto.get('ean', ''),
                    "ean2": producto.get('ean2', ''),
                    "cantidad": cantidad_num
})


        manual_codigo = request.form.get("manual_codigo", "").strip()
        manual_descripcion = request.form.get("manual_descripcion", "").strip()
        manual_ean = request.form.get("manual_ean", "").strip()
        manual_ean2 = request.form.get("manual_ean2", "").strip()
        manual_cantidad = request.form.get("manual_cantidad", "").strip()

        if manual_codigo and manual_descripcion and manual_cantidad:
            try:
                cantidad_manual = int(manual_cantidad)
            except Exception:
                cantidad_manual = 0
            if cantidad_manual > 0:
                conn.execute(
                    'INSERT INTO conteos_fisicos (tienda, codigo, descripcion, ean, ean2, stock_fisico, fecha, autor) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)',
                    (tienda, manual_codigo, manual_descripcion, manual_ean, manual_ean2, cantidad_manual, autor)
                )
                productos_modificados += 1
                inventario_actual.append({
                    "codigo": manual_codigo,
                    "descripcion": manual_descripcion,
                    "cod_barras": manual_ean,
                    "ean": manual_ean,
                    "ean2": manual_ean2,
                    "cantidad": cantidad_manual
})


        conn.commit()

        if productos_modificados > 0 and autor:
            conn.execute(
                "INSERT INTO inventario_historico (autor, tienda, productos_json) VALUES (?, ?, ?)",
                (autor, tienda, json.dumps(inventario_actual, ensure_ascii=False))
            )
            conn.commit()

        conn.close()

        mensaje = (
            f"Se guardaron {productos_modificados} productos correctamente."
            if productos_modificados > 0 else
            "No se guardó ningún producto (no se modificó cantidad)."
        )

        # ✅ Vuelve a unir productos después del POST
        productos_sql = get_db_connection().execute('SELECT * FROM productos').fetchall()
        productos_db = productos_sql_a_dict(productos_sql)
        productos_json_transformados = [transformar_json(p) for p in productos]
        productos_dict = {p["codigo"]: p for p in productos_db}
        productos_dict.update({p["codigo"]: p for p in productos_json_transformados})
        productos_unidos = list(productos_dict.values())

        productos_unidos.sort(key=lambda x: (
            str(x.get('ean', '')),
            str(x.get('ean2', '')),
            x.get('codigo', ''),
            x.get('descripcion', '')
        ))

        return render_template('inventario_fisico.html', tiendas=tiendas, productos=productos_unidos, mensaje=mensaje)

    return render_template('inventario_fisico.html', tiendas=tiendas, productos=productos_unidos)


@app.route('/conteos_fisicos', methods=['GET'])
@login_requerido
def conteos_fisicos():
    conn = get_db_connection()
    tienda_seleccionada = request.args.get('tienda', '')
    fecha_seleccionada = request.args.get('fecha', '')

    query = 'SELECT * FROM conteos_fisicos'
    params = []
    filtros = []

    if tienda_seleccionada:
        filtros.append('tienda = ?')
        params.append(tienda_seleccionada)
    if fecha_seleccionada:
        filtros.append('DATE(fecha) = ?')
        params.append(fecha_seleccionada)
    if filtros:
        query += ' WHERE ' + ' AND '.join(filtros)
    query += ' ORDER BY rowid DESC'

    conteos = conn.execute(query, params).fetchall()
    conn.close()
    return render_template(
        'conteos_fisicos.html',
        conteos=conteos,
        tiendas=tiendas,
        tienda_seleccionada=tienda_seleccionada,
        fecha_seleccionada=fecha_seleccionada
    )

@app.route('/editar_conteo/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_conteo(id):
    conn = get_db_connection()
    conteo = conn.execute('SELECT * FROM conteos_fisicos WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        nuevo_stock = request.form['stock_fisico']
        conn.execute('UPDATE conteos_fisicos SET stock_fisico = ? WHERE id = ?', (nuevo_stock, id))
        conn.commit()
        conn.close()
        return redirect(url_for('conteos_fisicos'))
    conn.close()
    return render_template('editar_conteo.html', conteo=conteo)  # <-- Aquí está bien

@app.route('/eliminar_conteo', methods=['POST'])
@login_requerido
def eliminar_conteo():
    id_eliminar = request.form['id_eliminar']
    motivo = request.form['motivo_eliminacion']
    conn = get_db_connection()
    conn.execute('UPDATE conteos_fisicos SET eliminado=1, motivo_eliminacion=? WHERE id=?', (motivo, id_eliminar))
    conn.commit()
    conn.close()
    return redirect(url_for('conteos_fisicos'))

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_requerido
def eliminar_producto(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('inventario'))

import os
import io
import pandas as pd
from flask import render_template, request, send_file, session, url_for

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_producto(id):
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    if not producto:
        conn.close()
        return "Producto no encontrado", 404

    if request.method == 'POST':
        codigo = request.form['codigo']
        descripcion = request.form['descripcion']
        cod_barras = request.form['cod_barras']

        # Validar que no exista otro producto con el mismo código
        existe = conn.execute(
            "SELECT * FROM productos WHERE codigo = ? AND id != ?", (codigo, id)
        ).fetchone()
        if existe:
            conn.close()
            mensaje = "¡Ya existe otro producto con ese código!"
            return render_template('editar_producto.html', producto=producto, mensaje=mensaje)
        else:
            conn.execute(
                'UPDATE productos SET codigo = ?, descripcion = ?, cod_barras = ? WHERE id = ?',
                (codigo, descripcion, cod_barras, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('inventario'))
    conn.close()
    return render_template('editar_producto.html', producto=producto)



@app.route('/descargar_cruce')
@login_requerido
def descargar_cruce():
    import os
    from flask import send_file, session
    path = session.get('resultado_cruce_path')
    if path and os.path.exists(path):
        return send_file(path, download_name='cruce_inventario.xlsx', as_attachment=True)
    return "No hay archivo para descargar", 404

import json
from flask import render_template

@app.route('/inventario_historico')
@login_requerido
def inventario_historico():
    conn = get_db_connection()
    historicos = conn.execute(
        "SELECT * FROM inventario_historico ORDER BY fecha DESC"
    ).fetchall()
    historicos_lista = []
    for h in historicos:
        try:
            productos = json.loads(h['productos_json'])
        except Exception:
            productos = []
        # Busca estado eliminado/motivo para cada producto:
        for p in productos:
            cf = conn.execute(
                "SELECT eliminado, motivo_eliminacion FROM conteos_fisicos WHERE codigo = ? AND tienda = ? ORDER BY fecha DESC LIMIT 1",
                (p['codigo'], h['tienda'])
            ).fetchone()
            if cf:
                p['eliminado'] = cf['eliminado']
                p['motivo_eliminacion'] = cf['motivo_eliminacion']
            else:
                p['eliminado'] = 0
                p['motivo_eliminacion'] = None
        historicos_lista.append({
            "id": h['id'],
            "autor": h['autor'],
            "tienda": h['tienda'],
            "fecha": h['fecha'],
            "productos": productos
        })
    conn.close()
    return render_template('inventario_historico.html', historicos=historicos_lista)

@app.route('/descargar_historico_excel/<int:historico_id>')
@login_requerido
def descargar_historico_excel(historico_id):
    import json
    import pandas as pd
    from io import BytesIO
    from flask import send_file

    try:
        conn = get_db_connection()
        historico = conn.execute('SELECT * FROM inventario_historico WHERE id = ?', (historico_id,)).fetchone()
        conn.close()
        if not historico:
            return "Histórico no encontrado", 404

        try:
            productos = json.loads(historico['productos_json'])
        except Exception as e:
            print("ERROR al cargar JSON:", e)
            return f"Error al cargar los productos de este histórico: {e}", 500

        data = []
        for p in productos:
            data.append({
                'Código': p.get('codigo', ''),
                'Descripción': p.get('descripcion', ''),
                'Código de Barras': str(p.get('cod_barras', '')),  # Fuerza a texto
                'Cantidad': p.get('cantidad', '')
            })

        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
            workbook = writer.book
            worksheet = writer.sheets['Inventario']
            # Busca columna de código de barras y ponla como texto
            for idx, col in enumerate(df.columns):
                if col.lower().startswith('código de barras'):
                    text_fmt = workbook.add_format({'num_format': '@'})
                    worksheet.set_column(idx, idx, 20, text_fmt)

        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f"historico_{historico_id}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print("ERROR GENERAL EN DESCARGAR HISTORICO EXCEL:", e)
        return f"Error interno: {e}", 500

def importar_productos_fijos():
    conn = get_db_connection()
    cursor = conn.cursor()
    for prod in productos:
        codigo = prod["codigo"]
        descripcion = prod["descripcion"]
        cod_barras = prod["cod_barras"]
        # Comprueba si ya existe el producto por código
        existe = cursor.execute("SELECT 1 FROM productos WHERE codigo = ?", (codigo,)).fetchone()
        if not existe:
            cursor.execute(
                "INSERT INTO productos (codigo, descripcion, cod_barras) VALUES (?, ?, ?)",
                (codigo, descripcion, cod_barras)
            )
            print(f"Producto añadido: {codigo} - {descripcion}")
    conn.commit()
    conn.close()
    print("Importación terminada")

    from flask import send_file

@app.route('/descargar_db')
def descargar_db():
    return send_file('database.db', as_attachment=True)

def agregar_columnas_ean():
    conn = get_db_connection()
    try:
        conn.execute("ALTER TABLE productos ADD COLUMN ean TEXT;")
    except:
        print("La columna 'ean' ya existe.")
    try:
        conn.execute("ALTER TABLE productos ADD COLUMN ean2 TEXT;")
    except:
        print("La columna 'ean2' ya existe.")
    conn.commit()
    conn.close()

@app.route('/cruce_inventario', methods=['GET', 'POST'])
@login_requerido
def cruce_inventario():
    mensaje = ''
    resumen = {}
    tabla_diferencias = []
    lista_solo_as400 = []
    hay_faltantes_as400 = False

    if request.method == 'POST':
        # 1) Cargar archivos
        f_as400 = request.files.get('archivo_as400')
        f_casa = request.files.get('archivo_casa_ricardo')
        if not f_as400 or not f_casa:
            mensaje = "Debes subir ambos ficheros: AS400 y Casa Ricardo."
            return render_template('cruce.html', mensaje=mensaje)

        # 2) Leer ambos archivos
        df_as400 = pd.read_excel(f_as400, dtype=str)
        df_casa = pd.read_excel(f_casa, dtype=str)

        # 3) Verificar columnas mínimas necesarias
        columnas_necesarias = ['Código artículo', 'Descripción artículo', 'EAN', 'EAN2', 'Stock', 'Nombre almacén']
        for col in columnas_necesarias:
            if col not in df_as400.columns or col not in df_casa.columns:
                mensaje = f"Falta la columna '{col}' en uno de los archivos."
                return render_template('cruce.html', mensaje=mensaje)

        # 4) Normalizar códigos
        df_as400['Código artículo'] = df_as400['Código artículo'].astype(str).str.strip()
        df_casa['Código artículo'] = df_casa['Código artículo'].astype(str).str.strip()

        # 5) Filtrar por tienda única
        tiendas = df_casa['Nombre almacén'].astype(str).str.strip().unique()
        if len(tiendas) != 1:
            mensaje = f"El archivo de Casa Ricardo debe contener una sola tienda. Encontradas: {', '.join(tiendas)}"
            return render_template('cruce.html', mensaje=mensaje)
        tienda = tiendas[0]
        df_casa = df_casa[df_casa['Nombre almacén'].astype(str).str.strip() == tienda]

        # 6) Renombrar columnas para merge
        df_as400 = df_as400.rename(columns={'Stock': 'Stock_AS400'})
        df_casa = df_casa.rename(columns={'Stock': 'Stock_CASA'})

        # 7) Convertir cantidades a números enteros
        df_as400['Stock_AS400'] = pd.to_numeric(df_as400['Stock_AS400'], errors='coerce').fillna(0).astype(int)
        df_casa['Stock_CASA'] = pd.to_numeric(df_casa['Stock_CASA'], errors='coerce').fillna(0).astype(int)

        # 8) Hacer merge
        df_merge = pd.merge(
            df_as400,
            df_casa[['Código artículo', 'Stock_CASA']],
            on='Código artículo',
            how='outer',
            indicator=True
        )

        # 9) Rellenar valores faltantes
        for col in ['Stock_AS400', 'Stock_CASA', 'Descripción artículo', 'EAN', 'EAN2']:
            if col not in df_merge.columns:
                df_merge[col] = ''
        df_merge['Stock_AS400'] = df_merge['Stock_AS400'].fillna(0).astype(int)
        df_merge['Stock_CASA'] = df_merge['Stock_CASA'].fillna(0).astype(int)
        df_merge['Descripción artículo'] = df_merge['Descripción artículo'].fillna('')
        df_merge['EAN'] = df_merge['EAN'].fillna('').astype(str).str.replace('.0', '', regex=False)
        df_merge['EAN2'] = df_merge['EAN2'].fillna('').astype(str).str.replace('.0', '', regex=False)

        # 10) Calcular diferencias
        df_merge['DIFERENCIA'] = df_merge['Stock_CASA'] - df_merge['Stock_AS400']

        # 11) Crear alias para tabla
        df_merge['CODIGO'] = df_merge['Código artículo']
        df_merge['DESCRIPCION'] = df_merge['Descripción artículo']
        df_merge['Cantidad Física_AS400'] = df_merge['Stock_AS400']
        df_merge['Cantidad Física_CASA'] = df_merge['Stock_CASA']

        # 12) Tabla de diferencias
        diffs = df_merge[df_merge['DIFERENCIA'] != 0].copy()
        tabla_diferencias = diffs[[
            'CODIGO',
            'DESCRIPCION',
            'EAN',
            'EAN2',
            'Cantidad Física_AS400',
            'Cantidad Física_CASA',
            'DIFERENCIA'
        ]].to_dict(orient='records')

        # 13) Faltantes solo en AS400
        faltantes = df_merge[df_merge['_merge'] == 'left_only']
        if not faltantes.empty:
            hay_faltantes_as400 = True
            lista_solo_as400 = faltantes[[
                'CODIGO',
                'DESCRIPCION',
                'EAN',
                'EAN2',
                'Cantidad Física_AS400'
            ]].to_dict(orient='records')

        # 14) Resumen
        resumen = {
            'tienda': tienda,
            'diferente_stock': len(tabla_diferencias),
            'num_faltantes_as400': len(lista_solo_as400)
        }

        # 15) Exportar Excel (NO altera nada más)
        import xlsxwriter
        from io import BytesIO

        df_export = diffs[[
            'CODIGO',
            'DESCRIPCION',
            'EAN',
            'EAN2',
            'Cantidad Física_AS400',
            'Cantidad Física_CASA',
            'DIFERENCIA'
        ]]

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Diferencias')
            workbook = writer.book
            worksheet = writer.sheets['Diferencias']

            formato_rojo = workbook.add_format({'font_color': 'red'})
            formato_verde = workbook.add_format({'font_color': 'green'})

            for row_num, value in enumerate(df_export['DIFERENCIA'], start=1):
                if value < 0:
                    worksheet.write(row_num, 6, value, formato_rojo)
                elif value > 0:
                    worksheet.write(row_num, 6, value, formato_verde)
                else:
                    worksheet.write(row_num, 6, value)

        ruta_export = os.path.join("static", "temp", "cruce_export.xlsx")
        with open(ruta_export, 'wb') as f:
            f.write(output.getvalue())

        session['resultado_cruce_path'] = ruta_export

        return render_template(
            'cruce.html',
            resumen=resumen,
            tabla_diferencias=tabla_diferencias,
            hay_faltantes_as400=hay_faltantes_as400,
            lista_solo_as400=lista_solo_as400,
            num_faltantes_as400=len(lista_solo_as400),
            archivo_listo=True  # Para activar botón de descarga
        )

    return render_template('cruce.html', mensaje=mensaje)


if __name__ == "__main__":
    # importar_productos_fijos()  # <--- COMENTADO: NO se ejecuta la importación al iniciar la app
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

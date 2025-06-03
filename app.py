from flask import Flask, render_template, request, redirect, url_for, send_file, make_response, session, flash
from functools import wraps
import sqlite3
import pandas as pd
from io import BytesIO
from xhtml2pdf import pisa
import io
import os

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
    return [
        {
            "codigo": p["codigo"],
            "descripcion": p["descripcion"],
            "cod_barras": p["cod_barras"]
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
        cod_barras = request.form['cod_barras']
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
                'INSERT INTO productos (codigo, descripcion, cod_barras) VALUES (?, ?, ?)',
                (codigo, descripcion, cod_barras)
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
        'codigo': 'COD. ARTICULO',
        'CODIGO': 'COD. ARTICULO',
        'cod_articulo': 'COD. ARTICULO',
        'cod_barras': 'COD.BARRAS',
        'CODBARRAS': 'COD.BARRAS',
        'COD.BARRAS': 'COD.BARRAS',
        'descripcion': 'DESCRIPCION',
        'DESCRIPCIÓN': 'DESCRIPCION',
        'stock_fisico': 'Cantidad Física',
        'STOCK_FISICO': 'Cantidad Física'
    })

    columnas_finales = ['id', 'tienda', 'COD. ARTICULO', 'DESCRIPCION', 'COD.BARRAS', 'Cantidad Física', 'fecha']

    # Sólo usa columnas que existen realmente en el df (puedes avisar si falta alguna)
    columnas_existentes = [col for col in columnas_finales if col in df.columns]
    df = df[columnas_existentes]

    # Si falta alguna columna, puedes avisar
    if len(columnas_existentes) < len(columnas_finales):
        faltan = set(columnas_finales) - set(columnas_existentes)
        print("FALTAN COLUMNAS en exportar_conteos_excel:", faltan)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="conteos_fisicos.xlsx", as_attachment=True)

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
    html = render_template('conteos_fisicos_pdf.html', conteos=conteos)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=conteos_fisicos.pdf"
        return response
    return "Error al generar PDF", 500

# ------------ Inventario físico por tienda, guay! ------------
import json

@app.route('/inventario_fisico', methods=['GET', 'POST'])
@login_requerido
def inventario_fisico():
    mensaje = ''
    conn = get_db_connection()
    productos_sql = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()

    # Convierte productos de SQL a dict para unirlos a la lista estática
    productos_db = productos_sql_a_dict(productos_sql)

    # Unir listas, pero que no se repita un código ya en la base de datos
    codigos_db = set(p["codigo"] for p in productos_db)
    productos_unidos = productos_db + [p for p in productos if p["codigo"] not in codigos_db]

    if request.method == 'POST':
        tienda = request.form['tienda']
        autor = request.form.get('autor', '').strip()  # <--- Recoge el nombre del autor (del input hidden del modal)
        productos_modificados = 0
        inventario_actual = []  # <--- Lista para guardar productos y cantidades de este inventario
        conn = get_db_connection()

        # Guarda cantidades de los productos en el listado normal
        for producto in productos_unidos:
            cantidad = request.form.get(f"stock_{producto['codigo']}")
            try:
                cantidad_num = int(cantidad)
            except Exception:
                cantidad_num = 0
            if cantidad_num > 0:
                conn.execute(
                    'INSERT INTO conteos_fisicos (tienda, codigo, descripcion, cod_barras, stock_fisico, fecha, autor) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)',
                    (tienda, producto['codigo'], producto['descripcion'], producto['cod_barras'], cantidad_num, autor)
                )
                productos_modificados += 1
                inventario_actual.append({
                    "codigo": producto['codigo'],
                    "descripcion": producto['descripcion'],
                    "cod_barras": producto['cod_barras'],
                    "cantidad": cantidad_num
                })

        # ---- Guarda el producto escrito a mano si lo hay ----
        manual_codigo = request.form.get("manual_codigo", "").strip()
        manual_descripcion = request.form.get("manual_descripcion", "").strip()
        manual_cod_barras = request.form.get("manual_cod_barras", "").strip()
        manual_cantidad = request.form.get("manual_cantidad", "").strip()

        if manual_codigo and manual_descripcion and manual_cantidad:
            try:
                cantidad_manual = int(manual_cantidad)
            except Exception:
                cantidad_manual = 0
            if cantidad_manual > 0:
                conn.execute(
                    'INSERT INTO conteos_fisicos (tienda, codigo, descripcion, cod_barras, stock_fisico, fecha, autor) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)',
                    (tienda, manual_codigo, manual_descripcion, manual_cod_barras, cantidad_manual, autor)
                )
                productos_modificados += 1
                inventario_actual.append({
                    "codigo": manual_codigo,
                    "descripcion": manual_descripcion,
                    "cod_barras": manual_cod_barras,
                    "cantidad": cantidad_manual
                })

        conn.commit()

        # ----------- GUARDADO DEL HISTÓRICO -----------
        if productos_modificados > 0 and autor:
            conn.execute(
                "INSERT INTO inventario_historico (autor, tienda, productos_json) VALUES (?, ?, ?)",
                (autor, tienda, json.dumps(inventario_actual, ensure_ascii=False))
            )
            conn.commit()
        # -----------------------------------------------

        conn.close()
        if productos_modificados > 0:
            mensaje = f"Se guardaron {productos_modificados} productos correctamente."
        else:
            mensaje = "No se guardó ningún producto (no se modificó cantidad)."
        # Vuelve a unir listas para mostrar después de POST
        productos_sql = get_db_connection().execute('SELECT * FROM productos').fetchall()
        productos_db = productos_sql_a_dict(productos_sql)
        codigos_db = set(p["codigo"] for p in productos_db)
        productos_unidos = productos_db + [p for p in productos if p["codigo"] not in codigos_db]
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

@app.route('/cruce_inventario', methods=['GET', 'POST'])
@login_requerido
def cruce_inventario():
    mensaje = ''
    resumen = None
    tabla_diferencias = None
    archivo_listo = False

    if request.method == 'POST':
        file_as400 = request.files.get('archivo_as400')
        file_casa = request.files.get('archivo_casa_ricardo')

        if not file_as400 or not file_casa:
            mensaje = "¡Debes subir ambos archivos!"
            return render_template('cruce.html', mensaje=mensaje)

        # Lee archivos Excel
        df_as400 = pd.read_excel(file_as400)
        df_casa = pd.read_excel(file_casa)

        # Renombrar columnas para coincidir
        df_casa = df_casa.rename(columns={
            'stock_fisico': 'Cantidad Física',
            'COD.ARTICULO': 'COD. ARTICULO',
            'COD.BARRAS': 'COD. BARRAS',
            'DESCRIPCION': 'DESCRIPCION'
        })
        df_as400 = df_as400.rename(columns={
            'EXISTENCIAS': 'Cantidad Física',
            'COD. ARTICULO': 'COD. ARTICULO',
            'COD. BARRAS': 'COD. BARRAS',
            'DESCRIPCION': 'DESCRIPCION'
        })

        # Forzar clave de cruce a string
        df_casa['DESCRIPCION'] = df_casa['DESCRIPCION'].astype(str)
        df_as400['DESCRIPCION'] = df_as400['DESCRIPCION'].astype(str)

        # Merge por DESCRIPCION
        df_merge = pd.merge(
            df_casa, df_as400,
            how='outer',
            on=['DESCRIPCION'],
            suffixes=('_CASA', '_AS400'),
            indicator=True
        )

        solo_casa = df_merge[df_merge['_merge'] == 'left_only']
        solo_as400 = df_merge[df_merge['_merge'] == 'right_only']
        en_ambos = df_merge[df_merge['_merge'] == 'both'].copy()
        en_ambos['DIFERENCIA'] = (en_ambos['Cantidad Física_CASA'].fillna(0) - en_ambos['Cantidad Física_AS400'].fillna(0))
        diferencias_stock = en_ambos[en_ambos['DIFERENCIA'] != 0]

        resumen = {
            'diferente_stock': int(len(diferencias_stock))
        }

        # --------- NUEVO: Productos solo en AS400 con existencias ---------
        solo_as400_con_stock = solo_as400[solo_as400['Cantidad Física_AS400'].fillna(0) > 0]

        if not solo_as400_con_stock.empty:
            lista_solo_as400 = solo_as400_con_stock[['DESCRIPCION', 'Cantidad Física_AS400']].head(30).to_dict(orient='records')
            hay_faltantes_as400 = True
            num_faltantes_as400 = len(solo_as400_con_stock)
        else:
            lista_solo_as400 = []
            hay_faltantes_as400 = False
            num_faltantes_as400 = 0
        # --------------------------------------------------------------

        # ...después de calcular diferencias_stock...
        if not diferencias_stock.empty:
            cols_tabla = ['tienda', 'DESCRIPCION', 'Cantidad Física_CASA', 'Cantidad Física_AS400', 'DIFERENCIA']
            cols_tabla = [col for col in cols_tabla if col in diferencias_stock.columns]
            tabla_diferencias = diferencias_stock[cols_tabla].head(50).to_dict(orient='records')
        else:
            tabla_diferencias = None



        # Exporta el resultado en memoria y guarda el archivo en disco
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            solo_casa.to_excel(writer, sheet_name='Solo en Casa', index=False)
            solo_as400.to_excel(writer, sheet_name='Solo en AS400', index=False)
            diferencias_stock.to_excel(writer, sheet_name='Diferencias Stock', index=False)
        output.seek(0)
        ruta_excel = os.path.join('static', 'temp', 'resultado_cruce.xlsx')
        os.makedirs(os.path.dirname(ruta_excel), exist_ok=True)
        with open(ruta_excel, 'wb') as f:
            f.write(output.read())
        session['resultado_cruce_path'] = ruta_excel
        archivo_listo = True

        return render_template(
            'cruce.html',
            mensaje=mensaje,
            resumen=resumen,
            archivo_listo=archivo_listo,
            tabla_diferencias=tabla_diferencias,
            hay_faltantes_as400=hay_faltantes_as400,
            num_faltantes_as400=num_faltantes_as400,
            lista_solo_as400=lista_solo_as400
        )

    # Si es GET (o si no subió archivos), render vacío:
    return render_template('cruce.html', mensaje=mensaje)

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

if __name__ == "__main__":
    # importar_productos_fijos()  # <--- COMENTADO: NO se ejecuta la importación al iniciar la app
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

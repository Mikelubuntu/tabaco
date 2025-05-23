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

# ------------ Lista de productos (aquí pon todos los productos a mostrar chaval NO TOCAR!) ------------
productos = [
  {
    "codigo":"Z010100000",
    "descripcion":"CAMEL FILTERS CARTON 10x20 Ud.",
    "cod_barras":8416500140962
  },
  {
    "codigo":"Z010100001",
    "descripcion":"CAMEL BLUE CARTON 10x20 Udes.",
    "cod_barras":8416500010784
  },
  {
    "codigo":"Z010100002",
    "descripcion":"CAMEL FILTERS SOFT 10x20 Udes.",
    "cod_barras":8416500800866
  },
  {
    "codigo":"Z010100003",
    "descripcion":"CAMEL ACTIVA DOBLE 20x10 Udes.",
    "cod_barras":8416500103325
  },
  {
    "codigo":"Z010100004",
    "descripcion":"CAMEL ACTIVA 10x20 Udes.",
    "cod_barras":8416500103257
  },
  {
    "codigo":"Z010100020",
    "descripcion":"CAMEL RYO LEGEND 10X30 Grms.",
    "cod_barras":8416500021797
  },
  {
    "codigo":"Z010200000",
    "descripcion":"WINSTON CLAS.BOX CT 10x20 Ude.",
    "cod_barras":8416500140948
  },
  {
    "codigo":"Z010200001",
    "descripcion":"WINSTON RED SOFT CT 10x20 Udes",
    "cod_barras":8416500100300
  },
  {
    "codigo":"Z010200002",
    "descripcion":"WINSTON RED 100s.CARTON 10X20U",
    "cod_barras":8416500100621
  },
  {
    "codigo":"Z010200003",
    "descripcion":"WINSTON RED CARTON 10x20 Udes.",
    "cod_barras":8416500100294
  },
  {
    "codigo":"Z010200004",
    "descripcion":"WINSTON BLUE CARTON 10x20 Udes",
    "cod_barras":8416500101321
  },
  {
    "codigo":"Z010200005",
    "descripcion":"+WINSTON XS PLUS GOLD 10x20 Ud",
    "cod_barras":8416500103264
  },
  {
    "codigo":"Z010200006",
    "descripcion":"WINSTON COMPACT BLUE 10x20 Ud.",
    "cod_barras":8416500104643
  },
  {
    "codigo":"Z010300000",
    "descripcion":"+CORONAS BY BENSON ROJO 10x21U",
    "cod_barras":8416500102236
  },
  {
    "codigo":"Z010400000",
    "descripcion":"CORONAS NEGRO CLAS.10x20 Udes.",
    "cod_barras":8416600100118
  },
  {
    "codigo":"Z010400001",
    "descripcion":"CORONAS NEGRO ORO  10x20 Udes.",
    "cod_barras":8416600100170
  },
  {
    "codigo":"Z010400002",
    "descripcion":"KRUGER  CARTON 10x20 Udes.",
    "cod_barras":8416600100583
  },
  {
    "codigo":"Z010500001",
    "descripcion":"BENSON LONDON RED  8x24 Udes.",
    "cod_barras":8416500102700
  },
  {
    "codigo":"Z010500002",
    "descripcion":"BENSON LONDON RED 100s 10x20Ud",
    "cod_barras":8416500101932
  },
  {
    "codigo":"Z010500003",
    "descripcion":"BENSON LONDON BLUE 10x20 Udes.",
    "cod_barras":9008100288763
  },
  {
    "codigo":"Z010500004",
    "descripcion":"BENSON LONDON OPTION 10x20 Ud.",
    "cod_barras":8416500103301
  },
  {
    "codigo":"Z010500006",
    "descripcion":"BENSON GOLD 10x20 Ud.",
    "cod_barras":5010175655016
  },
  {
    "codigo":"Z010600000",
    "descripcion":"SILK CUT WHITE 10x20 Ud.",
    "cod_barras":5010175500217
  },
  {
    "codigo":"Z010600001",
    "descripcion":"SILK CUT PURPLE 10x20 Ud.",
    "cod_barras":5010175500002
  },
  {
    "codigo":"Z010900000",
    "descripcion":"MAYFAIR KS 10x20 Ud.",
    "cod_barras":5010175539439
  },
  {
    "codigo":"Z010900001",
    "descripcion":"MAYFAIR SKY BLUE 10x20 Ud.",
    "cod_barras":5010175539446
  },
  {
    "codigo":"Z010900020",
    "descripcion":"STERLING KS 10x20 Ud.",
    "cod_barras":5010175808603
  },
  {
    "codigo":"Z010900021",
    "descripcion":"STERLING DUAL 10x20 Ud.",
    "cod_barras":8416500103318
  },
  {
    "codigo":"Z010900030",
    "descripcion":"STERLING RYO 10X50g.",
    "cod_barras":8416500004820
  },
  {
    "codigo":"Z013100005",
    "descripcion":"AMBER LEAF 5x50Grs",
    "cod_barras":5010175578889
  },
  {
    "codigo":"Z015000050",
    "descripcion":"DIP.PLOOM DEVICE AVANCE NAVY B",
    "cod_barras":8416500020714
  },
  {
    "codigo":"Z015000051",
    "descripcion":"DIP.PLOOM DEVICE AVANCE SILVER",
    "cod_barras":8416500005148
  },
  {
    "codigo":"Z015000052",
    "descripcion":"DIP.PLOOM DEVICE AVANCE BLACK",
    "cod_barras":8416500005131
  },
  {
    "codigo":"Z015000053",
    "descripcion":"DIP.PLOOM DEVICE AVANCE CHAMP.",
    "cod_barras":8416500005155
  },
  {
    "codigo":"Z015000054",
    "descripcion":"DIP.PLOOM DEVICE ADVANCED RED",
    "cod_barras":5600868341854
  },
  {
    "codigo":"Z015000055",
    "descripcion":"DIP.PLOOM DEVICE ADV.ROSE SHIM",
    "cod_barras":5600868341724
  },
  {
    "codigo":"Z020100001",
    "descripcion":"FORTUNA RED LINE CT 10x20 Udes",
    "cod_barras":8416000501355
  },
  {
    "codigo":"Z020100002",
    "descripcion":"FORTUNA BLUE LINE CT 10x20 Ud.",
    "cod_barras":8416000501447
  },
  {
    "codigo":"Z020100003",
    "descripcion":"FORTUNA RED LINE XL  10x20 Ud.",
    "cod_barras":8416000501539
  },
  {
    "codigo":"Z020100004",
    "descripcion":"FORTUNA 24 CARTON 8x24 Udes",
    "cod_barras":8416000501782
  },
  {
    "codigo":"Z020100005",
    "descripcion":"FORTUNA 29 CARTON   8x29 Udes",
    "cod_barras":4030600223208
  },
  {
    "codigo":"Z020100006",
    "descripcion":"+FORTUNA FRESH 10x20 Udes",
    "cod_barras":4030600250846
  },
  {
    "codigo":"Z020200003",
    "descripcion":"NEW RED 24 CARTON  8x24 Udes",
    "cod_barras":3258171940770
  },
  {
    "codigo":"Z020200004",
    "descripcion":"NEW RED 29 CARTON  8x29 Udes",
    "cod_barras":4030600222997
  },
  {
    "codigo":"Z020200005",
    "descripcion":"NEW & CO ROUGE CARTON 10x20Ud.",
    "cod_barras":4030600194614
  },
  {
    "codigo":"Z020200006",
    "descripcion":"NEW DUO AIR CARTON 10x20 Udes",
    "cod_barras":4030600242643
  },
  {
    "codigo":"Z020200007",
    "descripcion":"NEW RED 100  10X20 UND",
    "cod_barras":4030600170830
  },
  {
    "codigo":"Z020400001",
    "descripcion":"PARAMOUNT RED CARTON 10x20 U.",
    "cod_barras":4030600252512
  },
  {
    "codigo":"Z020400002",
    "descripcion":"PARAMOUNT RED CARTON 8x25 U.",
    "cod_barras":4030600260722
  },
  {
    "codigo":"Z023100001",
    "descripcion":"PICADURA HORIZON 5x30Grs.",
    "cod_barras":8710900002012
  },
  {
    "codigo":"Z023100002",
    "descripcion":"PICADURA ORIGENES 10x30Grs.",
    "cod_barras":8710900082953
  },
  {
    "codigo":"Z023100003",
    "descripcion":"PICADURA GOLDEN VIRGINIA 10x30",
    "cod_barras":8710900030008
  },
  {
    "codigo":"Z023100004",
    "descripcion":"PICADURA HORIZON BLUE 5x30Grs.",
    "cod_barras":4030700124795
  },
  {
    "codigo":"Z023100005",
    "descripcion":"PICAD.HORIZON VIRG.GREEN 5x30g",
    "cod_barras":4030700124764
  },
  {
    "codigo":"Z025000001",
    "descripcion":"+VAPEADOR MYBLU DISP.BLUE Edit",
    "cod_barras":8719964004123
  },
  {
    "codigo":"Z025000002",
    "descripcion":"+VAPEADOR MYBLU DISP.GOLD Edit",
    "cod_barras":8719964004338
  },
  {
    "codigo":"Z025000003",
    "descripcion":"+VAPEADOR MYBLU DISP.PURPLE Ed",
    "cod_barras":8719964004260
  },
  {
    "codigo":"Z025000004",
    "descripcion":"+VAPEADOR MYBLU DISP.RED Edit.",
    "cod_barras":8719964003911
  },
  {
    "codigo":"Z025000010",
    "descripcion":"BLU DRY KIT 2.0 VAPED.BLACK1X5",
    "cod_barras":8719964031112
  },
  {
    "codigo":"Z025000011",
    "descripcion":"BLU DRY KIT 2.0 VAPED.BLUEK1X5",
    "cod_barras":8719964044631
  },
  {
    "codigo":"Z025000100",
    "descripcion":"+MYBLU Sabor BlueIce Caps.0,0%",
    "cod_barras":8719964024244
  },
  {
    "codigo":"Z025000101",
    "descripcion":"+MYBLU Sabor BlueIce Caps.0,8%",
    "cod_barras":8719874065801
  },
  {
    "codigo":"Z025000120",
    "descripcion":"+MYBLU Sabor Blueberry Cap1,6%",
    "cod_barras":8719964024992
  },
  {
    "codigo":"Z025000122",
    "descripcion":"+MYBLU Sabor Cereza Capsul0,8%",
    "cod_barras":8719874065740
  },
  {
    "codigo":"Z025000126",
    "descripcion":"+MYBLU Sabor Green Apple C0,0%",
    "cod_barras":8719874065702
  },
  {
    "codigo":"Z025000127",
    "descripcion":"+MYBLU Sabor Green AppleC.0,8%",
    "cod_barras":8719874065719
  },
  {
    "codigo":"Z025000130",
    "descripcion":"+MYBLU Sabor Menthol Capsl0,0%",
    "cod_barras":8719964024183
  },
  {
    "codigo":"Z025000131",
    "descripcion":"+MYBLU Sabor Menthol Caps.0,8%",
    "cod_barras":8719874065658
  },
  {
    "codigo":"Z025000132",
    "descripcion":"+MYBLU Sabor Menthol Capsl1,6%",
    "cod_barras":8719874068383
  },
  {
    "codigo":"Z025000140",
    "descripcion":"+MYBLU Sabor Straw\/Mint Cp1,6%",
    "cod_barras":8719874068376
  },
  {
    "codigo":"Z025000143",
    "descripcion":"+MYBLU TABAC.CLAS.Capsula 1,6%",
    "cod_barras":8719874068345
  },
  {
    "codigo":"Z025000144",
    "descripcion":"+MYBLU Sabor Tobac Capsu 0,8%",
    "cod_barras":8719874395632
  },
  {
    "codigo":"Z025000145",
    "descripcion":"BLU POD 2.0 FRESH MINT 0MG 1X5",
    "cod_barras":8719964031532
  },
  {
    "codigo":"Z025000146",
    "descripcion":"BLU POD 2.0 TABACCO 0MG 1X5",
    "cod_barras":8719964031501
  },
  {
    "codigo":"Z025000147",
    "descripcion":"BLU POD 2.0 BLUE ICE 9MG 1X5",
    "cod_barras":8719964031327
  },
  {
    "codigo":"Z025000148",
    "descripcion":"BLU POD 2.0 TABACCO 18MG 1X5",
    "cod_barras":8719964031174
  },
  {
    "codigo":"Z025000149",
    "descripcion":"BLU POD 2.0 BLUE ICE 18MG 1X5",
    "cod_barras":8719964031358
  },
  {
    "codigo":"Z025000150",
    "descripcion":"BLU POD 2.0 TABACCO 9MG 1X5",
    "cod_barras":8719964031143
  },
  {
    "codigo":"Z025000151",
    "descripcion":"BLU POD2.0 FRESH MANGO 18MG1X5",
    "cod_barras":8719964031471
  },
  {
    "codigo":"Z025000152",
    "descripcion":"BLU POD 2.0 POLAR MENT 9MG 1X5",
    "cod_barras":8719964031204
  },
  {
    "codigo":"Z025000153",
    "descripcion":"BLU POD2.0 GREEN APPLE 18MG1X5",
    "cod_barras":8719964034878
  },
  {
    "codigo":"Z025000154",
    "descripcion":"BLU POD2.0 STRAWB&MINT 9MG 1X5",
    "cod_barras":8719964034908
  },
  {
    "codigo":"Z025000155",
    "descripcion":"BLU POD 2.0 UVA ICE 9MG 1X5",
    "cod_barras":8719964044990
  },
  {
    "codigo":"Z025000170",
    "descripcion":"BLU BAR MANG.20MG 1000PUF 1X10",
    "cod_barras":8719964052889
  },
  {
    "codigo":"Z025000171",
    "descripcion":"BLU BAR MANZAN.20MG 1000P.1X10",
    "cod_barras":8719964052407
  },
  {
    "codigo":"Z025000172",
    "descripcion":"BLU BAR ARD-CZ.20MG 1000P.1X10",
    "cod_barras":8719964052674
  },
  {
    "codigo":"Z025000173",
    "descripcion":"BLU BAR TROP.M.20MG 1000P.1X10",
    "cod_barras":8719964052582
  },
  {
    "codigo":"Z025000174",
    "descripcion":"BLU BAR BLUE I.20MG 1000P.1X10",
    "cod_barras":8719964052285
  },
  {
    "codigo":"Z025000175",
    "descripcion":"BLU BAR F.BOSQ.20MG 1000P.1X10",
    "cod_barras":8719964052919
  },
  {
    "codigo":"Z025000176",
    "descripcion":"BLU BAR KIWI P.20MG 1000P.1X10",
    "cod_barras":8719964052810
  },
  {
    "codigo":"Z025000190",
    "descripcion":"BLU BOX 1.0 WATERM.20mg 800p10",
    "cod_barras":8719964056955
  },
  {
    "codigo":"Z025000191",
    "descripcion":"BLU BOX 1.0 STAWBE.20mg 800p10",
    "cod_barras":8719964056986
  },
  {
    "codigo":"Z025000192",
    "descripcion":"BLU BOX 1.0 F.ROJOS20mg 800p10",
    "cod_barras":8719964057044
  },
  {
    "codigo":"Z025000193",
    "descripcion":"BLU BOX 1.0 BLUE 20mg 800p10",
    "cod_barras":8719964057013
  },
  {
    "codigo":"Z025000194",
    "descripcion":"BLU BOX 1.0 PINEAP.20mg 800p10",
    "cod_barras":8719964056894
  },
  {
    "codigo":"Z030100004",
    "descripcion":"+MARLBORO SILVER  CT 10x20 Ud.",
    "cod_barras":8437012200630
  },
  {
    "codigo":"Z030100007",
    "descripcion":"MARLBORO POCKET PACK 10x20 Uds",
    "cod_barras":8437008795157
  },
  {
    "codigo":"Z030100008",
    "descripcion":"+MARLBORO MIX  CT 10x20 Ud.",
    "cod_barras":8436555610067
  },
  {
    "codigo":"Z030100009",
    "descripcion":"+MARLBORO TOUCH  CT 10x20 Ud.",
    "cod_barras":8436555614676
  },
  {
    "codigo":"Z030100010",
    "descripcion":"MARLBORO CRAFTED  CT 10x20 Ud.",
    "cod_barras":8436555618186
  },
  {
    "codigo":"Z030100011",
    "descripcion":"+MARLBORO 25 CT 8X25Ud.",
    "cod_barras":8436555619435
  },
  {
    "codigo":"Z030100012",
    "descripcion":"+MARLBORO RED BOX 21 10X21",
    "cod_barras":8436609722012
  },
  {
    "codigo":"Z030100013",
    "descripcion":"MARLBORO BOX 24   8X24",
    "cod_barras":8436609722111
  },
  {
    "codigo":"Z030200000",
    "descripcion":"L&M RED 8x24 Ud.",
    "cod_barras":8436555618780
  },
  {
    "codigo":"Z030200001",
    "descripcion":"L&M RED CARTON 10x20 Ud.",
    "cod_barras":8437008795775
  },
  {
    "codigo":"Z030200002",
    "descripcion":"L&M BLUE CARTON 10x20 Ud.",
    "cod_barras":8437012200470
  },
  {
    "codigo":"Z030200003",
    "descripcion":"+L&M FORWARD CARTON 10x20 Ud.",
    "cod_barras":8436555610814
  },
  {
    "codigo":"Z030200004",
    "descripcion":"L&M POCKET RED CARTON 10x20 Ud",
    "cod_barras":8437008795829
  },
  {
    "codigo":"Z030200005",
    "descripcion":"L&M POCKET BLUE CARTON 10x20U.",
    "cod_barras":8437008795843
  },
  {
    "codigo":"Z030200006",
    "descripcion":"L&M FIRST CUT CARTON 10x20 Ud.",
    "cod_barras":8436555617172
  },
  {
    "codigo":"Z030300002",
    "descripcion":"CHESTERFIELD RED KS  8x24 Ud.",
    "cod_barras":8436555614553
  },
  {
    "codigo":"Z030300010",
    "descripcion":"CHESTER.CIGARRITOS REMIX 10X17",
    "cod_barras":8436609722494
  },
  {
    "codigo":"Z030400003",
    "descripcion":"+PHILIP MORRIS DARK B.10x20 Ud",
    "cod_barras":8436555611552
  },
  {
    "codigo":"Z030400004",
    "descripcion":"PHILIP MORRIS RED KS  8x24 Ud.",
    "cod_barras":8436555611187
  },
  {
    "codigo":"Z031000001",
    "descripcion":"+HEETS IQOS RUSSET 1x10 Ud.",
    "cod_barras":8436555615383
  },
  {
    "codigo":"Z031000002",
    "descripcion":"+HEETS IQOS AMBER 1x10 Ud.",
    "cod_barras":8436555610890
  },
  {
    "codigo":"Z031000003",
    "descripcion":"+HEETS IQOS YELLOW 1x10 Ud.",
    "cod_barras":8436555610913
  },
  {
    "codigo":"Z031000004",
    "descripcion":"+HEETS IQOS BLUE 1x10 Ud.",
    "cod_barras":8436555614126
  },
  {
    "codigo":"Z031000005",
    "descripcion":"+HEETS IQOS TURQUOISE 1x10 Ud.",
    "cod_barras":8436555610937
  },
  {
    "codigo":"Z031000006",
    "descripcion":"+HEETS IQOS SIENNA 1x10 Ud.",
    "cod_barras":8436555613099
  },
  {
    "codigo":"Z031000007",
    "descripcion":"+HEETS IQOS BRONZE 1x10 Ud.",
    "cod_barras":8436555613150
  },
  {
    "codigo":"Z031000008",
    "descripcion":"+HEETS IQOS SIENNA CAPS 1x10Ud",
    "cod_barras":8436555615000
  },
  {
    "codigo":"Z031000009",
    "descripcion":"+HEETS IQOS GREEN 1x10 Ud.",
    "cod_barras":8436555614935
  },
  {
    "codigo":"Z031000010",
    "descripcion":"+HEETS IQOS TEAK 1x10 Ud.",
    "cod_barras":8436555615406
  },
  {
    "codigo":"Z031000011",
    "descripcion":"+HEETS IQOS MAUVE 1x10 Ud.",
    "cod_barras":8436555618001
  },
  {
    "codigo":"Z031000100",
    "descripcion":"HEETS IQOS TRIPACK",
    "cod_barras":8436555615628
  },
  {
    "codigo":"Z031000200",
    "descripcion":"TEREA IQOS AMBER 1x10 Ud.",
    "cod_barras":8436555616595
  },
  {
    "codigo":"Z031000201",
    "descripcion":"TEREA IQOS YELLOW 1x10 Ud.",
    "cod_barras":8436555617073
  },
  {
    "codigo":"Z031000202",
    "descripcion":"TEREA IQOS TURQUOISE 1x10 Ud.",
    "cod_barras":8436555617059
  },
  {
    "codigo":"Z031000203",
    "descripcion":"TEREA IQOS SIENNA 1x10 Ud.",
    "cod_barras":8436555617097
  },
  {
    "codigo":"Z031000204",
    "descripcion":"+TEREA IQOS BLUE 1x10 Ud.",
    "cod_barras":8436555617035
  },
  {
    "codigo":"Z031000205",
    "descripcion":"+TEREA IQOS MAUVE 1x10 Ud.",
    "cod_barras":8436555618018
  },
  {
    "codigo":"Z031000206",
    "descripcion":"TEREA IQOS RUSSET 1x10 Ud.",
    "cod_barras":8436555617158
  },
  {
    "codigo":"Z031000207",
    "descripcion":"TEREA IQOS TEAK 1x10 Ud.",
    "cod_barras":8436555617134
  },
  {
    "codigo":"Z031000208",
    "descripcion":"TEREA IQOS WARM FUSE 1x10 Ud.",
    "cod_barras":8436609721572
  },
  {
    "codigo":"Z031000209",
    "descripcion":"TEREA IQOS SOFT FUSE 1x10 Ud.",
    "cod_barras":8436555619053
  },
  {
    "codigo":"Z031000260",
    "descripcion":"TEREA IQOS TRIPACK",
    "cod_barras":8436555618834
  },
  {
    "codigo":"Z031000300",
    "descripcion":"+FIIT ROXO MNT  1x10 Ud.",
    "cod_barras":8436555618353
  },
  {
    "codigo":"Z031000301",
    "descripcion":"+FIIT REGULAR   1x10 Ud.",
    "cod_barras":8436555616212
  },
  {
    "codigo":"Z031000302",
    "descripcion":"+FIIT MARINE MNT 1x10 Ud.",
    "cod_barras":8436555616236
  },
  {
    "codigo":"Z031000303",
    "descripcion":"+FIIT REGULAR DEEP 1x10 Ud.",
    "cod_barras":8436555618339
  },
  {
    "codigo":"Z031000304",
    "descripcion":"FIIT REGULAR SKY 1x10 Ud.",
    "cod_barras":8436555618865
  },
  {
    "codigo":"Z032000001",
    "descripcion":"DANNEMANN MOODS S\/FILTRO 5X20u",
    "cod_barras":8414912510205
  },
  {
    "codigo":"Z032000003",
    "descripcion":"DANNEMANN MOODS C\/FILT.10x20Ud",
    "cod_barras":8414912522000
  },
  {
    "codigo":"Z033000001",
    "descripcion":"DON JULIAN Nº1 5x5Uds",
    "cod_barras":8414912310058
  },
  {
    "codigo":"Z033000002",
    "descripcion":"DON JULIAN Nº5 5x5Uds",
    "cod_barras":8414912340055
  },
  {
    "codigo":"Z035000001",
    "descripcion":"+IQOS 2.4+Navy",
    "cod_barras":8436555611668
  },
  {
    "codigo":"Z035000002",
    "descripcion":"+IQOS 2.4+White",
    "cod_barras":8436555611651
  },
  {
    "codigo":"Z035000003",
    "descripcion":"+IQOS MULTI Dorado",
    "cod_barras":8436555613587
  },
  {
    "codigo":"Z035000004",
    "descripcion":"+IQOS 3 Duo Azul",
    "cod_barras":8436555614454
  },
  {
    "codigo":"Z035000020",
    "descripcion":"IQOS Iluma AZURE BLUE",
    "cod_barras":8436555617813
  },
  {
    "codigo":"Z035000021",
    "descripcion":"IQOS Iluma MOSS GREEN",
    "cod_barras":8436555617653
  },
  {
    "codigo":"Z035000022",
    "descripcion":"IQOS Iluma SUNSET RED",
    "cod_barras":8436555617714
  },
  {
    "codigo":"Z035000023",
    "descripcion":"IQOS Iluma PEBBLE GREY",
    "cod_barras":8436555617677
  },
  {
    "codigo":"Z035000024",
    "descripcion":"IQOS Iluma PEBBLE BEIG",
    "cod_barras":8436555617790
  },
  {
    "codigo":"Z035000025",
    "descripcion":"IQOS Iluma ONE AZURE BLUE",
    "cod_barras":8436555617271
  },
  {
    "codigo":"Z035000026",
    "descripcion":"IQOS Iluma ONE MOSS GREEN",
    "cod_barras":7622100597193
  },
  {
    "codigo":"Z035000027",
    "descripcion":"IQOS Iluma ONE PEBBLE BEIGE",
    "cod_barras":8436555617257
  },
  {
    "codigo":"Z035000028",
    "descripcion":"IQOS Iluma ONE PEBBLE GREY",
    "cod_barras":8436555617219
  },
  {
    "codigo":"Z035000029",
    "descripcion":"IQOS Iluma ONE SUNSET RED",
    "cod_barras":8436555617196
  },
  {
    "codigo":"Z035000100",
    "descripcion":"+LIL SOLID 2,0 COSMIC BLUE",
    "cod_barras":8436555616434
  },
  {
    "codigo":"Z035000101",
    "descripcion":"+LIL SOLID 2,0 STONE GREY",
    "cod_barras":8436555616373
  },
  {
    "codigo":"Z040100001",
    "descripcion":"MECANICO ESP.VERDE 10x20 Udes",
    "cod_barras":8421572000021
  },
  {
    "codigo":"Z040100002",
    "descripcion":"MECANICO EXTRAF.AZUL 10x20 Ud.",
    "cod_barras":8421572000076
  },
  {
    "codigo":"Z040300001",
    "descripcion":"CLEVER CARTON 10x20 Udes",
    "cod_barras":8421572100110
  },
  {
    "codigo":"Z040300050",
    "descripcion":"ELIXYR RED 10X20",
    "cod_barras":5450524053436
  },
  {
    "codigo":"Z040300051",
    "descripcion":"ELIXYR PLUS 10X20",
    "cod_barras":5400827017420
  },
  {
    "codigo":"Z040500002",
    "descripcion":"ROTHMANS LON.BLUE SMOOTH 10x20",
    "cod_barras":8421881205407
  },
  {
    "codigo":"Z040500003",
    "descripcion":"+ROTHMANS SURROUND 10x20",
    "cod_barras":8421881003775
  },
  {
    "codigo":"Z040500004",
    "descripcion":"ROTHMANS ESSENCE 10x20",
    "cod_barras":5000219010635
  },
  {
    "codigo":"Z040500005",
    "descripcion":"ROTHMANS LONDON RED 24 8X24",
    "cod_barras":8421881006745
  },
  {
    "codigo":"Z040500006",
    "descripcion":"ROTHMANS LONDON RED 100S 10X20",
    "cod_barras":8421881017420
  },
  {
    "codigo":"Z040500050",
    "descripcion":"PALL MALL NEW ORLE.RED 10X20Un",
    "cod_barras":4031300009482
  },
  {
    "codigo":"Z040500051",
    "descripcion":"PALL MALL S.FRANC.BLUE 10X20Un",
    "cod_barras":4031800001122
  },
  {
    "codigo":"Z040600001",
    "descripcion":"DUNHILL INTERNATIONAL  10x20",
    "cod_barras":8721700917512
  },
  {
    "codigo":"Z040700002",
    "descripcion":"LUCKY STRIKE S\/ADITIVOS 10x20U",
    "cod_barras":4031300095171
  },
  {
    "codigo":"Z040700003",
    "descripcion":"LUCKY STRIKE ECLIPSE 10x20U",
    "cod_barras":8421881001658
  },
  {
    "codigo":"Z040700004",
    "descripcion":"LUCKY STRIKE TWIST 10x20U",
    "cod_barras":8421881003782
  },
  {
    "codigo":"Z040700005",
    "descripcion":"LUCKY STRIKE SILVER BAY 10X20U",
    "cod_barras":5000219046580
  },
  {
    "codigo":"Z040700010",
    "descripcion":"LUCKY STRIKE S\/ADITIVO 24 8X24",
    "cod_barras":8421881006332
  },
  {
    "codigo":"Z040800001",
    "descripcion":"VOGUE BLUE 10x20 Udes.",
    "cod_barras":5000219021891
  },
  {
    "codigo":"Z040800020",
    "descripcion":"JPS RED CARTON 10X20 Und.",
    "cod_barras":8421881017406
  },
  {
    "codigo":"Z040800025",
    "descripcion":"JPS BLUE CARTON 10X20 Und.",
    "cod_barras":5998900427131
  },
  {
    "codigo":"Z040890001",
    "descripcion":"+NEO FRESCO MENTHOL 10X20 Und.",
    "cod_barras":8421881008398
  },
  {
    "codigo":"Z040890002",
    "descripcion":"NEO CLASIC TABACCO 10X20 Und.",
    "cod_barras":8421881008305
  },
  {
    "codigo":"Z040890003",
    "descripcion":"+NEO FRUTOS ROJOS 10X20 Und.",
    "cod_barras":8421881008459
  },
  {
    "codigo":"Z040890004",
    "descripcion":"NEO GOLDEN TABACCO 10X20 Und.",
    "cod_barras":8421881002396
  },
  {
    "codigo":"Z040890005",
    "descripcion":"NEO TERRACOTA 10X20 Und.",
    "cod_barras":8421881008336
  },
  {
    "codigo":"Z040890006",
    "descripcion":"+NEO BERYL CLICK 10X20 Und.",
    "cod_barras":8421881014641
  },
  {
    "codigo":"Z040890007",
    "descripcion":"+NEO BLUE CLICK 10X20 Und.",
    "cod_barras":8421881008367
  },
  {
    "codigo":"Z040890030",
    "descripcion":"VEO PURPLE CLICK 1X20 Und.",
    "cod_barras":8421881016997
  },
  {
    "codigo":"Z040890031",
    "descripcion":"VEO SCARLET CLICK 1X20 Und.",
    "cod_barras":8421881016973
  },
  {
    "codigo":"Z040890032",
    "descripcion":"VEO GREEN CLICK 1X20 Und.",
    "cod_barras":8421881016881
  },
  {
    "codigo":"Z040890033",
    "descripcion":"VEO ARCTIC CLICK 1X20 Und.",
    "cod_barras":8421881016911
  },
  {
    "codigo":"Z040890035",
    "descripcion":"VEO TROPICAL TWIST 10X20Und.",
    "cod_barras":8421881030504
  },
  {
    "codigo":"Z040900001",
    "descripcion":"+VUSE GO BER.WATEMR.0%NIC.1X10",
    "cod_barras":8421882007185
  },
  {
    "codigo":"Z040900002",
    "descripcion":"+VUSE GO BLUEBERRY 0%NIC.1X10",
    "cod_barras":8421881006967
  },
  {
    "codigo":"Z040900003",
    "descripcion":"+VUSE GO PEPPER.ICE O%NIC.1X10",
    "cod_barras":8421882007215
  },
  {
    "codigo":"Z040900010",
    "descripcion":"+VUSE GO BERRY ICE 500 1X10",
    "cod_barras":8421881006424
  },
  {
    "codigo":"Z040900011",
    "descripcion":"+VUSE GO BLUEBERR.ICE 500 1X10",
    "cod_barras":8421882007062
  },
  {
    "codigo":"Z040900012",
    "descripcion":"+VUSE GO CREAMI TOBAC.500 1X10",
    "cod_barras":8421881006394
  },
  {
    "codigo":"Z040900013",
    "descripcion":"+VUSE GO GRAPE ICE 500 1X10",
    "cod_barras":8421882007093
  },
  {
    "codigo":"Z040900014",
    "descripcion":"+VUSE GO MANGO ICE 500 1X10",
    "cod_barras":8421881006516
  },
  {
    "codigo":"Z040900015",
    "descripcion":"+VUSE GO PEPPERMI,ICE 500 1X10",
    "cod_barras":8421881006486
  },
  {
    "codigo":"Z040900016",
    "descripcion":"+VUSE GO STRAWBER.ICE 500 1X10",
    "cod_barras":8421881006578
  },
  {
    "codigo":"Z040900017",
    "descripcion":"+VUSE GO WATERMEL.ICE 500 1X10",
    "cod_barras":8421881006639
  },
  {
    "codigo":"Z040900018",
    "descripcion":"+VUSE GO BERRY\/WATER.ICE 1X10",
    "cod_barras":8421882007031
  },
  {
    "codigo":"Z040900020",
    "descripcion":"+VUSE GO BERRY\/WATER.700p.1x10",
    "cod_barras":8421881017666
  },
  {
    "codigo":"Z040900021",
    "descripcion":"+VUSE GO BLUEBER.ICE 700p.1x10",
    "cod_barras":8421881017697
  },
  {
    "codigo":"Z040900022",
    "descripcion":"+VUSE GO WATERML.ICE 700p.1x10",
    "cod_barras":8421881017819
  },
  {
    "codigo":"Z040900023",
    "descripcion":"+VUSE GO BANANA ICE 700pf.1x10",
    "cod_barras":8421881017901
  },
  {
    "codigo":"Z040900024",
    "descripcion":"+VUSE GO CREAMY PEACH700p.1x10",
    "cod_barras":8421881018021
  },
  {
    "codigo":"Z040900025",
    "descripcion":"+VUSE GO TROP.COCONUT700p.1x10",
    "cod_barras":8421881018113
  },
  {
    "codigo":"Z040900026",
    "descripcion":"+VUSE GO DARK CHERRY 700p.1x10",
    "cod_barras":8421881018236
  },
  {
    "codigo":"Z040900027",
    "descripcion":"+VUSE GO APPLE SOUR 700p.1x10",
    "cod_barras":8421881018052
  },
  {
    "codigo":"Z040900028",
    "descripcion":"+VUSE GO BER.WATERM 0%700p1x10",
    "cod_barras":8421881019233
  },
  {
    "codigo":"Z040900029",
    "descripcion":"+VUSE GO BLUEBERRY 0% 700f1x10",
    "cod_barras":8421881019264
  },
  {
    "codigo":"Z040900030",
    "descripcion":"+VUSE GO STRAWB.KIWI 700pf1x10",
    "cod_barras":8421881018007
  },
  {
    "codigo":"Z040900100",
    "descripcion":"+VUSE GO BLUE RASPERY 800p1x10",
    "cod_barras":8421881015525
  },
  {
    "codigo":"Z040900101",
    "descripcion":"+VUSE GO BERRY BLEND 800pf1x10",
    "cod_barras":8421881015617
  },
  {
    "codigo":"Z040900102",
    "descripcion":"+VUSE GO PEPPERMINT 800pf 1x10",
    "cod_barras":8421881015730
  },
  {
    "codigo":"Z040900103",
    "descripcion":"+VUSE GO STRAMB.KIWI 800pf1x10",
    "cod_barras":8421881015495
  },
  {
    "codigo":"Z040900105",
    "descripcion":"DISP.VUSE GO RELOAD 1000 B.WAR",
    "cod_barras":8421881026248
  },
  {
    "codigo":"Z040900106",
    "descripcion":"DISP.VUSE GO RELOAD 1000 BLUBR",
    "cod_barras":8421881026309
  },
  {
    "codigo":"Z040900107",
    "descripcion":"DISP.VUSE GO RELOAD 1000 STRAB",
    "cod_barras":8421881026279
  },
  {
    "codigo":"Z040900108",
    "descripcion":"DISP.VUSE GO RELOAD1000 PEPPER",
    "cod_barras":8421881030382
  },
  {
    "codigo":"Z040900115",
    "descripcion":"VUSE POD WATERMELON ICE 1UND.",
    "cod_barras":8421881026484
  },
  {
    "codigo":"Z040900116",
    "descripcion":"VUSE POD STRAWBERRY ICE 1UND.",
    "cod_barras":8421881026514
  },
  {
    "codigo":"Z040900117",
    "descripcion":"VUSE POD PEPPERMINT ICE 1UND.",
    "cod_barras":8421881026576
  },
  {
    "codigo":"Z040900118",
    "descripcion":"VUSE POD BLUEBERRY ICE 1UND.",
    "cod_barras":8421881026606
  },
  {
    "codigo":"Z040900119",
    "descripcion":"VUSE POD BERRY WATERMELON 1UND",
    "cod_barras":8421881026637
  },
  {
    "codigo":"Z040900120",
    "descripcion":"VUSE POD STRAWBERRY KIWI 1UND",
    "cod_barras":8421881026880
  },
  {
    "codigo":"Z040900121",
    "descripcion":"VUSE POD MANGO ICE 1UND",
    "cod_barras":8421881026545
  },
  {
    "codigo":"Z040900150",
    "descripcion":"VUSE GO PEN 1000 BERYWATERM.20",
    "cod_barras":8421881029355
  },
  {
    "codigo":"Z040900151",
    "descripcion":"VUSE GO PEN 1000 STRAWBERRY.20",
    "cod_barras":8421881029263
  },
  {
    "codigo":"Z040900152",
    "descripcion":"VUSE GO PEN 1000 WATERMELON.20",
    "cod_barras":8421881029294
  },
  {
    "codigo":"Z040900153",
    "descripcion":"VUSE GO PEN 1000 STRBRRYKIW.20",
    "cod_barras":8421881029539
  },
  {
    "codigo":"Z040900154",
    "descripcion":"VUSE GO PEN 1000 APLE SOUR.20",
    "cod_barras":8421881029591
  },
  {
    "codigo":"Z040900155",
    "descripcion":"VUSE GO PEN 1000 BERYWATERM 0%",
    "cod_barras":8421881029775
  },
  {
    "codigo":"Z040900156",
    "descripcion":"VUSE GO PEN 1000 BLUEBER.ICE0%",
    "cod_barras":8421881029805
  },
  {
    "codigo":"Z040900157",
    "descripcion":"VUSE GO PEN 1000 STWBRRYKIW 0%",
    "cod_barras":8421881029928
  },
  {
    "codigo":"Z040900158",
    "descripcion":"VUSE GO PEN 1000 PEPPERMINT 0%",
    "cod_barras":8421881029898
  },
  {
    "codigo":"Z040900200",
    "descripcion":"VUSE GO BOX 1000 PEPPERMINT 20",
    "cod_barras":8421881028815
  },
  {
    "codigo":"Z040900201",
    "descripcion":"VUSE GO BOX 1000 STWBRRYKIW 20",
    "cod_barras":8421881028877
  },
  {
    "codigo":"Z040900202",
    "descripcion":"VUSE GO BOX 1000 WATERMELON 20",
    "cod_barras":8421881028907
  },
  {
    "codigo":"Z040900203",
    "descripcion":"VUSE GO BOX 1000 SPEARMINT 20",
    "cod_barras":8421881028846
  },
  {
    "codigo":"Z040900204",
    "descripcion":"VUSE GO BOX 1000 BERRY FIZZ 20",
    "cod_barras":8421881028969
  },
  {
    "codigo":"Z040900205",
    "descripcion":"VUSE GO BOX 1000 WATERMELON 0%",
    "cod_barras":8421881028990
  },
  {
    "codigo":"Z040900901",
    "descripcion":"DISPOSITIVO GLO AIR TURQUESA 1",
    "cod_barras":8027463008512
  },
  {
    "codigo":"Z040900902",
    "descripcion":"DISPOSITIVO GLO AIR DORADO 1Un",
    "cod_barras":8027463008536
  },
  {
    "codigo":"Z040900903",
    "descripcion":"DISPOSITIVO GLO AIR BLACK 1Un",
    "cod_barras":8027463008499
  },
  {
    "codigo":"Z040900904",
    "descripcion":"DISPOSITIVO GLO BLUE 1Un",
    "cod_barras":8027463008574
  },
  {
    "codigo":"Z040900905",
    "descripcion":"DISPOSITIVO GLO ROSA 1Un",
    "cod_barras":8027463008802
  },
  {
    "codigo":"Z040900908",
    "descripcion":"DISP.GLO X3 PRO NEGRO RUBI",
    "cod_barras":5208049012649
  },
  {
    "codigo":"Z040900909",
    "descripcion":"DISP.GLO X3 PRO VIOLETA",
    "cod_barras":5208049012700
  },
  {
    "codigo":"Z040900910",
    "descripcion":"DISP.GLO X3 PRO AZUL",
    "cod_barras":5208049012670
  },
  {
    "codigo":"Z040900911",
    "descripcion":"DISP.GLO X3 PRO TURQUESA",
    "cod_barras":5208049012687
  },
  {
    "codigo":"Z040900930",
    "descripcion":"VELO SPIFFY SPEARMINT 6mg.1x5",
    "cod_barras":8421881024442
  },
  {
    "codigo":"Z040900931",
    "descripcion":"VELO BRIGHT SPEARMINT 10mg.1x5",
    "cod_barras":8421881024534
  },
  {
    "codigo":"Z040900932",
    "descripcion":"VELO GROOVY GRAPE 10mg.1x5",
    "cod_barras":8421881024565
  },
  {
    "codigo":"Z040900933",
    "descripcion":"VELO LIME FLAME 8mg. 1x5",
    "cod_barras":8421881024626
  },
  {
    "codigo":"Z040900934",
    "descripcion":"VELO FREZING PEPPER.10,9mg.1x5",
    "cod_barras":8421881024657
  },
  {
    "codigo":"Z040900935",
    "descripcion":"VELO CRISPY PEPPERMI.10mg. 1x5",
    "cod_barras":8421881024596
  },
  {
    "codigo":"Z040900936",
    "descripcion":"VELO STRAWBERRY ICE 10mg. 1x5",
    "cod_barras":8421881025487
  },
  {
    "codigo":"Z040900937",
    "descripcion":"VELO FREZING PEPPER.14mg.1x5",
    "cod_barras":8421881031174
  },
  {
    "codigo":"Z042000001",
    "descripcion":"CIG.1,69 PREM.BLEN.NEW ST10X20",
    "cod_barras":8435233369532
  },
  {
    "codigo":"Z042000002",
    "descripcion":"CIG.1,69 PREM.BLUE NEW ST1X10",
    "cod_barras":8435233323411
  },
  {
    "codigo":"Z042000050",
    "descripcion":"PUROS PALMERITO TUBO 1X50Und.",
    "cod_barras":8435233365428
  },
  {
    "codigo":"Z042000052",
    "descripcion":"PUROS PALMERITO TUBO 1X4Und.",
    "cod_barras":8435233347837
  },
  {
    "codigo":"Z042000055",
    "descripcion":"BREVAS PALMERITO caja 1X10Und.",
    "cod_barras":8435233365541
  },
  {
    "codigo":"Z042000056",
    "descripcion":"BREVAS PALMERITO caja 1X5Und.",
    "cod_barras":8435233365510
  },
  {
    "codigo":"Z042000060",
    "descripcion":"MINITOS PALMERITO mazo 1X10 Ud",
    "cod_barras":8435233349367
  },
  {
    "codigo":"Z042000061",
    "descripcion":"MINITOS PALMERITO caja 1X10 Ud",
    "cod_barras":8435233365466
  },
  {
    "codigo":"Z042000065",
    "descripcion":"SEÑORITAS PALMERITO mazo 1X10u",
    "cod_barras":8435233349428
  },
  {
    "codigo":"Z042000066",
    "descripcion":"SEÑORITAS PALMERITO mazo 1X25u",
    "cod_barras":8435233349435
  },
  {
    "codigo":"Z042000068",
    "descripcion":"SEÑORITAS PALMERITO caja 1X10u",
    "cod_barras":8435233365503
  },
  {
    "codigo":"Z042000070",
    "descripcion":"PETITOS PALMERITO mazo 1X10 Ud",
    "cod_barras":8435233349398
  },
  {
    "codigo":"Z042000073",
    "descripcion":"PETITOS PALMERITO caja 1X10 Ud",
    "cod_barras":8435233365459
  },
  {
    "codigo":"Z043100004",
    "descripcion":"PICADURA MANITOU GREEN 5x30Grs",
    "cod_barras":4006396012777
  },
  {
    "codigo":"Z043100005",
    "descripcion":"PICADURA MANITOU GOLD 5x30Grs.",
    "cod_barras":4006396154125
  },
  {
    "codigo":"Z045000001",
    "descripcion":"+VAPER.DESE.COOLPLAY SABORE.10",
    "cod_barras":6972461601949
  },
  {
    "codigo":"Z045000010",
    "descripcion":"+VAPEYOU FRESH BREEZE 600 1X10",
    "cod_barras":8435233385952
  },
  {
    "codigo":"Z045000011",
    "descripcion":"+VAPEYOU RASPBRRY 600 1X10U",
    "cod_barras":8435233386010
  },
  {
    "codigo":"Z045000012",
    "descripcion":"+VAPEYOU COLD MANGO 600 1X10U",
    "cod_barras":8435233385815
  },
  {
    "codigo":"Z045000013",
    "descripcion":"+VAPEYOU COLD PEACH 600 1X10U",
    "cod_barras":8435233385938
  },
  {
    "codigo":"Z045000014",
    "descripcion":"+VAPEYOU GRAPE 600  1X10U",
    "cod_barras":8435233385990
  },
  {
    "codigo":"Z045000015",
    "descripcion":"+VAPEYOU BANANA 600  1X10U",
    "cod_barras":8435233385884
  },
  {
    "codigo":"Z045000020",
    "descripcion":"+VAPEYOU BLUBRRY 600 S\/N.1X10U",
    "cod_barras":8435233389738
  },
  {
    "codigo":"Z045000021",
    "descripcion":"+VAPEYOU WTRMELO 600 S\/N.1X10U",
    "cod_barras":8435233389639
  },
  {
    "codigo":"Z045000022",
    "descripcion":"+VAPEYOU GRAPE 600 S\/N 1X10U",
    "cod_barras":8435233389769
  },
  {
    "codigo":"Z046000002",
    "descripcion":"PAPEL SMOK.DELUXE+FILTRO 1x24",
    "cod_barras":8414775013011
  },
  {
    "codigo":"Z046000005",
    "descripcion":"SMOKING RED KING SIZE+FILT1X24",
    "cod_barras":8414775016388
  },
  {
    "codigo":"Z046000020",
    "descripcion":"SMOKING FILTERS 6X15mm 30x180U",
    "cod_barras":8414775016012
  },
  {
    "codigo":"Z046000021",
    "descripcion":"SMOKING FILTERS 6X22mm 30x120U",
    "cod_barras":8414775015534
  },
  {
    "codigo":"Z046000022",
    "descripcion":"SMOK.FILT.BROWN 6X15mm 10x120U",
    "cod_barras":8414775016647
  },
  {
    "codigo":"Z046000100",
    "descripcion":"MECHERO CLIPER ET 48 Udes.",
    "cod_barras":8412765412745
  }
]
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
        df = pd.read_sql_query("SELECT * FROM conteos_fisicos WHERE tienda = ? ORDER BY fecha DESC", conn, params=(tienda,))
    else:
        df = pd.read_sql_query("SELECT * FROM conteos_fisicos ORDER BY fecha DESC", conn)
    conn.close()

    # DEBUG: Imprime los nombres reales
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
        for producto in productos_unidos:
            cantidad = request.form.get(f"stock_{producto['codigo']}")
            try:
                cantidad_num = int(cantidad)
            except Exception:
                cantidad_num = 0
            if cantidad_num > 0:
                # Guarda en conteos normales (como antes)
                conn.execute(
                'INSERT INTO conteos_fisicos (tienda, codigo, descripcion, cod_barras, stock_fisico, fecha, autor) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)',
                 (tienda, producto['codigo'], producto['descripcion'], producto['cod_barras'], cantidad_num, autor)
                )

                productos_modificados += 1
                # También guarda el producto para el histórico
                inventario_actual.append({
                    "codigo": producto['codigo'],
                    "descripcion": producto['descripcion'],
                    "cod_barras": producto['cod_barras'],
                    "cantidad": cantidad_num
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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Railway te asigna el puerto por variable de entorno
    app.run(host="0.0.0.0", port=port)


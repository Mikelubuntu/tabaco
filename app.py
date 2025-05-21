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

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        password = request.form['password']
        if password == '0022':
            session['logueado'] = True
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

    {"codigo": "20101000001", "descripcion": "3-M INTERNATIONAL IBERICA ***", "cod_barras": "8410016804075"},
    {"codigo": "20101000002", "descripcion": "CAMEL FILTERS CARTON 10x20 Ud.", "cod_barras": "8410016804556"},
    {"codigo": "20101000003", "descripcion": "CAMEL BLUE CARTON 10x20 Ud.", "cod_barras": "8410016804549"},
    {"codigo": "20101000004", "descripcion": "CAMEL FILTERS SOFT 10x20 Ud.", "cod_barras": "8410016804532"},
    {"codigo": "20101000005", "descripcion": "CAMEL ACTIVA DOUBLE 20x10 Udes.", "cod_barras": "8410016810526"},
    {"codigo": "20101000006", "descripcion": "CAMEL ACTIVA YELLOW 20x10 Ud.", "cod_barras": "8410016810595"},
    {"codigo": "20101000007", "descripcion": "CAMEL ACTIVA PLAYER. DPS 20X10", "cod_barras": "8410016810571"},
    {"codigo": "20101000008", "descripcion": "CAMEL YELLOW 20x23 Ud. Udes.", "cod_barras": "8410016810588"},
    {"codigo": "20101000009", "descripcion": "WINSTON RED 10x20 Ud.", "cod_barras": "8410044501867"},
    {"codigo": "20101000010", "descripcion": "WINSTON GOLD BOX 10x20 Ud.", "cod_barras": "8410044501898"},
    {"codigo": "20101000011", "descripcion": "WINSTON BLUE BOX 10x20 Ud.", "cod_barras": "8410044501904"},
    {"codigo": "20101000012", "descripcion": "WINSTON SILVER BOX 10x20 Ud.", "cod_barras": "8410044501928"},
    {"codigo": "20101000013", "descripcion": "WINSTON XSTYLE BLUE 10x20 Ud.", "cod_barras": "8410044502192"},
    {"codigo": "20101000014", "descripcion": "WINSTON XSTYLE RED 10x20 Ud.", "cod_barras": "8410044502185"},
    {"codigo": "20101000015", "descripcion": "LUCKY STRIKE RED 10x20 Ud.", "cod_barras": "8410044502543"},
    {"codigo": "20101000016", "descripcion": "LUCKY STRIKE BLUE 10x20 Ud.", "cod_barras": "8410044502550"},
    {"codigo": "20101000017", "descripcion": "LUCKY STRIKE CLICK & ROLL 10x20", "cod_barras": "8410044502581"},
    {"codigo": "20101000018", "descripcion": "LUCKY STRIKE SILVER 10x20 Ud.", "cod_barras": "8410044502574"},
    {"codigo": "20101000019", "descripcion": "CHESTERFIELD RED 10x20 Ud.", "cod_barras": "8410016900082"},
    {"codigo": "20101000020", "descripcion": "CHESTERFIELD BLUE 10x20 Ud.", "cod_barras": "8410016900099"},
    {"codigo": "20101000021", "descripcion": "CHESTERFIELD ORIGINAL 10x20 Ud.", "cod_barras": "8410016900112"},
    {"codigo": "20101000022", "descripcion": "CHESTERFIELD MENTHOL 10x20 Ud.", "cod_barras": "8410016900129"},
    {"codigo": "20101000023", "descripcion": "FORTUNA 10x20 Ud.", "cod_barras": "8410016000858"},
    {"codigo": "20101000024", "descripcion": "NOBEL 10x20 Ud.", "cod_barras": "8410016400718"},
    {"codigo": "20101000025", "descripcion": "DUCATI RED 10x20 Ud.", "cod_barras": "8410016200905"},
    {"codigo": "20101000026", "descripcion": "DUCATI BLUE 10x20 Ud.", "cod_barras": "8410016200912"},
    {"codigo": "20101000027", "descripcion": "DUCATI SILVER 10x20 Ud.", "cod_barras": "8410016200929"},
    {"codigo": "20101000028", "descripcion": "WEST RED 10x20 Ud.", "cod_barras": "4001090000681"},
    {"codigo": "20101000029", "descripcion": "WEST BLUE 10x20 Ud.", "cod_barras": "4001090000698"},
    {"codigo": "20101000030", "descripcion": "WEST ICE 10x20 Ud.", "cod_barras": "4001090000704"},
    {"codigo": "20101000031", "descripcion": "MARLBORO RED 10x20 Ud.", "cod_barras": "7622100711334"},
    {"codigo": "20101000032", "descripcion": "MARLBORO GOLD 10x20 Ud.", "cod_barras": "7622100711341"},
    {"codigo": "20101000033", "descripcion": "MARLBORO FUSION 10x20 Ud.", "cod_barras": "7622100711365"},
    {"codigo": "20101000034", "descripcion": "MARLBORO TOUCH 10x20 Ud.", "cod_barras": "7622100711372"},
    {"codigo": "20101000035", "descripcion": "MARLBORO SILVER 10x20 Ud.", "cod_barras": "7622100711358"},
    {"codigo": "20101000036", "descripcion": "PHILIP MORRIS RED 10x20 Ud.", "cod_barras": "7622100711679"},
    {"codigo": "20101000037", "descripcion": "PHILIP MORRIS BLUE 10x20 Ud.", "cod_barras": "7622100711686"},
    {"codigo": "20101000038", "descripcion": "PHILIP MORRIS SILVER 10x20 Ud.", "cod_barras": "7622100711693"},
    {"codigo": "20101000039", "descripcion": "L&M RED LABEL 10x20 Ud.", "cod_barras": "7622100711716"},
    {"codigo": "20101000040", "descripcion": "L&M BLUE LABEL 10x20 Ud.", "cod_barras": "7622100711723"},
    {"codigo": "20101000041", "descripcion": "L&M SILVER LABEL 10x20 Ud.", "cod_barras": "7622100711730"},
    {"codigo": "20101000042", "descripcion": "L&M BLUE LABEL 10x20 Ud.", "cod_barras": "7622100711747"},
    {"codigo": "20101000043", "descripcion": "L&M L8 10x20 Ud.", "cod_barras": "7622100711754"},
    {"codigo": "20101000044", "descripcion": "L&M MOTION 10x20 Ud.", "cod_barras": "7622100711761"},
    {"codigo": "20101000045", "descripcion": "ELIXYR RED 10x20 Ud.", "cod_barras": "5410133800018"},
    {"codigo": "20101000046", "descripcion": "ELIXYR BLUE 10x20 Ud.", "cod_barras": "5410133800025"},
    {"codigo": "20101000047", "descripcion": "ELIXYR SILVER 10x20 Ud.", "cod_barras": "5410133800032"},
    {"codigo": "20101000048", "descripcion": "ELIXYR MENTHOL 10x20 Ud.", "cod_barras": "5410133800049"},
    {"codigo": "20101000049", "descripcion": "PALL MALL RED 10x20 Ud.", "cod_barras": "4082300325655"},
    {"codigo": "20101000050", "descripcion": "PALL MALL BLUE 10x20 Ud.", "cod_barras": "4082300325662"},
    {"codigo": "20101000051", "descripcion": "PALL MALL SILVER 10x20 Ud.", "cod_barras": "4082300325679"},
    {"codigo": "20101000052", "descripcion": "PALL MALL ORANGE 10x20 Ud.", "cod_barras": "4082300325686"},
    {"codigo": "20101000053", "descripcion": "PALL MALL MENTHOL 10x20 Ud.", "cod_barras": "4082300325693"},
    {"codigo": "20101000054", "descripcion": "DUNHILL INTERNATIONAL 10x20 Ud.", "cod_barras": "5000267013871"},
    {"codigo": "20101000055", "descripcion": "DUNHILL FINE CUT WHITE 10x20 Ud.", "cod_barras": "5000267013888"},
    {"codigo": "20101000056", "descripcion": "DUNHILL SWITCH 10x20 Ud.", "cod_barras": "5000267013895"},
    {"codigo": "20101000057", "descripcion": "GOLOISE BLONDE 10x20 Ud.", "cod_barras": "3086126006901"},
    {"codigo": "20101000058", "descripcion": "GOLOISE BLEUE 10x20 Ud.", "cod_barras": "3086126006918"},
    {"codigo": "20101000059", "descripcion": "GOLOISE BRUNE 10x20 Ud.", "cod_barras": "3086126006925"},
    {"codigo": "20101000060", "descripcion": "LUCKY STRIKE SUNSET 10x20 Ud.", "cod_barras": "8410044502567"},
    {"codigo": "20101000061", "descripcion": "LUCKY STRIKE NIGHT 10x20 Ud.", "cod_barras": "8410044502598"},
    {"codigo": "20101000062", "descripcion": "LUCKY STRIKE ICE 10x20 Ud.", "cod_barras": "8410044502604"},
    {"codigo": "20101000063", "descripcion": "MARLBORO ICE BLAST 10x20 Ud.", "cod_barras": "7622100711389"},
    {"codigo": "20101000064", "descripcion": "MARLBORO CRUSHBALL 10x20 Ud.", "cod_barras": "7622100711396"},
    {"codigo": "20101000065", "descripcion": "MARLBORO DOUBLE MIX 10x20 Ud.", "cod_barras": "7622100711402"},
    {"codigo": "20101000066", "descripcion": "CHESTERFIELD MINT 10x20 Ud.", "cod_barras": "8410016900136"},
    {"codigo": "20101000067", "descripcion": "CHESTERFIELD CHERRY 10x20 Ud.", "cod_barras": "8410016900143"},
    {"codigo": "20101000068", "descripcion": "WEST CHERRY 10x20 Ud.", "cod_barras": "4001090000711"},
    {"codigo": "20101000069", "descripcion": "WEST MENTHOL 10x20 Ud.", "cod_barras": "4001090000728"},
    {"codigo": "20101000070", "descripcion": "WEST ICE BLAST 10x20 Ud.", "cod_barras": "4001090000735"},
    {"codigo": "20101000071", "descripcion": "DUCATI MENTHOL 10x20 Ud.", "cod_barras": "8410016200936"},
    {"codigo": "20101000072", "descripcion": "NOBEL MENTHOL 10x20 Ud.", "cod_barras": "8410016400725"},
    {"codigo": "20101000073", "descripcion": "FORTUNA MENTHOL 10x20 Ud.", "cod_barras": "8410016000865"},
    {"codigo": "20101000074", "descripcion": "CAMEL MENTHOL 10x20 Ud.", "cod_barras": "8410016810601"},
    {"codigo": "20101000075", "descripcion": "CAMEL ICE BLAST 10x20 Ud.", "cod_barras": "8410016810618"},
    {"codigo": "20101000076", "descripcion": "PALL MALL ICE 10x20 Ud.", "cod_barras": "4082300325709"},
    {"codigo": "20101000077", "descripcion": "PALL MALL SUNSET 10x20 Ud.", "cod_barras": "4082300325716"},
    {"codigo": "20101000078", "descripcion": "GOLOISE ICE 10x20 Ud.", "cod_barras": "3086126006932"},
    {"codigo": "20101000079", "descripcion": "L&M ICE 10x20 Ud.", "cod_barras": "7622100711778"},
    {"codigo": "20101000080", "descripcion": "ELIXYR ICE 10x20 Ud.", "cod_barras": "5410133800056"},
    {"codigo": "20101000081", "descripcion": "WINSTON ICE 10x20 Ud.", "cod_barras": "8410044501935"},
    {"codigo": "20101000082", "descripcion": "LUCKY STRIKE CHERRY 10x20 Ud.", "cod_barras": "8410044502611"},
    {"codigo": "20101000083", "descripcion": "LUCKY STRIKE MENTHOL 10x20 Ud.", "cod_barras": "8410044502628"},
    {"codigo": "20101000084", "descripcion": "MARLBORO CHERRY 10x20 Ud.", "cod_barras": "7622100711419"},
    {"codigo": "20101000085", "descripcion": "PHILIP MORRIS CHERRY 10x20 Ud.", "cod_barras": "7622100711709"},
    {"codigo": "20101000086", "descripcion": "CHESTERFIELD ICE 10x20 Ud.", "cod_barras": "8410016900150"},
    {"codigo": "20101000087", "descripcion": "DUCATI ICE 10x20 Ud.", "cod_barras": "8410016200943"},
    {"codigo": "20101000088", "descripcion": "NOBEL ICE 10x20 Ud.", "cod_barras": "8410016400732"},
    {"codigo": "20101000089", "descripcion": "FORTUNA ICE 10x20 Ud.", "cod_barras": "8410016000872"},
    {"codigo": "20101000090", "descripcion": "CAMEL CHERRY 10x20 Ud.", "cod_barras": "8410016810625"},
    {"codigo": "20101000091", "descripcion": "CAMEL MINT 10x20 Ud.", "cod_barras": "8410016810632"},
    {"codigo": "20101000092", "descripcion": "WEST ICE MINT 10x20 Ud.", "cod_barras": "4001090000742"},
    {"codigo": "20101000093", "descripcion": "WEST DOUBLE ICE 10x20 Ud.", "cod_barras": "4001090000759"},
    {"codigo": "20101000094", "descripcion": "DUCATI CHERRY 10x20 Ud.", "cod_barras": "8410016200950"},
    {"codigo": "20101000095", "descripcion": "NOBEL CHERRY 10x20 Ud.", "cod_barras": "8410016400749"},
    {"codigo": "20101000096", "descripcion": "FORTUNA CHERRY 10x20 Ud.", "cod_barras": "8410016000889"},
    {"codigo": "20101000097", "descripcion": "GOLOISE MINT 10x20 Ud.", "cod_barras": "3086126006949"},
    {"codigo": "20101000098", "descripcion": "L&M MINT 10x20 Ud.", "cod_barras": "7622100711785"},
    {"codigo": "20101000099", "descripcion": "ELIXYR CHERRY 10x20 Ud.", "cod_barras": "5410133800063"},
    {"codigo": "20101000100", "descripcion": "WINSTON MINT 10x20 Ud.", "cod_barras": "8410044501942"},
    {"codigo": "20101000101", "descripcion": "LUCKY STRIKE ICE MINT 10x20 Ud.", "cod_barras": "8410044502635"},
    {"codigo": "20101000102", "descripcion": "MARLBORO ICE MINT 10x20 Ud.", "cod_barras": "7622100711426"},
    {"codigo": "20101000103", "descripcion": "PHILIP MORRIS ICE MINT 10x20 Ud.", "cod_barras": "7622100711716"},
    {"codigo": "20101000104", "descripcion": "CHESTERFIELD ICE MINT 10x20 Ud.", "cod_barras": "8410016900167"},
    {"codigo": "20101000105", "descripcion": "DUCATI ICE MINT 10x20 Ud.", "cod_barras": "8410016200967"},
    {"codigo": "20101000106", "descripcion": "NOBEL ICE MINT 10x20 Ud.", "cod_barras": "8410016400756"},
    {"codigo": "20101000107", "descripcion": "FORTUNA ICE MINT 10x20 Ud.", "cod_barras": "8410016000896"},
    {"codigo": "20101000108", "descripcion": "CAMEL ICE MINT 10x20 Ud.", "cod_barras": "8410016810649"},
    {"codigo": "20101000109", "descripcion": "GOLOISE ICE MINT 10x20 Ud.", "cod_barras": "3086126006956"},
    {"codigo": "20101000110", "descripcion": "L&M ICE MINT 10x20 Ud.", "cod_barras": "7622100711792"},
    {"codigo": "20101000111", "descripcion": "ELIXYR ICE MINT 10x20 Ud.", "cod_barras": "5410133800070"},
    {"codigo": "20101000112", "descripcion": "WINSTON ICE MINT 10x20 Ud.", "cod_barras": "8410044501959"},
    {"codigo": "20101000113", "descripcion": "LUCKY STRIKE DOUBLE ICE 10x20 Ud.", "cod_barras": "8410044502642"},
    {"codigo": "20101000114", "descripcion": "MARLBORO DOUBLE ICE 10x20 Ud.", "cod_barras": "7622100711433"},
    {"codigo": "20101000115", "descripcion": "PHILIP MORRIS DOUBLE ICE 10x20 Ud.", "cod_barras": "7622100711723"},
    {"codigo": "20101000116", "descripcion": "CHESTERFIELD DOUBLE ICE 10x20 Ud.", "cod_barras": "8410016900174"},
    {"codigo": "20101000117", "descripcion": "DUCATI DOUBLE ICE 10x20 Ud.", "cod_barras": "8410016200974"},
    {"codigo": "20101000118", "descripcion": "NOBEL DOUBLE ICE 10x20 Ud.", "cod_barras": "8410016400763"},
    {"codigo": "20101000119", "descripcion": "FORTUNA DOUBLE ICE 10x20 Ud.", "cod_barras": "8410016000902"},
    {"codigo": "20101000120", "descripcion": "CAMEL DOUBLE ICE 10x20 Ud.", "cod_barras": "8410016810656"},
    {"codigo": "20101000121", "descripcion": "GOLOISE DOUBLE ICE 10x20 Ud.", "cod_barras": "3086126006963"},
    {"codigo": "20101000122", "descripcion": "L&M DOUBLE ICE 10x20 Ud.", "cod_barras": "7622100711808"},
    {"codigo": "20101000123", "descripcion": "ELIXYR DOUBLE ICE 10x20 Ud.", "cod_barras": "5410133800087"},
    {"codigo": "20101000124", "descripcion": "WINSTON DOUBLE ICE 10x20 Ud.", "cod_barras": "8410044501966"},
    {"codigo": "20101000125", "descripcion": "MARLBORO DOUBLE CHERRY 10x20 Ud.", "cod_barras": "7622100711440"},
    {"codigo": "20101000126", "descripcion": "LUCKY STRIKE DOUBLE CHERRY 10x20 Ud.", "cod_barras": "8410044502659"},
    {"codigo": "20101000127", "descripcion": "CHESTERFIELD DOUBLE CHERRY 10x20 Ud.", "cod_barras": "8410016900181"},
    {"codigo": "20101000128", "descripcion": "CAMEL DOUBLE CHERRY 10x20 Ud.", "cod_barras": "8410016810663"},
    {"codigo": "20101000129", "descripcion": "DUCATI DOUBLE CHERRY 10x20 Ud.", "cod_barras": "8410016200981"},
    {"codigo": "20101000130", "descripcion": "NOBEL DOUBLE CHERRY 10x20 Ud.", "cod_barras": "8410016400770"},
    {"codigo": "20101000131", "descripcion": "FORTUNA DOUBLE CHERRY 10x20 Ud.", "cod_barras": "8410016000919"},
    {"codigo": "20101000132", "descripcion": "GOLOISE DOUBLE CHERRY 10x20 Ud.", "cod_barras": "3086126006970"},
    {"codigo": "20101000133", "descripcion": "L&M DOUBLE CHERRY 10x20 Ud.", "cod_barras": "7622100711815"},
    {"codigo": "20101000134", "descripcion": "ELIXYR DOUBLE CHERRY 10x20 Ud.", "cod_barras": "5410133800094"},
    {"codigo": "20101000135", "descripcion": "WINSTON DOUBLE CHERRY 10x20 Ud.", "cod_barras": "8410044501973"},
    {"codigo": "20101000136", "descripcion": "MARLBORO DOUBLE MINT 10x20 Ud.", "cod_barras": "7622100711457"},
    {"codigo": "20101000137", "descripcion": "LUCKY STRIKE DOUBLE MINT 10x20 Ud.", "cod_barras": "8410044502666"},
    {"codigo": "20101000138", "descripcion": "CHESTERFIELD DOUBLE MINT 10x20 Ud.", "cod_barras": "8410016900198"},
    {"codigo": "20101000139", "descripcion": "CAMEL DOUBLE MINT 10x20 Ud.", "cod_barras": "8410016810670"},
    {"codigo": "20101000140", "descripcion": "DUCATI DOUBLE MINT 10x20 Ud.", "cod_barras": "8410016200998"},
    {"codigo": "20101000141", "descripcion": "NOBEL DOUBLE MINT 10x20 Ud.", "cod_barras": "8410016400787"},
    {"codigo": "20101000142", "descripcion": "FORTUNA DOUBLE MINT 10x20 Ud.", "cod_barras": "8410016000926"},
    {"codigo": "20101000143", "descripcion": "GOLOISE DOUBLE MINT 10x20 Ud.", "cod_barras": "3086126006987"},
    {"codigo": "20101000144", "descripcion": "L&M DOUBLE MINT 10x20 Ud.", "cod_barras": "7622100711822"},
    {"codigo": "20101000145", "descripcion": "ELIXYR DOUBLE MINT 10x20 Ud.", "cod_barras": "5410133800100"},
    {"codigo": "20101000146", "descripcion": "WINSTON DOUBLE MINT 10x20 Ud.", "cod_barras": "8410044501980"},
    {"codigo": "20101000147", "descripcion": "MARLBORO SUNSET 10x20 Ud.", "cod_barras": "7622100711464"},
    {"codigo": "20101000148", "descripcion": "LUCKY STRIKE SUNSET 10x20 Ud.", "cod_barras": "8410044502673"},
    {"codigo": "20101000149", "descripcion": "CHESTERFIELD SUNSET 10x20 Ud.", "cod_barras": "8410016900204"},
    {"codigo": "20101000150", "descripcion": "CAMEL SUNSET 10x20 Ud.", "cod_barras": "8410016810687"},
    {"codigo": "20101000151", "descripcion": "DUCATI SUNSET 10x20 Ud.", "cod_barras": "8410016201001"},
    {"codigo": "20101000152", "descripcion": "NOBEL SUNSET 10x20 Ud.", "cod_barras": "8410016400794"},
    {"codigo": "20101000153", "descripcion": "FORTUNA SUNSET 10x20 Ud.", "cod_barras": "8410016000933"},
    {"codigo": "20101000154", "descripcion": "GOLOISE SUNSET 10x20 Ud.", "cod_barras": "3086126006994"},
    {"codigo": "20101000155", "descripcion": "L&M SUNSET 10x20 Ud.", "cod_barras": "7622100711839"},
    {"codigo": "20101000156", "descripcion": "ELIXYR SUNSET 10x20 Ud.", "cod_barras": "5410133800117"},
    {"codigo": "20101000157", "descripcion": "WINSTON SUNSET 10x20 Ud.", "cod_barras": "8410044501997"},
    {"codigo": "20101000158", "descripcion": "MARLBORO NIGHT 10x20 Ud.", "cod_barras": "7622100711471"},
    {"codigo": "20101000159", "descripcion": "LUCKY STRIKE NIGHT 10x20 Ud.", "cod_barras": "8410044502680"},
    {"codigo": "20101000160", "descripcion": "CHESTERFIELD NIGHT 10x20 Ud.", "cod_barras": "8410016900211"},
    {"codigo": "20101000161", "descripcion": "CAMEL NIGHT 10x20 Ud.", "cod_barras": "8410016810694"},
    {"codigo": "20101000162", "descripcion": "DUCATI NIGHT 10x20 Ud.", "cod_barras": "8410016201018"},
    {"codigo": "20101000163", "descripcion": "NOBEL NIGHT 10x20 Ud.", "cod_barras": "8410016400800"},
    {"codigo": "20101000164", "descripcion": "FORTUNA NIGHT 10x20 Ud.", "cod_barras": "8410016000940"},
    {"codigo": "20101000165", "descripcion": "GOLOISE NIGHT 10x20 Ud.", "cod_barras": "3086126007007"},
    {"codigo": "20101000166", "descripcion": "L&M NIGHT 10x20 Ud.", "cod_barras": "7622100711846"},
    {"codigo": "20101000167", "descripcion": "ELIXYR NIGHT 10x20 Ud.", "cod_barras": "5410133800124"},
    {"codigo": "20101000168", "descripcion": "WINSTON NIGHT 10x20 Ud.", "cod_barras": "8410044502000"},
    {"codigo": "60101000001", "descripcion": "HEETS AMBER 20 UDS", "cod_barras": "7630048301417"},
    {"codigo": "60101000002", "descripcion": "HEETS YELLOW 20 UDS", "cod_barras": "7630048301424"},
    {"codigo": "60101000003", "descripcion": "HEETS TURQUOISE 20 UDS", "cod_barras": "7630048301431"},
    {"codigo": "60101000004", "descripcion": "HEETS SIENNA 20 UDS", "cod_barras": "7630048301448"},
    {"codigo": "60101000005", "descripcion": "HEETS GREEN ZING 20 UDS", "cod_barras": "7630048301455"},
    {"codigo": "60101000006", "descripcion": "HEETS BRONZE 20 UDS", "cod_barras": "7630048301462"},
    {"codigo": "60101000007", "descripcion": "HEETS SILVER 20 UDS", "cod_barras": "7630048301479"},
    {"codigo": "60101000008", "descripcion": "TEREA AMBER 20 UDS", "cod_barras": "7630048302049"},
    {"codigo": "60101000009", "descripcion": "TEREA YELLOW 20 UDS", "cod_barras": "7630048302056"},
    {"codigo": "60101000010", "descripcion": "TEREA BLUE 20 UDS", "cod_barras": "7630048302063"},
    {"codigo": "60101000011", "descripcion": "TEREA BRONZE 20 UDS", "cod_barras": "7630048302070"},
    {"codigo": "60101000012", "descripcion": "TEREA GREEN 20 UDS", "cod_barras": "7630048302087"},
    {"codigo": "60102000001", "descripcion": "IQOS ILUMA ONE", "cod_barras": "7630048303091"},
    {"codigo": "60102000002", "descripcion": "IQOS ILUMA PRIME", "cod_barras": "7630048303107"},
    {"codigo": "60102000003", "descripcion": "IQOS 3 DUO", "cod_barras": "7630048303084"},
    {"codigo": "60103000001", "descripcion": "IQOS CLEANING STICKS 30U", "cod_barras": "7630048302506"},
    {"codigo": "60103000002", "descripcion": "IQOS ILUMA CAP", "cod_barras": "7630048302704"},
    {"codigo": "60103000003", "descripcion": "IQOS CARGADOR USB", "cod_barras": "7630048302681"},
    {"codigo": "60103000004", "descripcion": "IQOS HOLDER", "cod_barras": "7630048302674"},

    {"codigo": "70101000001", "descripcion": "VELO POLAR MINT", "cod_barras": "5704841053914"},
    {"codigo": "70101000002", "descripcion": "VELO BERRY FROST", "cod_barras": "5704841053907"},
    {"codigo": "70101000003", "descripcion": "VELO ICE COOL", "cod_barras": "5704841053921"},
    {"codigo": "70101000004", "descripcion": "VELO TROPICAL", "cod_barras": "5704841053938"},

    {"codigo": "70201000001", "descripcion": "VUSE POD MANGO ICE", "cod_barras": "4031300168585"},
    {"codigo": "70201000002", "descripcion": "VUSE POD CLASSIC TOBACCO", "cod_barras": "4031300168592"},
    {"codigo": "70201000003", "descripcion": "VUSE POD WILD BERRIES", "cod_barras": "4031300168608"},
    {"codigo": "70201000004", "descripcion": "VUSE ePOD 2 KIT", "cod_barras": "4031300168714"},

    {"codigo": "70301000001", "descripcion": "BLU PRO KIT", "cod_barras": "4031300256985"},
    {"codigo": "70301000002", "descripcion": "BLU LIQUID CHERRY CRUSH", "cod_barras": "4031300256992"},
    {"codigo": "70301000003", "descripcion": "BLU INTENSE POD BLUEBERRY", "cod_barras": ""},

    {"codigo": "80101000001", "descripcion": "PUEBLO NATURAL 30g", "cod_barras": "4030400069726"},
    {"codigo": "80101000002", "descripcion": "PUEBLO BLUE 30g", "cod_barras": "4030400069740"},
    {"codigo": "80101000003", "descripcion": "CHESTERFIELD ORIGINAL 30g", "cod_barras": "7622100340597"},
    {"codigo": "80101000004", "descripcion": "CHESTERFIELD BLUE 30g", "cod_barras": "7622100340603"},
    {"codigo": "80101000005", "descripcion": "AMERICAN SPIRIT YELLOW 30g", "cod_barras": "4001012042915"},
    {"codigo": "80101000006", "descripcion": "AMERICAN SPIRIT BLUE 30g", "cod_barras": "4001012042908"},
    {"codigo": "80101000007", "descripcion": "GOLDEN VIRGINIA ORIGINAL 30g", "cod_barras": "5000157091326"},
    {"codigo": "80101000008", "descripcion": "GOLDEN VIRGINIA RUBIO 30g", "cod_barras": "5000157118429"},
    {"codigo": "80101000009", "descripcion": "NOBEL FINA SELECCION 30g", "cod_barras": "8410016400817"},
    {"codigo": "80101000010", "descripcion": "NOBEL FINA SELECCION 45g", "cod_barras": "8410016400824"},
    {"codigo": "80101000011", "descripcion": "CHESTERFIELD RYO 30g", "cod_barras": "7622100340610"},
    {"codigo": "80101000012", "descripcion": "WEST RED 30g", "cod_barras": "4001090302852"},
    {"codigo": "80101000013", "descripcion": "WEST BLUE 30g", "cod_barras": "4001090302869"},
    {"codigo": "80101000014", "descripcion": "FINE CUT ORIGINAL 30g", "cod_barras": "5000157118412"},
    {"codigo": "80101000015", "descripcion": "AMBASSADOR RUBIO 30g", "cod_barras": "8410016400855"},
    {"codigo": "90101000001", "descripcion": "OCB SLIM PREMIUM 32 LIBRILLOS", "cod_barras": "3057067170146"},
    {"codigo": "90101000002", "descripcion": "OCB XPERT SLIM 50 LIBRILLOS", "cod_barras": "3057067190199"},
    {"codigo": "90101000003", "descripcion": "RIZLA BLUE 50 LIBRILLOS", "cod_barras": "5410113302147"},
    {"codigo": "90101000004", "descripcion": "RIZLA SILVER 50 LIBRILLOS", "cod_barras": "5410113302154"},
    {"codigo": "90101000005", "descripcion": "RAW CLASSIC 32 LIBRILLOS", "cod_barras": "716165174511"},
    {"codigo": "90101000006", "descripcion": "RAW BLACK KING SIZE 32 LIBRILLOS", "cod_barras": "716165279568"},
    {"codigo": "90101000007", "descripcion": "SMOKING BLUE 60 LIBRILLOS", "cod_barras": "8414775012166"},
    {"codigo": "90101000008", "descripcion": "SMOKING GREEN 60 LIBRILLOS", "cod_barras": "8414775012180"},
    {"codigo": "90101000009", "descripcion": "FILTROS OCB SLIM 150 UDS", "cod_barras": "3057067180732"},
    {"codigo": "90101000010", "descripcion": "FILTROS RIZLA SLIM 120 UDS", "cod_barras": "5410113307012"},
    {"codigo": "90101000011", "descripcion": "FILTROS SMOKING BROWN 120 UDS", "cod_barras": "8414775016232"},
    {"codigo": "90101000012", "descripcion": "TUBOS RIZLA 100 UDS", "cod_barras": "5410113307012"},
    {"codigo": "90101000013", "descripcion": "TUBOS SMOKING 200 UDS", "cod_barras": "8414775014993"},
    {"codigo": "90101000014", "descripcion": "FILTROS CLIPPER REGULAR 100 UDS", "cod_barras": "8412765033800"},
    {"codigo": "100101000001", "descripcion": "CLIPPER ENCENDEDOR METAL", "cod_barras": "8412765903264"},
    {"codigo": "100101000002", "descripcion": "CLIPPER ENCENDEDOR CLASSIC", "cod_barras": "8412765903240"},
    {"codigo": "100101000003", "descripcion": "BIC ENCENDEDOR MINI", "cod_barras": "3086126203218"},
    {"codigo": "100101000004", "descripcion": "BIC ENCENDEDOR MAXI", "cod_barras": "3086126203126"},
    {"codigo": "100101000005", "descripcion": "CLIPPER GAS 300ML", "cod_barras": "8412765901802"},
    {"codigo": "100101000006", "descripcion": "CLIPPER PEDERNAL 9 UDS", "cod_barras": "8412765901758"},
    {"codigo": "100101000007", "descripcion": "MAQUINA LIAR OCB PREMIUM", "cod_barras": "3057067170108"},
    {"codigo": "100101000008", "descripcion": "MAQUINA TUBOS OCB", "cod_barras": "3057067272017"},
    {"codigo": "100101000009", "descripcion": "GRINDER METAL 4 PARTES", "cod_barras": "8435047502083"},
    {"codigo": "100101000010", "descripcion": "GRINDER PLASTICO", "cod_barras": "8435047502038"},
    {"codigo": "100101000011", "descripcion": "BOLSAS ZIP 100 UDS", "cod_barras": "8424295101001"},
    {"codigo": "100101000012", "descripcion": "MASCARILLA HIGIENICA PACK", "cod_barras": ""},
    {"codigo": "100101000013", "descripcion": "PAPEL ROLLING KING SIZE", "cod_barras": "716165175525"},
    {"codigo": "100101000014", "descripcion": "PIPA MADERA STANDARD", "cod_barras": ""},
    {"codigo": "100101000015", "descripcion": "CACHIMBA MINI 1 UDS", "cod_barras": ""},
    {"codigo": "60101000013", "descripcion": "TEREA MAUVE 20 UDS", "cod_barras": "7630048302094"},
{"codigo": "60101000014", "descripcion": "TEREA SIENNA 20 UDS", "cod_barras": "7630048302100"},
{"codigo": "60101000015", "descripcion": "TEREA TEAK 20 UDS", "cod_barras": "7630048302117"},
{"codigo": "60101000016", "descripcion": "TEREA PURPLE 20 UDS", "cod_barras": "7630048302124"},
{"codigo": "60101000017", "descripcion": "TEREA BRIGHT 20 UDS", "cod_barras": "7630048302131"},
{"codigo": "60101000018", "descripcion": "TEREA INDIGO 20 UDS", "cod_barras": "7630048302148"},
{"codigo": "60101000019", "descripcion": "TEREA TURQUOISE 20 UDS", "cod_barras": "7630048302155"},
{"codigo": "60101000020", "descripcion": "TEREA MARINE 20 UDS", "cod_barras": "7630048302162"},
{"codigo": "60101000021", "descripcion": "TEREA YELLOW SELECTION 20 UDS", "cod_barras": "7630048302179"},
{"codigo": "60102000004", "descripcion": "IQOS LIL SOLID 2.0", "cod_barras": "8809686510801"},
{"codigo": "60102000005", "descripcion": "IQOS ILUMA STANDARD", "cod_barras": "7630048303114"},
{"codigo": "60102000006", "descripcion": "IQOS ILUMA KIT", "cod_barras": "7630048303121"},
{"codigo": "60102000007", "descripcion": "IQOS 2.4 PLUS", "cod_barras": "7630048303077"},
{"codigo": "60102000008", "descripcion": "IQOS ILUMA RING", "cod_barras": "7630048302711"},
{"codigo": "60103000005", "descripcion": "IQOS HEATER CLEANER", "cod_barras": "7630048302728"},
{"codigo": "60103000006", "descripcion": "IQOS TRAVEL CASE", "cod_barras": "7630048302735"},
{"codigo": "70101000005", "descripcion": "VELO URBAN VIBE", "cod_barras": "5704841053945"},
{"codigo": "70101000006", "descripcion": "VELO CITRUS", "cod_barras": "5704841053952"},
{"codigo": "70101000007", "descripcion": "VELO FREEZE", "cod_barras": "5704841053969"},
{"codigo": "70101000008", "descripcion": "VELO ROYAL PURPLE", "cod_barras": "5704841053976"},
{"codigo": "70101000009", "descripcion": "VELO RUBY BERRY", "cod_barras": "5704841053983"},
{"codigo": "70201000005", "descripcion": "VUSE POD POLAR MINT", "cod_barras": "4031300168615"},
{"codigo": "70201000006", "descripcion": "VUSE POD STRAWBERRY", "cod_barras": "4031300168622"},
{"codigo": "70201000007", "descripcion": "VUSE ePOD 2 MINI KIT", "cod_barras": "4031300168721"},
{"codigo": "70201000008", "descripcion": "VUSE ePEN 3 KIT", "cod_barras": "4031300168738"},
{"codigo": "70301000004", "descripcion": "BLU INTENSE POD MANGO APRICOT", "cod_barras": "4031300257005"},
{"codigo": "70301000005", "descripcion": "BLU INTENSE POD TOBACCO", "cod_barras": "4031300257012"},
{"codigo": "80101000016", "descripcion": "DRUM ORIGINAL 30g", "cod_barras": "8710908948766"},
{"codigo": "80101000017", "descripcion": "DRUM BLUE 30g", "cod_barras": "8710908948773"},
{"codigo": "80101000018", "descripcion": "DUCADO AZUL 30g", "cod_barras": "8410016400862"},
{"codigo": "80101000019", "descripcion": "WEST ORIGINAL 30g", "cod_barras": "4001090302876"},
{"codigo": "80101000020", "descripcion": "FORTUNA BLEND 30g", "cod_barras": "8410016001012"},
{"codigo": "80101000021", "descripcion": "MAC BAREN AMSTERDAMER 30g", "cod_barras": "5707294249217"},
{"codigo": "80101000022", "descripcion": "AMBASSADOR ORIGINAL 30g", "cod_barras": "8410016400879"},
{"codigo": "90101000015", "descripcion": "OCB SLIM ULTIMATE 32 LIBRILLOS", "cod_barras": "3057067170153"},
{"codigo": "90101000016", "descripcion": "RIZLA GREEN 50 LIBRILLOS", "cod_barras": "5410113302161"},
{"codigo": "90101000017", "descripcion": "FILTROS RAW 120 UDS", "cod_barras": "716165178502"},
{"codigo": "90101000018", "descripcion": "TUBOS OCB 200 UDS", "cod_barras": "3057067190212"},
{"codigo": "100101000016", "descripcion": "GRINDER RAW 2 PARTES", "cod_barras": "716165178419"},
{"codigo": "100101000017", "descripcion": "PIPA METALICA STANDARD", "cod_barras": "8435047502090"},
{"codigo": "100101000018", "descripcion": "BOLSAS ZIP PEQUEÑAS 100 UDS", "cod_barras": "8424295101025"},
{"codigo": "100101000019", "descripcion": "CLIPPER ENCENDEDOR MINI", "cod_barras": "8412765903271"},
{"codigo": "60101000013", "descripcion": "TEREA MAUVE 20 UDS", "cod_barras": "7630048302094"},
{"codigo": "60101000014", "descripcion": "TEREA SIENNA 20 UDS", "cod_barras": "7630048302100"},
{"codigo": "60101000015", "descripcion": "TEREA TEAK 20 UDS", "cod_barras": "7630048302117"},
{"codigo": "60101000016", "descripcion": "TEREA PURPLE 20 UDS", "cod_barras": "7630048302124"},
{"codigo": "60101000017", "descripcion": "TEREA BRIGHT 20 UDS", "cod_barras": "7630048302131"},
{"codigo": "60101000018", "descripcion": "TEREA INDIGO 20 UDS", "cod_barras": "7630048302148"},
{"codigo": "60101000019", "descripcion": "TEREA TURQUOISE 20 UDS", "cod_barras": "7630048302155"},
{"codigo": "60101000020", "descripcion": "TEREA MARINE 20 UDS", "cod_barras": "7630048302162"},
{"codigo": "60101000021", "descripcion": "TEREA YELLOW SELECTION 20 UDS", "cod_barras": "7630048302179"},
{"codigo": "60102000004", "descripcion": "IQOS LIL SOLID 2.0", "cod_barras": "8809686510801"},
{"codigo": "60102000005", "descripcion": "IQOS ILUMA STANDARD", "cod_barras": "7630048303114"},
{"codigo": "60102000006", "descripcion": "IQOS ILUMA KIT", "cod_barras": "7630048303121"},
{"codigo": "60102000007", "descripcion": "IQOS 2.4 PLUS", "cod_barras": "7630048303077"},
{"codigo": "60102000008", "descripcion": "IQOS ILUMA RING", "cod_barras": "7630048302711"},
{"codigo": "60103000005", "descripcion": "IQOS HEATER CLEANER", "cod_barras": "7630048302728"},
{"codigo": "60103000006", "descripcion": "IQOS TRAVEL CASE", "cod_barras": "7630048302735"},
{"codigo": "70101000005", "descripcion": "VELO URBAN VIBE", "cod_barras": "5704841053945"},
{"codigo": "70101000006", "descripcion": "VELO CITRUS", "cod_barras": "5704841053952"},
{"codigo": "70101000007", "descripcion": "VELO FREEZE", "cod_barras": "5704841053969"},
{"codigo": "70101000008", "descripcion": "VELO ROYAL PURPLE", "cod_barras": "5704841053976"},
{"codigo": "70101000009", "descripcion": "VELO RUBY BERRY", "cod_barras": "5704841053983"},
{"codigo": "70201000005", "descripcion": "VUSE POD POLAR MINT", "cod_barras": "4031300168615"},
{"codigo": "70201000006", "descripcion": "VUSE POD STRAWBERRY", "cod_barras": "4031300168622"},
{"codigo": "70201000007", "descripcion": "VUSE ePOD 2 MINI KIT", "cod_barras": "4031300168721"},
{"codigo": "70201000008", "descripcion": "VUSE ePEN 3 KIT", "cod_barras": "4031300168738"},
{"codigo": "70301000004", "descripcion": "BLU INTENSE POD MANGO APRICOT", "cod_barras": "4031300257005"},
{"codigo": "70301000005", "descripcion": "BLU INTENSE POD TOBACCO", "cod_barras": "4031300257012"},
{"codigo": "80101000016", "descripcion": "DRUM ORIGINAL 30g", "cod_barras": "8710908948766"},
{"codigo": "80101000017", "descripcion": "DRUM BLUE 30g", "cod_barras": "8710908948773"},
{"codigo": "80101000018", "descripcion": "DUCADO AZUL 30g", "cod_barras": "8410016400862"},
{"codigo": "80101000019", "descripcion": "WEST ORIGINAL 30g", "cod_barras": "4001090302876"},
{"codigo": "80101000020", "descripcion": "FORTUNA BLEND 30g", "cod_barras": "8410016001012"},
{"codigo": "80101000021", "descripcion": "MAC BAREN AMSTERDAMER 30g", "cod_barras": "5707294249217"},
{"codigo": "80101000022", "descripcion": "AMBASSADOR ORIGINAL 30g", "cod_barras": "8410016400879"},
{"codigo": "90101000015", "descripcion": "OCB SLIM ULTIMATE 32 LIBRILLOS", "cod_barras": "3057067170153"},
{"codigo": "90101000016", "descripcion": "RIZLA GREEN 50 LIBRILLOS", "cod_barras": "5410113302161"},
{"codigo": "90101000017", "descripcion": "FILTROS RAW 120 UDS", "cod_barras": "716165178502"},
{"codigo": "90101000018", "descripcion": "TUBOS OCB 200 UDS", "cod_barras": "3057067190212"},
{"codigo": "100101000016", "descripcion": "GRINDER RAW 2 PARTES", "cod_barras": "716165178419"},
{"codigo": "100101000017", "descripcion": "PIPA METALICA STANDARD", "cod_barras": "8435047502090"},
{"codigo": "100101000018", "descripcion": "BOLSAS ZIP PEQUEÑAS 100 UDS", "cod_barras": "8424295101025"},
{"codigo": "100101000019", "descripcion": "CLIPPER ENCENDEDOR MINI", "cod_barras": "8412765903271"},
{"codigo": "100101000020", "descripcion": "BIC ENCENDEDOR ELECTRÓNICO", "cod_barras": "3086126903019"},
{"codigo": "100101000021", "descripcion": "CLIPPER ENCENDEDOR MICRO", "cod_barras": "8412765903295"},
{"codigo": "100101000022", "descripcion": "CLIPPER GAS 90ML", "cod_barras": "8412765901819"},
{"codigo": "100101000023", "descripcion": "OCB MAQUINA LIAR SLIM", "cod_barras": "3057067170115"},
{"codigo": "100101000024", "descripcion": "OCB MAQUINA LIAR REGULAR", "cod_barras": "3057067170122"},
{"codigo": "100101000025", "descripcion": "MAQUINA LIAR SMOKING", "cod_barras": "8414775016300"},
{"codigo": "100101000026", "descripcion": "MAQUINA TUBOS SMOKING", "cod_barras": "8414775016324"},
{"codigo": "100101000027", "descripcion": "PAPEL RAW KING SIZE SLIM", "cod_barras": "716165177405"},
{"codigo": "100101000028", "descripcion": "PAPEL RIZLA SILVER KS SLIM", "cod_barras": "5410113302208"},
{"codigo": "100101000029", "descripcion": "PAPEL SMOKING GOLD KS SLIM", "cod_barras": "8414775012159"},
{"codigo": "100101000030", "descripcion": "PAPEL SMOKING BROWN KS SLIM", "cod_barras": "8414775012173"},
{"codigo": "100101000031", "descripcion": "OCB SLIM VIRGIN 32 LIBRILLOS", "cod_barras": "3057067170139"},
{"codigo": "100101000032", "descripcion": "OCB XPERT VIRGIN 50 LIBRILLOS", "cod_barras": "3057067190205"},
{"codigo": "100101000033", "descripcion": "PAPEL OCB BAMBOO KS SLIM", "cod_barras": "3057067170160"},
{"codigo": "100101000034", "descripcion": "RAW BAMBOO KS SLIM 32 LIBRILLOS", "cod_barras": "716165279520"},
{"codigo": "100101000035", "descripcion": "FILTROS OCB VIRGIN 150 UDS", "cod_barras": "3057067180763"},
{"codigo": "100101000036", "descripcion": "FILTROS RAW SLIM 120 UDS", "cod_barras": "716165178397"},
{"codigo": "100101000037", "descripcion": "FILTROS SMOKING WHITE 120 UDS", "cod_barras": "8414775016249"},
{"codigo": "100101000038", "descripcion": "TUBOS RAW 200 UDS", "cod_barras": "716165179851"},
{"codigo": "100101000039", "descripcion": "TUBOS OCB VIRGIN 200 UDS", "cod_barras": "3057067190236"},
{"codigo": "100101000040", "descripcion": "TUBOS RIZLA MENTHOL 100 UDS", "cod_barras": "5410113307029"},
    {"codigo": "60101000013", "descripcion": "TEREA TURQUOISE 20 UDS", "cod_barras": "7630048302094"},
    {"codigo": "60101000014", "descripcion": "TEREA SIENNA 20 UDS", "cod_barras": "7630048302100"},
    {"codigo": "60101000015", "descripcion": "TEREA PURPLE 20 UDS", "cod_barras": "7630048302117"},
    {"codigo": "60101000016", "descripcion": "TEREA FUSION MENTHOL 20 UDS", "cod_barras": "7630048302124"},
    {"codigo": "60101000017", "descripcion": "TEREA MENTHOL 20 UDS", "cod_barras": "7630048302131"},
    {"codigo": "60102000001", "descripcion": "IQOS ILUMA ONE", "cod_barras": "7630048303091"},
    {"codigo": "60102000002", "descripcion": "IQOS ILUMA PRIME", "cod_barras": "7630048303107"},
    {"codigo": "60102000003", "descripcion": "IQOS 3 DUO", "cod_barras": "7630048303084"},
    {"codigo": "60103000001", "descripcion": "IQOS CLEANING STICKS 30U", "cod_barras": "7630048302506"},
    {"codigo": "60103000002", "descripcion": "IQOS ILUMA CAP", "cod_barras": "7630048302704"},
    {"codigo": "60103000003", "descripcion": "IQOS CARGADOR USB", "cod_barras": "7630048302681"},
    {"codigo": "60103000004", "descripcion": "IQOS HOLDER", "cod_barras": "7630048302674"},

    {"codigo": "70101000005", "descripcion": "VELO ROYAL PURPLE", "cod_barras": "5704841053945"},
    {"codigo": "70101000006", "descripcion": "VELO RUBY BERRY", "cod_barras": "5704841053952"},

    {"codigo": "70201000005", "descripcion": "VUSE POD MINT", "cod_barras": "4031300168615"},
    {"codigo": "70201000006", "descripcion": "VUSE POD BLEND 12", "cod_barras": "4031300168622"},
    {"codigo": "70201000007", "descripcion": "VUSE POD CHERRY", "cod_barras": "4031300168639"},
    {"codigo": "70201000008", "descripcion": "VUSE GO WATERMELON ICE", "cod_barras": "4031300168721"},

    {"codigo": "70301000004", "descripcion": "BLU INTENSE POD TOBACCO", "cod_barras": "4031300257005"},
    {"codigo": "70301000005", "descripcion": "BLU INTENSE POD MINT", "cod_barras": "4031300257012"},

    {"codigo": "80101000016", "descripcion": "AMERICAN SPIRIT ORIGINAL BLEND 30g", "cod_barras": "4001012042922"},
    {"codigo": "80101000017", "descripcion": "AMERICAN SPIRIT PERIQUE 30g", "cod_barras": "4001012042939"},
    {"codigo": "80101000018", "descripcion": "WEST ORIGINAL 30g", "cod_barras": "4001090302876"},
    {"codigo": "80101000019", "descripcion": "FINE CUT GOLD 30g", "cod_barras": "5000157118436"},
    {"codigo": "80101000020", "descripcion": "AMBASSADOR AMERICAN BLEND 30g", "cod_barras": "8410016400862"},

    {"codigo": "90101000015", "descripcion": "FILTROS SMOKING RED 120 UDS", "cod_barras": "8414775016256"},
    {"codigo": "90101000016", "descripcion": "RAW ORGANIC 32 LIBRILLOS", "cod_barras": "716165274749"},
    {"codigo": "90101000017", "descripcion": "RAW CLASSIC 1¼ 50 LIBRILLOS", "cod_barras": "716165277320"},
    {"codigo": "90101000018", "descripcion": "OCB PREMIUM 1¼ 25 LIBRILLOS", "cod_barras": "3057067170177"},
    {"codigo": "90101000019", "descripcion": "OCB X-PERT SLIM FIT", "cod_barras": "3057067190212"},
    {"codigo": "100101000016", "descripcion": "CLIPPER ENCENDEDOR MICRO METAL", "cod_barras": "8412765903271"},
    {"codigo": "100101000017", "descripcion": "CLIPPER GAS 90ML", "cod_barras": "8412765901819"},
    {"codigo": "100101000018", "descripcion": "CLIPPER GAS 300ML PACK 3", "cod_barras": "8412765901826"},
    {"codigo": "100101000019", "descripcion": "BIC ENCENDEDOR ELECTRÓNICO", "cod_barras": "3086126903019"},
    {"codigo": "100101000020", "descripcion": "CLIPPER GAS 150ML", "cod_barras": "8412765901833"},
    {"codigo": "100101000021", "descripcion": "OCB MAQUINA LIAR SLIM", "cod_barras": "3057067170115"},
    {"codigo": "100101000022", "descripcion": "OCB MAQUINA LIAR REGULAR", "cod_barras": "3057067170122"},
    {"codigo": "100101000023", "descripcion": "MAQUINA LIAR SMOKING", "cod_barras": "8414775016300"},
    {"codigo": "100101000024", "descripcion": "MAQUINA TUBOS SMOKING", "cod_barras": "8414775016324"},
    {"codigo": "100101000025", "descripcion": "PAPEL RAW KING SIZE SLIM", "cod_barras": "716165177405"},
    {"codigo": "100101000026", "descripcion": "PAPEL RIZLA SILVER KS SLIM", "cod_barras": "5410113302208"},
    {"codigo": "100101000027", "descripcion": "PAPEL SMOKING GOLD KS SLIM", "cod_barras": "8414775012159"},
    {"codigo": "100101000028", "descripcion": "PAPEL SMOKING BROWN KS SLIM", "cod_barras": "8414775012173"},
    {"codigo": "100101000029", "descripcion": "OCB SLIM VIRGIN 32 LIBRILLOS", "cod_barras": "3057067170139"},
    {"codigo": "100101000030", "descripcion": "OCB XPERT VIRGIN 50 LIBRILLOS", "cod_barras": "3057067190205"},
    {"codigo": "100101000031", "descripcion": "PAPEL OCB BAMBOO KS SLIM", "cod_barras": "3057067170160"},
    {"codigo": "100101000032", "descripcion": "RAW BAMBOO KS SLIM 32 LIBRILLOS", "cod_barras": "716165279520"},
    {"codigo": "100101000033", "descripcion": "FILTROS OCB VIRGIN 150 UDS", "cod_barras": "3057067180763"},
    {"codigo": "100101000034", "descripcion": "FILTROS RAW SLIM 120 UDS", "cod_barras": "716165178397"},
    {"codigo": "100101000035", "descripcion": "FILTROS SMOKING WHITE 120 UDS", "cod_barras": "8414775016249"},
    {"codigo": "100101000036", "descripcion": "TUBOS RAW 200 UDS", "cod_barras": "716165179851"},
    {"codigo": "100101000037", "descripcion": "TUBOS OCB VIRGIN 200 UDS", "cod_barras": "3057067190236"},
    {"codigo": "100101000038", "descripcion": "TUBOS RIZLA MENTHOL 100 UDS", "cod_barras": "5410113307029"}
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
    return render_template('inventario.html', productos=productos_sql)

@app.route('/agregar_producto', methods=('GET', 'POST'))
@login_requerido
def agregar_producto():
    mensaje = ""
    if request.method == 'POST':
        codigo = request.form['codigo']
        descripcion = request.form['descripcion']
        cod_barras = request.form['cod_barras']
        tienda = request.form['tienda']

        conn = get_db_connection()
        # Comprueba si ya existe el código en la misma tienda
        existe = conn.execute(
            "SELECT * FROM productos WHERE codigo = ? AND tienda = ?",
            (codigo, tienda)
        ).fetchone()
        if existe:
            mensaje = "¡Ya existe un producto con ese código en esa tienda!"
            conn.close()
            return render_template('agregar_producto.html', mensaje=mensaje, tiendas=tiendas)
        else:
            # Si tu tabla 'productos' NO tiene el campo 'stock':
            conn.execute(
                'INSERT INTO productos (codigo, descripcion, cod_barras, tienda) VALUES (?, ?, ?, ?)',
                (codigo, descripcion, cod_barras, tienda)
            )
            # Si tu tabla 'productos' SÍ tiene el campo 'stock' y NO es NOT NULL, puedes poner 0 o NULL:
            # conn.execute(
            #     'INSERT INTO productos (codigo, descripcion, cod_barras, stock, tienda) VALUES (?, ?, ?, ?, ?)',
            #     (codigo, descripcion, cod_barras, 0, tienda)
            # )
            conn.commit()
            conn.close()
            return redirect(url_for('inventario'))

    return render_template('agregar_producto.html', mensaje=mensaje, tiendas=tiendas)

from flask import send_file, make_response
import pandas as pd
import io
from xhtml2pdf import pisa

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
                    'INSERT INTO conteos_fisicos (tienda, codigo, descripcion, cod_barras, stock_fisico, fecha) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
                    (tienda, producto['codigo'], producto['descripcion'], producto['cod_barras'], cantidad_num)
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
    if tienda_seleccionada:
        conteos = conn.execute(
            'SELECT * FROM conteos_fisicos WHERE tienda = ? ORDER BY rowid DESC',
            (tienda_seleccionada,)
        ).fetchall()
    else:
        conteos = conn.execute(
            'SELECT * FROM conteos_fisicos ORDER BY rowid DESC'
        ).fetchall()
    conn.close()
    return render_template('conteos_fisicos.html', conteos=conteos, tiendas=tiendas, tienda_seleccionada=tienda_seleccionada)

@app.route('/eliminar_todos_conteos', methods=['POST', 'GET'])
@login_requerido
def eliminar_todos_conteos():
    conn = get_db_connection()
    # Si quieres borrar solo de una tienda, usa algo como:
    # tienda = request.args.get('tienda', '') o request.form['tienda']
    # conn.execute('DELETE FROM conteos_fisicos WHERE tienda = ?', (tienda,))
    # Si quieres borrar todos:
    conn.execute('DELETE FROM conteos_fisicos')
    conn.commit()
    conn.close()
    return redirect(url_for('conteos_fisicos'))

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

@app.route('/eliminar_conteo/<int:id>', methods=['POST', 'GET'])
@login_requerido
def eliminar_conteo(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM conteos_fisicos WHERE id = ?', (id,))
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
    conn.close()

    # Decodifica el JSON de productos para cada histórico
    historicos_lista = []
    for h in historicos:
        try:
            productos = json.loads(h['productos_json'])
        except Exception:
            productos = []
        historicos_lista.append({
            "id": h['id'],
            "autor": h['autor'],
            "tienda": h['tienda'],
            "fecha": h['fecha'],
            "productos": productos
        })
    return render_template('inventario_historico.html', historicos=historicos_lista)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Railway te asigna el puerto por variable de entorno
    app.run(host="0.0.0.0", port=port)

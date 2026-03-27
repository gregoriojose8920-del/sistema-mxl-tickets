from flask import Flask, render_template_string, redirect, url_for, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Carpeta de Fotos
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    db_path = '/tmp/mxl_tickets.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Tabla de Stock con división por método de pago
    cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
        tipo TEXT PRIMARY KEY, total INTEGER, vendidos INTEGER, precio REAL,
        efectivo REAL DEFAULT 0, tarjeta REAL DEFAULT 0, transf REAL DEFAULT 0
    )''')
    cursor.execute('CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nombre TEXT, logo TEXT, color TEXT)')
    
    cursor.execute("INSERT OR IGNORE INTO config (id, nombre, logo, color) VALUES (1, 'SISTEMA MXL PRO', '', '#D4AF37')")
    data = [('VIP', 1000, 0, 1500.0), ('Regular', 3500, 0, 500.0), ('Guest', 500, 0, 0.0)]
    for d in data:
        cursor.execute("INSERT OR IGNORE INTO stock (tipo, total, vendidos, precio) VALUES (?,?,?,?)", d)
    conn.commit()
    conn.close()

# --- VISTA DE VENTAS CON AVISO DE TARJETA ---
HTML_VENTAS = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <title>{{ conf[1] }}</title>
    <style>
        :root { --main: {{ conf[3] }}; }
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; margin: 0; padding: 10px; }
        .logo { max-width: 100px; margin: 10px; border-radius: 8px; }
        .card { background: #1E1E1E; border-radius: 15px; margin-bottom: 15px; padding: 15px; border-top: 5px solid var(--main); }
        .btn-group { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 15px; }
        .btn-pago { background: var(--main); color: black; padding: 15px 5px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 0.8em; border: none; cursor: pointer; }
        /* Ventana de confirmación Tarjeta */
        .modal { display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); }
        .modal-content { background: #fff; color: #000; margin: 20% auto; padding: 20px; border-radius: 15px; width: 80%; max-width: 300px; }
    </style>
    <script>
        function confirmarTarjeta(tipo, precio) {
            if(confirm("¿El Verifone aprobó la transacción de RD$ " + precio + "?")) {
                window.location.href = "/vender/" + tipo + "/tarjeta";
            }
        }
    </script>
</head>
<body>
    {% if conf[2] %}<img src="/uploads/{{ conf[2] }}" class="logo">{% endif %}
    <h1>{{ conf[1] }}</h1>
    
    {% for s in data %}
    <div class="card">
        <h3>{{ s[0] }} - RD$ {{ "{:,.0f}".format(s[3]) }}</h3>
        <div class="btn-group">
            <a href="/vender/{{ s[0] }}/efectivo" class="btn-pago">💵 EFECT.</a>
            <button onclick="confirmarTarjeta('{{ s[0] }}', '{{ s[3] }}')" class="btn-pago">💳 TARJETA</button>
            <a href="/vender/{{ s[0] }}/transf" class="btn-pago">📱 TRANSF.</a>
        </div>
    </div>
    {% endfor %}
</body>
</html>"""

# --- PANEL ADMIN CON CUADRE DETALLADO ---
HTML_ADMIN = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #f4f4f4; padding: 15px; }
        .box { background: white; padding: 20px; border-radius: 15px; max-width: 500px; margin: auto; }
        .cuadre { background: #121212; color: #fff; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
        .val { color: #4CAF50; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h2>📊 CUADRE DE CAJA</h2>
        <div class="cuadre">
            <p>💵 Efectivo: <span class="val">RD$ {{ "{:,.2f}".format(total_efectivo) }}</span></p>
            <p>💳 Tarjeta: <span class="val">RD$ {{ "{:,.2f}".format(total_tarjeta) }}</span></p>
            <p>📱 Transf: <span class="val">RD$ {{ "{:,.2f}".format(total_transf) }}</span></p>
            <hr>
            <h2 style="margin:0;">TOTAL: RD$ {{ "{:,.2f}".format(total_efectivo + total_tarjeta + total_transf) }}</h2>
        </div>
        
        <form action="/update_all" method="POST" enctype="multipart/form-data">
            <input type="text" name="nombre" value="{{ conf[1] }}" placeholder="Nombre Negocio" style="width:100%; padding:10px; margin-bottom:10px;">
            <input type="file" name="logo_file" style="margin-bottom:10px;">
            <input type="color" name="color" value="{{ conf[3] }}" style="width:100%; height:40px; margin-bottom:10px;">
            <button type="submit" style="width:100%; padding:15px; background:#27ae60; color:white; border:none; border-radius:10px; font-weight:bold;">GUARDAR CAMBIOS</button>
        </form>
        <br><a href="/" style="display:block; text-align:center; color:blue;">Ver Ventas</a>
    </div>
</body>
</html>"""

@app.route('/uploads/<filename>')
def uploaded_file(filename): return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    init_db()
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    data = conn.execute('SELECT * FROM stock').fetchall()
    conf = conn.execute('SELECT * FROM config WHERE id = 1').fetchone()
    conn.close()
    return render_template_string(HTML_VENTAS, data=data, conf=conf)

@app.route('/admin-mxl')
def admin():
    init_db()
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    data = conn.execute('SELECT * FROM stock').fetchall()
    conf = conn.execute('SELECT * FROM config WHERE id = 1').fetchone()
    total_efectivo = sum(row[4] for row in data)
    total_tarjeta = sum(row[5] for row in data)
    total_transf = sum(row[6] for row in data)
    conn.close()
    return render_template_string(HTML_ADMIN, data=data, conf=conf, total_efectivo=total_efectivo, total_tarjeta=total_tarjeta, total_transf=total_transf)

@app.route('/vender/<tipo>/<metodo>')
def vender(tipo, metodo):
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    # Actualizamos el contador de ventas y sumamos al método de pago correspondiente
    conn.execute(f'UPDATE stock SET vendidos = vendidos + 1, {metodo} = {metodo} + precio WHERE tipo = ?', (tipo,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update_all', methods=['POST'])
def update_all():
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    file = request.files.get('logo_file')
    if file and file.filename != '':
        filename = "logo_cliente.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn.execute('UPDATE config SET nombre=?, logo=?, color=? WHERE id=1', (request.form['nombre'], filename, request.form['color']))
    else:
        conn.execute('UPDATE config SET nombre=?, color=? WHERE id=1', (request.form['nombre'], request.form['color']))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)

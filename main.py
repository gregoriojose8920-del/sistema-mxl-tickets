from flask import Flask, render_template_string, redirect, url_for, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Carpeta Multimedia
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    db_path = '/tmp/mxl_tickets.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Tabla de Tickets con Dinero Recaudado
    cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
        tipo TEXT PRIMARY KEY, total INTEGER, vendidos INTEGER, precio REAL, recaudado REAL DEFAULT 0
    )''')
    # Tabla de Configuración
    cursor.execute('CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nombre TEXT, logo TEXT, color TEXT)')
    
    cursor.execute("INSERT OR IGNORE INTO config (id, nombre, logo, color) VALUES (1, 'SISTEMA MXL PRO', '', '#D4AF37')")
    data = [('VIP', 1000, 0, 1500.0, 0), ('Regular', 3500, 0, 500.0, 0), ('Guest', 500, 0, 0.0, 0)]
    for d in data:
        cursor.execute("INSERT OR IGNORE INTO stock (tipo, total, vendidos, precio, recaudado) VALUES (?,?,?,?,?)", d)
    conn.commit()
    conn.close()

# --- DISEÑO DE VENTAS (MODO POS) ---
HTML_VENTAS = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <title>{{ conf[1] }}</title>
    <style>
        :root { --main: {{ conf[3] }}; }
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; margin: 0; padding: 10px; }
        .logo { max-width: 120px; border-radius: 10px; margin-top: 10px; }
        h1 { color: var(--main); margin: 5px 0; text-transform: uppercase; }
        .card { background: #1E1E1E; border-radius: 15px; margin-bottom: 15px; padding: 15px; border-top: 4px solid var(--main); }
        .price { color: #4CAF50; font-size: 1.4em; font-weight: bold; }
        .pay-options { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; margin-top: 10px; }
        .btn-pay { background: var(--main); color: black; text-decoration: none; padding: 12px 5px; border-radius: 8px; font-weight: bold; font-size: 0.8em; }
        .btn-pay:active { transform: scale(0.95); opacity: 0.8; }
    </style>
</head>
<body>
    {% if conf[2] %}<img src="/uploads/{{ conf[2] }}" class="logo">{% endif %}
    <h1>{{ conf[1] }}</h1>
    
    {% for s in data %}
    <div class="card">
        <h3>{{ s[0] }} - RD$ {{ "{:,.0f}".format(s[3]) }}</h3>
        <p style="font-size:0.8em; color:#888;">Disponibles: {{ s[1] - s[2] }}</p>
        <div class="pay-options">
            <a href="/vender/{{ s[0] }}/Efectivo" class="btn-pay">💵 Efectivo</a>
            <a href="/vender/{{ s[0] }}/Transf" class="btn-pay">📱 Transf.</a>
            <a href="/vender/{{ s[0] }}/Tarjeta" class="btn-pay">💳 Tarjeta</a>
        </div>
    </div>
    {% endfor %}
</body>
</html>"""

# --- PANEL ADMIN CON RECAUDACIÓN ---
HTML_ADMIN = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 15px; }
        .box { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        .total-box { background: #121212; color: #4CAF50; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        input { width: 100%; padding: 10px; margin: 8px 0; border-radius: 5px; border: 1px solid #ddd; box-sizing: border-box; }
        .btn-save { background: #27ae60; color: white; width: 100%; padding: 15px; border: none; border-radius: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h2>💰 RECAUDACIÓN TOTAL</h2>
        <div class="total-box">
            <h1 style="margin:0;">RD$ {{ "{:,.2f}".format(total_dinero) }}</h1>
        </div>
        
        <form action="/update_all" method="POST" enctype="multipart/form-data">
            <h3>⚙️ Personalización</h3>
            <label>Nombre Cliente:</label><input type="text" name="nombre" value="{{ conf[1] }}">
            <label>Logo Multimedia:</label><input type="file" name="logo_file" accept="image/*">
            <label>Color:</label><input type="color" name="color" value="{{ conf[3] }}" style="height:40px;">
            
            <hr>
            <h3>Precios</h3>
            {% for s in data %}
            <label>{{ s[0] }}:</label><input type="number" name="precio_{{ s[0] }}" value="{{ s[3] }}">
            {% endfor %}
            
            <button type="submit" class="btn-save">GUARDAR Y REINICIAR DÍA</button>
        </form>
        <br><a href="/" style="display:block; text-align:center;">Ir a Pantalla de Ventas</a>
    </div>
</body>
</html>"""

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
    total_dinero = sum(row[4] for row in data)
    conn.close()
    return render_template_string(HTML_ADMIN, data=data, conf=conf, total_dinero=total_dinero)

@app.route('/vender/<tipo>/<metodo>')
def vender(tipo, metodo):
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    # Sumar uno vendido y sumar el precio al recaudado
    conn.execute('UPDATE stock SET vendidos = vendidos + 1, recaudado = recaudado + precio WHERE tipo = ?', (tipo,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update_all', methods=['POST'])
def update_all():
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    # Actualizar config y precios (igual que antes)
    file = request.files.get('logo_file')
    if file and file.filename != '':
        filename = "logo_cliente.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn.execute('UPDATE config SET nombre=?, logo=?, color=? WHERE id=1', (request.form['nombre'], filename, request.form['color']))
    else:
        conn.execute('UPDATE config SET nombre=?, color=? WHERE id=1', (request.form['nombre'], request.form['color']))
    
    for tipo in ['VIP', 'Regular', 'Guest']:
        precio = request.form.get(f'precio_{tipo}')
        if precio: conn.execute('UPDATE stock SET precio=? WHERE tipo=?', (precio, tipo))
    
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)

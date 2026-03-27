from flask import Flask, render_template_string, redirect, url_for, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Configuración de carpetas para guardar las fotos multimedia
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    db_path = '/tmp/mxl_tickets.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS stock (tipo TEXT PRIMARY KEY, total INTEGER, vendidos INTEGER, precio REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nombre TEXT, logo TEXT, color TEXT)')
    
    # Datos iniciales
    cursor.execute("INSERT OR IGNORE INTO config (id, nombre, logo, color) VALUES (1, 'SISTEMA MXL', '', '#D4AF37')")
    data = [('VIP', 1000, 0, 1500.0), ('Regular', 3500, 0, 500.0), ('Guest', 500, 0, 0.0)]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# Ruta para que el navegador pueda ver la imagen guardada
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- VISTA DE VENTAS ---
HTML_VENTAS = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ conf[1] }}</title>
    <style>
        :root { --main-color: {{ conf[3] }}; }
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; margin: 0; padding: 15px; }
        .header { padding: 20px; border-bottom: 2px solid var(--main-color); margin-bottom: 20px; }
        .logo { max-width: 150px; height: auto; margin-bottom: 10px; border-radius: 10px; }
        h1 { color: var(--main-color); margin: 0; text-transform: uppercase; }
        .card { background: #1E1E1E; border-radius: 15px; margin-bottom: 15px; padding: 20px; border-left: 6px solid var(--main-color); }
        .btn-vender { background: var(--main-color); color: black; text-decoration: none; padding: 18px; border-radius: 12px; display: block; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        {% if conf[2] %}
            <img src="/uploads/{{ conf[2] }}" class="logo">
        {% endif %}
        <h1>{{ conf[1] }}</h1>
    </div>
    {% for s in data %}
    <div class="card">
        <h2>{{ s[0] }}</h2>
        <div style="color:#4CAF50; font-size:1.5em; font-weight:bold;">RD$ {{ "{:,.2f}".format(s[3]) }}</div>
        <p>Disponibles: {{ s[1] - s[2] }}</p>
        <a href="/vender/{{ s[0] }}" class="btn-vender">VENDER {{ s[0] }}</a>
    </div>
    {% endfor %}
</body>
</html>"""

# --- VISTA DE ADMIN CON SUBIDA DE ARCHIVOS ---
HTML_ADMIN = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CONFIGURACIÓN MULTIMEDIA</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
        .panel { background: white; padding: 20px; border-radius: 15px; max-width: 450px; margin: auto; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; }
        .btn-save { background: #27ae60; color: white; border: none; width: 100%; padding: 18px; border-radius: 12px; font-weight: bold; font-size: 1.1em; cursor: pointer; }
    </style>
</head>
<body>
    <div class="panel">
        <h2>⚙️ Personalizar Sistema</h2>
        <form action="/update_all" method="POST" enctype="multipart/form-data">
            <label><b>Nombre del Cliente:</b></label>
            <input type="text" name="nombre" value="{{ conf[1] }}">
            
            <label><b>Subir Logo (Multimedia):</b></label>
            <input type="file" name="logo_file" accept="image/*">
            
            <label><b>Color de Marca:</b></label>
            <input type="color" name="color" value="{{ conf[3] }}" style="height:50px;">

            <hr>
            <h3>Precios de Tickets</h3>
            {% for s in data %}
            <label>Precio {{ s[0] }}:</label>
            <input type="number" name="precio_{{ s[0] }}" value="{{ s[3] }}" step="0.01">
            {% endfor %}
            
            <button type="submit" class="btn-save">GUARDAR Y APLICAR</button>
        </form>
        <br><a href="/" style="display:block; text-align:center; color:#666;">Ver Pantalla de Ventas</a>
    </div>
</body>
</html>"""

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
    conn.close()
    return render_template_string(HTML_ADMIN, data=data, conf=conf)

@app.route('/vender/<tipo>')
def vender(tipo):
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    conn.execute('UPDATE stock SET vendidos = vendidos + 1 WHERE tipo = ?', (tipo,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update_all', methods=['POST'])
def update_all():
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    nombre = request.form['nombre']
    color = request.form['color']
    
    # Manejo del archivo multimedia (Logo)
    file = request.files.get('logo_file')
    if file and file.filename != '':
        filename = "logo_cliente.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn.execute('UPDATE config SET nombre=?, logo=?, color=? WHERE id=1', (nombre, filename, color))
    else:
        conn.execute('UPDATE config SET nombre=?, color=? WHERE id=1', (nombre, color))

    for tipo in ['VIP', 'Regular', 'Guest']:
        precio = request.form.get(f'precio_{tipo}')
        if precio: conn.execute('UPDATE stock SET precio=? WHERE tipo=?', (precio, tipo))
    
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)

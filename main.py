from flask import Flask, render_template_string, redirect, url_for, request
import sqlite3
import os

app = Flask(__name__)

def init_db():
    db_path = '/tmp/mxl_tickets.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Tabla de Tickets
    cursor.execute('CREATE TABLE IF NOT EXISTS stock (tipo TEXT PRIMARY KEY, total INTEGER, vendidos INTEGER, precio REAL)')
    # Tabla de Configuración (Logo, Nombre, Color)
    cursor.execute('CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nombre TEXT, logo TEXT, color TEXT)')
    
    # Datos por defecto
    cursor.execute("INSERT OR IGNORE INTO config (id, nombre, logo, color) VALUES (1, 'SISTEMA MXL', '', '#D4AF37')")
    data = [('VIP', 1000, 0, 1500.0), ('Regular', 3500, 0, 500.0), ('Guest', 500, 0, 0.0)]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# --- DISEÑO ÚNICO (Se adapta al color que elijas) ---
HTML_VENTAS = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ conf[1] }}</title>
    <style>
        :root { --main-color: {{ conf[3] }}; }
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; margin: 0; padding: 15px; }
        .header { padding: 20px; border-bottom: 2px solid var(--main-color); margin-bottom: 20px; }
        .logo { max-width: 120px; margin-bottom: 10px; border-radius: 10px; }
        h1 { color: var(--main-color); margin: 0; text-transform: uppercase; }
        .card { background: #1E1E1E; border-radius: 15px; margin-bottom: 15px; padding: 20px; border-left: 6px solid var(--main-color); }
        .price { color: #4CAF50; font-size: 1.5em; font-weight: bold; }
        .btn-vender { background: var(--main-color); color: black; text-decoration: none; padding: 18px; border-radius: 12px; display: block; font-weight: bold; font-size: 1.2em; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        {% if conf[2] %}<img src="{{ conf[2] }}" class="logo">{% endif %}
        <h1>{{ conf[1] }}</h1>
    </div>
    {% for s in data %}
    <div class="card">
        <h2>{{ s[0] }}</h2>
        <div class="price">RD$ {{ "{:,.2f}".format(s[3]) }}</div>
        <p>Disponibles: {{ s[1] - s[2] }}</p>
        <a href="/vender/{{ s[0] }}" class="btn-vender">VENDER {{ s[0] }}</a>
    </div>
    {% endfor %}
</body>
</html>"""

HTML_ADMIN = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CONFIGURACIÓN MXL</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
        .panel { background: white; padding: 20px; border-radius: 15px; max-width: 450px; margin: auto; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        h2 { border-bottom: 2px solid #333; padding-bottom: 10px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; }
        .btn-save { background: #27ae60; color: white; border: none; width: 100%; padding: 15px; border-radius: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="panel">
        <h2>⚙️ Configuración del Cliente</h2>
        <form action="/update_all" method="POST">
            <label>Nombre del Negocio:</label>
            <input type="text" name="nombre" value="{{ conf[1] }}">
            
            <label>Link del Logo (URL):</label>
            <input type="text" name="logo" value="{{ conf[2] }}" placeholder="https://imagen.com/logo.png">
            
            <label>Color del Sistema (Hex):</label>
            <input type="color" name="color" value="{{ conf[3] }}" style="height:50px;">

            <hr>
            <h3>Precios</h3>
            {% for s in data %}
            <label>Precio {{ s[0] }}:</label>
            <input type="number" name="precio_{{ s[0] }}" value="{{ s[3] }}" step="0.01">
            {% endfor %}
            
            <button type="submit" class="btn-save">GUARDAR TODO Y APLICAR</button>
        </form>
        <br><a href="/">Ver Pantalla de Ventas</a>
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
    # Actualizar Config
    conn.execute('UPDATE config SET nombre=?, logo=?, color=? WHERE id=1', 
                 (request.form['nombre'], request.form['logo'], request.form['color']))
    # Actualizar Precios
    for tipo in ['VIP', 'Regular', 'Guest']:
        precio = request.form.get(f'precio_{tipo}')
        if precio: conn.execute('UPDATE stock SET precio=? WHERE tipo=?', (precio, tipo))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)

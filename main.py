from flask import Flask, render_template_string, redirect, url_for, request
import sqlite3
import os

app = Flask(__name__)

def init_db():
    db_path = '/tmp/mxl_tickets.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            tipo TEXT PRIMARY KEY, total INTEGER, vendidos INTEGER, precio REAL
        )
    ''')
    data = [('VIP', 1000, 0, 1500.0), ('Regular', 3500, 0, 500.0), ('Guest', 500, 0, 0.0)]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# --- DISEÑO PARA EL VENDEDOR (PÚBLICO) ---
HTML_VENDEDOR = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MXL - VENTAS</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 15px; }
        .card { background: #1E1E1E; border-radius: 15px; margin-bottom: 15px; padding: 20px; border-left: 6px solid #D4AF37; }
        .btn-vender { background: #D4AF37; color: black; text-decoration: none; padding: 18px; border-radius: 12px; display: block; font-weight: bold; font-size: 1.2em; margin-top: 10px; }
        h1 { color: #D4AF37; }
        .price { color: #4CAF50; font-size: 1.3em; font-weight: bold; }
    </style>
</head>
<body>
    <h1>SISTEMA MXL</h1>
    <p>PUNTO DE VENTA AUTOMÁTICO</p>
    {% for s in data %}
    <div class="card">
        <h2>{{ s[0] }}</h2>
        <div class="price">RD$ {{ "{:,.2f}".format(s[3]) }}</div>
        <p>Disponibles: <b>{{ s[1] - s[2] }}</b></p>
        <a href="/vender/{{ s[0] }}" class="btn-vender">VENDER {{ s[0] }}</a>
    </div>
    {% endfor %}
</body>
</html>"""

# --- DISEÑO PARA EL ADMINISTRADOR (SOLO TÚ) ---
HTML_ADMIN = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MXL - PANEL CONTROL</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f4; color: #333; padding: 20px; }
        .panel { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        h1 { color: #121212; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }
        .row { margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #ddd; }
        input { width: 100%; padding: 10px; margin-top: 5px; border-radius: 5px; border: 1px solid #ccc; font-size: 1.1em; }
        .btn-save { background: #2ecc71; color: white; border: none; width: 100%; padding: 15px; border-radius: 10px; font-weight: bold; font-size: 1.1em; cursor: pointer; }
        .back { display: block; text-align: center; margin-top: 20px; color: #666; text-decoration: none; }
    </style>
</head>
<body>
    <div class="panel">
        <h1>⚙️ Ajustes de Precios</h1>
        <form action="/update_prices" method="POST">
            {% for s in data %}
            <div class="row">
                <label>Precio de <b>{{ s[0] }}</b>:</label>
                <input type="number" name="precio_{{ s[0] }}" value="{{ s[3] }}" step="0.01">
            </div>
            {% endfor %}
            <button type="submit" class="btn-save">GUARDAR CAMBIOS</button>
        </form>
        <a href="/" class="back">← Volver a Ventas</a>
    </div>
</body>
</html>"""

@app.route('/')
def index():
    init_db()
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    data = conn.execute('SELECT * FROM stock').fetchall()
    conn.close()
    return render_template_string(HTML_VENDEDOR, data=data)

@app.route('/admin-mxl') # RUTA SECRETA
def admin():
    init_db()
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    data = conn.execute('SELECT * FROM stock').fetchall()
    conn.close()
    return render_template_string(HTML_ADMIN, data=data)

@app.route('/vender/<tipo>')
def vender(tipo):
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    conn.execute('UPDATE stock SET vendidos = vendidos + 1 WHERE tipo = ? AND vendidos < total', (tipo,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update_prices', methods=['POST'])
def update_prices():
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    for tipo in ['VIP', 'Regular', 'Guest']:
        nuevo_precio = request.form.get(f'precio_{tipo}')
        if nuevo_precio:
            conn.execute('UPDATE stock SET precio = ? WHERE tipo = ?', (nuevo_precio, tipo))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

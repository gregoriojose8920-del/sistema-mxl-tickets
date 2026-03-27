from flask import Flask, render_template_string, redirect, url_for, request
import sqlite3
import os

app = Flask(__name__)

# Configuración de la base de datos para los 5,000 tickets
def init_db():
    db_path = '/tmp/mxl_tickets.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            tipo TEXT PRIMARY KEY, 
            total INTEGER, 
            vendidos INTEGER, 
            precio REAL
        )
    ''')
    # Datos iniciales (VIP: 1000, Regular: 3500, Guest: 500)
    data = [
        ('VIP', 1000, 0, 1500.0), 
        ('Regular', 3500, 0, 500.0), 
        ('Guest', 500, 0, 0.0)
    ]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# --- VISTA PARA EL CLIENTE/VENDEDOR (PÚBLICA) ---
HTML_VENTAS = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA MXL - VENTAS</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; margin: 0; padding: 15px; }
        .header { padding: 20px; border-bottom: 2px solid #D4AF37; margin-bottom: 20px; }
        h1 { color: #D4AF37; margin: 0; letter-spacing: 2px; text-transform: uppercase; }
        .card { background: #1E1E1E; border-radius: 15px; margin-bottom: 15px; padding: 20px; border-left: 6px solid #D4AF37; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .price { color: #4CAF50; font-size: 1.5em; font-weight: bold; margin: 10px 0; }
        .stock-info { color: #aaa; font-size: 0.9em; }
        .btn-vender { background: #D4AF37; color: black; text-decoration: none; padding: 18px; border-radius: 12px; display: block; font-weight: bold; font-size: 1.2em; margin-top: 10px; transition: 0.2s; }
        .btn-vender:active { background: #b8972f; transform: scale(0.95); }
    </style>
</head>
<body>
    <div class="header">
        <h1>SISTEMA MXL</h1>
        <p>VENTA DE TICKETS</p>
    </div>
    {% for s in data %}
    <div class="card">
        <h2>{{ s[0] }}</h2>
        <div class="price">RD$ {{ "{:,.2f}".format(s[3]) }}</div>
        <p class="stock-info">Disponibles: <b>{{ s[1] - s[2] }}</b> / {{ s[1] }}</p>
        <a href="/vender/{{ s[0] }}" class="btn-vender">VENDER {{ s[0] }}</a>
    </div>
    {% endfor %}
</body>
</html>"""

# --- VISTA PARA EL DUEÑO/ADMIN (SECRETA) ---
HTML_ADMIN = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MXL - ADMIN</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; color: #333; padding: 20px; }
        .admin-panel { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 450px; margin: auto; }
        h1 { color: #121212; border-bottom: 3px solid #D4AF37; padding-bottom: 10px; }
        .form-group { margin-bottom: 20px; text-align: left; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
        input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd; font-size: 1.1em; box-sizing: border-box; }
        .btn-save { background: #27ae60; color: white; border: none; width: 100%; padding: 18px; border-radius: 12px; font-weight: bold; font-size: 1.1em; margin-top: 10px; cursor: pointer; }
        .btn-save:active { background: #219150; }
        .footer-link { display: block; text-align: center; margin-top: 20px; color: #888; text-decoration: none; }
    </style>
</head>
<body>
    <div class="admin-panel">
        <h1>⚙️ Ajustes de Precios</h1>
        <p>Cambia el valor de los tickets aquí:</p>
        <form action="/update_prices" method="POST">
            {% for s in data %}
            <div class="form-group">
                <label>Precio Ticket {{ s[0] }}:</label>
                <input type="number" name="precio_{{ s[0] }}" value="{{ s[3] }}" step="0.01">
            </div>
            {% endfor %}
            <button type="submit" class="btn-save">GUARDAR CAMBIOS</button>
        </form>
        <a href="/" class="footer-link">← Volver a Ventas</a>
    </div>
</body>
</html>"""

@app.route('/')
def index():
    init_db()
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    data = conn.execute('SELECT * FROM stock').fetchall()
    conn.close()
    return render_template_string(HTML_VENTAS, data=data)

@app.route('/admin-mxl')
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
    return redirect(url_for('index'))

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

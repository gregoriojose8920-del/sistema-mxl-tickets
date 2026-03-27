from flask import Flask, render_template_string, redirect
import sqlite3
import os

app = Flask(__name__)

# Configuración de la base de datos de los 5,000 boletos
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
    data = [('VIP', 1000, 0, 1500), ('Regular', 3500, 0, 500), ('Guest', 500, 0, 0)]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tickets MXL</title>
    <style>
        body { font-family: sans-serif; background: #1a1a1a; color: white; text-align: center; padding: 20px; }
        .card { background: #333; margin-bottom: 20px; padding: 20px; border-radius: 15px; border-left: 8px solid gold; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .btn { background: gold; color: black; padding: 15px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; margin-top: 10px; font-size: 1.2em; }
        h1 { color: gold; text-transform: uppercase; }
        .info { font-size: 0.9em; color: #aaa; margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>SISTEMA MXL - VENTAS</h1>
    <p class="info">Capacidad Total: 5,000 Tickets</p>
    {% for s in data %}
    <div class="card">
        <h2>{{ s[0] }}</h2>
        <p>Precio: ${{ s[3] }} | Disponibles: {{ s[1] - s[2] }}</p>
        <a href="/vender/{{ s[0] }}" class="btn">VENDER {{ s[0] }}</a>
    </div>
    {% endfor %}
</body>
</html>"""

@app.route('/')
def index():
    init_db()
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    data = conn.execute('SELECT * FROM stock').fetchall()
    conn.close()
    return render_template_string(HTML, data=data)

@app.route('/vender/<tipo>')
def vender(tipo):
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    conn.execute('UPDATE stock SET vendidos = vendidos + 1 WHERE tipo = ? AND vendidos < total', (tipo,))
    conn.commit()
    conn.close()
    return redirect('/')

# ESTO ES LO QUE CAMBIAMOS PARA QUE FUNCIONE EN RAILWAY
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Agregamos threaded=True para que el celular y Railway no se traben
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

from flask import Flask, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Base de datos optimizada para MXL
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
    data = [
        ('VIP', 1000, 0, 1500.00), 
        ('Regular', 3500, 0, 500.00), 
        ('Guest', 500, 0, 0.00)
    ]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# DISEÑO MAESTRO - ESTILO APP PROFESIONAL
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SISTEMA MXL PRO</title>
    <style>
        :root { --gold: #D4AF37; --dark: #121212; --card: #1E1E1E; --text: #E0E0E0; }
        body { font-family: 'Segoe UI', Roboto, sans-serif; background: var(--dark); color: var(--text); margin: 0; padding: 10px; }
        .header { background: linear-gradient(145deg, #1e1e1e, #121212); padding: 25px 10px; border-bottom: 2px solid var(--gold); margin-bottom: 20px; border-radius: 0 0 20px 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: var(--gold); margin: 0; font-size: 1.8em; text-transform: uppercase; letter-spacing: 3px; }
        .container { max-width: 500px; margin: auto; }
        .card { background: var(--card); border-radius: 20px; margin-bottom: 15px; padding: 20px; border: 1px solid #333; position: relative; overflow: hidden; box-shadow: 0 8px 16px rgba(0,0,0,0.3); transition: transform 0.2s; }
        .card:active { transform: scale(0.98); }
        .card::before { content: ''; position: absolute; left: 0; top: 0; height: 100%; width: 6px; background: var(--gold); }
        h2 { margin: 0; color: var(--gold); font-size: 1.5em; }
        .stats { display: flex; justify-content: space-between; margin: 15px 0; font-size: 1.1em; border-top: 1px solid #333; padding-top: 10px; }
        .price { font-weight: bold; color: #4CAF50; }
        .available { font-weight: bold; }
        .btn { background: var(--gold); color: black; text-decoration: none; padding: 18px; border-radius: 12px; display: block; font-weight: 800; font-size: 1.2em; text-transform: uppercase; text-align: center; box-shadow: 0 4px 0 #997a1d; transition: all 0.1s; }
        .btn:active { box-shadow: 0 0 0; transform: translateY(4px); background: #b8972f; }
        .footer { margin-top: 30px; font-size: 0.8em; color: #666; }
        .badge { background: #333; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; color: var(--gold); }
    </style>
</head>
<body>
    <div class="header">
        <h1>SISTEMA MXL</h1>
        <span class="badge">PANEL DE CONTROL PROFESIONAL</span>
    </div>
    
    <div class="container">
        {% for s in data %}
        <div class="card">
            <h2>{{ s[0] }}</h2>
            <div class="stats">
                <span class="price">RD$ {{ "{:,.2f}".format(s[3]) }}</span>
                <span class="available">LIBRES: {{ s[1] - s[2] }}</span>
            </div>
            <a href="{{ url_for('vender', tipo=s[0]) }}" class="btn">PROCESAR VENTA</a>
        </div>
        {% endfor %}
        
        <div class="footer">
            Socio mxl & Gemini © 2026 | Capacidad: 5,000 Tickets
        </div>
    </div>
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
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

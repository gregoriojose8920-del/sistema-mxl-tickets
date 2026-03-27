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
            tipo TEXT PRIMARY KEY, 
            total INTEGER, 
            vendidos INTEGER, 
            precio REAL
        )
    ''')
    data = [('VIP', 1000, 0, 1500.0), ('Regular', 3500, 0, 500.0), ('Guest', 500, 0, 0.0)]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# DISEÑO CON PANEL DE PRECIOS
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA MXL PRO</title>
    <style>
        :root { --gold: #D4AF37; --dark: #121212; --card: #1E1E1E; --text: #E0E0E0; }
        body { font-family: sans-serif; background: var(--dark); color: var(--text); margin: 0; padding: 15px; }
        .header { text-align: center; padding: 20px; border-bottom: 2px solid var(--gold); margin-bottom: 20px; }
        h1 { color: var(--gold); margin: 0; letter-spacing: 2px; }
        .card { background: var(--card); border-radius: 15px; margin-bottom: 15px; padding: 15px; border-left: 5px solid var(--gold); box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
        .stats { display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }
        .price { color: #4CAF50; font-weight: bold; font-size: 1.2em; }
        .btn { background: var(--gold); color: black; text-decoration: none; padding: 15px; border-radius: 10px; display: block; text-align: center; font-weight: bold; margin-top: 10px; }
        
        /* Estilos del Panel de Admin */
        .admin-section { margin-top: 40px; padding: 20px; background: #222; border-radius: 15px; border: 1px dashed var(--gold); }
        .admin-section h3 { color: var(--gold); margin-top: 0; }
        .input-group { margin-bottom: 15px; text-align: left; }
        input { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #333; color: white; box-sizing: border-box; }
        .btn-save { background: #4CAF50; border: none; width: 100%; color: white; padding: 15px; border-radius: 10px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SISTEMA MXL</h1>
        <small>VENTA DE TICKETS OFICIAL</small>
    </div>

    {% for s in data %}
    <div class="card">
        <div style="display:flex; justify-content:space-between;">
            <h2 style="margin:0;">{{ s[0] }}</h2>
            <span style="color:var(--gold)">Disponibles: {{ s[1] - s[2] }}</span>
        </div>
        <div class="stats">
            <span class="price">RD$ {{ "{:,.2f}".format(s[3]) }}</span>
        </div>
        <a href="/vender/{{ s[0] }}" class="btn">VENDER TICKET</a>
    </div>
    {% endfor %}

    <!-- PANEL PARA CAMBIAR PRECIOS -->
    <div class="admin-section">
        <h3>⚙️ PANEL DE PRECIOS (ADMIN)</h3>
        <form action="/update_prices" method="POST">
            {% for s in data %}
            <div class="input-group">
                <label>Precio {{ s[0] }}:</label>
                <input type="number" name="precio_{{ s[0] }}" value="{{ s[3] }}" step="0.01">
            </div>
            {% endfor %}
            <button type="submit" class="btn-save">GUARDAR NUEVOS PRECIOS</button>
        </form>
    </div>

    <p style="font-size: 0.7em; color: #555; text-align: center; margin-top: 20px;">
        Socio mxl & Gemini © 2026 | Logueado como: Admin
    </p>
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

@app.route('/update_prices', methods=['POST'])
def update_prices():
    conn = sqlite3.connect('/tmp/mxl_tickets.db')
    # Actualizamos cada precio según lo que se escribió en el formulario
    for tipo in ['VIP', 'Regular', 'Guest']:
        nuevo_precio = request.form.get(f'precio_{tipo}')
        if nuevo_precio:
            conn.execute('UPDATE stock SET precio = ? WHERE tipo = ?', (nuevo_precio, tipo))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

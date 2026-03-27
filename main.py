from flask import Flask, render_template_string, redirect
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('mxl_tickets.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS stock (tipo TEXT PRIMARY KEY, total INTEGER, vendidos INTEGER, precio REAL)')
    data = [('VIP', 1000, 0, 1500), ('Regular', 3500, 0, 500), ('Guest', 500, 0, 0)]
    cursor.executemany("INSERT OR IGNORE INTO stock VALUES (?,?,?,?)", data)
    conn.commit()
    conn.close()

# ✅ Esto se ejecuta cuando Gunicorn importa el módulo
init_db()

HTML = """..."""  # tu HTML igual que antes

@app.route('/')
def index():
    conn = sqlite3.connect('mxl_tickets.db')
    data = conn.execute('SELECT * FROM stock').fetchall()
    conn.close()
    return render_template_string(HTML, data=data)

@app.route('/vender/<tipo>')
def vender(tipo):
    conn = sqlite3.connect('mxl_tickets.db')
    conn.execute('UPDATE stock SET vendidos = vendidos + 1 WHERE tipo = ? AND vendidos < total', (tipo,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
```

También verifica que en Railway tengas configurado el **Start Command** como:
```
gunicorn main:app --bind 0.0.0.0:$PORT

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import matplotlib.pyplot as plt

app = Flask(__name__)
DATABASE = 'database.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Create ventas table
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_producto TEXT,
        nombre_cliente TEXT,
        precio_total REAL,
        precio_compra REAL,
        estado TEXT DEFAULT 'En proceso'
    )''')
    # Create inventario table
    c.execute('''CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_producto TEXT UNIQUE,
        cantidad INTEGER
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        nombre_cliente = request.form['nombre_cliente']
        precio_total = float(request.form['precio_total'])
        precio_compra = float(request.form['precio_compra'])
        # Insert into ventas
        c.execute('INSERT INTO ventas (nombre_producto, nombre_cliente, precio_total, precio_compra) VALUES (?, ?, ?, ?)',
                  (nombre_producto, nombre_cliente, precio_total, precio_compra))
        # Update inventory
        c.execute('UPDATE inventario SET cantidad = cantidad - 1 WHERE nombre_producto = ?', (nombre_producto,))
        conn.commit()
    c.execute('SELECT * FROM ventas')
    ventas = c.fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas)

@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        cantidad = int(request.form['cantidad'])
        # Insert or update inventory
        c.execute('INSERT INTO inventario (nombre_producto, cantidad) VALUES (?, ?) ON CONFLICT(nombre_producto) DO UPDATE SET cantidad = cantidad + ?',
                  (nombre_producto, cantidad, cantidad))
        conn.commit()
    c.execute('SELECT * FROM inventario')
    inventario = c.fetchall()
    conn.close()
    return render_template('inventario.html', inventario=inventario)

@app.route('/estadisticas')
def estadisticas():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT nombre_producto, COUNT(*) FROM ventas GROUP BY nombre_producto ORDER BY COUNT(*) DESC')
    data = c.fetchall()
    conn.close()
    productos = [row[0] for row in data]
    ventas = [row[1] for row in data]
    plt.bar(productos, ventas)
    plt.xlabel('Producto')
    plt.ylabel('Cantidad Vendida')
    plt.title('Ventas por Producto')
    plt.savefig(f"{project_name}/static/estadisticas.png")
    plt.close()
    return render_template('estadisticas.html', imagen='estadisticas.png')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

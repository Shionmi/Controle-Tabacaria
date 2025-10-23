from flask import send_file
from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm
import io

app = Flask(__name__)

@app.route('/imprimir_etiqueta/<int:id_produto>')
def imprimir_etiqueta(id_produto):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nome, codigo_barras FROM produtos WHERE id_produto=?", (id_produto,))
    produto = cur.fetchone()
    conn.close()

    if not produto:
        return "Produto não encontrado", 404

    nome, codigo_barras = produto

    # Gerar o código de barras temporário
    from barcode import Code128
    from barcode.writer import ImageWriter
    ean = Code128(codigo_barras, writer=ImageWriter())
    caminho_temp = f'static/barcodes/{codigo_barras}.png'
    ean.save(caminho_temp)

    # Criar PDF em memória
    buffer = io.BytesIO()
    largura, altura = 50 * mm, 30 * mm
    c = canvas.Canvas(buffer, pagesize=(largura, altura))

    # Configuração do texto


    # Inserir código de barras centralizado
    c.drawImage(caminho_temp, (largura - 40*mm)/2, 8*mm, width=40*mm, height=20*mm)
    # Procurar o arquivo com ou sem extensão .png
    caminho_barcode = f"static/barcodes/{codigo_barras}.png"
    if not os.path.exists(caminho_barcode):
    # tenta sem extensão, caso o python-barcode tenha salvo assim
        if os.path.exists(f"static/barcodes/{codigo_barras}"):
            caminho_barcode = f"static/barcodes/{codigo_barras}"

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"etiqueta_{codigo_barras}.pdf",
        mimetype='application/pdf'
    )

DB = 'estoque_tabacaria.db'
os.makedirs('static/barcodes', exist_ok=True)

# ===== Função para conectar ao banco =====
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ===== Página inicial =====
@app.route('/')
def index():
    return render_template('index.html')

# ===== Página de registrar produtos =====
@app.route('/registrar')
def registrar():
    return render_template('registrar.html')

# ===== Página de estoque =====
@app.route('/estoque')
def estoque():
    return render_template('estoque.html')

# ===== API para listar produtos =====
@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    conn = get_db()
    cur = conn.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(produtos)

# ===== API para adicionar produto =====
@app.route('/api/produtos', methods=['POST'])
def adicionar_produto():
    data = request.json

    nome = data.get('nome', '').strip()
    categoria = data.get('categoria', '').strip()
    preco = float(data.get('preco', 0.0))
    quantidade = int(data.get('quantidade', 0))

    if not nome:
        return jsonify({"erro": "O nome do produto é obrigatório."}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO produtos (nome, categoria, preco, quantidade, codigo_barras)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, categoria, preco, quantidade, 'TEMP'))
    conn.commit()
    pid = cur.lastrowid

    # Gerar código de barras definitivo (ex: 789000 + id)
    codigo_def = f"789000{pid:06d}"
    conn.execute("UPDATE produtos SET codigo_barras=? WHERE id_produto=?", (codigo_def, pid))
    conn.commit()
    conn.close()

    # Geração do código de barras
    from barcode import Code128
    from barcode.writer import ImageWriter
    ean = Code128(codigo_def, writer=ImageWriter())
    caminho = f'static/barcodes/{codigo_def}'
    ean.save(caminho)

    return jsonify({
        "mensagem": "Produto registrado com sucesso!",
        "id_produto": pid,
        "codigo_barras": codigo_def
    }), 201

if __name__ == '__main__':
    app.run(debug=True)

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


@app.route('/imprimir_etiqueta_html/<int:id_produto>')
def imprimir_etiqueta_html(id_produto):
    # Renderiza uma página simples com a imagem do código de barras e dispara window.print()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nome, codigo_barras FROM produtos WHERE id_produto=?", (id_produto,))
    produto = cur.fetchone()
    conn.close()

    if not produto:
        return "Produto não encontrado", 404

    nome, codigo_barras = produto
    caminho_png = f'static/barcodes/{codigo_barras}.png'

    # Garante que o arquivo PNG exista (gera se necessário)
    if not os.path.exists(caminho_png):
        try:
            from barcode import Code128
            from barcode.writer import ImageWriter
            ean = Code128(codigo_barras, writer=ImageWriter())
            ean.save(f'static/barcodes/{codigo_barras}')
        except Exception:
            pass

    return render_template('print_label.html', nome=nome, codigo_barras=codigo_barras)

# Configurações da aplicação
DB = 'estoque_tabacaria.db'
BARCODE_DIR = os.path.join('static', 'barcodes')
os.makedirs(BARCODE_DIR, exist_ok=True)

# ===== Função para conectar ao banco de dados =====
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


@app.route('/fornecedor')
def fornecedor():
    return render_template('fornecedor.html')

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


@app.route('/api/produtos/<int:id_produto>', methods=['PUT'])
def atualizar_produto(id_produto):
    data = request.json or {}
    nome = data.get('nome', '').strip()
    categoria = data.get('categoria', '').strip()
    preco = float(data.get('preco', 0.0))
    quantidade = int(data.get('quantidade', 0))

    if not nome:
        return jsonify({"erro": "O nome do produto é obrigatório."}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id_produto FROM produtos WHERE id_produto=?", (id_produto,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"erro": "Produto não encontrado."}), 404

    cur.execute("UPDATE produtos SET nome=?, categoria=?, preco=?, quantidade=? WHERE id_produto=?",
                (nome, categoria, preco, quantidade, id_produto))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto atualizado com sucesso."})


@app.route('/api/produtos/<int:id_produto>', methods=['DELETE'])
def deletar_produto(id_produto):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id_produto FROM produtos WHERE id_produto=?", (id_produto,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"erro": "Produto não encontrado."}), 404

    cur.execute("DELETE FROM produtos WHERE id_produto=?", (id_produto,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto removido com sucesso."})


@app.route('/api/generate_barcode/<int:id_produto>', methods=['GET'])
def api_generate_barcode(id_produto):
    """Garante que exista o PNG do barcode e retorna o código e nome do produto."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nome, codigo_barras FROM produtos WHERE id_produto=?", (id_produto,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"erro": "Produto não encontrado."}), 404

    nome, codigo_barras = row
    caminho_png = os.path.join('static', 'barcodes', f"{codigo_barras}.png")

    if not os.path.exists(caminho_png):
        try:
            from barcode import Code128
            from barcode.writer import ImageWriter
            ean = Code128(codigo_barras, writer=ImageWriter())
            ean.save(os.path.join('static', 'barcodes', f"{codigo_barras}"))
        except Exception as e:
            return jsonify({"erro": "Falha ao gerar imagem do código de barras.", "detalhe": str(e)}), 500

    return jsonify({"nome": nome, "codigo_barras": codigo_barras, "path": f"/static/barcodes/{codigo_barras}.png"})

# Tratamento de erros HTTP
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Página não encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Erro interno do servidor'), 500

if __name__ == '__main__':
    # Em produção, use waitress ou outro servidor WSGI
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=8000)
    app.run(debug=True)

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

def ensure_schema():
    """Create required tables if they don't exist"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # revendedores (clients/resellers to whom we sell)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS revendedores (
            id_revendedor INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            contato TEXT,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            notas TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # vendas: sale header
    cur.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
            id_revendedor INTEGER,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observacao TEXT,
            FOREIGN KEY(id_revendedor) REFERENCES revendedores(id_revendedor)
        )
    ''')

    # venda_items: items per sale
    cur.execute('''
        CREATE TABLE IF NOT EXISTS venda_items (
            id_item INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venda INTEGER NOT NULL,
            id_produto INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL,
            FOREIGN KEY(id_venda) REFERENCES vendas(id_venda),
            FOREIGN KEY(id_produto) REFERENCES produtos(id_produto)
        )
    ''')

    # logs / audit trail with enhanced detail
    cur.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id_log INTEGER PRIMARY KEY AUTOINCREMENT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acao TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('venda', 'entrada', 'saida', 'produto', 'sistema')) NOT NULL,
            quantidade INTEGER,
            valor REAL,
            produto_id INTEGER,
            detalhe TEXT,
            FOREIGN KEY(produto_id) REFERENCES produtos(id_produto)
        )
    ''')

    conn.commit()
    conn.close()

# Ensure schema on startup
ensure_schema()

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


@app.route('/venda')
def venda():
    return render_template('venda.html')

# ===== Página de estoque =====
@app.route('/estoque')
def estoque():
    return render_template('estoque.html')


@app.route('/movimentacoes')
def movimentacoes_page():
    return render_template('movimentacoes.html')

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
    
    # Get product details before deletion for barcode cleanup
    cur.execute("SELECT codigo_barras FROM produtos WHERE id_produto=?", (id_produto,))
    produto = cur.fetchone()
    
    if not produto:
        conn.close()
        return jsonify({"erro": "Produto não encontrado."}), 404
    
    try:
        # Delete product
        cur.execute("DELETE FROM produtos WHERE id_produto=?", (id_produto,))
        conn.commit()
        
        # Clean up barcode images
        codigo_barras = produto['codigo_barras']
        barcode_path = os.path.join('static', 'barcodes', f"{codigo_barras}.png")
        barcode_path_noext = os.path.join('static', 'barcodes', f"{codigo_barras}")
        
        if os.path.exists(barcode_path):
            os.remove(barcode_path)
        if os.path.exists(barcode_path_noext):
            os.remove(barcode_path_noext)
            
        log_event('produto_removido', 'produto', produto_id=id_produto, 
                 detalhe=f'Produto {id_produto} removido com código de barras {codigo_barras}')
            
    except Exception as e:
        conn.close()
        return jsonify({"erro": f"Erro ao remover produto: {str(e)}"}), 500
        
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


def log_event(acao, tipo, quantidade=None, valor=None, produto_id=None, detalhe=None):
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO logs (acao, tipo, quantidade, valor, produto_id, detalhe)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (acao, tipo, quantidade, valor, produto_id, detalhe))
        conn.commit()
        conn.close()
    except Exception:
        # best-effort logging, do not break main flow
        pass


@app.route('/api/revendedores', methods=['GET'])
def listar_revendedores():
    conn = get_db()
    cur = conn.execute('SELECT * FROM revendedores ORDER BY nome')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/revendedores', methods=['POST'])
def criar_revendedor():
    data = request.json or {}
    nome = (data.get('nome') or '').strip()
    if not nome:
        return jsonify({'erro': 'Nome é obrigatório.'}), 400
    contato = (data.get('contato') or '').strip()
    telefone = (data.get('telefone') or '').strip()
    email = (data.get('email') or '').strip()
    endereco = (data.get('endereco') or '').strip()
    notas = (data.get('notas') or '').strip()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''INSERT INTO revendedores (nome, contato, telefone, email, endereco, notas)
                       VALUES (?, ?, ?, ?, ?, ?)''', (nome, contato or None, telefone or None, email or None, endereco or None, notas or None))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        # record creation in logs
        log_event('revendedor_criado', 'sistema', detalhe=f'id={rid} nome={nome}')
        return jsonify({'mensagem': 'Revendedor criado', 'id_revendedor': rid}), 201
    except Exception as e:
        return jsonify({'erro': 'Falha ao criar revendedor', 'detalhe': str(e)}), 500


@app.route('/api/vendas', methods=['POST'])
def criar_venda():
    data = request.json or {}
    revendedor_id = data.get('id_revendedor')
    items = data.get('items') or []
    observacao = data.get('observacao')

    if not items or not isinstance(items, list):
        return jsonify({'erro': 'Lista de itens é obrigatória.'}), 400

    # validate items
    errors = []
    for idx, it in enumerate(items, start=1):
        try:
            pid = int(it.get('id_produto'))
            qty = int(it.get('quantidade'))
            if qty <= 0:
                errors.append(f'Item {idx}: quantidade inválida')
        except Exception:
            errors.append(f'Item {idx}: dados inválidos')

    if errors:
        return jsonify({'erro': 'Itens inválidos', 'detalhes': errors}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        # start transaction
        cur.execute('BEGIN')
        # optional revendedor existence check
        if revendedor_id:
            cur.execute('SELECT id_revendedor FROM revendedores WHERE id_revendedor=?', (revendedor_id,))
            if not cur.fetchone():
                conn.rollback(); conn.close()
                return jsonify({'erro': 'Revendedor não encontrado.'}), 404

        # create venda
        cur.execute('INSERT INTO vendas (id_revendedor, observacao) VALUES (?, ?)', (revendedor_id, observacao))
        venda_id = cur.lastrowid

        # process each item: check stock and decrement
        for it in items:
            pid = int(it.get('id_produto'))
            qty = int(it.get('quantidade'))
            # get product and price
            cur.execute('SELECT quantidade, preco FROM produtos WHERE id_produto=?', (pid,))
            row = cur.fetchone()
            if not row:
                conn.rollback(); conn.close()
                return jsonify({'erro': f'Produto {pid} não encontrado.'}), 404
            estoque_atual = row['quantidade']
            preco_unit = row['preco']
            if estoque_atual < qty:
                conn.rollback(); conn.close()
                return jsonify({'erro': f'Estoque insuficiente para produto {pid}. Disponível: {estoque_atual}'}), 400
            # decrement
            cur.execute('UPDATE produtos SET quantidade = quantidade - ? WHERE id_produto=?', (qty, pid))
            # insert item
            cur.execute('INSERT INTO venda_items (id_venda, id_produto, quantidade, preco_unitario) VALUES (?, ?, ?, ?)', (venda_id, pid, qty, preco_unit))

        # For each sold item, also register a movimentacao (saida) and log it
        for it in items:
            pid = int(it.get('id_produto'))
            qty = int(it.get('quantidade'))
            try:
                cur.execute('INSERT INTO movimentacoes (id_produto, tipo, quantidade, observacao, data_mov) VALUES (?, ?, ?, ?, datetime("now"))',
                            (pid, 'saida', qty, f'Venda #{venda_id}'))
            except Exception:
                # ignore mov insertion failures but continue
                pass

        conn.commit()
        conn.close()
        log_event('venda_criada', 'venda', quantidade=len(items), detalhe=f'id_venda={venda_id} revendedor={revendedor_id}')
        return jsonify({'mensagem': 'Venda registrada', 'id_venda': venda_id}), 201
    except Exception as e:
        conn.rollback(); conn.close()
        return jsonify({'erro': 'Falha ao registrar venda', 'detalhe': str(e)}), 500


@app.route('/api/vendas', methods=['GET'])
def listar_vendas():
    limit = request.args.get('limit', type=int)
    conn = get_db()
    cur = conn.cursor()
    q = '''SELECT v.id_venda, v.data_venda, v.observacao, r.id_revendedor, r.nome as revendedor_nome
           FROM vendas v
           LEFT JOIN revendedores r ON r.id_revendedor = v.id_revendedor
           ORDER BY v.data_venda DESC'''
    if limit and limit>0:
        q = q + f' LIMIT {limit}'
    cur.execute(q)
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({
            'id_venda': r[0], 'data_venda': r[1], 'observacao': r[2], 'id_revendedor': r[3], 'revendedor_nome': r[4]
        })
    conn.close()
    return jsonify(result)


def validar_movimentacao_data(data):
    errors = {}
    # id_produto
    try:
        id_prod = int(data.get('id_produto'))
        if id_prod <= 0:
            errors['id_produto'] = 'Produto inválido.'
    except Exception:
        errors['id_produto'] = 'Produto inválido.'

    # tipo
    tipo = (data.get('tipo') or '').strip()
    if tipo not in ('entrada', 'saida'):
        errors['tipo'] = "Tipo inválido. Deve ser 'entrada' ou 'saida'."

    # quantidade
    try:
        quantidade = int(data.get('quantidade'))
        if quantidade <= 0:
            errors['quantidade'] = 'Quantidade deve ser maior que zero.'
    except Exception:
        errors['quantidade'] = 'Quantidade inválida.'

    observacao = (data.get('observacao') or '').strip()
    data_mov = data.get('data_mov')

    cleaned = {
        'id_produto': id_prod if 'id_produto' not in errors else None,
        'tipo': tipo,
        'quantidade': quantidade if 'quantidade' not in errors else None,
        'observacao': observacao,
        'data_mov': data_mov
    }
    return cleaned, errors


@app.route('/api/movimentacoes', methods=['GET'])
def listar_movimentacoes():
    """List movimentacoes joined with product. Supports ?limit=n, q, start_date, end_date"""
    limit = request.args.get('limit', type=int)
    q_param = request.args.get('q', type=str)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db()
    cur = conn.cursor()
    base = '''SELECT m.id_mov, m.id_produto, m.tipo, m.quantidade, m.observacao, m.data_mov,
                     p.nome as produto_nome
              FROM movimentacoes m
              LEFT JOIN produtos p ON p.id_produto = m.id_produto
              WHERE 1=1'''

    params = []
    if q_param:
        base += ' AND (p.nome LIKE ? OR m.observacao LIKE ?)'
        likeq = f'%{q_param}%'
        params.extend([likeq, likeq])
    if start_date:
        base += ' AND m.data_mov >= ?'
        params.append(start_date)
    if end_date:
        base += ' AND m.data_mov <= ?'
        params.append(end_date)

    base += ' ORDER BY m.data_mov DESC'
    if limit and limit > 0:
        base += ' LIMIT ?'
        params.append(limit)

    cur.execute(base, params)
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'id_mov': r[0],
            'id_produto': r[1],
            'tipo': r[2],
            'quantidade': r[3],
            'observacao': r[4],
            'data_mov': r[5],
            'produto_nome': r[6]
        })
    return jsonify(result)


@app.route('/api/movimentacoes', methods=['POST'])
def criar_movimentacao():
    data = request.json or {}
    cleaned, errors = validar_movimentacao_data(data)
    if errors:
        return jsonify({'erro': 'Dados inválidos', 'detalhes': errors}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        # check product exists
        cur.execute('SELECT quantidade FROM produtos WHERE id_produto=?', (cleaned['id_produto'],))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({'erro': 'Produto não encontrado.'}), 404

        # update stock
        if cleaned['tipo'] == 'entrada':
            cur.execute('UPDATE produtos SET quantidade = quantidade + ? WHERE id_produto=?', (cleaned['quantidade'], cleaned['id_produto']))
        else:
            # saida
            estoque_atual = row['quantidade']
            if estoque_atual < cleaned['quantidade']:
                conn.close()
                return jsonify({'erro': 'Estoque insuficiente.'}), 400
            cur.execute('UPDATE produtos SET quantidade = quantidade - ? WHERE id_produto=?', (cleaned['quantidade'], cleaned['id_produto']))

        cur.execute('INSERT INTO movimentacoes (id_produto, tipo, quantidade, observacao, data_mov) VALUES (?, ?, ?, ?, ?)',
                    (cleaned['id_produto'], cleaned['tipo'], cleaned['quantidade'], cleaned.get('observacao'), cleaned.get('data_mov') or None))
        mov_id = cur.lastrowid
        conn.commit()
        # log
        log_event('movimentacao_criada', cleaned['tipo'], quantidade=cleaned['quantidade'], produto_id=cleaned['id_produto'], detalhe=f'id_mov={mov_id}')
    except Exception as e:
        conn.rollback(); conn.close()
        return jsonify({'erro': 'Falha ao registrar movimentação', 'detalhe': str(e)}), 500
    conn.close()
    return jsonify({'mensagem': 'Movimentação registrada', 'id_mov': mov_id}), 201


@app.route('/api/movimentacoes/<int:id_mov>', methods=['DELETE'])
def deletar_movimentacao(id_mov):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id_mov FROM movimentacoes WHERE id_mov=?', (id_mov,))
    if not cur.fetchone():
        conn.close()
        return jsonify({'erro': 'Movimentação não encontrada.'}), 404
    cur.execute('DELETE FROM movimentacoes WHERE id_mov=?', (id_mov,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Movimentação removida.'})

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

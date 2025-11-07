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
    try:
        # Conexão com o banco de dados
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT nome, codigo_barras FROM produtos WHERE id_produto=?", (id_produto,))
        produto = cur.fetchone()
        conn.close()

        if not produto:
            app.logger.error(f"Produto não encontrado: {id_produto}")
            return "Produto não encontrado", 404

        nome, codigo_barras = produto

        # Validar e formatar o código de barras
        if not isinstance(codigo_barras, str):
            codigo_barras = str(codigo_barras)
        codigo_barras = codigo_barras.strip()

        # Gerar o código de barras em SVG
        from barcode import Code128
        from barcode.writer import SVGWriter
        
        # Configurar o writer SVG para um resultado mais compacto
        writer = SVGWriter()
        writer.set_options({
            'module_width': 0.4,
            'module_height': 15.0,
            'quiet_zone': 3.0,
            'font_size': 10,
            'text_distance': 5.0,
            'background': 'white'
        })
        
        # Gerar SVG em memória
        ean = Code128(codigo_barras, writer=writer)
        svg_data = ean.render()

        # Criar PDF em memória usando svglib para converter SVG para PDF
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
        import tempfile

        # Criar arquivo SVG temporário em memória
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False, mode='w+') as f:
            f.write(svg_data)
            temp_svg = f.name

        try:
            # Converter SVG para PDF
            drawing = svg2rlg(temp_svg)
            
            # Criar PDF em memória
            buffer = io.BytesIO()
            largura, altura = 50 * mm, 30 * mm
            
            # Ajustar escala do desenho para caber na etiqueta
            scale_x = (40 * mm) / drawing.width
            scale_y = (20 * mm) / drawing.height
            scale = min(scale_x, scale_y)
            drawing.scale(scale, scale)
            
            # Centralizar na etiqueta
            drawing.translate(
                ((largura - drawing.width * scale) / 2),
                ((altura - drawing.height * scale) / 2)
            )
            
            renderPDF.drawToFile(drawing, buffer)
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"etiqueta_{codigo_barras}.pdf",
                mimetype='application/pdf'
            )
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(temp_svg)
            except:
                pass

    except Exception as e:
        app.logger.error(f"Erro ao gerar etiqueta para produto {id_produto}: {str(e)}")
        return jsonify({"error": "Erro ao gerar etiqueta", "details": str(e)}), 500


@app.route('/imprimir_etiqueta_html/<int:id_produto>')
def imprimir_etiqueta_html(id_produto):
    try:
        # Renderiza uma página simples com o código de barras em SVG
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT nome, codigo_barras FROM produtos WHERE id_produto=?", (id_produto,))
        produto = cur.fetchone()
        conn.close()

        if not produto:
            return "Produto não encontrado", 404

        nome, codigo_barras = produto

        # Validar e formatar o código de barras
        if not isinstance(codigo_barras, str):
            codigo_barras = str(codigo_barras)
        codigo_barras = codigo_barras.strip()

        # Gerar o código de barras em SVG
        from barcode import Code128
        from barcode.writer import SVGWriter
        
        # Configurar o writer SVG para um resultado mais compacto
        writer = SVGWriter()
        writer.set_options({
            'module_width': 0.4,
            'module_height': 15.0,
            'quiet_zone': 3.0,
            'font_size': 10,
            'text_distance': 5.0,
            'background': 'white'
        })
        
        # Gerar SVG em memória
        ean = Code128(codigo_barras, writer=writer)
        svg_data = ean.render()

        # Retornar o template com o SVG
        return render_template('print_label.html', 
                            nome=nome, 
                            codigo_barras=codigo_barras,
                            svg_data=svg_data)

    except Exception as e:
        app.logger.error(f"Erro ao gerar etiqueta HTML para produto {id_produto}: {str(e)}")
        return f"Erro ao gerar etiqueta: {str(e)}", 500

# Configurações da aplicação
DB = 'estoque_tabacaria.db'
BARCODE_DIR = os.path.join('static', 'barcodes')
os.makedirs(BARCODE_DIR, exist_ok=True)

def ensure_schema():
    """Create required tables if they don't exist"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # clientes 
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            cidade TEXT,
            estado TEXT,
            observacoes TEXT,
            ultima_compra TIMESTAMP,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# ===== Página de clientes =====
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')


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

# ===== API para listar clientes =====
@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    conn = get_db()
    cur = conn.execute("SELECT * FROM clientes ORDER BY nome")
    clientes = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(clientes)

# ===== API para adicionar cliente =====
@app.route('/api/clientes', methods=['POST'])
def adicionar_cliente():
    data = request.json

    nome = data.get('nome', '').strip()
    cpf = data.get('cpf', '').strip()
    telefone = data.get('telefone', '').strip()
    email = data.get('email', '').strip()
    endereco = data.get('endereco', '').strip()
    cidade = data.get('cidade', '').strip()
    estado = data.get('estado', '').strip()
    observacoes = data.get('observacoes', '').strip()

    if not nome:
        return jsonify({"erro": "O nome do cliente é obrigatório."}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO clientes (
                nome, cpf, telefone, email, 
                endereco, cidade, estado, observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, cpf, telefone, email, endereco, cidade, estado, observacoes))
        conn.commit()
        cliente_id = cur.lastrowid

        return jsonify({
            "mensagem": "Cliente registrado com sucesso!",
            "id_cliente": cliente_id
        })

    except sqlite3.IntegrityError:
        return jsonify({"erro": "CPF já cadastrado."}), 400
    finally:
        conn.close()

# ===== API para buscar cliente =====
@app.route('/api/clientes/<int:id_cliente>', methods=['GET'])
def buscar_cliente(id_cliente):
    conn = get_db()
    cur = conn.execute("SELECT * FROM clientes WHERE id_cliente=?", (id_cliente,))
    cliente = cur.fetchone()
    conn.close()

    if cliente is None:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    return jsonify(dict(cliente))

# ===== API para atualizar cliente =====
@app.route('/api/clientes/<int:id_cliente>', methods=['PUT'])
def atualizar_cliente(id_cliente):
    data = request.json

    nome = data.get('nome', '').strip()
    cpf = data.get('cpf', '').strip()
    telefone = data.get('telefone', '').strip()
    email = data.get('email', '').strip()
    endereco = data.get('endereco', '').strip()
    cidade = data.get('cidade', '').strip()
    estado = data.get('estado', '').strip()
    observacoes = data.get('observacoes', '').strip()

    if not nome:
        return jsonify({"erro": "O nome do cliente é obrigatório."}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE clientes 
            SET nome=?, cpf=?, telefone=?, email=?,
                endereco=?, cidade=?, estado=?, observacoes=?,
                atualizado_em=CURRENT_TIMESTAMP
            WHERE id_cliente=?
        """, (nome, cpf, telefone, email, endereco, cidade, estado, observacoes, id_cliente))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        return jsonify({"mensagem": "Cliente atualizado com sucesso!"})

    except sqlite3.IntegrityError:
        return jsonify({"erro": "CPF já cadastrado para outro cliente."}), 400
    finally:
        conn.close()

# ===== API para excluir cliente =====
@app.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
def excluir_cliente(id_cliente):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM clientes WHERE id_cliente=?", (id_cliente,))
    conn.commit()
    
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"erro": "Cliente não encontrado"}), 404

    conn.close()
    return jsonify({"mensagem": "Cliente excluído com sucesso!"})

# ===== API para listar produtos =====
@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    conn = get_db()
    cur = conn.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(produtos)

# ===== Rota para registrar cliente =====
@app.route('/api/clientes', methods=['POST'])
def registrar_cliente():
    try:
        data = request.json
        nome = data.get('nome', '').strip()
        cpf = data.get('cpf', '').strip()
        telefone = data.get('telefone', '').strip()
        email = data.get('email', '').strip()
        endereco = data.get('endereco', '').strip()
        cidade = data.get('cidade', '').strip()
        estado = data.get('estado', '').strip()
        observacoes = data.get('observacoes', '').strip()

        if not nome:
            return jsonify({"erro": "O nome do cliente é obrigatório."}), 400

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO clientes (nome, cpf, telefone, email, endereco, cidade, estado, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, cpf, telefone, email, endereco, cidade, estado, observacoes))
        conn.commit()
        cliente_id = cur.lastrowid

        return jsonify({
            "mensagem": "Cliente registrado com sucesso!",
            "id_cliente": cliente_id
        })

    except sqlite3.IntegrityError:
        return jsonify({"erro": "CPF já cadastrado."}), 400
    finally:
        conn.close()


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


@app.route('/registrar_cliente')
@app.route('/clientes/novo')
def pagina_registrar_cliente():
    return render_template('registrar_cliente.html')


@app.route('/api/generate_barcode/<int:id_produto>', methods=['GET'])
def api_generate_barcode(id_produto):
    """Gera o código de barras em PNG com nome do produto."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT nome, codigo_barras FROM produtos WHERE id_produto=?", (id_produto,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "Produto não encontrado"}), 404

        nome, codigo_barras = row

        # Validar e formatar o código de barras
        if not isinstance(codigo_barras, str):
            codigo_barras = str(codigo_barras)
        codigo_barras = codigo_barras.strip()

        # Criar uma nova imagem para a etiqueta completa
        from PIL import Image, ImageDraw, ImageFont
        import os

        # Tamanho da etiqueta em pixels (5cm x 3cm em 300 DPI)
        width = int(5 * 118.11)  # 5cm em pixels (300 DPI)
        height = int(3 * 118.11)  # 3cm em pixels (300 DPI)

        # Criar imagem em branco
        label = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(label)

        # Carregar fonte
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        # Desenhar o nome do produto
        text_width = draw.textlength(nome, font=font)
        text_x = (width - text_width) / 2
        draw.text((text_x, 10), nome, fill='black', font=font)

        # Gerar o código de barras
        from barcode import Code128
        from barcode.writer import ImageWriter
        
        writer = ImageWriter()
        writer.set_options({
            'module_width': 0.6,
            'module_height': 15.0,
            'quiet_zone': 6.0,
            'font_size': 10,
            'text_distance': 5.0,
            'background': 'white'
        })

        # Gerar PNG do código de barras
        os.makedirs(os.path.join(app.static_folder, 'barcodes'), exist_ok=True)
        temp_path = os.path.join(app.static_folder, 'barcodes', 'temp_' + codigo_barras)
        ean = Code128(codigo_barras, writer=writer)
        ean.save(temp_path)

        # Carregar o código de barras gerado
        barcode_img = Image.open(temp_path + '.png')
        
        # Redimensionar o código de barras para caber na etiqueta
        barcode_width = int(width * 0.8)  # 80% da largura da etiqueta
        ratio = barcode_width / barcode_img.width
        barcode_height = int(barcode_img.height * ratio)
        barcode_img = barcode_img.resize((barcode_width, barcode_height))

        # Colar o código de barras na etiqueta
        barcode_x = (width - barcode_width) // 2
        barcode_y = height - barcode_height - 10
        label.paste(barcode_img, (barcode_x, barcode_y))

        # Salvar a etiqueta final
        save_path = os.path.join(app.static_folder, 'barcodes', codigo_barras + '.png')
        label.save(save_path, 'PNG')

        # Limpar arquivo temporário
        try:
            os.remove(temp_path + '.png')
        except:
            pass

        # Retornar o caminho relativo do arquivo PNG
        return jsonify({
            "path": f"/static/barcodes/{codigo_barras}.png",
            "nome": nome
        })

    except Exception as e:
        app.logger.error(f"Erro ao gerar código de barras para produto {id_produto}: {str(e)}")
        return jsonify({
            "error": "Erro ao gerar código de barras", 
            "details": str(e)
        }), 500


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
    cliente_id = data.get('id_cliente')
    cliente_nome = data.get('cliente_nome')
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

        # optional cliente existence check
        if cliente_id is not None:
            cur.execute('SELECT id_cliente FROM clientes WHERE id_cliente=?', (cliente_id,))
            if not cur.fetchone():
                conn.rollback(); conn.close()
                return jsonify({'erro': 'Cliente não encontrado.'}), 404

        # Ensure vendas table has optional client columns
        cur2 = conn.cursor()
        cur2.execute("PRAGMA table_info('vendas')")
        cols = [r['name'] for r in cur2.fetchall()]
        if 'id_cliente' not in cols:
            cur2.execute('ALTER TABLE vendas ADD COLUMN id_cliente INTEGER')
        if 'cliente_nome' not in cols:
            cur2.execute("ALTER TABLE vendas ADD COLUMN cliente_nome TEXT")
        # ensure discount and total columns exist so we can persist them when provided
        if 'discount_percent' not in cols:
            try:
                cur2.execute('ALTER TABLE vendas ADD COLUMN discount_percent REAL')
            except Exception:
                pass
        if 'total' not in cols:
            try:
                cur2.execute('ALTER TABLE vendas ADD COLUMN total REAL')
            except Exception:
                pass

        # create venda (include optional fields)
        insert_cols = ['id_revendedor', 'observacao']
        insert_vals = [revendedor_id, observacao]
        if cliente_id is not None:
            insert_cols.append('id_cliente'); insert_vals.append(cliente_id)
        if cliente_nome:
            insert_cols.append('cliente_nome'); insert_vals.append(cliente_nome)
        # optional financial fields
        discount_percent = data.get('discount_percent')
        total_final = data.get('total')
        if discount_percent is not None:
            try:
                dp = float(discount_percent)
                insert_cols.append('discount_percent'); insert_vals.append(dp)
            except Exception:
                pass
        if total_final is not None:
            try:
                tf = float(total_final)
                insert_cols.append('total'); insert_vals.append(tf)
            except Exception:
                pass

        cols_sql = ','.join(insert_cols)
        qmarks = ','.join('?' for _ in insert_vals)
        cur.execute(f'INSERT INTO vendas ({cols_sql}) VALUES ({qmarks})', tuple(insert_vals))
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

        # Register a single movimentacao summarizing the venda (saida)
        try:
            total_qty = 0
            first_pid = None
            for idx, it in enumerate(items):
                pid = int(it.get('id_produto'))
                qty = int(it.get('quantidade'))
                total_qty += qty
                if idx == 0:
                    first_pid = pid
            if first_pid is None:
                first_pid = items[0]['id_produto'] if items else None
            # insert one movimentacao linking to a representative product and total quantity
            if first_pid is not None:
                cur.execute('INSERT INTO movimentacoes (id_produto, tipo, quantidade, observacao, data_mov) VALUES (?, ?, ?, ?, datetime("now"))',
                            (first_pid, 'saida', total_qty, f'Venda #{venda_id}'))
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
    q = '''SELECT v.id_venda, v.data_venda, v.observacao, r.id_revendedor, r.nome as revendedor_nome,
                  v.id_cliente, COALESCE(c.nome, v.cliente_nome) as cliente_nome
           FROM vendas v
           LEFT JOIN revendedores r ON r.id_revendedor = v.id_revendedor
           LEFT JOIN clientes c ON c.id_cliente = v.id_cliente
           ORDER BY v.data_venda DESC'''
    if limit and limit>0:
        q = q + f' LIMIT {limit}'
    cur.execute(q)
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({
            'id_venda': r[0], 'data_venda': r[1], 'observacao': r[2], 'id_revendedor': r[3], 'revendedor_nome': r[4], 'id_cliente': r[5], 'cliente_nome': r[6]
        })
    conn.close()
    return jsonify(result)


@app.route('/api/vendas/<int:id_venda>', methods=['GET'])
def buscar_venda(id_venda):
    conn = get_db()
    cur = conn.cursor()
    # select core fields and include optional columns if present
    cur.execute("PRAGMA table_info('vendas')")
    vcols = [r['name'] for r in cur.fetchall()]
    extra = []
    if 'discount_percent' in vcols: extra.append('v.discount_percent')
    if 'total' in vcols: extra.append('v.total')
    extras_sql = (', ' + ', '.join(extra)) if extra else ''
    sql = f"SELECT v.id_venda, v.data_venda, v.observacao, v.id_revendedor, v.id_cliente, COALESCE(c.nome, v.cliente_nome) as cliente_nome{extras_sql} FROM vendas v LEFT JOIN clientes c ON c.id_cliente = v.id_cliente WHERE v.id_venda=?"
    cur.execute(sql, (id_venda,))
    vh = cur.fetchone()
    if not vh:
        conn.close()
        return jsonify({'erro': 'Venda não encontrada'}), 404
    venda = {
        'id_venda': vh[0], 'data_venda': vh[1], 'observacao': vh[2], 'id_revendedor': vh[3], 'id_cliente': vh[4], 'cliente_nome': vh[5]
    }
    idx = 6
    if 'discount_percent' in vcols:
        venda['discount_percent'] = vh[idx]; idx += 1
    if 'total' in vcols:
        venda['total'] = vh[idx]; idx += 1
    cur.execute('''SELECT vi.id_item, vi.id_produto, vi.quantidade, vi.preco_unitario, p.nome as produto_nome
                   FROM venda_items vi LEFT JOIN produtos p ON p.id_produto = vi.id_produto WHERE vi.id_venda=?''', (id_venda,))
    items = []
    for it in cur.fetchall():
        items.append({'id_item': it[0], 'id_produto': it[1], 'quantidade': it[2], 'preco_unitario': it[3], 'produto_nome': it[4]})
    venda['items'] = items
    conn.close()
    return jsonify(venda)


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

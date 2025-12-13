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
import socket
from pyngrok import ngrok
import atexit
from colorama import init, Fore, Back, Style
import sys
import logging

# Inicializar colorama para Windows
init(autoreset=True)

# Suprimir logs verbosos do ngrok e do pyngrok
logging.getLogger('pyngrok').setLevel(logging.CRITICAL)
logging.getLogger('pyngrok.ngrok').setLevel(logging.CRITICAL)
os.environ['NGROK_LOG_LEVEL'] = 'critical'
os.environ['NGROK_LOG'] = 'false'

# Variável de controle para executar setup apenas uma vez
_ngrok_initialized = False

app = Flask(__name__)

# Variável global para armazenar a URL pública
public_url = None

def get_local_ip():
    try:
        # Tenta conectar a um DNS público para descobrir qual interface tem internet
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def print_banner():
    """Exibe banner amigável e colorido"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}" + "═" * 70)
    print(f"{Fore.YELLOW}{Style.BRIGHT}                    🏪 JM TABACARIA - SISTEMA ATIVO 🏪")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + Style.RESET_ALL)

def setup_ngrok():
    global public_url, _ngrok_initialized
    
    # Evitar múltiplas inicializações (debug mode do Flask reinicia o processo)
    if _ngrok_initialized:
        return
    
    _ngrok_initialized = True
    
    try:
        # Verificar se há túneis ativos
        existing_tunnels = ngrok.get_tunnels()
        if existing_tunnels:
            print(f"\n{Fore.YELLOW}⚠️  Detectado túnel ngrok já ativo!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Reutilizando túnel existente...{Style.RESET_ALL}")
            public_url = existing_tunnels[0].public_url
            print(f"\n{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{Style.BRIGHT}              🌍 ACESSO PÚBLICO ATIVADO! 🌍{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}")
            print(f"\n{Fore.WHITE}{Style.BRIGHT}  ✅ Acesse de QUALQUER LUGAR (celular, tablet, etc):{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}     → {public_url}{Style.RESET_ALL}")
            print(f"\n{Fore.MAGENTA}  💡 Compartilhe este link com quem precisar acessar!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}\n")
            return
        
        # Criar novo túnel público na porta 5000
        print(f"\n{Fore.CYAN}🔄 Criando túnel público...{Style.RESET_ALL}")
        tunnel = ngrok.connect(5000, bind_tls=True)
        public_url = tunnel.public_url
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}              🌍 ACESSO PÚBLICO ATIVADO! 🌍{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}")
        print(f"\n{Fore.WHITE}{Style.BRIGHT}  ✅ Acesse de QUALQUER LUGAR (celular, tablet, etc):{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}     → {public_url}{Style.RESET_ALL}")
        print(f"\n{Fore.MAGENTA}  💡 Compartilhe este link com quem precisar acessar!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}\n")
        
        # Fechar túnel ao encerrar
        atexit.register(ngrok.kill)
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Tratamento específico para erro de limite de sessões
        if 'limited to' in error_msg and 'simultaneous' in error_msg:
            print(f"\n{Fore.RED}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  ⚠️  LIMITE DE SESSÕES NGROK ATINGIDO{Style.RESET_ALL}")
            print(f"{Fore.RED}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}")
            print(f"\n{Fore.WHITE}  Você já tem 3 sessões ngrok abertas.{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}  💡 Soluções:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}1.{Style.RESET_ALL} Feche outras sessões em: {Fore.YELLOW}https://dashboard.ngrok.com/agents{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}2.{Style.RESET_ALL} Use o acesso local na sua rede Wi-Fi")
            print(f"\n{Fore.MAGENTA}  → O sistema funcionará normalmente na rede local!{Style.RESET_ALL}")
            print(f"\n{Fore.RED}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}\n")
        
        # Tratamento para endpoint já em uso
        elif 'already online' in error_msg:
            print(f"\n{Fore.YELLOW}⚠️  Túnel ngrok já está ativo em outra janela!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 Feche as outras janelas do sistema ou use o túnel existente.{Style.RESET_ALL}\n")
        
        # Outros erros
        else:
            print(f"\n{Fore.YELLOW}⚠️  Não foi possível criar túnel público{Style.RESET_ALL}")
            print(f"{Fore.WHITE}   Detalhes: {str(e)[:100]}...{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Sistema funcionará na rede local!{Style.RESET_ALL}\n")
        public_url = None

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
    mobile_ip = get_local_ip()
    # Usar URL pública se disponível, senão IP local
    display_url = public_url if public_url else f"http://{mobile_ip}:5000"
    return render_template('index.html', mobile_ip=mobile_ip, public_url=display_url)

# ===== Página de registrar produtos (Redirecionado para Estoque) =====
@app.route('/registrar')
def registrar():
    from flask import redirect, url_for
    return redirect(url_for('estoque'))

# ===== Página de clientes =====
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')


@app.route('/venda')
def venda():
    return render_template('venda.html')

@app.route('/estornar_venda')
def estornar_venda_page():
    return render_template('estornar_venda.html')

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


@app.route('/api/produtos/<int:id_produto>/detalhes', methods=['GET'])
def detalhes_produto(id_produto):
    """Retorna informações detalhadas do produto incluindo histórico de movimentações"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Buscar dados do produto
        cur.execute("SELECT * FROM produtos WHERE id_produto=?", (id_produto,))
        produto = cur.fetchone()
        
        if not produto:
            conn.close()
            return jsonify({"erro": "Produto não encontrado."}), 404
        
        produto_dict = dict(produto)
        
        # Buscar histórico de movimentações
        cur.execute("""
            SELECT tipo, quantidade, observacao, data_mov 
            FROM movimentacoes 
            WHERE id_produto=? 
            ORDER BY data_mov DESC 
            LIMIT 50
        """, (id_produto,))
        movimentacoes = [dict(row) for row in cur.fetchall()]
        
        # Calcular estatísticas
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE 0 END), 0) as total_entradas,
                COALESCE(SUM(CASE WHEN tipo='saida' THEN quantidade ELSE 0 END), 0) as total_saidas,
                COUNT(*) as total_movimentacoes
            FROM movimentacoes 
            WHERE id_produto=?
        """, (id_produto,))
        stats = dict(cur.fetchone())
        
        # Buscar vendas relacionadas
        cur.execute("""
            SELECT COUNT(*) as total_vendas, 
                   COALESCE(SUM(quantidade), 0) as quantidade_vendida,
                   COALESCE(SUM(quantidade * preco_unitario), 0) as valor_total_vendido
            FROM venda_items 
            WHERE id_produto=?
        """, (id_produto,))
        vendas_stats = dict(cur.fetchone())
        
        conn.close()
        
        return jsonify({
            "produto": produto_dict,
            "movimentacoes": movimentacoes,
            "estatisticas": stats,
            "vendas": vendas_stats
        })
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar detalhes: {str(e)}"}), 500


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
    from flask import redirect, url_for
    return redirect(url_for('clientes'))


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
        # ensure forma_pagamento and data_vencimento columns exist
        if 'forma_pagamento' not in cols:
            try:
                cur2.execute('ALTER TABLE vendas ADD COLUMN forma_pagamento TEXT')
            except Exception:
                pass
        if 'data_vencimento' not in cols:
            try:
                cur2.execute('ALTER TABLE vendas ADD COLUMN data_vencimento TEXT')
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
        forma_pagamento = data.get('forma_pagamento')
        data_vencimento = data.get('data_vencimento')
        
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
        if forma_pagamento:
            insert_cols.append('forma_pagamento'); insert_vals.append(forma_pagamento)
        if data_vencimento:
            insert_cols.append('data_vencimento'); insert_vals.append(data_vencimento)

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

        # Integração Financeira: Criar Conta a Receber (à prazo) ou Fluxo de Caixa (à vista)
        try:
            forma_pagamento = data.get('forma_pagamento')
            data_vencimento = data.get('data_vencimento')
            total_venda = total_final if total_final is not None else sum(
                float(cur.execute('SELECT preco FROM produtos WHERE id_produto=?', (int(it['id_produto']),)).fetchone()['preco']) * int(it['quantidade'])
                for it in items
            )
            
            if forma_pagamento == 'prazo':
                # Criar conta a receber
                if cliente_id:
                    cur.execute("""
                        INSERT INTO contas_receber (id_cliente, descricao, valor, data_vencimento, status)
                        VALUES (?, ?, ?, ?, 'pendente')
                    """, (
                        cliente_id,
                        f'Venda #{venda_id}',
                        total_venda,
                        data_vencimento
                    ))
            elif forma_pagamento in ['dinheiro', 'debito', 'credito', 'pix']:
                # Criar entrada no fluxo de caixa
                forma_descricao = {
                    'dinheiro': 'Dinheiro',
                    'debito': 'Cartão Débito',
                    'credito': 'Cartão Crédito',
                    'pix': 'PIX'
                }.get(forma_pagamento, forma_pagamento)
                
                cur.execute("""
                    INSERT INTO fluxo_caixa (tipo, categoria, valor, descricao, data_movimentacao)
                    VALUES ('entrada', ?, ?, ?, datetime('now'))
                """, (
                    forma_descricao,
                    total_venda,
                    f'Venda #{venda_id} - {forma_descricao}'
                ))
        except Exception as e:
            # Log error but don't fail the sale
            print(f'Erro ao criar registro financeiro: {e}')

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


@app.route('/api/vendas/<int:id_venda>/estornar', methods=['POST'])
def estornar_venda(id_venda):
    """Estorna uma venda: reverte estoque, fluxo de caixa e conta a receber"""
    data = request.json or {}
    motivo = data.get('motivo', 'Estorno solicitado')
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Verificar se venda existe
        cur.execute("PRAGMA table_info('vendas')")
        vcols = [r['name'] for r in cur.fetchall()]
        
        # Adicionar coluna status se não existir
        if 'status' not in vcols:
            cur.execute('ALTER TABLE vendas ADD COLUMN status TEXT DEFAULT "ativa"')
            conn.commit()
        
        cur.execute("SELECT * FROM vendas WHERE id_venda=?", (id_venda,))
        venda = cur.fetchone()
        if not venda:
            conn.close()
            return jsonify({'erro': 'Venda não encontrada'}), 404
        
        # Verificar se já foi estornada
        venda_dict = dict(venda)
        if venda_dict.get('status') == 'estornada':
            conn.close()
            return jsonify({'erro': 'Esta venda já foi estornada'}), 400
        
        # Buscar itens da venda
        cur.execute("SELECT * FROM venda_items WHERE id_venda=?", (id_venda,))
        items = cur.fetchall()
        
        # Reverter estoque - devolver produtos
        for item in items:
            item_dict = dict(item)
            cur.execute("""
                UPDATE produtos SET quantidade = quantidade + ?
                WHERE id_produto=?
            """, (item_dict['quantidade'], item_dict['id_produto']))
            
            # Registrar movimentação de estorno
            cur.execute("""
                INSERT INTO movimentacoes (id_produto, tipo, quantidade, observacao)
                VALUES (?, 'entrada', ?, ?)
            """, (item_dict['id_produto'], item_dict['quantidade'], 
                   f'Estorno da venda #{id_venda} - {motivo}'))
        
        # Reverter fluxo de caixa (se foi à vista)
        forma_pagamento = venda_dict.get('forma_pagamento')
        if forma_pagamento in ['dinheiro', 'debito', 'credito', 'pix']:
            # Criar saída para cancelar a entrada
            valor = venda_dict.get('total', 0)
            cur.execute("""
                INSERT INTO fluxo_caixa (tipo, categoria, descricao, valor, data_movimentacao)
                VALUES ('saida', 'Estorno', ?, ?, datetime('now'))
            """, (f'Estorno venda #{id_venda}', valor))
        
        # Cancelar conta a receber (se foi à prazo)
        if forma_pagamento == 'prazo':
            cur.execute("""
                UPDATE contas_receber 
                SET status='cancelada', observacao=COALESCE(observacao, '') || ' | Estornada: ' || ?
                WHERE id_venda=? AND status != 'recebido'
            """, (motivo, id_venda))
        
        # Marcar venda como estornada
        cur.execute("""
            UPDATE vendas SET status='estornada', observacao=COALESCE(observacao, '') || ' | ESTORNADA: ' || ?
            WHERE id_venda=?
        """, (motivo, id_venda))
        
        conn.commit()
        log_event('venda_estornada', 'sistema', detalhe=f'Venda #{id_venda} estornada: {motivo}')
        conn.close()
        
        return jsonify({'mensagem': 'Venda estornada com sucesso'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500

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
                     p.nome as produto_nome, p.preco as produto_preco,
                     v.id_venda, v.total as venda_total, v.forma_pagamento,
                     c.nome as cliente_nome
              FROM movimentacoes m
              LEFT JOIN produtos p ON p.id_produto = m.id_produto
              LEFT JOIN vendas v ON m.observacao LIKE '%Venda #' || v.id_venda || '%'
              LEFT JOIN clientes c ON c.id_cliente = v.id_cliente
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
        mov_dict = {
            'id_mov': r[0],
            'id_produto': r[1],
            'tipo': r[2],
            'quantidade': r[3],
            'observacao': r[4],
            'data_mov': r[5],
            'produto_nome': r[6],
            'produto_preco': r[7]
        }
        # Adicionar dados da venda se existir
        if r[8]:  # id_venda existe
            mov_dict['venda'] = {
                'id_venda': r[8],
                'total': r[9],
                'forma_pagamento': r[10],
                'cliente_nome': r[11] or 'Cliente não identificado'
            }
        result.append(mov_dict)
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


# ============================================
# MÓDULO ERP: FORNECEDORES
# ============================================

@app.route('/fornecedores')
def fornecedores_page():
    return render_template('fornecedores.html')

@app.route('/api/fornecedores', methods=['GET'])
def listar_fornecedores():
    conn = get_db()
    q = request.args.get('q', '').strip()
    ativo = request.args.get('ativo')
    
    query = "SELECT * FROM fornecedores WHERE 1=1"
    params = []
    
    if q:
        query += " AND (nome_fantasia LIKE ? OR razao_social LIKE ? OR cnpj LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
    
    if ativo is not None:
        query += " AND ativo = ?"
        params.append(int(ativo))
    
    query += " ORDER BY nome_fantasia"
    
    cur = conn.execute(query, params)
    fornecedores = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(fornecedores)

@app.route('/api/fornecedores', methods=['POST'])
def criar_fornecedor():
    data = request.json or {}
    
    nome_fantasia = data.get('nome_fantasia', '').strip()
    razao_social = data.get('razao_social', '').strip()
    cnpj = data.get('cnpj', '').strip()
    
    if not nome_fantasia:
        return jsonify({'erro': 'Nome fantasia é obrigatório'}), 400
    
    conn = get_db()
    try:
        cur = conn.execute("""
            INSERT INTO fornecedores (
                nome_fantasia, razao_social, cnpj, ie, contato, telefone, email, site,
                endereco, cidade, estado, cep, banco, agencia, conta, observacoes, ativo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nome_fantasia, razao_social, cnpj, data.get('ie'), data.get('contato'),
            data.get('telefone'), data.get('email'), data.get('site'), data.get('endereco'),
            data.get('cidade'), data.get('estado'), data.get('cep'), data.get('banco'),
            data.get('agencia'), data.get('conta'), data.get('observacoes'), 
            data.get('ativo', 1)
        ))
        conn.commit()
        fornecedor_id = cur.lastrowid
        log_event('fornecedor_criado', 'sistema', detalhe=f'Fornecedor {nome_fantasia} criado')
        conn.close()
        return jsonify({'mensagem': 'Fornecedor criado', 'id_fornecedor': fornecedor_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'erro': 'CNPJ já cadastrado'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/fornecedores/<int:id_fornecedor>', methods=['GET'])
def obter_fornecedor(id_fornecedor):
    conn = get_db()
    cur = conn.execute("SELECT * FROM fornecedores WHERE id_fornecedor=?", (id_fornecedor,))
    fornecedor = cur.fetchone()
    conn.close()
    
    if not fornecedor:
        return jsonify({'erro': 'Fornecedor não encontrado'}), 404
    
    return jsonify(dict(fornecedor))

@app.route('/api/fornecedores/<int:id_fornecedor>', methods=['PUT'])
def atualizar_fornecedor(id_fornecedor):
    data = request.json or {}
    conn = get_db()
    
    cur = conn.execute("SELECT id_fornecedor FROM fornecedores WHERE id_fornecedor=?", (id_fornecedor,))
    if not cur.fetchone():
        conn.close()
        return jsonify({'erro': 'Fornecedor não encontrado'}), 404
    
    try:
        conn.execute("""
            UPDATE fornecedores SET
                nome_fantasia=?, razao_social=?, cnpj=?, ie=?, contato=?, telefone=?,
                email=?, site=?, endereco=?, cidade=?, estado=?, cep=?, banco=?, 
                agencia=?, conta=?, observacoes=?, ativo=?, atualizado_em=datetime('now')
            WHERE id_fornecedor=?
        """, (
            data.get('nome_fantasia'), data.get('razao_social'), data.get('cnpj'),
            data.get('ie'), data.get('contato'), data.get('telefone'), data.get('email'),
            data.get('site'), data.get('endereco'), data.get('cidade'), data.get('estado'),
            data.get('cep'), data.get('banco'), data.get('agencia'), data.get('conta'),
            data.get('observacoes'), data.get('ativo', 1), id_fornecedor
        ))
        conn.commit()
        conn.close()
        return jsonify({'mensagem': 'Fornecedor atualizado'})
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/fornecedores/<int:id_fornecedor>', methods=['DELETE'])
def deletar_fornecedor(id_fornecedor):
    conn = get_db()
    cur = conn.execute("SELECT id_fornecedor FROM fornecedores WHERE id_fornecedor=?", (id_fornecedor,))
    if not cur.fetchone():
        conn.close()
        return jsonify({'erro': 'Fornecedor não encontrado'}), 404
    
    try:
        conn.execute("DELETE FROM fornecedores WHERE id_fornecedor=?", (id_fornecedor,))
        conn.commit()
        conn.close()
        return jsonify({'mensagem': 'Fornecedor removido'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'erro': 'Fornecedor possui registros vinculados'}), 400


# ============================================
# MÓDULO ERP: COMPRAS
# ============================================

@app.route('/compras')
def compras_page():
    return render_template('compras.html')

@app.route('/api/compras', methods=['GET'])
def listar_compras():
    conn = get_db()
    status = request.args.get('status')
    fornecedor_id = request.args.get('fornecedor_id')
    
    query = """
        SELECT c.*, f.nome_fantasia as fornecedor_nome
        FROM compras c
        LEFT JOIN fornecedores f ON f.id_fornecedor = c.id_fornecedor
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND c.status = ?"
        params.append(status)
    
    if fornecedor_id:
        query += " AND c.id_fornecedor = ?"
        params.append(int(fornecedor_id))
    
    query += " ORDER BY c.data_compra DESC"
    
    cur = conn.execute(query, params)
    compras = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(compras)

@app.route('/api/compras', methods=['POST'])
def criar_compra():
    data = request.json or {}
    
    id_fornecedor = data.get('id_fornecedor')
    if not id_fornecedor:
        return jsonify({'erro': 'Fornecedor é obrigatório'}), 400
    
    conn = get_db()
    try:
        cur = conn.execute("""
            INSERT INTO compras (
                id_fornecedor, numero_pedido, data_compra, data_entrega_prevista,
                status, observacao
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id_fornecedor, data.get('numero_pedido'), 
            data.get('data_compra', 'now'), data.get('data_entrega_prevista'),
            'pendente', data.get('observacao')
        ))
        compra_id = cur.lastrowid
        
        # Adicionar itens da compra
        items = data.get('items', [])
        valor_total = 0
        
        for item in items:
            subtotal = item['quantidade'] * item['preco_unitario'] - item.get('desconto_item', 0)
            valor_total += subtotal
            
            conn.execute("""
                INSERT INTO compra_items (id_compra, id_produto, quantidade, preco_unitario, desconto_item, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                compra_id, item['id_produto'], item['quantidade'], 
                item['preco_unitario'], item.get('desconto_item', 0), subtotal
            ))
        
        # Atualizar valor total da compra
        desconto = data.get('desconto', 0)
        frete = data.get('valor_frete', 0)
        valor_final = valor_total - desconto + frete
        
        conn.execute("""
            UPDATE compras SET valor_total=?, desconto=?, valor_frete=?, valor_final=?
            WHERE id_compra=?
        """, (valor_total, desconto, frete, valor_final, compra_id))
        
        # Criar conta a pagar automaticamente
        # Calcular data de vencimento (padrão: 30 dias da data da compra)
        conn.execute("""
            INSERT INTO contas_pagar (
                id_fornecedor, descricao, valor, data_vencimento, status, numero_documento, observacao
            ) VALUES (?, ?, ?, date(?, '+30 days'), 'pendente', ?, ?)
        """, (
            id_fornecedor,
            f'Compra #{compra_id} - {data.get("numero_pedido", "")}',
            valor_final,
            data.get('data_compra', 'now'),
            data.get('numero_pedido'),
            f'Conta gerada automaticamente da compra #{compra_id}'
        ))
        
        conn.commit()
        log_event('compra_criada', 'sistema', valor=valor_final, detalhe=f'Compra #{compra_id}')
        conn.close()
        
        return jsonify({'mensagem': 'Compra criada e conta a pagar gerada', 'id_compra': compra_id}), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/compras/<int:id_compra>/receber', methods=['POST'])
def receber_compra(id_compra):
    """Receber itens da compra e atualizar estoque"""
    data = request.json or {}
    conn = get_db()
    
    try:
        # Verificar compra
        cur = conn.execute("SELECT * FROM compras WHERE id_compra=?", (id_compra,))
        compra = cur.fetchone()
        if not compra:
            conn.close()
            return jsonify({'erro': 'Compra não encontrada'}), 404
        
        # Receber itens
        items_recebidos = data.get('items', [])
        
        for item in items_recebidos:
            id_item = item['id_item']
            qtd_recebida = item['quantidade_recebida']
            
            # Atualizar item da compra
            conn.execute("""
                UPDATE compra_items SET recebido = recebido + ?
                WHERE id_item=?
            """, (qtd_recebida, id_item))
            
            # Atualizar estoque
            cur.execute("SELECT id_produto FROM compra_items WHERE id_item=?", (id_item,))
            id_produto = cur.fetchone()['id_produto']
            
            conn.execute("""
                UPDATE produtos SET quantidade = quantidade + ?
                WHERE id_produto=?
            """, (qtd_recebida, id_produto))
            
            # Registrar movimentação
            conn.execute("""
                INSERT INTO movimentacoes (id_produto, tipo, quantidade, observacao)
                VALUES (?, 'entrada', ?, ?)
            """, (id_produto, qtd_recebida, f'Recebimento compra #{id_compra}'))
        
        # Atualizar status da compra
        conn.execute("UPDATE compras SET data_entrega_real=datetime('now') WHERE id_compra=?", (id_compra,))
        
        # Verificar se todos itens foram recebidos
        cur.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN recebido >= quantidade THEN 1 ELSE 0 END) as completos
            FROM compra_items WHERE id_compra=?
        """, (id_compra,))
        status_check = cur.fetchone()
        
        if status_check['total'] == status_check['completos']:
            conn.execute("UPDATE compras SET status='concluida' WHERE id_compra=?", (id_compra,))
        else:
            conn.execute("UPDATE compras SET status='parcial' WHERE id_compra=?", (id_compra,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Itens recebidos com sucesso'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/compras/<int:id_compra>', methods=['GET'])
def obter_compra(id_compra):
    conn = get_db()
    cur = conn.execute("""
        SELECT c.*, f.nome_fantasia as fornecedor_nome
        FROM compras c
        LEFT JOIN fornecedores f ON f.id_fornecedor = c.id_fornecedor
        WHERE c.id_compra=?
    """, (id_compra,))
    compra = cur.fetchone()
    conn.close()
    
    if compra:
        return jsonify(dict(compra))
    return jsonify({'erro': 'Compra não encontrada'}), 404

@app.route('/api/compras/<int:id_compra>/items', methods=['GET'])
def listar_itens_compra(id_compra):
    conn = get_db()
    cur = conn.execute("""
        SELECT ci.*, p.nome as produto_nome
        FROM compra_items ci
        LEFT JOIN produtos p ON p.id_produto = ci.id_produto
        WHERE ci.id_compra=?
    """, (id_compra,))
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/api/compras/<int:id_compra>', methods=['PUT'])
def atualizar_compra(id_compra):
    data = request.json or {}
    conn = get_db()
    
    try:
        # Update only the fields provided
        updates = []
        params = []
        
        if 'status' in data:
            updates.append('status = ?')
            params.append(data['status'])
        
        if updates:
            query = f"UPDATE compras SET {', '.join(updates)} WHERE id_compra=?"
            params.append(id_compra)
            conn.execute(query, params)
            conn.commit()
        
        conn.close()
        return jsonify({'mensagem': 'Compra atualizada'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500


# ============================================
# MÓDULO ERP: CONTAS A PAGAR
# ============================================

@app.route('/contas_pagar')
def contas_pagar_page():
    return render_template('contas_pagar.html')

@app.route('/api/contas_pagar', methods=['GET'])
def listar_contas_pagar():
    conn = get_db()
    status = request.args.get('status')
    vencidas = request.args.get('vencidas')
    
    query = """
        SELECT cp.*, f.nome_fantasia as fornecedor_nome, cat.nome as categoria_nome
        FROM contas_pagar cp
        LEFT JOIN fornecedores f ON f.id_fornecedor = cp.id_fornecedor
        LEFT JOIN categorias_financeiras cat ON cat.id_categoria = cp.id_categoria
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND cp.status = ?"
        params.append(status)
    
    if vencidas == '1':
        query += " AND cp.status = 'pendente' AND cp.data_vencimento < datetime('now')"
    
    query += " ORDER BY cp.data_vencimento ASC"
    
    cur = conn.execute(query, params)
    contas = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(contas)

@app.route('/api/contas_pagar', methods=['POST'])
def criar_conta_pagar():
    data = request.json or {}
    conn = get_db()
    
    try:
        cur = conn.execute("""
            INSERT INTO contas_pagar (
                id_fornecedor, id_compra, id_categoria, descricao, valor,
                data_vencimento, status, forma_pagamento, numero_documento, observacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('id_fornecedor'), data.get('id_compra'), data.get('id_categoria'),
            data['descricao'], data['valor'], data['data_vencimento'],
            'pendente', data.get('forma_pagamento'), data.get('numero_documento'),
            data.get('observacao')
        ))
        conta_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Conta a pagar criada', 'id_conta': conta_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/contas_pagar/<int:id_conta>/estornar', methods=['POST'])
def estornar_pagamento(id_conta):
    """Estorna um pagamento: volta conta para pendente e reverte fluxo de caixa"""
    data = request.json or {}
    motivo = data.get('motivo', 'Estorno de pagamento')
    
    conn = get_db()
    
    try:
        # Buscar conta
        cur = conn.execute("SELECT * FROM contas_pagar WHERE id_conta=?", (id_conta,))
        conta = cur.fetchone()
        if not conta:
            conn.close()
            return jsonify({'erro': 'Conta não encontrada'}), 404
        
        # Verificar se está paga
        if conta['status'] != 'pago':
            conn.close()
            return jsonify({'erro': 'Esta conta não está paga'}), 400
        
        # Reverter status da conta
        conn.execute("""
            UPDATE contas_pagar SET
                status='pendente',
                data_pagamento=NULL,
                observacao=COALESCE(observacao, '') || ' | Pagamento estornado: ' || ?
            WHERE id_conta=?
        """, (motivo, id_conta))
        
        # Criar entrada no fluxo para cancelar a saída
        conn.execute("""
            INSERT INTO fluxo_caixa (tipo, categoria, descricao, valor, data_movimentacao)
            VALUES ('entrada', 'Estorno', ?, ?, datetime('now'))
        """, (f'Estorno pagamento conta #{id_conta}', conta['valor']))
        
        conn.commit()
        log_event('pagamento_estornado', 'sistema', valor=conta['valor'], detalhe=f'Conta #{id_conta} estornada')
        conn.close()
        
        return jsonify({'mensagem': 'Pagamento estornado com sucesso'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/contas_pagar/<int:id_conta>/pagar', methods=['POST'])
def pagar_conta(id_conta):
    data = request.json or {}
    conn = get_db()
    
    try:
        # Buscar conta
        cur = conn.execute("SELECT * FROM contas_pagar WHERE id_conta=?", (id_conta,))
        conta = cur.fetchone()
        if not conta:
            conn.close()
            return jsonify({'erro': 'Conta não encontrada'}), 404
        
        # Verificar se já foi paga
        if conta['status'] == 'pago':
            conn.close()
            return jsonify({'erro': 'Esta conta já foi paga'}), 400
        
        # Atualizar conta
        conn.execute("""
            UPDATE contas_pagar SET
                status='pago',
                data_pagamento=?,
                forma_pagamento=?,
                observacao=?
            WHERE id_conta=?
        """, (data.get('data_pagamento'), data.get('forma_pagamento'), data.get('observacao'), id_conta))
        
        # Registrar no fluxo de caixa usando categoria como texto
        forma_desc = data.get('forma_pagamento', 'Não especificado')
        conn.execute("""
            INSERT INTO fluxo_caixa (tipo, categoria, descricao, valor, data_movimentacao)
            VALUES ('saida', ?, ?, ?, ?)
        """, (forma_desc, conta['descricao'], conta['valor'], data.get('data_pagamento')))
        
        conn.commit()
        log_event('conta_paga', 'sistema', valor=conta['valor'], detalhe=f'Conta #{id_conta} paga')
        conn.close()
        
        return jsonify({'mensagem': 'Conta paga com sucesso'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500


# ============================================
# MÓDULO ERP: CONTAS A RECEBER
# ============================================

@app.route('/contas_receber')
def contas_receber_page():
    return render_template('contas_receber.html')

@app.route('/api/contas_receber', methods=['GET'])
def listar_contas_receber():
    conn = get_db()
    status = request.args.get('status')
    vencidas = request.args.get('vencidas')
    
    query = """
        SELECT cr.*, c.nome as cliente_nome, cat.nome as categoria_nome
        FROM contas_receber cr
        LEFT JOIN clientes c ON c.id_cliente = cr.id_cliente
        LEFT JOIN categorias_financeiras cat ON cat.id_categoria = cr.id_categoria
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND cr.status = ?"
        params.append(status)
    
    if vencidas == '1':
        query += " AND cr.status = 'pendente' AND cr.data_vencimento < datetime('now')"
    
    query += " ORDER BY cr.data_vencimento ASC"
    
    cur = conn.execute(query, params)
    contas = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(contas)

@app.route('/api/contas_receber', methods=['POST'])
def criar_conta_receber():
    data = request.json or {}
    conn = get_db()
    
    try:
        cur = conn.execute("""
            INSERT INTO contas_receber (
                id_cliente, id_venda, id_categoria, descricao, valor,
                data_vencimento, status, forma_recebimento, numero_documento, observacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('id_cliente'), data.get('id_venda'), data.get('id_categoria'),
            data['descricao'], data['valor'], data['data_vencimento'],
            'pendente', data.get('forma_recebimento'), data.get('numero_documento'),
            data.get('observacao')
        ))
        conta_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Conta a receber criada', 'id_conta': conta_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/contas_receber/<int:id_conta>/estornar', methods=['POST'])
def estornar_recebimento(id_conta):
    """Estorna um recebimento: volta conta para pendente e reverte fluxo de caixa"""
    data = request.json or {}
    motivo = data.get('motivo', 'Estorno de recebimento')
    
    conn = get_db()
    
    try:
        # Buscar conta
        cur = conn.execute("SELECT * FROM contas_receber WHERE id_conta=?", (id_conta,))
        conta = cur.fetchone()
        if not conta:
            conn.close()
            return jsonify({'erro': 'Conta não encontrada'}), 404
        
        # Verificar se está recebida
        if conta['status'] != 'recebido':
            conn.close()
            return jsonify({'erro': 'Esta conta não está recebida'}), 400
        
        # Reverter status da conta
        conn.execute("""
            UPDATE contas_receber SET
                status='pendente',
                data_recebimento=NULL,
                observacao=COALESCE(observacao, '') || ' | Recebimento estornado: ' || ?
            WHERE id_conta=?
        """, (motivo, id_conta))
        
        # Criar saída no fluxo para cancelar a entrada
        conn.execute("""
            INSERT INTO fluxo_caixa (tipo, categoria, descricao, valor, data_movimentacao)
            VALUES ('saida', 'Estorno', ?, ?, datetime('now'))
        """, (f'Estorno recebimento conta #{id_conta}', conta['valor']))
        
        conn.commit()
        log_event('recebimento_estornado', 'sistema', valor=conta['valor'], detalhe=f'Conta #{id_conta} estornada')
        conn.close()
        
        return jsonify({'mensagem': 'Recebimento estornado com sucesso'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/contas_receber/<int:id_conta>/receber', methods=['POST'])
def receber_conta(id_conta):
    data = request.json or {}
    conn = get_db()
    
    try:
        # Buscar conta
        cur = conn.execute("SELECT * FROM contas_receber WHERE id_conta=?", (id_conta,))
        conta = cur.fetchone()
        if not conta:
            conn.close()
            return jsonify({'erro': 'Conta não encontrada'}), 404
        
        # Verificar se já foi recebida
        if conta['status'] == 'recebido':
            conn.close()
            return jsonify({'erro': 'Esta conta já foi recebida'}), 400
        
        # Atualizar conta
        conn.execute("""
            UPDATE contas_receber SET
                status='recebido',
                data_recebimento=?,
                forma_recebimento=?,
                observacao=?
            WHERE id_conta=?
        """, (data.get('data_pagamento'), data.get('forma_pagamento'), data.get('observacao'), id_conta))
        
        # Registrar no fluxo de caixa usando categoria como texto
        forma_desc = data.get('forma_pagamento', 'Não especificado')
        conn.execute("""
            INSERT INTO fluxo_caixa (tipo, categoria, descricao, valor, data_movimentacao)
            VALUES ('entrada', ?, ?, ?, ?)
        """, (forma_desc, conta['descricao'], conta['valor'], data.get('data_pagamento')))
        
        conn.commit()
        log_event('conta_recebida', 'sistema', valor=conta['valor'], detalhe=f'Conta #{id_conta} recebida')
        conn.close()
        
        return jsonify({'mensagem': 'Conta recebida com sucesso'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500


# ============================================
# MÓDULO ERP: FLUXO DE CAIXA
# ============================================

@app.route('/fluxo_caixa')
def fluxo_caixa_page():
    return render_template('fluxo_caixa.html')

@app.route('/api/fluxo_caixa', methods=['GET'])
def listar_fluxo_caixa():
    conn = get_db()
    
    # Garantir que a coluna 'categoria' existe
    cur = conn.execute("PRAGMA table_info('fluxo_caixa')")
    cols = [r['name'] for r in cur.fetchall()]
    if 'categoria' not in cols:
        try:
            conn.execute('ALTER TABLE fluxo_caixa ADD COLUMN categoria TEXT')
            conn.commit()
        except Exception:
            pass
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    tipo = request.args.get('tipo')
    
    query = """
        SELECT fc.*, cat.nome as categoria_nome,
               COALESCE(fc.categoria, cat.nome) as categoria_display
        FROM fluxo_caixa fc
        LEFT JOIN categorias_financeiras cat ON cat.id_categoria = fc.id_categoria
        WHERE 1=1
    """
    params = []
    
    if data_inicio:
        query += " AND DATE(fc.data_movimentacao) >= ?"
        params.append(data_inicio)
    
    if data_fim:
        query += " AND DATE(fc.data_movimentacao) <= ?"
        params.append(data_fim)
    
    if tipo:
        query += " AND fc.tipo = ?"
        params.append(tipo)
    
    query += " ORDER BY fc.data_movimentacao DESC"
    
    cur = conn.execute(query, params)
    registros = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(registros)

@app.route('/api/fluxo_caixa/resumo', methods=['GET'])
def resumo_fluxo_caixa():
    conn = get_db()
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = """
        SELECT 
            SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END) as total_entradas,
            SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END) as total_saidas,
            SUM(CASE WHEN tipo='entrada' THEN valor ELSE -valor END) as saldo
        FROM fluxo_caixa
        WHERE 1=1
    """
    params = []
    
    if data_inicio:
        query += " AND DATE(data_movimentacao) >= ?"
        params.append(data_inicio)
    
    if data_fim:
        query += " AND DATE(data_movimentacao) <= ?"
        params.append(data_fim)
    
    cur = conn.execute(query, params)
    resumo = dict(cur.fetchone())
    conn.close()
    
    return jsonify(resumo)

@app.route('/api/fluxo_caixa', methods=['POST'])
def criar_fluxo_caixa():
    """Cria novo registro de fluxo de caixa"""
    data = request.json or {}
    conn = get_db()
    
    try:
        cur = conn.execute("""
            INSERT INTO fluxo_caixa (tipo, categoria, valor, descricao, data_movimentacao)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get('tipo'),
            data.get('categoria'),
            data.get('valor'),
            data.get('descricao'),
            data.get('data_movimentacao')
        ))
        
        conn.commit()
        id_movimentacao = cur.lastrowid
        conn.close()
        
        return jsonify({'mensagem': 'Movimentação criada', 'id_movimentacao': id_movimentacao}), 201
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/fluxo_caixa/<int:id_movimentacao>', methods=['DELETE'])
def excluir_fluxo_caixa(id_movimentacao):
    """Exclui registro de fluxo de caixa"""
    conn = get_db()
    
    try:
        conn.execute("DELETE FROM fluxo_caixa WHERE id_movimentacao=?", (id_movimentacao,))
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Movimentação excluída'})
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500


# ============================================
# MÓDULO ERP: CATEGORIAS FINANCEIRAS
# ============================================

@app.route('/api/categorias_financeiras', methods=['GET'])
def listar_categorias_financeiras():
    conn = get_db()
    tipo = request.args.get('tipo')
    
    query = "SELECT * FROM categorias_financeiras WHERE ativo=1"
    params = []
    
    if tipo:
        query += " AND tipo=?"
        params.append(tipo)
    
    query += " ORDER BY nome"
    
    cur = conn.execute(query, params)
    categorias = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(categorias)


# ============================================
# MÓDULO ERP: DASHBOARD FINANCEIRO
# ============================================

@app.route('/dashboard_financeiro')
def dashboard_financeiro():
    return render_template('dashboard_financeiro.html')

@app.route('/api/dashboard/kpis', methods=['GET'])
def dashboard_kpis():
    """Retorna indicadores financeiros para o dashboard"""
    conn = get_db()
    
    # Contas a pagar pendentes
    cur = conn.execute("""
        SELECT COUNT(*) as total, COALESCE(SUM(valor), 0) as valor_total
        FROM contas_pagar WHERE status='pendente'
    """)
    contas_pagar = dict(cur.fetchone())
    
    # Contas a receber pendentes
    cur = conn.execute("""
        SELECT COUNT(*) as total, COALESCE(SUM(valor), 0) as valor_total
        FROM contas_receber WHERE status='pendente'
    """)
    contas_receber = dict(cur.fetchone())
    
    # Contas vencidas a pagar
    cur = conn.execute("""
        SELECT COUNT(*) as total, COALESCE(SUM(valor), 0) as valor_total
        FROM contas_pagar 
        WHERE status='pendente' AND data_vencimento < datetime('now')
    """)
    vencidas_pagar = dict(cur.fetchone())
    
    # Contas vencidas a receber
    cur = conn.execute("""
        SELECT COUNT(*) as total, COALESCE(SUM(valor), 0) as valor_total
        FROM contas_receber 
        WHERE status='pendente' AND data_vencimento < datetime('now')
    """)
    vencidas_receber = dict(cur.fetchone())
    
    # Fluxo de caixa do mês
    cur = conn.execute("""
        SELECT 
            SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END) as entradas,
            SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END) as saidas
        FROM fluxo_caixa
        WHERE strftime('%Y-%m', data_movimentacao) = strftime('%Y-%m', 'now')
    """)
    fluxo_mes = dict(cur.fetchone())
    
    # Valor em estoque
    cur = conn.execute("""
        SELECT COALESCE(SUM(quantidade * preco), 0) as valor_estoque
        FROM produtos
    """)
    valor_estoque = cur.fetchone()['valor_estoque']
    
    # Produtos com estoque baixo (menos de 10)
    cur = conn.execute("""
        SELECT COUNT(*) as total FROM produtos WHERE quantidade < 10
    """)
    produtos_baixo_estoque = cur.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'contas_pagar': contas_pagar,
        'contas_receber': contas_receber,
        'vencidas_pagar': vencidas_pagar,
        'vencidas_receber': vencidas_receber,
        'fluxo_mes': fluxo_mes,
        'valor_estoque': valor_estoque,
        'produtos_baixo_estoque': produtos_baixo_estoque
    })


# ============================================
# MÓDULO ERP: INVENTÁRIO
# ============================================

@app.route('/inventario')
def inventario_page():
    return render_template('inventario.html')

@app.route('/api/inventarios', methods=['GET'])
def listar_inventarios():
    conn = get_db()
    cur = conn.execute("SELECT * FROM inventarios ORDER BY data_inicio DESC")
    inventarios = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(inventarios)

@app.route('/api/inventarios', methods=['POST'])
def criar_inventario():
    data = request.json or {}
    conn = get_db()
    
    try:
        cur = conn.execute("""
            INSERT INTO inventarios (responsavel, observacao, status)
            VALUES (?, ?, 'em_andamento')
        """, (data.get('responsavel'), data.get('observacao')))
        
        inventario_id = cur.lastrowid
        
        # Criar items baseado no estoque atual
        conn.execute("""
            INSERT INTO inventario_items (id_inventario, id_produto, quantidade_sistema)
            SELECT ?, id_produto, quantidade FROM produtos
        """, (inventario_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Inventário criado', 'id_inventario': inventario_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/inventarios/<int:id_inventario>/items', methods=['GET'])
def listar_items_inventario(id_inventario):
    conn = get_db()
    cur = conn.execute("""
        SELECT ii.*, p.nome as produto_nome, p.codigo_barras
        FROM inventario_items ii
        JOIN produtos p ON p.id_produto = ii.id_produto
        WHERE ii.id_inventario=?
        ORDER BY p.nome
    """, (id_inventario,))
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/api/inventarios/<int:id_inventario>/items/<int:id_item>', methods=['PUT'])
def atualizar_item_inventario(id_inventario, id_item):
    data = request.json or {}
    conn = get_db()
    
    try:
        qtd_contada = data.get('quantidade_contada')
        
        # Buscar quantidade do sistema
        cur = conn.execute("""
            SELECT quantidade_sistema FROM inventario_items WHERE id_item=?
        """, (id_item,))
        item = cur.fetchone()
        
        diferenca = qtd_contada - item['quantidade_sistema']
        
        conn.execute("""
            UPDATE inventario_items 
            SET quantidade_contada=?, diferenca=?, observacao=?
            WHERE id_item=?
        """, (qtd_contada, diferenca, data.get('observacao'), id_item))
        
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Item atualizado', 'diferenca': diferenca})
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/inventarios/<int:id_inventario>/finalizar', methods=['POST'])
def finalizar_inventario(id_inventario):
    """Finaliza inventário e ajusta estoque com base nas diferenças"""
    conn = get_db()
    
    try:
        # Buscar items com diferença
        cur = conn.execute("""
            SELECT * FROM inventario_items 
            WHERE id_inventario=? AND diferenca IS NOT NULL AND diferenca != 0
        """, (id_inventario,))
        
        items_com_diferenca = cur.fetchall()
        
        for item in items_com_diferenca:
            id_produto = item['id_produto']
            diferenca = item['diferenca']
            
            # Atualizar estoque
            conn.execute("""
                UPDATE produtos SET quantidade = quantidade + ?
                WHERE id_produto=?
            """, (diferenca, id_produto))
            
            # Registrar ajuste
            conn.execute("""
                INSERT INTO ajustes_estoque (
                    id_produto, tipo_ajuste, quantidade, motivo, id_inventario
                ) VALUES (?, 'ajuste_inventario', ?, ?, ?)
            """, (id_produto, diferenca, f'Ajuste inventário #{id_inventario}', id_inventario))
        
        # Finalizar inventário
        conn.execute("""
            UPDATE inventarios 
            SET status='concluido', data_fim=datetime('now')
            WHERE id_inventario=?
        """, (id_inventario,))
        
        conn.commit()
        log_event('inventario_finalizado', 'sistema', detalhe=f'Inventário #{id_inventario} com {len(items_com_diferenca)} ajustes')
        conn.close()
        
        return jsonify({
            'mensagem': 'Inventário finalizado',
            'ajustes_realizados': len(items_com_diferenca)
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/inventarios/<int:id_inventario>', methods=['DELETE'])
def excluir_inventario(id_inventario):
    """Exclui um inventário e seus itens"""
    conn = get_db()
    
    try:
        # Verificar se o inventário existe
        cur = conn.execute("SELECT status FROM inventarios WHERE id_inventario=?", (id_inventario,))
        inventario = cur.fetchone()
        
        if not inventario:
            conn.close()
            return jsonify({'erro': 'Inventário não encontrado'}), 404
        
        if inventario['status'] == 'concluido':
            conn.close()
            return jsonify({'erro': 'Não é possível excluir um inventário já finalizado'}), 400
        
        # Excluir itens do inventário
        conn.execute("DELETE FROM inventario_items WHERE id_inventario=?", (id_inventario,))
        
        # Excluir inventário
        conn.execute("DELETE FROM inventarios WHERE id_inventario=?", (id_inventario,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Inventário excluído com sucesso'})
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500


# ============================================
# MÓDULO ERP: RELATÓRIOS
# ============================================

@app.route('/relatorios')
def relatorios_page():
    return render_template('relatorios.html')

@app.route('/api/relatorios/curva_abc', methods=['GET'])
def relatorio_curva_abc():
    """Análise ABC de produtos por valor de estoque"""
    conn = get_db()
    cur = conn.execute("""
        SELECT 
            id_produto, nome, categoria, quantidade, preco,
            (quantidade * preco) as valor_estoque
        FROM produtos
        WHERE quantidade > 0
        ORDER BY valor_estoque DESC
    """)
    
    produtos = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    if not produtos:
        return jsonify([])
    
    # Calcular valor total
    valor_total = sum(p['valor_estoque'] for p in produtos)
    
    # Calcular percentuais acumulados e classificar
    acumulado = 0
    for produto in produtos:
        percentual = (produto['valor_estoque'] / valor_total) * 100 if valor_total > 0 else 0
        acumulado += percentual
        produto['percentual'] = round(percentual, 2)
        produto['acumulado'] = round(acumulado, 2)
        
        # Classificação ABC
        if acumulado <= 80:
            produto['classe'] = 'A'
        elif acumulado <= 95:
            produto['classe'] = 'B'
        else:
            produto['classe'] = 'C'
    
    return jsonify(produtos)

@app.route('/api/relatorios/lucratividade', methods=['GET'])
def relatorio_lucratividade():
    """Análise de lucratividade por produto"""
    conn = get_db()
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = """
        SELECT 
            p.id_produto, p.nome, p.categoria, p.preco as preco_atual,
            COUNT(vi.id_item) as total_vendas,
            SUM(vi.quantidade) as quantidade_vendida,
            AVG(vi.preco_unitario) as preco_medio_venda,
            SUM(vi.quantidade * vi.preco_unitario) as receita_total
        FROM produtos p
        LEFT JOIN venda_items vi ON vi.id_produto = p.id_produto
        LEFT JOIN vendas v ON v.id_venda = vi.id_venda
        WHERE 1=1
    """
    params = []
    
    if data_inicio:
        query += " AND DATE(v.data_venda) >= ?"
        params.append(data_inicio)
    
    if data_fim:
        query += " AND DATE(v.data_venda) <= ?"
        params.append(data_fim)
    
    query += " GROUP BY p.id_produto ORDER BY receita_total DESC"
    
    cur = conn.execute(query, params)
    produtos = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return jsonify(produtos)

@app.route('/api/relatorios/estoque_valorizado', methods=['GET'])
def relatorio_estoque_valorizado():
    """Relatório de estoque com valor total por categoria"""
    conn = get_db()
    cur = conn.execute("""
        SELECT 
            categoria,
            COUNT(*) as total_produtos,
            SUM(quantidade) as quantidade_total,
            SUM(quantidade * preco) as valor_total,
            AVG(preco) as preco_medio
        FROM produtos
        GROUP BY categoria
        ORDER BY valor_total DESC
    """)
    
    categorias = [dict(row) for row in cur.fetchall()]
    
    # Total geral
    cur.execute("""
        SELECT 
            COUNT(*) as total_produtos,
            SUM(quantidade) as quantidade_total,
            SUM(quantidade * preco) as valor_total
        FROM produtos
    """)
    total = dict(cur.fetchone())
    
    conn.close()
    
    return jsonify({
        'por_categoria': categorias,
        'total_geral': total
    })

# Tratamento de erros HTTP

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Página não encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Erro interno do servidor'), 500

if __name__ == '__main__':
    # Exibir banner amigável
    print_banner()
    
    # Configurar túnel público (ngrok)
    setup_ngrok()
    
    # Mostrar informações de acesso local
    local_ip = get_local_ip()
    print(f"{Fore.CYAN}{Style.BRIGHT}╔" + "═" * 68 + f"╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.WHITE}{Style.BRIGHT}                     🏠 ACESSO NA REDE LOCAL                       {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}╠" + "═" * 68 + f"╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║  {Fore.WHITE}💻 Neste computador:{Style.RESET_ALL}  {Fore.YELLOW}{Style.BRIGHT}http://127.0.0.1:5000{Style.RESET_ALL}" + " " * 20 + f"{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║  {Fore.WHITE}📱 Outros dispositivos:{Style.RESET_ALL} {Fore.YELLOW}{Style.BRIGHT}http://{local_ip}:5000{Style.RESET_ALL}" + " " * (27 - len(local_ip)) + f"{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}╚" + "═" * 68 + f"╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Sistema inicializado com sucesso!{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   MANTENHA ESTA JANELA ABERTA enquanto usa o sistema.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   Para fechar: pressione Ctrl+C ou feche esta janela.{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "═" * 70 + f"{Style.RESET_ALL}\n")
    
    # Desabilitar reloader para evitar múltiplas instâncias do ngrok
    # Mantém debug para desenvolvimento mas sem recarregar automaticamente
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

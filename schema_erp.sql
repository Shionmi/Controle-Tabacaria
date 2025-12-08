-- SCHEMA ERP - EXPANSÃO DO SISTEMA DE TABACARIA
-- Módulos: Fornecedores, Compras, Financeiro, Inventário, Relatórios

PRAGMA foreign_keys = ON;

-- ============================================
-- MÓDULO: FORNECEDORES
-- ============================================
CREATE TABLE IF NOT EXISTS fornecedores (
  id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
  nome_fantasia TEXT NOT NULL,
  razao_social TEXT,
  cnpj TEXT UNIQUE,
  ie TEXT,  -- Inscrição Estadual
  contato TEXT,
  telefone TEXT,
  email TEXT,
  site TEXT,
  endereco TEXT,
  cidade TEXT,
  estado TEXT,
  cep TEXT,
  banco TEXT,
  agencia TEXT,
  conta TEXT,
  observacoes TEXT,
  ativo INTEGER DEFAULT 1,
  criado_em TIMESTAMP DEFAULT (datetime('now')),
  atualizado_em TIMESTAMP DEFAULT (datetime('now'))
);

-- ============================================
-- MÓDULO: COMPRAS (PEDIDOS AO FORNECEDOR)
-- ============================================
CREATE TABLE IF NOT EXISTS compras (
  id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
  id_fornecedor INTEGER NOT NULL,
  numero_pedido TEXT,
  data_compra TIMESTAMP DEFAULT (datetime('now')),
  data_entrega_prevista TIMESTAMP,
  data_entrega_real TIMESTAMP,
  status TEXT CHECK(status IN ('pendente','parcial','concluida','cancelada')) DEFAULT 'pendente',
  valor_total REAL DEFAULT 0.0,
  desconto REAL DEFAULT 0.0,
  valor_frete REAL DEFAULT 0.0,
  valor_final REAL DEFAULT 0.0,
  observacao TEXT,
  criado_em TIMESTAMP DEFAULT (datetime('now')),
  atualizado_em TIMESTAMP DEFAULT (datetime('now')),
  FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE RESTRICT
);

-- ITENS DA COMPRA
CREATE TABLE IF NOT EXISTS compra_items (
  id_item INTEGER PRIMARY KEY AUTOINCREMENT,
  id_compra INTEGER NOT NULL,
  id_produto INTEGER NOT NULL,
  quantidade INTEGER NOT NULL CHECK(quantidade > 0),
  preco_unitario REAL NOT NULL,
  desconto_item REAL DEFAULT 0.0,
  subtotal REAL NOT NULL,
  recebido INTEGER DEFAULT 0,  -- quantidade já recebida
  FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);

-- ============================================
-- MÓDULO: FINANCEIRO
-- ============================================

-- CATEGORIAS FINANCEIRAS
CREATE TABLE IF NOT EXISTS categorias_financeiras (
  id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  tipo TEXT CHECK(tipo IN ('receita','despesa')) NOT NULL,
  descricao TEXT,
  ativo INTEGER DEFAULT 1,
  criado_em TIMESTAMP DEFAULT (datetime('now'))
);

-- CONTAS A PAGAR
CREATE TABLE IF NOT EXISTS contas_pagar (
  id_conta INTEGER PRIMARY KEY AUTOINCREMENT,
  id_fornecedor INTEGER,
  id_compra INTEGER,
  id_categoria INTEGER,
  descricao TEXT NOT NULL,
  valor REAL NOT NULL,
  data_vencimento TIMESTAMP NOT NULL,
  data_pagamento TIMESTAMP,
  status TEXT CHECK(status IN ('pendente','pago','vencido','cancelado')) DEFAULT 'pendente',
  forma_pagamento TEXT,  -- dinheiro, cartão, pix, boleto, etc
  numero_documento TEXT,
  observacao TEXT,
  criado_em TIMESTAMP DEFAULT (datetime('now')),
  atualizado_em TIMESTAMP DEFAULT (datetime('now')),
  FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE SET NULL,
  FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE SET NULL,
  FOREIGN KEY (id_categoria) REFERENCES categorias_financeiras(id_categoria) ON DELETE SET NULL
);

-- CONTAS A RECEBER
CREATE TABLE IF NOT EXISTS contas_receber (
  id_conta INTEGER PRIMARY KEY AUTOINCREMENT,
  id_cliente INTEGER,
  id_venda INTEGER,
  id_categoria INTEGER,
  descricao TEXT NOT NULL,
  valor REAL NOT NULL,
  data_vencimento TIMESTAMP NOT NULL,
  data_recebimento TIMESTAMP,
  status TEXT CHECK(status IN ('pendente','recebido','vencido','cancelado')) DEFAULT 'pendente',
  forma_recebimento TEXT,
  numero_documento TEXT,
  observacao TEXT,
  criado_em TIMESTAMP DEFAULT (datetime('now')),
  atualizado_em TIMESTAMP DEFAULT (datetime('now')),
  FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL,
  FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE SET NULL,
  FOREIGN KEY (id_categoria) REFERENCES categorias_financeiras(id_categoria) ON DELETE SET NULL
);

-- FLUXO DE CAIXA (MOVIMENTAÇÕES FINANCEIRAS)
CREATE TABLE IF NOT EXISTS fluxo_caixa (
  id_fluxo INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT CHECK(tipo IN ('entrada','saida')) NOT NULL,
  id_categoria INTEGER,
  descricao TEXT NOT NULL,
  valor REAL NOT NULL,
  data_movimentacao TIMESTAMP DEFAULT (datetime('now')),
  forma_pagamento TEXT,
  id_conta_pagar INTEGER,
  id_conta_receber INTEGER,
  observacao TEXT,
  criado_em TIMESTAMP DEFAULT (datetime('now')),
  FOREIGN KEY (id_categoria) REFERENCES categorias_financeiras(id_categoria) ON DELETE SET NULL,
  FOREIGN KEY (id_conta_pagar) REFERENCES contas_pagar(id_conta) ON DELETE SET NULL,
  FOREIGN KEY (id_conta_receber) REFERENCES contas_receber(id_conta) ON DELETE SET NULL
);

-- ============================================
-- MÓDULO: INVENTÁRIO
-- ============================================

-- INVENTÁRIO (CONTAGEM FÍSICA)
CREATE TABLE IF NOT EXISTS inventarios (
  id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
  data_inicio TIMESTAMP DEFAULT (datetime('now')),
  data_fim TIMESTAMP,
  responsavel TEXT,
  status TEXT CHECK(status IN ('em_andamento','concluido','cancelado')) DEFAULT 'em_andamento',
  observacao TEXT,
  criado_em TIMESTAMP DEFAULT (datetime('now'))
);

-- ITENS DO INVENTÁRIO
CREATE TABLE IF NOT EXISTS inventario_items (
  id_item INTEGER PRIMARY KEY AUTOINCREMENT,
  id_inventario INTEGER NOT NULL,
  id_produto INTEGER NOT NULL,
  quantidade_sistema INTEGER NOT NULL,  -- quantidade no sistema
  quantidade_contada INTEGER,           -- quantidade física contada
  diferenca INTEGER,                    -- diferença (contada - sistema)
  observacao TEXT,
  FOREIGN KEY (id_inventario) REFERENCES inventarios(id_inventario) ON DELETE CASCADE,
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);

-- AJUSTES DE ESTOQUE (PERDAS, QUEBRAS, AJUSTES)
CREATE TABLE IF NOT EXISTS ajustes_estoque (
  id_ajuste INTEGER PRIMARY KEY AUTOINCREMENT,
  id_produto INTEGER NOT NULL,
  tipo_ajuste TEXT CHECK(tipo_ajuste IN ('perda','quebra','vencimento','furto','ajuste_inventario','outros')) NOT NULL,
  quantidade INTEGER NOT NULL,  -- pode ser negativo
  motivo TEXT NOT NULL,
  custo_unitario REAL,
  valor_total REAL,
  data_ajuste TIMESTAMP DEFAULT (datetime('now')),
  responsavel TEXT,
  id_inventario INTEGER,  -- se foi ajuste de inventário
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT,
  FOREIGN KEY (id_inventario) REFERENCES inventarios(id_inventario) ON DELETE SET NULL
);

-- ============================================
-- MÓDULO: NOTAS FISCAIS
-- ============================================
CREATE TABLE IF NOT EXISTS notas_fiscais (
  id_nota INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT CHECK(tipo IN ('entrada','saida')) NOT NULL,
  numero_nota TEXT NOT NULL,
  serie TEXT,
  chave_acesso TEXT UNIQUE,
  id_fornecedor INTEGER,  -- para NF de entrada
  id_cliente INTEGER,     -- para NF de saída
  id_compra INTEGER,
  id_venda INTEGER,
  data_emissao TIMESTAMP NOT NULL,
  valor_total REAL NOT NULL,
  valor_produtos REAL,
  valor_frete REAL DEFAULT 0.0,
  valor_seguro REAL DEFAULT 0.0,
  desconto REAL DEFAULT 0.0,
  impostos REAL DEFAULT 0.0,
  xml_path TEXT,
  pdf_path TEXT,
  status TEXT CHECK(status IN ('autorizada','cancelada','denegada')) DEFAULT 'autorizada',
  observacao TEXT,
  criado_em TIMESTAMP DEFAULT (datetime('now')),
  FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE SET NULL,
  FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL,
  FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE SET NULL,
  FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE SET NULL
);

-- ============================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_compras_fornecedor ON compras(id_fornecedor);
CREATE INDEX IF NOT EXISTS idx_compras_status ON compras(status);
CREATE INDEX IF NOT EXISTS idx_contas_pagar_status ON contas_pagar(status);
CREATE INDEX IF NOT EXISTS idx_contas_pagar_vencimento ON contas_pagar(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_contas_receber_status ON contas_receber(status);
CREATE INDEX IF NOT EXISTS idx_contas_receber_vencimento ON contas_receber(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_fluxo_caixa_data ON fluxo_caixa(data_movimentacao);
CREATE INDEX IF NOT EXISTS idx_notas_fiscais_tipo ON notas_fiscais(tipo);
CREATE INDEX IF NOT EXISTS idx_ajustes_estoque_produto ON ajustes_estoque(id_produto);

-- ============================================
-- VIEWS PARA RELATÓRIOS
-- ============================================

-- VIEW: ESTOQUE COM VALOR
CREATE VIEW IF NOT EXISTS v_estoque_valor AS
SELECT 
    p.id_produto,
    p.nome,
    p.categoria,
    p.quantidade,
    p.preco,
    (p.quantidade * p.preco) as valor_total_estoque
FROM produtos p
WHERE p.quantidade > 0;

-- VIEW: CONTAS VENCIDAS
CREATE VIEW IF NOT EXISTS v_contas_vencidas AS
SELECT 
    'pagar' as tipo,
    cp.id_conta,
    cp.descricao,
    cp.valor,
    cp.data_vencimento,
    f.nome_fantasia as contraparte,
    cp.observacao
FROM contas_pagar cp
LEFT JOIN fornecedores f ON f.id_fornecedor = cp.id_fornecedor
WHERE cp.status = 'pendente' AND cp.data_vencimento < datetime('now')
UNION ALL
SELECT 
    'receber' as tipo,
    cr.id_conta,
    cr.descricao,
    cr.valor,
    cr.data_vencimento,
    c.nome as contraparte,
    cr.observacao
FROM contas_receber cr
LEFT JOIN clientes c ON c.id_cliente = cr.id_cliente
WHERE cr.status = 'pendente' AND cr.data_vencimento < datetime('now');

-- VIEW: FLUXO DE CAIXA RESUMO
CREATE VIEW IF NOT EXISTS v_fluxo_resumo AS
SELECT 
    DATE(data_movimentacao) as data,
    SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) as total_entradas,
    SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) as total_saidas,
    SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE -valor END) as saldo_dia
FROM fluxo_caixa
GROUP BY DATE(data_movimentacao);

-- ============================================
-- DADOS INICIAIS (CATEGORIAS PADRÃO)
-- ============================================
INSERT OR IGNORE INTO categorias_financeiras (nome, tipo, descricao) VALUES
('Venda de Produtos', 'receita', 'Receita com vendas de mercadorias'),
('Prestação de Serviços', 'receita', 'Receita com serviços'),
('Outras Receitas', 'receita', 'Outras receitas operacionais'),
('Compra de Mercadorias', 'despesa', 'Compra de produtos para revenda'),
('Aluguel', 'despesa', 'Pagamento de aluguel'),
('Energia Elétrica', 'despesa', 'Contas de energia'),
('Água', 'despesa', 'Contas de água'),
('Telefone/Internet', 'despesa', 'Telecomunicações'),
('Salários e Encargos', 'despesa', 'Folha de pagamento'),
('Impostos e Taxas', 'despesa', 'Tributos diversos'),
('Material de Escritório', 'despesa', 'Materiais administrativos'),
('Marketing', 'despesa', 'Publicidade e propaganda'),
('Manutenção', 'despesa', 'Reparos e manutenções'),
('Frete e Transporte', 'despesa', 'Custos de logística'),
('Outras Despesas', 'despesa', 'Despesas diversas');

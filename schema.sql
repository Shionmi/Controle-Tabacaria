PRAGMA foreign_keys = ON;

-- Usuários para autenticação
CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  email TEXT,
  ativo INTEGER DEFAULT 1,
  criado_em TEXT DEFAULT (datetime('now')),
  ultimo_login TEXT
);

-- Criar usuário padrão (admin/admin123)
INSERT OR IGNORE INTO usuarios (id_usuario, username, password_hash, email, ativo)
VALUES (1, 'admin', 'scrypt:32768:8:1$r4yOlbea8JQFtLf8$18b751a6f7bf9359c33c5f720abb5df7d8cf539441c249657f032dd1e1e50594ab28c29ca6e98522744bc83be085fb9de3e79e91eb40d3e120287679f2b5899a', NULL, 1);

CREATE TABLE IF NOT EXISTS produtos (
  id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  categoria TEXT,
  preco REAL NOT NULL DEFAULT 0.0,
  quantidade INTEGER NOT NULL DEFAULT 0,
  codigo_barras TEXT UNIQUE,
  criado_em TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS movimentacoes (
  id_mov INTEGER PRIMARY KEY AUTOINCREMENT,
  id_produto INTEGER NOT NULL,
  tipo TEXT CHECK(tipo IN ('entrada','saida')) NOT NULL,
  quantidade INTEGER NOT NULL CHECK (quantidade > 0),
  observacao TEXT,
  data_mov TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS revendedores (
  id_revendedor INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  contato TEXT,
  telefone TEXT,
  email TEXT,
  endereco TEXT,
  notas TEXT,
  criado_em TIMESTAMP DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS vendas (
  id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
  id_revendedor INTEGER,
  id_cliente INTEGER,
  cliente_nome TEXT,
  discount_percent REAL,
  total REAL,
  forma_pagamento TEXT,
  data_vencimento TEXT,
  status TEXT DEFAULT 'ativa',
  data_venda TIMESTAMP DEFAULT (datetime('now')),
  observacao TEXT,
  FOREIGN KEY (id_revendedor) REFERENCES revendedores(id_revendedor) ON DELETE SET NULL,
  FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS venda_items (
  id_item INTEGER PRIMARY KEY AUTOINCREMENT,
  id_venda INTEGER NOT NULL,
  id_produto INTEGER NOT NULL,
  quantidade INTEGER NOT NULL,
  preco_unitario REAL NOT NULL,
  FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE CASCADE,
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS clientes (
  id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  cpf TEXT UNIQUE,
  telefone TEXT NOT NULL,
  email TEXT,
  endereco TEXT,
  cidade TEXT,
  estado TEXT,
  observacoes TEXT,
  ultima_compra TEXT,
  criado_em TEXT DEFAULT (datetime('now')),
  atualizado_em TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS logs (
  id_log INTEGER PRIMARY KEY AUTOINCREMENT,
  criado_em TIMESTAMP DEFAULT (datetime('now')),
  acao TEXT NOT NULL,
  tipo TEXT,
  quantidade INTEGER,
  valor REAL,
  produto_id INTEGER,
  detalhe TEXT,
  FOREIGN KEY (produto_id) REFERENCES produtos(id_produto) ON DELETE SET NULL
);

-- Fornecedores
CREATE TABLE IF NOT EXISTS fornecedores (
  id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  cnpj TEXT UNIQUE,
  telefone TEXT,
  email TEXT,
  endereco TEXT,
  cidade TEXT,
  estado TEXT,
  observacoes TEXT,
  ativo INTEGER DEFAULT 1,
  criado_em TEXT DEFAULT (datetime('now')),
  atualizado_em TEXT DEFAULT (datetime('now'))
);

-- Compras
CREATE TABLE IF NOT EXISTS compras (
  id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
  id_fornecedor INTEGER,
  numero_nf TEXT,
  data_compra TEXT DEFAULT (datetime('now')),
  data_entrega TEXT,
  valor_total REAL DEFAULT 0,
  status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente','parcial','concluida','cancelada')),
  observacao TEXT,
  criado_em TEXT DEFAULT (datetime('now')),
  atualizado_em TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE SET NULL
);

-- Itens de compra
CREATE TABLE IF NOT EXISTS compra_items (
  id_item INTEGER PRIMARY KEY AUTOINCREMENT,
  id_compra INTEGER NOT NULL,
  id_produto INTEGER NOT NULL,
  quantidade_pedida INTEGER NOT NULL,
  quantidade_recebida INTEGER DEFAULT 0,
  preco_unitario REAL NOT NULL,
  FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);

-- Contas a Pagar
CREATE TABLE IF NOT EXISTS contas_pagar (
  id_conta INTEGER PRIMARY KEY AUTOINCREMENT,
  descricao TEXT NOT NULL,
  valor REAL NOT NULL,
  data_vencimento TEXT NOT NULL,
  data_pagamento TEXT,
  status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente','pago','cancelado')),
  categoria TEXT,
  id_fornecedor INTEGER,
  id_compra INTEGER,
  observacao TEXT,
  criado_em TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE SET NULL,
  FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE SET NULL
);

-- Contas a Receber
CREATE TABLE IF NOT EXISTS contas_receber (
  id_conta INTEGER PRIMARY KEY AUTOINCREMENT,
  descricao TEXT NOT NULL,
  valor REAL NOT NULL,
  data_vencimento TEXT NOT NULL,
  data_recebimento TEXT,
  status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente','recebido','cancelado')),
  categoria TEXT,
  id_cliente INTEGER,
  id_venda INTEGER,
  observacao TEXT,
  criado_em TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL,
  FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE SET NULL
);

-- Fluxo de Caixa
CREATE TABLE IF NOT EXISTS fluxo_caixa (
  id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL CHECK(tipo IN ('entrada','saida')),
  categoria TEXT,
  id_categoria INTEGER,
  valor REAL NOT NULL,
  descricao TEXT NOT NULL,
  data_movimentacao TEXT DEFAULT (datetime('now')),
  criado_em TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (id_categoria) REFERENCES categorias_financeiras(id_categoria) ON DELETE SET NULL
);

-- Categorias Financeiras
CREATE TABLE IF NOT EXISTS categorias_financeiras (
  id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  tipo TEXT NOT NULL CHECK(tipo IN ('entrada','saida')),
  ativo INTEGER DEFAULT 1,
  criado_em TEXT DEFAULT (datetime('now'))
);

-- Inventários
CREATE TABLE IF NOT EXISTS inventarios (
  id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
  data_inicio TEXT DEFAULT (datetime('now')),
  data_fim TEXT,
  responsavel TEXT NOT NULL,
  observacao TEXT,
  status TEXT DEFAULT 'em_andamento' CHECK(status IN ('em_andamento','concluido','cancelado')),
  criado_em TEXT DEFAULT (datetime('now'))
);

-- Itens de Inventário
CREATE TABLE IF NOT EXISTS inventario_items (
  id_item INTEGER PRIMARY KEY AUTOINCREMENT,
  id_inventario INTEGER NOT NULL,
  id_produto INTEGER NOT NULL,
  quantidade_sistema INTEGER NOT NULL,
  quantidade_contada INTEGER,
  diferenca INTEGER,
  observacao TEXT,
  FOREIGN KEY (id_inventario) REFERENCES inventarios(id_inventario) ON DELETE CASCADE,
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);

-- Ajustes de Estoque
CREATE TABLE IF NOT EXISTS ajustes_estoque (
  id_ajuste INTEGER PRIMARY KEY AUTOINCREMENT,
  id_produto INTEGER NOT NULL,
  tipo_ajuste TEXT NOT NULL,
  quantidade INTEGER NOT NULL,
  motivo TEXT,
  id_inventario INTEGER,
  criado_em TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT,
  FOREIGN KEY (id_inventario) REFERENCES inventarios(id_inventario) ON DELETE SET NULL
);

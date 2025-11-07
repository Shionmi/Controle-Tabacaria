PRAGMA foreign_keys = ON;

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
  data_venda TIMESTAMP DEFAULT (datetime('now')),
  observacao TEXT,
  FOREIGN KEY (id_revendedor) REFERENCES revendedores(id_revendedor) ON DELETE SET NULL
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

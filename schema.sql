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

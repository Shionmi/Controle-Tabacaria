import sqlite3

# Aplicar schema ERP ao banco de dados
DB = 'estoque_tabacaria.db'

print("Aplicando schema ERP expandido...")

with open('schema_erp.sql', 'r', encoding='utf-8') as f:
    schema_sql = f.read()

conn = sqlite3.connect(DB)
cur = conn.cursor()

try:
    cur.executescript(schema_sql)
    conn.commit()
    print("✓ Schema ERP aplicado com sucesso!")
    
    # Verificar tabelas criadas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cur.fetchall()
    print(f"\n✓ Total de tabelas no banco: {len(tables)}")
    print("\nTabelas criadas:")
    for table in tables:
        print(f"  - {table[0]}")
        
except Exception as e:
    print(f"✗ Erro ao aplicar schema: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nFeito!")

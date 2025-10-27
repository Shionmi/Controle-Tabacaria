import sqlite3

conn = sqlite3.connect('estoque_tabacaria.db')
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print('Tables in database:', tables)

# Check schema of each table
for table in tables:
    cur.execute(f"PRAGMA table_info({table})")
    columns = cur.fetchall()
    print(f"\nTable {table} columns:")
    for col in columns:
        print(f"  {col[1]} {col[2]}")

conn.close()
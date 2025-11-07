import sqlite3

DB = 'estoque_tabacaria.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
rows = cur.fetchall()
if not rows:
    print('No tables found')
else:
    for r in rows:
        print(r[0])
conn.close()

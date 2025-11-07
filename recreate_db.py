import os
import sqlite3

print('Backing up current database...')
if os.path.exists('estoque_tabacaria.db'):
    os.rename('estoque_tabacaria.db', 'estoque_tabacaria.db.bak')

print('Creating new database...')
conn = sqlite3.connect('estoque_tabacaria.db')

print('Running schema...')
with open('schema.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

conn.commit()
conn.close()
print('Done! Old database backed up as estoque_tabacaria.db.bak')
import sqlite3

def migrate():
    conn = sqlite3.connect('estoque_tabacaria.db')
    cursor = conn.cursor()
    
    # Check if color column exists
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'color' not in columns:
        print("Adding color column to usuarios table...")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN color TEXT DEFAULT '#3b82f6'")
        conn.commit()
        print("Migration successful.")
    else:
        print("Color column already exists.")
        
    conn.close()

if __name__ == '__main__':
    migrate()

import sqlite3

def migrate():
    conn = sqlite3.connect('estoque_tabacaria.db')
    cursor = conn.cursor()
    
    # Check if avatar column exists
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'avatar' not in columns:
        print("Adding avatar column to usuarios table...")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN avatar TEXT DEFAULT 'default'")
        conn.commit()
        print("Migration successful.")
    else:
        print("Avatar column already exists.")
        
    conn.close()

if __name__ == '__main__':
    migrate()

import sqlite3

# Nome do arquivo do banco de dados
DB_FILE = 'users.db'

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

try:
    # Tenta adicionar a coluna 'ativo' se ela não existir
    cursor.execute("ALTER TABLE users ADD COLUMN ativo INTEGER DEFAULT 1;")
    print("Coluna 'ativo' adicionada com sucesso!")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print("A coluna 'ativo' já existe.")
    else:
        print(f"Erro ao adicionar coluna: {e}")
finally:
    conn.commit()
    conn.close()

# db.py
import sqlite3
from datetime import datetime

import re
DATABASE = "users.db"

def get_connection():
    # Adiciona um timeout para evitar erros de "database is locked" em ambientes com múltiplas threads
    return sqlite3.connect(DATABASE, timeout=30) # Espera até 30 segundos

class User:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def create_user(self, name, email, password):
        try:
            self.cursor.execute('''
                INSERT INTO users (name, email, password, ativo)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password, 1))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            self.conn.close()

    def get_user_by_email(self, email):
        self.cursor.execute('''
            SELECT * FROM users WHERE email = ?
        ''', (email,))
        return self.cursor.fetchone()

    def login_user(self, email, password):
        """Autentica um usuário 'comprador'."""
        try:
            self.cursor.execute('''
                SELECT id, name, email FROM users WHERE email = ? AND password = ? AND ativo = 1
            ''', (email, password))
            user = self.cursor.fetchone()
            
            if user:
                # Retorna um dicionário com os dados do usuário se o login for bem-sucedido
                return {"id": user[0], "name": user[1], "email": user[2], "type": "comprador"}
            return None
        except Exception as e:
            print(f"Erro ao tentar fazer login de usuário: {e}")
            return None
        finally:
            self.conn.close()


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            ativo INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Criar a tabela para cadastrar vendedor CPF ou CNPJ
def create_table_vendedor():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendedor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_pessoa TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            cnpj TEXT UNIQUE,
            cpf TEXT UNIQUE,
            telefone TEXT NOT NULL,
            rua TEXT NOT NULL,
            numero TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            cep TEXT NOT NULL,
            password TEXT NOT NULL,
            ativo INTEGER NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (
                (tipo_pessoa = 'Pessoa Física' AND cpf IS NOT NULL AND cnpj IS NULL) OR
                (tipo_pessoa = 'Pessoa Jurídica' AND cnpj IS NOT NULL AND cpf IS NULL)
            )
        )
        ''')

    conn.commit()
    conn.close()

def _generate_slug(text):
    """Gera um slug a partir de um texto: minúsculas, sem acentos, espaços por hífens."""
    # Normaliza para minúsculas e remove acentos
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    # Remove caracteres não alfanuméricos (exceto espaços e hífens)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Substitui espaços e múltiplos hífens por um único hífen
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text

# Criar função para cadastro de vendedor
def create_vendedor(tipo_pessoa, name, email, cnpj, cpf, telefone, rua, numero, bairro, cidade, estado, cep, password):
    conn = get_connection()
    cursor = conn.cursor()
    slug = _generate_slug(name)
    
    try:
        cursor.execute('''
            INSERT INTO vendedor (
                tipo_pessoa, name, email, slug, cnpj, cpf, telefone, rua, numero,
                bairro, cidade, estado, cep, password, ativo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tipo_pessoa, name, email, slug, cnpj, cpf, telefone, rua, numero,
            bairro, cidade, estado, cep, password, 1  # Define o vendedor como ativo por padrão
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        # O erro pode ocorrer se o email, CPF ou CNPJ já existirem.
        print(f"Erro de integridade ao cadastrar vendedor: {e}")
        if 'slug' in str(e):
            # Se o slug já existe, tenta adicionar um sufixo numérico
            count = 1
            while True:
                new_slug = f"{slug}-{count}"
                try:
                    cursor.execute('INSERT INTO vendedor (tipo_pessoa, name, email, slug, cnpj, cpf, telefone, rua, numero, bairro, cidade, estado, cep, password, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                                   (tipo_pessoa, name, email, new_slug, cnpj, cpf, telefone, rua, numero, bairro, cidade, estado, cep, password, 1))
                    conn.commit()
                    return True
                except sqlite3.IntegrityError:
                    count += 1
                if count > 100: # Limite para evitar loop infinito
                     return False

        return False
    finally:
        conn.close()

# Função para autenticar um vendedor
def login_vendedor(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, name, email FROM vendedor WHERE email = ? AND password = ? AND ativo = 1
        ''', (email, password))
        vendedor = cursor.fetchone()
        
        if vendedor:
            # Retorna um dicionário com os dados do vendedor se o login for bem-sucedido
            return {"id": vendedor[0], "name": vendedor[1], "email": vendedor[2], "type": "vendedor"}
        return None

    except Exception as e:
        print(f"Erro ao tentar fazer login: {e}")
        return False
    finally:
        conn.close()

# Função para buscar todos os vendedores (lojas)
def get_all_vendedores():
    """Busca todos os vendedores ativos no banco de dados."""
    conn = get_connection()
    # Usar row_factory para retornar dicionários em vez de tuplas
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, name, slug, cidade, estado FROM vendedor WHERE ativo = 1 ORDER BY name
        ''')
        vendedores = cursor.fetchall()
        # Converter os objetos Row para dicionários para facilitar o uso
        return [dict(row) for row in vendedores]
    except Exception as e:
        print(f"Erro ao buscar vendedores: {e}")
        return []
    finally:
        conn.close()

# Função para buscar um vendedor específico pelo ID
def get_vendedor_by_id(vendedor_id):
    """Busca os dados de um vendedor específico pelo seu ID."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, name, slug, cidade, estado FROM vendedor WHERE id = ?', (vendedor_id,))
        vendedor = cursor.fetchone()
        return dict(vendedor) if vendedor else None
    except Exception as e:
        print(f"Erro ao buscar vendedor por ID: {e}")
        return None
    finally:
        conn.close()

# Função para buscar um vendedor específico pelo SLUG
def get_vendedor_by_slug(slug):
    """Busca os dados de um vendedor específico pelo seu slug."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, name, slug, cidade, estado FROM vendedor WHERE slug = ?', (slug,))
        vendedor = cursor.fetchone()
        return dict(vendedor) if vendedor else None
    except Exception as e:
        print(f"Erro ao buscar vendedor por slug: {e}")
        return None
    finally:
        conn.close()

# Função para buscar produtos de um vendedor específico
def get_produtos_by_vendedor(vendedor_id):
    """Busca todos os produtos ativos de um vendedor específico."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT p.id, p.nome, p.descricao, p.preco, p.quantidade, p.img, c.nome as categoria_nome
            FROM produto p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.vendedor_id = ? AND p.ativo = 1
            ORDER BY p.nome
        ''', (vendedor_id,))
        produtos = cursor.fetchall()
        return [dict(row) for row in produtos]
    except Exception as e:
        print(f"Erro ao buscar produtos por vendedor: {e}")
        return []
    finally:
        conn.close()

# Criar a tabela produto, ela deve conter o id do vendedor que cadastrou o produto
"""def create_table_produto():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            ativo INTEGER NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendedor_id) REFERENCES vendedor(id)
            img BLOB,
        )
    ''')

    conn.commit()
    conn.close()

# Função para insrir novos campos na tabela produto
def alterar_table_produto():
    pass"""

# Criar a tabela produto (com campo de imagem)
def create_table_produto():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            categoria_id INTEGER,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL, 
            quantidade INTEGER NOT NULL,
            ativo INTEGER NOT NULL,
            img BLOB,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendedor_id) REFERENCES vendedor(id)
        )
    ''')

    conn.commit()
    conn.close()

# Criar a tabela de categorias
def create_table_categorias():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (vendedor_id) REFERENCES vendedor(id),
            UNIQUE(vendedor_id, nome)
        )
    ''')
    conn.commit()
    conn.close()

# Função para criar uma nova categoria
def create_categoria(vendedor_id, nome):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categorias (vendedor_id, nome) VALUES (?, ?)', (vendedor_id, nome,))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Ocorre se a categoria já existe (UNIQUE)
        return False
    finally:
        conn.close()

# Função para buscar todas as categorias
def get_categorias_by_vendedor(vendedor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM categorias WHERE vendedor_id = ? ORDER BY nome', (vendedor_id,))
    return cursor.fetchall()

# Função para atualizar uma categoria
def update_categoria(categoria_id, vendedor_id, novo_nome):
    """Atualiza o nome de uma categoria, verificando a permissão do vendedor."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # A verificação de vendedor_id previne que um vendedor altere a categoria de outro
        cursor.execute('UPDATE categorias SET nome = ? WHERE id = ? AND vendedor_id = ?', (novo_nome, categoria_id, vendedor_id))
        conn.commit()
        # Retorna True se alguma linha foi afetada (ou seja, a atualização foi bem-sucedida)
        return cursor.rowcount > 0
    except sqlite3.IntegrityError: # Ocorre se o novo nome já existe para este vendedor
        return False
    finally:
        conn.close()

# Função para deletar uma categoria
def delete_categoria(categoria_id, vendedor_id):
    """Deleta uma categoria, verificando a permissão do vendedor."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Inicia uma transação para garantir a atomicidade das operações
        cursor.execute("BEGIN TRANSACTION")
        # 1. Desvincula os produtos que usam esta categoria (define categoria_id como NULL)
        cursor.execute('UPDATE produto SET categoria_id = NULL WHERE categoria_id = ? AND vendedor_id = ?', (categoria_id, vendedor_id))
        # 2. Deleta a categoria
        cursor.execute('DELETE FROM categorias WHERE id = ? AND vendedor_id = ?', (categoria_id, vendedor_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao deletar categoria: {e}")
        conn.rollback() # Desfaz a transação em caso de erro
        return False
    finally:
        conn.close()

# Função para cadastrar um novo produto
def create_produto(vendedor_id, nome, descricao, categoria_id, preco, quantidade, img_path=None):
    """
    Insere um novo produto no banco de dados associado a um vendedor.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    img_data = None
    if img_path:
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()
        except Exception as e:
            print(f"Erro ao ler o arquivo de imagem: {e}")
            # Decide se quer continuar sem imagem ou retornar erro

    try:
        cursor.execute('''
            INSERT INTO produto (vendedor_id, nome, descricao, categoria_id, preco, quantidade, ativo, img)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (vendedor_id, nome, descricao, categoria_id, preco, quantidade, 1, img_data))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        return False
    finally:
        conn.close()
# Função para atualizar um produto existente
def update_produto(produto_id, nome=None, descricao=None, categoria_id=None, preco=None, quantidade=None, img_path=None, remover_img=False):
    """
    Atualiza os detalhes de um produto existente.
    Apenas os campos fornecidos serão atualizados.
    """
    conn = get_connection()
    cursor = conn.cursor()

    fields_to_update = []
    values = []

    if nome is not None:
        fields_to_update.append("nome = ?")
        values.append(nome)
    if descricao is not None:
        fields_to_update.append("descricao = ?")
        values.append(descricao)
    if categoria_id is not None:
        fields_to_update.append("categoria_id = ?")
        values.append(categoria_id)
    if preco is not None:
        fields_to_update.append("preco = ?")
        values.append(preco)
    if quantidade is not None:
        fields_to_update.append("quantidade = ?")
        values.append(quantidade)
    
    if img_path:
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()
            fields_to_update.append("img = ?")
            values.append(img_data)
        except Exception as e:
            print(f"Erro ao ler o arquivo de imagem para atualização: {e}")
    elif remover_img:
        fields_to_update.append("img = ?")
        values.append(None)

    if not fields_to_update:
        return True # Nada a atualizar

    sql = f"UPDATE produto SET {', '.join(fields_to_update)} WHERE id = ?"
    values.append(produto_id)

    try:
        cursor.execute(sql, tuple(values))
        conn.commit()
        return True
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print(f"Database is locked during update_produto for produto_id {produto_id}. Retrying...")
            # Optionally, implement retry logic here
            return False
        else:
            print(f"Erro ao atualizar produto: {e}")
            return False
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        return False
    finally:
        conn.close()

def get_produto_by_id(produto_id):
    """Busca um produto específico pelo seu ID."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM produto WHERE id = ?', (produto_id,))
        produto = cursor.fetchone()
        return dict(produto) if produto else None
    except Exception as e:
        print(f"Erro ao buscar produto por ID: {e}")
        return None
    finally:
        conn.close()

# Função genérica para inserir novos campos na tabela produto
def alterar_table_produto(coluna_nome, tipo_coluna):
    """
    Adiciona uma nova coluna à tabela produto caso ela ainda não exista.
    
    Parâmetros:
        coluna_nome (str): nome da nova coluna
        tipo_coluna (str): tipo de dado SQL (ex: TEXT, INTEGER, REAL, BLOB)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se a coluna já existe
    cursor.execute("PRAGMA table_info(produto)")
    colunas = [col[1] for col in cursor.fetchall()]

    if coluna_nome not in colunas:
        cursor.execute(f"ALTER TABLE produto ADD COLUMN {coluna_nome} {tipo_coluna}")
        print(f"✅ Coluna '{coluna_nome}' adicionada com sucesso.")
    else:
        print(f"⚠️ A coluna '{coluna_nome}' já existe na tabela produto.")

    conn.commit()
    conn.close()

def alterar_table_categorias(coluna_nome, tipo_coluna):
    """
    Adiciona uma nova coluna à tabela categorias caso ela ainda não exista.
    
    Parâmetros:
        coluna_nome (str): nome da nova coluna
        tipo_coluna (str): tipo de dado SQL (ex: TEXT, INTEGER, REAL, BLOB)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se a coluna já existe
    cursor.execute("PRAGMA table_info(categorias)")
    colunas = [col[1] for col in cursor.fetchall()]

    if coluna_nome not in colunas:
        cursor.execute(f"ALTER TABLE categorias ADD COLUMN {coluna_nome} {tipo_coluna}")
        print(f"✅ Coluna '{coluna_nome}' adicionada com sucesso à tabela 'categorias'.")

    conn.commit()
    conn.close()

def alterar_table_vendedor(coluna_nome, tipo_coluna, unique=False):
    """
    Adiciona uma nova coluna à tabela vendedor caso ela ainda não exista.
    Lida com a adição de colunas UNIQUE em tabelas existentes.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(vendedor)")
        colunas = [col[1] for col in cursor.fetchall()]

        if coluna_nome not in colunas:
            # 1. Adiciona a coluna sem a restrição UNIQUE
            cursor.execute(f"ALTER TABLE vendedor ADD COLUMN {coluna_nome} {tipo_coluna}")
            print(f"✅ Coluna '{coluna_nome}' adicionada com sucesso à tabela 'vendedor'.")

            # 2. Se a coluna deve ser única (como o slug), popula os dados existentes
            if unique and coluna_nome == 'slug':
                print("Populando slugs para vendedores existentes...")
                cursor.execute("SELECT id, name FROM vendedor")
                vendedores = cursor.fetchall()
                
                slugs_existentes = set()
                for vendedor_id, nome in vendedores:
                    slug_base = _generate_slug(nome)
                    slug_final = slug_base
                    count = 1
                    while slug_final in slugs_existentes:
                        slug_final = f"{slug_base}-{count}"
                        count += 1
                    
                    slugs_existentes.add(slug_final)
                    cursor.execute("UPDATE vendedor SET slug = ? WHERE id = ?", (slug_final, vendedor_id))
                print("✅ Slugs populados.")

        # 3. Cria o índice UNIQUE se a coluna deve ser única
        if unique:
            cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_vendedor_{coluna_nome} ON vendedor({coluna_nome})")
            print(f"✅ Índice UNIQUE criado para a coluna '{coluna_nome}'.")

    except Exception as e:
        print(f"❌ Erro ao migrar a tabela 'vendedor': {e}")
    finally:
        conn.commit()
        conn.close()

# Tabela para salvar os pedidos dos compradores
def create_table_pedidos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comprador_id INTEGER NOT NULL,
            vendedor_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL,
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rua TEXT,
            numero TEXT,
            bairro TEXT,
            cidade TEXT,
            estado TEXT,
            cep TEXT,
            FOREIGN KEY (comprador_id) REFERENCES users(id),
            FOREIGN KEY (vendedor_id) REFERENCES vendedor(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (produto_id) REFERENCES produto(id)
        )
    ''')

    conn.commit()
    conn.close()

def table_taxa_entrega():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS taxa_entrega (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            cidade TEXT NOT NULL,
            bairro TEXT NOT NULL,
            estado TEXT NOT NULL,
            valor REAL NOT NULL,
            FOREIGN KEY (vendedor_id) REFERENCES vendedor(id)
        )
    ''')

    conn.commit()
    conn.close()
    
def cadastrar_taxa_entrega(vendedor_id, cidade, bairro, estado, valor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO taxa_entrega (vendedor_id, cidade, bairro, estado, valor) VALUES (?, ?, ?, ?, ?)", (vendedor_id, cidade, bairro, estado, valor))
    conn.commit()
    conn.close()

def get_taxas_by_vendedor(vendedor_id):
    """Busca todas as taxas de entrega de um vendedor específico."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, cidade, bairro, estado, valor FROM taxa_entrega WHERE vendedor_id = ? ORDER BY cidade, bairro', (vendedor_id,))
        taxas = cursor.fetchall()
        return [dict(row) for row in taxas]
    except Exception as e:
        print(f"Erro ao buscar taxas de entrega: {e}")
        return []
    finally:
        conn.close()

def delete_taxa_entrega(taxa_id, vendedor_id):
    """Deleta uma taxa de entrega, verificando a permissão do vendedor."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM taxa_entrega WHERE id = ? AND vendedor_id = ?', (taxa_id, vendedor_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
    
def create_pedido(comprador_id, vendedor_id, total, endereco, itens):
    """
    Cria um novo pedido no banco de dados, incluindo os itens e atualizando o estoque.
    'endereco' é um dicionário com rua, numero, bairro, cidade, estado, cep.
    'itens' é uma lista de dicionários, cada um com 'id', 'quantity', 'price'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Inicia a transação
        cursor.execute("BEGIN TRANSACTION")

        # 1. Inserir na tabela 'pedidos'
        cursor.execute('''
            INSERT INTO pedidos (comprador_id, vendedor_id, total, status, rua, numero, bairro, cidade, estado, cep)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (comprador_id, vendedor_id, total, 'Pendente', endereco['rua'], endereco['numero'], endereco['bairro'], endereco['cidade'], endereco['estado'], endereco['cep']))
        
        pedido_id = cursor.lastrowid

        # 2. Inserir na tabela 'itens_pedido' e atualizar o estoque
        for item in itens:
            produto_id = item['id']
            quantidade_comprada = item['quantity']
            
            # Inserir item no pedido
            cursor.execute('''
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
            ''', (pedido_id, produto_id, quantidade_comprada, item['price']))

            # Atualizar estoque do produto
            cursor.execute('UPDATE produto SET quantidade = quantidade - ? WHERE id = ?', (quantidade_comprada, produto_id))

        # Confirma a transação
        conn.commit()
        return pedido_id
    except Exception as e:
        print(f"Erro ao criar pedido: {e}")
        conn.rollback() # Desfaz todas as operações em caso de erro
        return None
    finally:
        conn.close()

def get_pedidos_by_vendedor(vendedor_id):
    """Busca todos os pedidos de um vendedor, incluindo o nome do comprador."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT p.*, u.name as comprador_nome FROM pedidos p
            JOIN users u ON p.comprador_id = u.id
            WHERE p.vendedor_id = ? ORDER BY p.data_pedido DESC
        ''', (vendedor_id,))
        pedidos = cursor.fetchall()
        return [dict(row) for row in pedidos]
    except Exception as e:
        print(f"Erro ao buscar pedidos do vendedor: {e}")
        return []
    finally:
        conn.close()

def init_db():
    """Garante que todas as tabelas sejam criadas."""
    create_tables()
    create_table_vendedor()
    create_table_produto()
    create_table_categorias()
    create_table_pedidos()
    table_taxa_entrega()
    # A função alterar_table_produto já verifica se a coluna existe, então é seguro chamar.
    alterar_table_vendedor('slug', 'TEXT', unique=True) # Garante a existência da coluna de slug
    alterar_table_categorias('vendedor_id', 'INTEGER') # Garante a existência da coluna de vendedor na tabela de categorias
    alterar_table_produto('categoria_id', 'INTEGER') # Garante a existência da coluna de categoria
    alterar_table_produto('img', 'BLOB') # Garante a existência da coluna de imagem
    

# Executa quando rodar python db.py
if __name__ == "__main__":
    init_db()
    print("Tabelas criadas com sucesso.")

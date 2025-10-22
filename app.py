import sqlite3

# Conectar (ou criar) o banco de dados
conn = sqlite3.connect("estoque_tabacaria.db")
cursor = conn.cursor()

# ===============================
# Funções principais do sistema
# ===============================

def adicionar_produto(nome, categoria, preco, quantidade):
    cursor.execute("""
        INSERT INTO produtos (nome, categoria, preco, quantidade)
        VALUES (?, ?, ?, ?)
    """, (nome, categoria, preco, quantidade))
    conn.commit()
    print(f"\n✅ Produto '{nome}' adicionado com sucesso!")

def listar_produtos():
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    print("\n📦 --- ESTOQUE ATUAL ---")
    for p in produtos:
        print(f"ID: {p[0]} | Nome: {p[1]} | Categoria: {p[2]} | Preço: R${p[3]:.2f} | Quantidade: {p[4]}")

def atualizar_estoque(id_produto, nova_quantidade):
    cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, id_produto))
    conn.commit()
    print(f"\n🔁 Estoque do produto ID {id_produto} atualizado para {nova_quantidade} unidades.")

def remover_produto(id_produto):
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conn.commit()
    print(f"\n🗑️ Produto ID {id_produto} removido com sucesso!")

# ===============================
# Menu interativo
# ===============================

while True:
    print("\n===============================")
    print("   SISTEMA DE ESTOQUE TABACARIA")
    print("===============================")
    print("1 - Adicionar Produto")
    print("2 - Listar Produtos")
    print("3 - Atualizar Estoque")
    print("4 - Remover Produto")
    print("0 - Sair")
    print("===============================")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        nome = input("Nome do produto: ")
        categoria = input("Categoria: ")
        preco = float(input("Preço: "))
        quantidade = int(input("Quantidade: "))
        adicionar_produto(nome, categoria, preco, quantidade)

    elif opcao == "2":
        listar_produtos()

    elif opcao == "3":
        id_produto = int(input("ID do produto: "))
        nova_qtd = int(input("Nova quantidade: "))
        atualizar_estoque(id_produto, nova_qtd)

    elif opcao == "4":
        id_produto = int(input("ID do produto a remover: "))
        remover_produto(id_produto)

    elif opcao == "0":
        print("\n👋 Encerrando o sistema...")
        break

    else:
        print("\n⚠️ Opção inválida, tente novamente.")

conn.close()

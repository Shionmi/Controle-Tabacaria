# 🏪 Sistema JM Tabacaria

Sistema completo e profissional de gestão para tabacaria com acesso mobile.

## 📁 Estrutura do Projeto

```
Tabacaria/
│
├── Iniciar_Sistema.bat          # ⭐ ARQUIVO PRINCIPAL - Execute este!
├── LEIA-ME.md                   # Instruções de uso
├── .gitignore                   # Proteção de arquivos sensíveis
│
├── app.py                       # Aplicação Flask principal
├── schema.sql                   # Estrutura do banco de dados
├── requirements.txt             # Dependências Python
│
├── scripts/
│   ├── setup_client.ps1        # Script de instalação automática
│   └── start_sistema.ps1       # Script de inicialização
│
├── Templates/                   # Páginas HTML do sistema
│   ├── base.html               # Template base
│   ├── index.html              # Dashboard
│   ├── estoque.html            # Gerenciamento de estoque
│   ├── venda.html              # Registro de vendas
│   ├── clientes.html           # Cadastro de clientes
│   ├── fornecedores.html       # Gestão de fornecedores
│   ├── compras.html            # Pedidos de compra
│   ├── contas_pagar.html       # Contas a pagar
│   ├── contas_receber.html     # Contas a receber
│   ├── fluxo_caixa.html        # Fluxo de caixa
│   ├── inventario.html         # Controle de inventário
│   ├── movimentacoes.html      # Histórico de movimentações
│   ├── relatorios.html         # Relatórios gerenciais
│   ├── print_label.html        # Impressão de etiquetas
│   └── error.html              # Página de erro
│
└── static/                      # Arquivos estáticos
    ├── style.css               # Estilos do sistema
    ├── Images/
    │   └── Logo_tabacaria.png  # Logo da empresa
    ├── barcodes/               # Códigos de barras gerados
    └── js/
        ├── common.js           # Scripts compartilhados
        └── sistema_products.js # Gestão de produtos
```

## 🚀 Instalação e Uso

### Para o Desenvolvedor (GitHub)

```bash
# Adicionar mudanças
git add .

# Commit
git commit -m "Sistema atualizado"

# Enviar para GitHub
git push
```

### Para o Cliente (Instalação)

1. Baixe o projeto do GitHub
2. **Clique com botão direito** em `Iniciar_Sistema.bat`
3. Selecione **"Executar como administrador"**
4. Aguarde instalação automática
5. Sistema abre automaticamente

### Uso Diário

- Simplesmente dê **dois cliques** em `Iniciar_Sistema.bat`
- O sistema detecta automaticamente se já está instalado

## 🔐 Segurança (.gitignore)

Arquivos protegidos (NÃO vão para GitHub):
- `.venv/` - Ambiente virtual Python
- `*.db` - Banco de dados (dados do cliente)
- `.ngrok_token` - Token de acesso remoto
- `__pycache__/` - Cache Python
- `static/barcodes/*.png` - Códigos de barras gerados

## 📱 Acesso Mobile

O sistema oferece duas formas de acesso mobile:

1. **Acesso Público (ngrok)** - Funciona de qualquer lugar
2. **Acesso Local (Wi-Fi)** - Mesmo Wi-Fi do computador

## 🛠️ Tecnologias

- **Backend**: Python Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Acesso Remoto**: ngrok (túnel público)
- **Códigos de Barras**: python-barcode
- **PDF**: ReportLab

---

**Sistema desenvolvido para JM Tabacaria**

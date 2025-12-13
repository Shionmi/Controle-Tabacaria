# 🏪 JM Tabacaria - Sistema de Gestão

Sistema completo de controle de estoque, vendas e gestão para tabacaria.

## 📋 Requisitos

- **Windows 10 ou 11**
- **Python 3.10 ou superior** ([Baixar aqui](https://www.python.org/downloads/))
- **Conexão com internet** (apenas para instalação inicial)

## 🚀 Como Instalar e Usar

### Primeira Vez (Instalação)

1. **Clique com o botão DIREITO** no arquivo `Iniciar_Sistema.bat`
2. Selecione **"Executar como administrador"**
3. Clique em **SIM** quando o Windows pedir permissão
4. Aguarde a instalação automática (pode levar alguns minutos)
5. O sistema vai abrir automaticamente

### Próximas Vezes (Uso Normal)

1. Dê **dois cliques** no arquivo `Iniciar_Sistema.bat`
2. Pronto! O sistema abre automaticamente

## 📱 Como Acessar pelo Celular

### Opção 1: Acesso Público (Recomendado)
- Na primeira vez, o sistema vai pedir um **código de acesso** (authtoken)
- Siga as instruções na tela para criar conta gratuita no ngrok
- Depois, você receberá um link tipo: `https://abc123.ngrok-free.app`
- **Acesse esse link de qualquer celular**, em qualquer lugar!

### Opção 2: Acesso Local (Mesma Rede Wi-Fi)
- Conecte o celular no mesmo Wi-Fi do computador
- Na tela inicial do sistema, copie o endereço que aparece
- Digite esse endereço no navegador do celular

## 📂 Estrutura do Projeto

```
JM_Tabacaria/
├── Iniciar_Sistema.bat      # Arquivo principal - execute este!
├── app.py                    # Aplicação Flask
├── schema.sql                # Estrutura do banco de dados
├── requirements.txt          # Dependências Python
├── Templates/                # Páginas HTML
├── static/                   # CSS, imagens, códigos de barras
├── scripts/                  # Scripts de instalação
└── README.md                 # Este arquivo
```

## 🛠️ Funcionalidades

- ✅ Controle de Estoque
- ✅ Registro de Vendas
- ✅ Gestão de Clientes
- ✅ Fornecedores e Compras
- ✅ Contas a Pagar e Receber
- ✅ Fluxo de Caixa
- ✅ Relatórios
- ✅ Impressão de Etiquetas com Código de Barras
- ✅ Acesso Mobile (Celular/Tablet)

## 🔒 Segurança

- Banco de dados local (SQLite)
- Acesso público protegido via ngrok (HTTPS)
- Token de acesso salvo localmente

## 📞 Suporte

Em caso de problemas:
1. Certifique-se de ter **Python instalado**
2. Execute como **Administrador** na primeira vez
3. Mantenha a janela azul (PowerShell) **aberta** enquanto usa o sistema

## 📝 Notas Importantes

- **NÃO feche** a janela azul (PowerShell) enquanto estiver usando o sistema
- O banco de dados é salvo em `estoque_tabacaria.db`
- Faça backup regular do arquivo `.db`
- Para fechar o sistema, feche a janela azul ou pressione `Ctrl+C`

---

**Desenvolvido para JM Tabacaria** | Sistema Profissional de Gestão

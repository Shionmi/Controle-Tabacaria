# Sistema ERP - Tabacaria Premium

## 📋 Visão Geral

Sistema completo de gestão empresarial (ERP) para tabacaria, incluindo controle de estoque, vendas, compras, financeiro e inventário.

## 🎨 Interface

**Tema:** Dark Blue / Red / Brown
- Background: Azul escuro (Slate 900/800)
- Acento Principal: Vermelho (#ef4444)
- Detalhes: Marrom (#78350f)

## 🚀 Módulos Implementados

### 1. **Dashboard Financeiro** (`/dashboard_financeiro`)
Indicadores em tempo real:
- ✅ Contas a Pagar pendentes
- ✅ Contas a Receber pendentes
- ✅ Contas vencidas (a pagar e receber)
- ✅ Valor total em estoque
- ✅ Produtos com estoque baixo
- ✅ Fluxo de caixa do mês (entradas, saídas, saldo)

**API:** `GET /api/dashboard/kpis`

---

### 2. **Fornecedores** (`/fornecedores`)
Gestão completa de fornecedores com CRUD funcional:
- ✅ Cadastro com dados completos (CNPJ, IE, endereço, contato)
- ✅ Listagem e busca
- ✅ Edição e exclusão
- ✅ Status (Ativo/Inativo)

**APIs:**
- `GET /api/fornecedores` - Listar (suporta `?q=busca`, `?ativo=1`)
- `POST /api/fornecedores` - Criar
- `GET /api/fornecedores/<id>` - Obter detalhes
- `PUT /api/fornecedores/<id>` - Atualizar
- `DELETE /api/fornecedores/<id>` - Deletar

---

### 3. **Compras** (`/compras`)
Sistema de pedidos de compra a fornecedores:
- ✅ Registro de compras com múltiplos itens
- ✅ Controle de status (pendente, parcial, concluída, cancelada)
- ✅ Recebimento de mercadorias e atualização automática de estoque
- ✅ Integração com movimentações

**APIs:**
- `GET /api/compras` - Listar (suporta `?status=`, `?fornecedor_id=`)
- `POST /api/compras` - Criar pedido
- `POST /api/compras/<id>/receber` - Receber mercadorias

**Fluxo de Recebimento:**
1. Criar compra com itens
2. Chamar `/receber` com itens e quantidades
3. Sistema atualiza estoque automaticamente
4. Registra movimentação de entrada

---

### 4. **Contas a Pagar** (`/contas_pagar`)
Gestão de compromissos financeiros:
- ✅ Registro de contas com vencimento
- ✅ Vínculo com fornecedores e compras
- ✅ Status (pendente, pago, vencido, cancelado)
- ✅ Baixa de contas com registro automático no fluxo de caixa
- ✅ Alertas de contas vencidas

**APIs:**
- `GET /api/contas_pagar` - Listar (suporta `?status=`, `?vencidas=1`)
- `POST /api/contas_pagar` - Criar conta
- `POST /api/contas_pagar/<id>/pagar` - Baixar conta

---

### 5. **Contas a Receber** (`/contas_receber`)
Controle de recebíveis:
- ✅ Registro de contas a receber
- ✅ Vínculo com clientes e vendas
- ✅ Status (pendente, recebido, vencido, cancelado)
- ✅ Baixa de contas com registro automático no fluxo de caixa
- ✅ Alertas de inadimplência

**APIs:**
- `GET /api/contas_receber` - Listar (suporta `?status=`, `?vencidas=1`)
- `POST /api/contas_receber` - Criar conta
- `POST /api/contas_receber/<id>/receber` - Baixar conta

---

### 6. **Fluxo de Caixa** (`/fluxo_caixa`)
Controle de movimentações financeiras:
- ✅ Registro automático de entradas e saídas
- ✅ Integração com contas a pagar/receber
- ✅ Categorização financeira
- ✅ Filtros por período e tipo
- ✅ Resumo com totais

**APIs:**
- `GET /api/fluxo_caixa` - Listar (suporta `?data_inicio=`, `?data_fim=`, `?tipo=`)
- `GET /api/fluxo_caixa/resumo` - Totais por período

---

### 7. **Inventário** (`/inventario`)
Contagem física e ajustes:
- ✅ Criação de inventários
- ✅ Listagem de itens com quantidade sistema vs contada
- ✅ Registro de diferenças
- ✅ Finalização com ajuste automático de estoque
- ✅ Rastreamento de ajustes

**APIs:**
- `GET /api/inventarios` - Listar inventários
- `POST /api/inventarios` - Criar novo
- `GET /api/inventarios/<id>/items` - Itens do inventário
- `PUT /api/inventarios/<id>/items/<id_item>` - Atualizar contagem
- `POST /api/inventarios/<id>/finalizar` - Finalizar e ajustar estoque

---

### 8. **Relatórios** (`/relatorios`)
Análises gerenciais:

#### **Curva ABC**
Classificação de produtos por valor de estoque:
- **Classe A:** 80% do valor (produtos críticos)
- **Classe B:** 15% do valor (produtos importantes)
- **Classe C:** 5% do valor (produtos de baixo impacto)

**API:** `GET /api/relatorios/curva_abc`

#### **Lucratividade**
Análise de vendas por produto:
- Total de vendas
- Quantidade vendida
- Preço médio de venda
- Receita total

**API:** `GET /api/relatorios/lucratividade`

#### **Estoque Valorizado**
Valor total em estoque por categoria:
- Total de produtos
- Quantidade total
- Preço médio
- Valor total

**API:** `GET /api/relatorios/estoque_valorizado`

---

## 📊 Estrutura do Banco de Dados

### Novas Tabelas Criadas:

1. **fornecedores** - Cadastro de fornecedores
2. **compras** - Pedidos de compra
3. **compra_items** - Itens dos pedidos
4. **categorias_financeiras** - Categorias de receitas/despesas
5. **contas_pagar** - Contas a pagar
6. **contas_receber** - Contas a receber
7. **fluxo_caixa** - Movimentações financeiras
8. **inventarios** - Inventários físicos
9. **inventario_items** - Itens dos inventários
10. **ajustes_estoque** - Ajustes de estoque
11. **notas_fiscais** - Notas fiscais (estrutura pronta)

### Views:
- **v_estoque_valor** - Estoque com valores
- **v_contas_vencidas** - Contas vencidas consolidadas
- **v_fluxo_resumo** - Resumo de fluxo de caixa por dia

---

## 🔧 Funcionalidades Técnicas

### Integração Automática:
- ✅ Recebimento de compras → Atualiza estoque + Movimentações
- ✅ Pagamento de contas → Registra no fluxo de caixa
- ✅ Recebimento de contas → Registra no fluxo de caixa
- ✅ Finalização de inventário → Ajusta estoque automaticamente

### Validações:
- ✅ Integridade referencial (Foreign Keys)
- ✅ Constraints de status
- ✅ Validação de quantidades

### Logs e Auditoria:
- ✅ Todas operações importantes são logadas
- ✅ Tabela `logs` com histórico completo

---

## 🎯 Status dos Módulos

| Módulo | Backend | Frontend | Status |
|--------|---------|----------|--------|
| Dashboard Financeiro | ✅ | ✅ | **Completo** |
| Fornecedores | ✅ | ✅ | **Completo** |
| Compras | ✅ | 🔶 | Backend pronto |
| Contas a Pagar | ✅ | 🔶 | Backend pronto |
| Contas a Receber | ✅ | 🔶 | Backend pronto |
| Fluxo de Caixa | ✅ | 🔶 | Backend pronto |
| Inventário | ✅ | 🔶 | Backend pronto |
| Relatórios | ✅ | ✅ | **Completo** |

**Legenda:**
- ✅ Completo e funcional
- 🔶 API pronta, interface simplificada
- ❌ Não implementado

---

## 📝 Categorias Financeiras Padrão

### Receitas:
- Venda de Produtos
- Prestação de Serviços
- Outras Receitas

### Despesas:
- Compra de Mercadorias
- Aluguel
- Energia Elétrica
- Água
- Telefone/Internet
- Salários e Encargos
- Impostos e Taxas
- Material de Escritório
- Marketing
- Manutenção
- Frete e Transporte
- Outras Despesas

---

## 🚀 Próximos Passos (Expansão)

### Frontend Completo:
1. Interface de compras com seleção de produtos
2. Interface de contas a pagar/receber com calendário
3. Gráficos no dashboard financeiro (Chart.js)
4. Interface de inventário com scanner de código de barras

### Funcionalidades Adicionais:
1. **Notas Fiscais:** Upload e vinculação de XMLs
2. **Conciliação Bancária:** Integração com extratos
3. **Projeção de Fluxo de Caixa:** Previsões baseadas em contas
4. **Alertas:** Notificações de vencimentos
5. **Multi-usuário:** Sistema de permissões
6. **Backup Automático:** Rotina de backup do banco

---

## 📞 Uso do Sistema

### Iniciar Sistema:
```bash
cd Tabacaria
python app.py
```

Acesse: `http://127.0.0.1:5000`

### Menu de Navegação:
- **Início:** Dashboard geral com acesso rápido
- **Estoque:** Gestão de produtos
- **Vendas:** Nova venda
- **Movimentações:** Histórico de entradas/saídas

**Compras:**
- Fornecedores
- Pedidos de Compra

**Financeiro:**
- Dashboard Financeiro
- Contas a Pagar
- Contas a Receber
- Fluxo de Caixa

**Gestão:**
- Inventário
- Relatórios

---

## 💡 Dicas de Uso

1. **Cadastre fornecedores primeiro** antes de criar compras
2. **Use categorias financeiras** para melhor organização
3. **Faça inventários periódicos** (mensais ou trimestrais)
4. **Monitore o dashboard financeiro** diariamente
5. **Analise a Curva ABC** para focar nos produtos importantes

---

**Desenvolvido com:** Flask, SQLite, HTML5, CSS3, JavaScript
**Tema:** Tabacaria Premium - Dark Blue, Red & Brown
**Versão:** 2.0 - Sistema ERP Completo

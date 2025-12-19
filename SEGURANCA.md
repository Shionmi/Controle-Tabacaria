# 🔒 Melhorias de Segurança - JM Tabacaria

**Data da Atualização:** Dezembro 2025

## ✅ O que foi implementado

### 1. **Autenticação e Controle de Acesso**
- ✅ Sistema de login obrigatório para acessar qualquer página
- ✅ Usuário padrão criado: `admin` / `admin123`
- ✅ Sessões seguras com Flask-Login
- ✅ Logout disponível no sistema

**Como usar:**
- Ao abrir o sistema, você será redirecionado para tela de login
- Entre com: **Usuário:** `admin` | **Senha:** `admin123`
- **IMPORTANTE:** Mude a senha padrão após primeiro acesso

### 2. **Proteção CSRF (Cross-Site Request Forgery)**
- ✅ Tokens CSRF automáticos em todos os formulários
- ✅ Proteção contra requisições forjadas
- ✅ Validação automática em todas as operações

**Benefício:** Impede que sites maliciosos enviem comandos para seu sistema.

### 3. **Validação de Dados**
- ✅ Valores monetários validados (apenas números positivos)
- ✅ Datas verificadas no formato correto
- ✅ IDs e quantidades validadas
- ✅ Formas de pagamento restritas a valores permitidos

**Benefício:** Evita corrupção de dados e tentativas de DoS.

### 4. **Túnel Público Ngrok - DESABILITADO por Padrão**
- ✅ Ngrok agora requer ativação manual via variável de ambiente
- ✅ Avisos de segurança claros quando habilitado
- ✅ Sistema funciona apenas na rede local por padrão

**Como habilitar acesso remoto (não recomendado):**
```powershell
$env:ENABLE_NGROK="1"
.\Iniciar_Sistema.bat
```

⚠️ **ATENÇÃO:** Mesmo com login, expor via internet aumenta riscos. Use apenas se necessário.

### 5. **Transações e Integridade de Dados**
- ✅ Todas as operações de escrita usam transações
- ✅ Rollback automático em caso de erro
- ✅ Consistência garantida em operações críticas

**Benefício:** Dados nunca ficam pela metade em caso de falha.

---

## 📋 Tarefas Pendentes Recomendadas

### Prioridade ALTA:
1. **Trocar senha padrão**
   - Criar nova senha forte para o usuário `admin`
   - Ou criar novos usuários e desabilitar o admin

2. **Backup Regular**
   - Copiar o arquivo `estoque_tabacaria.db` regularmente
   - Guardar em local seguro (pendrive, nuvem)

### Prioridade MÉDIA:
3. **Integridade de CDNs (SRI)**
   - Adicionar hashes de integridade em FontAwesome, DataTables
   - Previne ataques via CDN comprometida

4. **Rate Limiting**
   - Limitar tentativas de login (ex: máx 5 por minuto)
   - Evita ataques de força bruta

5. **Logs de Auditoria**
   - Expandir registro de ações sensíveis
   - Criar alertas para atividades suspeitas

---

## 🚀 Como Reinstalar/Atualizar

1. **Fazer backup do banco de dados:**
   ```
   Copiar: estoque_tabacaria.db → estoque_tabacaria.db.backup
   ```

2. **Apagar ambiente virtual antigo:**
   ```
   Deletar pasta: .venv
   Deletar arquivo: estoque_tabacaria.db (se quiser começar do zero)
   ```

3. **Executar instalação:**
   ```
   Clicar com botão direito em Iniciar_Sistema.bat
   "Executar como administrador"
   ```

4. **Primeiro login:**
   - Acesse: `http://127.0.0.1:5000`
   - Login: `admin` / `admin123`
   - Mude a senha!

---

## 📞 Suporte

Se encontrar problemas:

1. **Erro ao instalar:** Verifique se Python 3.10+ está instalado
2. **Não consegue fazer login:** Verifique usuário e senha (case-sensitive)
3. **Erro de CSRF:** Limpe cache/cookies do navegador
4. **Ngrok não funciona:** Verifique se definiu `ENABLE_NGROK=1`

---

## 📊 Comparativo: Antes vs Depois

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Autenticação | ❌ Nenhuma | ✅ Login obrigatório |
| Proteção CSRF | ❌ Não | ✅ Sim |
| Validação de entrada | ❌ Mínima | ✅ Completa |
| Túnel público | ⚠️ Sempre ativo | ✅ Desabilitado por padrão |
| Transações DB | ⚠️ Inconsistente | ✅ Completo |
| Debug em produção | ❌ Ativo | ✅ Desabilitado |
| Schema consolidado | ❌ Runtime ALTER | ✅ Schema único |

---

**Desenvolvido para JM Tabacaria** | Sistema Profissional de Gestão

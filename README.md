# Controle-Tabacaria
Sistema de controle de estoque para tabacaria
Este repositório contém um sistema simples em Flask para gerenciar produtos, gerar etiquetas (códigos de barras) e registrar fornecimentos.

Este arquivo descreve passo-a-passo o que você precisa instalar e configurar no computador da cliente (Windows) para rodar a aplicação localmente.

## Requisitos (Windows)
- Python 3.10 ou 3.11 instalado (64-bit recomendado). Baixe em https://www.python.org/
- Git (opcional, para clonar o repositório)
- Acesso à internet para baixar dependências e bibliotecas front-end (cdn)

## Passos de instalação

1. Abra PowerShell como o usuário que irá rodar a aplicação.

2. Navegue até a pasta do projeto:

```powershell

```

3. Crie e ative um ambiente virtual Python (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Instale dependências:

```powershell
pip install -r requirements.txt
```

5. Criar banco de dados SQLite usando o schema fornecido (`schema.sql`). Você pode usar sqlite3 (se tiver) ou um pequeno script Python:

PowerShell + sqlite3 (se instalado):
```powershell
sqlite3 estoque_tabacaria.db < schema.sql
```

Ou usando Python (sem sqlite3 CLI):
```powershell
python - <<'PY'
import sqlite3
print('Criando DB...')
conn = sqlite3.connect('estoque_tabacaria.db')
with open('schema.sql','r',encoding='utf-8') as f:
	conn.executescript(f.read())
conn.commit(); conn.close()
print('Feito')
PY
```

6. Crie a pasta para códigos de barras (se ainda não existir) e dê permissão de escrita:

```powershell
mkdir -Force static\barcodes
# No Windows a permissão normalmente já é suficiente, mas verifique se o usuário do processo pode escrever nessa pasta.
```

7. Coloque o logo da loja em `static/Images/Logo_tabacaria.png`. Se o logo estiver em `Templates/Logo_tabacaria.png` (como em alguns repositórios), há um script de utilidade em `scripts/move_logo.py` que copia o arquivo para `static/Images`.

Executar script (opcional):
```powershell
python .\scripts\move_logo.py
```

8. Rodar a aplicação (desenvolvimento):

```powershell
# Ative o venv se necessário
python app.py
```

Abra no navegador: http://127.0.0.1:5000

## Notas sobre impressão de etiquetas
- A aplicação gera imagens PNG do código de barras em `static/barcodes/` no momento em que um produto é registrado. A página de impressão mostra apenas a imagem do código de barras (sem o nome), e a regra `@media print` foi configurada para imprimir somente a etiqueta no tamanho aproximado de 50mm x 30mm.
- Se o diálogo de impressão não apresentar o tamanho correto, verifique as configurações da impressora (escala/pixels por polegada). Ajustes finos podem ser feitos no CSS (`static/style.css`) na classe `.print-area`.

## Dependências principais
- Flask — servidor web
- python-barcode — geração de códigos de barras (gera PNG quando Pillow estiver instalado)
- Pillow — suporte a imagens
- reportlab — geração de PDFs (opcional, usado por rota que gera PDF)

## Produção / Deploy
- Para produção em Windows, é comum usar o servidor Waitress ou empacotar como serviço Windows. Exemplo com Waitress:

```powershell
pip install waitress
python -m waitress --listen=0.0.0.0:8000 app:app
```

## Troubleshooting rápido
- Erro ao gerar PNG do barcode: verifique se `Pillow` está instalado (pip install Pillow) e se a pasta `static/barcodes` é gravável.
- Erro 404 no `/fornecedor`: verifique se reiniciou o servidor após mudanças no código.
- Dependências desatualizadas: rode `pip install -U -r requirements.txt` para atualizar.

## O que eu (desenvolvedor) já deixei preparado
- `requirements.txt` com dependências.
- `scripts/move_logo.py` para mover o logo entre pastas (se necessário).
- `schema.sql` com as tabelas `produtos` e `movimentacoes`.
- Páginas: `/` (index), `/registrar`, `/estoque`, `/fornecedor`.

Se quiser, eu posso gerar um instalador mais detalhado (PowerShell script) que automatize os passos 2–8 para a máquina da cliente.

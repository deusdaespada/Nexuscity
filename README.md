# 🏙️ Cidade Nexus — Bot Discord + Painel Administrativo

Sistema completo de cidade virtual/roleplay para Discord, com painel web administrativo, API REST e banco de dados PostgreSQL.

## 📁 Estrutura do Projeto

```
cidade-nexus/
├── main.py                 # Inicialização do bot e API
├── requirements.txt        # Dependências
├── .env.example           # Variáveis de ambiente
├── README.md              # Este arquivo
├── cogs/                  # Módulos do bot (Cogs)
│   ├── citizens.py        # Sistema de cidadãos
│   ├── economy.py         # Economia e banco
│   ├── police.py          # Sistema policial
│   ├── moderation.py      # Moderação do servidor
│   ├── tickets.py         # Sistema de tickets
│   ├── admin.py           # Comandos administrativos
│   └── ...                # Outros módulos
├── database/              # Banco de dados
│   ├── database.py        # Conexão SQLAlchemy
│   └── models.py          # Modelos ORM (30+ tabelas)
├── utils/                 # Utilitários
│   ├── embeds.py          # Embeds do Discord
│   ├── permissions.py     # Permissões RBAC
│   ├── checks.py          # Verificações de permissão
│   ├── helpers.py         # Funções auxiliares
│   └── logger.py          # Logger
├── api/                   # API FastAPI
│   └── app.py             # Rotas da API
└── web/                   # Painel Web
    └── index.html         # Interface administrativa
```

## 🚀 Instalação no Replit

### 1. Criar projeto
- No Replit, clique em **Create** → **Import from GitHub** (ou crie um Blank Repl em Python)
- Faça upload dos arquivos ou use o Git

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Secrets (Variáveis de Ambiente)
No Replit, vá em **Tools** → **Secrets** e adicione:

| Chave | Descrição |
|-------|-----------|
| `DISCORD_TOKEN` | Token do bot Discord |
| `DATABASE_URL` | URL do PostgreSQL |
| `GUILD_ID` | ID do servidor de desenvolvimento |
| `ADMIN_ROLE_ID` | ID do cargo de administrador |
| `LOG_CHANNEL_ID` | ID do canal de logs |
| `JWT_SECRET` | Chave secreta para JWT |
| `DISCORD_CLIENT_ID` | Client ID do app Discord |
| `DISCORD_CLIENT_SECRET` | Client Secret do app Discord |
| `DISCORD_REDIRECT_URI` | URL de callback OAuth2 |

### 4. Configurar Banco de Dados
Use o **Replit Database** ou conecte um PostgreSQL externo (ex: Supabase, Neon).

Se usar Replit Database PostgreSQL:
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/database
```

### 5. Iniciar o bot
```bash
python main.py
```

## 🤖 Comandos Slash Disponíveis

### Cidadãos
- `/cidadao registrar` — Registra novo cidadão
- `/cidadao perfil` — Visualiza perfil
- `/cidadao documentos` — Documentos oficiais
- `/cidadao historico` — Histórico criminal

### Economia
- `/economia saldo` — Consulta saldo
- `/economia transferir` — Transfere dinheiro
- `/economia extrato` — Extrato bancário

### Banco
- `/banco depositar` — Deposita dinheiro
- `/banco sacar` — Saca dinheiro

### Polícia
- `/policia ficha` — Consulta ficha
- `/policia prender` — Prende cidadão
- `/policia liberar` — Liberta cidadão
- `/policia multa` — Aplica multa
- `/policia ocorrencia` — Registra ocorrência

### Moderação
- `/moderacao warn` — Aplica aviso
- `/moderacao timeout` — Aplica timeout
- `/moderacao kick` — Expulsa membro
- `/moderacao ban` — Bane membro
- `/moderacao unban` — Desbane usuário
- `/moderacao clear` — Limpa mensagens
- `/moderacao lock/unlock` — Bloqueia/desbloqueia canal

### Tickets
- `/ticket abrir` — Abre ticket
- `/ticket painel` — Envia painel de tickets
- `/ticket fechar` — Fecha ticket

### Admin
- `/admin usuario` — Info de usuário
- `/admin economia` — Gerencia economia
- `/admin cargo` — Gerencia cargos admin
- `/admin estatisticas` — Estatísticas gerais

## 🔌 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Estatísticas gerais |
| GET | `/api/citizens` | Lista cidadãos |
| GET | `/api/citizens/{discord_id}` | Detalhes do cidadão |
| POST | `/api/citizens` | Cria cidadão |
| PATCH | `/api/citizens/{citizen_id}` | Atualiza cidadão |
| GET | `/api/economy/stats` | Stats econômicos |
| POST | `/api/economy/update` | Atualiza economia |
| GET | `/api/police/records` | Registros policiais |
| GET | `/api/police/arrests` | Prisões |
| GET | `/api/tickets` | Tickets |
| GET | `/api/audit-logs` | Logs de auditoria |
| GET | `/api/companies` | Empresas |
| GET | `/api/laws` | Leis |
| GET | `/api/jobs` | Empregos |
| GET | `/painel` | Painel administrativo web |

## 🔒 Segurança

- ✅ Discord OAuth2 para autenticação
- ✅ JWT para sessões
- ✅ RBAC (Role-Based Access Control)
- ✅ Variáveis de ambiente para secrets
- ✅ SQL Injection protection (SQLAlchemy ORM)
- ✅ Validação de dados (Pydantic)
- ✅ Logs de auditoria em todas as ações críticas

## 🏗️ Expandindo o Sistema

Para adicionar um novo sistema:

1. Crie `cogs/novo_sistema.py`
2. Implemente a classe Cog com `@app_commands.Group`
3. Adicione os comandos slash
4. O `main.py` carrega automaticamente

Exemplo mínimo:
```python
from discord.ext import commands
from discord import app_commands

class NovoSistemaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    grupo = app_commands.Group(name="sistema", description="Descrição")

    @grupo.command(name="comando", description="Descrição do comando")
    async def comando(self, interaction):
        await interaction.response.send_message("Funcionando!")

async def setup(bot):
    await bot.add_cog(NovoSistemaCog(bot))
```

## 📜 Licença

Projeto desenvolvido para Cidade Nexus. Uso interno.

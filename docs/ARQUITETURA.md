# Documentação Técnica - Arquitetura WhatsApp Imóveis DF

## Visão Geral

Sistema de atendimento via WhatsApp auto-hospedado para imobiliária em Brasília/DF, com arquitetura modular preparada para evolução com agentes de IA especializados.

---

## Componentes Principais

### 1. Evolution API (Camada WhatsApp)
- **Função**: Ponte WhatsApp Web ↔ REST API
- **Porta**: 8080
- **Banco**: PostgreSQL (db: evolution)
- **Cache**: Redis
- **Recursos**:
  - Multi-instância (vários números)
  - Webhooks para mensagens, status, conexão
  - Envio de mídia, localização, contatos
  - Gerenciamento de grupos
  - API Key auth

### 2. Typebot (Camada Conversacional)
- **Função**: Chatbot visual com lógica condicional
- **Portas**: 3000 (builder), 3001 (viewer)
- **Banco**: PostgreSQL (db: typebot)
- **Recursos**:
  - Drag-and-drop flow builder
  - Variáveis persistentes por sessão
  - Lógica condicional (if/else)
  - Webhooks nativos
  - Integração direta Evolution API
  - Viewer embeddable

### 3. N8N (Camada Automação)
- **Função**: Orquestração de workflows
- **Porta**: 5678
- **Banco**: PostgreSQL (db: n8n)
- **Recursos**:
  - 400+ integrações nativas
  - Webhooks HTTP
  - Code nodes (JS/Python)
  - Agendamento (cron)
  - Execução assíncrona

### 4. PostgreSQL (Dados)
- **Versão**: 16 Alpine
- **Databases**: evolution, typebot, n8n
- **Usuários**: evolution, typebot, n8n (próprios)
- **Persistência**: Volume Docker

### 5. Redis (Cache/Sessão)
- **Versão**: 7 Alpine
- **Uso**: Evolution API (filas, sessões, rate limit)
- **Persistência**: Volume Docker (AOF)

---

## Fluxo de Dados

### Entrada (WhatsApp → Sistema)
```
WhatsApp User
    │
    ▼
Evolution API (Webhook: messages.upsert)
    │
    ▼
Typebot (Webhook: /api/webhooks/evolution)
    │
    ├── Processa fluxo qualificacao-leads.json
    │   ├── Coleta variáveis (nome, tipo, região, valor, etc.)
    │   └── Lógica condicional por tipo_negocio
    │
    ▼
Webhook → N8N (lead-qualificado / captacao-imovel)
    │
    ├── N8N Workflow: Notifica corretor (WhatsApp/Email/Slack)
    ├── N8N Workflow: Cria/Atualiza lead no CRM
    └── N8N Workflow: Dispara automações (follow-up, tags, etc.)
```

### Saída (Sistema → WhatsApp)
```
N8N / Typebot / Agente IA
    │
    ▼
Evolution API (POST /message/sendText ou /message/sendMedia)
    │
    ▼
WhatsApp User
```

---

## Configuração de Webhooks

### Evolution API → Typebot
```
URL: https://seu-dominio.com/api/webhooks/evolution
Eventos: messages.upsert, connection.update
Headers: apikey: SUA_API_KEY
```

### Typebot → N8N
```
Lead Qualificado:
  URL: https://n8n.seu-dominio.com/webhook/lead-qualificado
  Method: POST
  Body: JSON com todas variáveis do fluxo

Captação Imóvel:
  URL: https://n8n.seu-dominio.com/webhook/captacao-imovel
  Method: POST
  Body: { endereco, telefone, origem }
```

---

## Variáveis de Ambiente Críticas

| Variável | Onde | Descrição |
|----------|------|-----------|
| `EVOLUTION_API_KEY` | Evolution, docker-compose | Chave secreta API Evolution |
| `TYPEBOT_ENCRYPTION_SECRET` | Typebot, docker-compose | 32 chars, criptografia dados sensíveis |
| `TYPEBOT_ADMIN_EMAIL` | Typebot, docker-compose | Email admin inicial |
| `N8N_BASIC_AUTH_USER/PASSWORD` | N8N, docker-compose | Login N8N |
| `WEBHOOK_URL` | N8N | URL pública para webhooks |

---

## Preparação para Agentes IA

### Estrutura agents/
```
agents/
├── atendimento/          # Agente conversacional principal
│   ├── prompts/          # System prompts por cenário
│   ├── tools/            # Ferramentas (busca imóveis, agenda, etc.)
│   ├── knowledge/        # Base conhecimento (RAG)
│   └── config.yaml       # Modelo, temp, limites
├── crm/                  # Agente CRM
│   ├── prompts/
│   ├── tools/            # CRUD leads, deals, activities
│   └── integrations/     # Pipedrive, HubSpot, Notion, etc.
├── captacao-imoveis/     # Agente captação
│   ├── prompts/
│   ├── tools/            # Scraping portais, avaliação, outreach
│   └── data/             # Dados mercado DF
└── captacao-contatos/    # Agente lead gen
    ├── prompts/
    ├── tools/            # Social scraping, lead magnets
    └── campaigns/        # Templates campanhas
```

### Integração Futura (OpenCode + LangChain)

```python
# Exemplo: agents/atendimento/main.py
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool
from tools.busca_imoveis import BuscaImoveisTool
from tools.agenda_visita import AgendaVisitaTool

class AtendimentoImoveisAgent:
    def __init__(self, llm, vectorstore):
        self.tools = [
            BuscaImoveisTool(vectorstore),
            AgendaVisitaTool(),
            # ... mais tools
        ]
        self.agent = create_openai_functions_agent(llm, self.tools, prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools)
    
    async def processar(self, mensagem: str, contexto: dict) -> str:
        return await self.executor.ainvoke({
            "input": mensagem,
            "contexto": contexto  # variáveis Typebot + histórico
        })
```

### RAG (Retrieval-Augmented Generation) para Imóveis

```yaml
# agents/atendimento/config.yaml
model: "gpt-4o-mini"  # ou ollama/llama3 local
temperature: 0.3
max_tokens: 2000

knowledge_base:
  source: "postgresql"  # ou arquivos, API
  tables: ["imoveis", "bairros", "condominios"]
  embedding_model: "text-embedding-3-small"
  chunk_size: 500
  top_k: 5

tools:
  - busca_imoveis
  - agenda_visita
  - envia_fotos
  - calcula_financiamento
  - verifica_disponibilidade
```

---

## Deploy Production

### Requisitos Mínimos
- CPU: 2 vCPU
- RAM: 4 GB (recomendado 8 GB para IA local)
- Disco: 50 GB SSD
- OS: Ubuntu 22.04+ / Debian 12

### SSL/HTTPS (Obrigatório para Webhooks)
```yaml
# docker-compose.override.yml para Traefik
services:
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik:/etc/traefik
    networks:
      - whatsapp-network
```

### Backup Automático
```bash
# Cron diário 03:00
#!/bin/bash
docker exec postgres pg_dumpall -U postgres | gzip > /backups/db_$(date +%F).sql.gz
tar -czf /backups/volumes_$(date +%F).tar.gz /var/lib/docker/volumes/whatsapp-imoveis-df_*
# Upload para S3/Wasabi/Backblaze B2
```

### Monitoramento
- **Portainer**: Gestão containers
- **Uptime Kuma**: Uptime webhooks
- **Grafana + Prometheus**: Métricas (opcional)

---

## Escalabilidade

### Horizontal (Múltiplos Atendentes)
1. Evolution API: Múltiplas instâncias (um número por corretor/equipe)
2. Typebot: Um bot por especialidade ou funil
3. N8N: Workers em modo queue (Redis/RabbitMQ)

### Vertical (Mais Recursos)
- Aumentar RAM/CPU do VPS
- PostgreSQL: `shared_buffers`, `work_mem`, `effective_cache_size`
- Redis: `maxmemory-policy allkeys-lru`

---

## Troubleshooting Comum

| Problema | Solução |
|----------|---------|
| Evolution não conecta WhatsApp | Verificar QR Code, limpar cache navegador, reiniciar container |
| Typebot não recebe webhook | Verificar URL pública, CORS, headers apikey |
| N8N não executa workflow | Verificar logs, credenciais, webhook URL acessível |
| Mensagens não chegam | Verificar Evolution logs, webhook response 200, formato JSON |
| Alto uso memória | Limitar containers, configurar swap, otimizar PostgreSQL |

---

## Logs Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f evolution
docker-compose logs -f typebot
docker-compose logs -f n8n

# Logs Evolution API específicos
docker exec evolution-api tail -f /evolution/logs/app.log
```

---

## Próximos Passos Técnicos

1. **Curto prazo**: Configurar N8N workflows para notificar corretores por região
2. **Médio prazo**: Implementar RAG com base de imóveis (pgvector)
3. **Longo prazo**: Agentes IA autônomos com OpenCode SDK
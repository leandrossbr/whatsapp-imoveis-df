# 🏠 WhatsApp Imóveis DF - Assistente Virtual Inteligente

Sistema completo de atendimento via WhatsApp para corretor de imóveis em Brasília/DF, com qualificação humanizada de leads e arquitetura preparada para agentes de IA especializados.

## 🎯 Objetivo

Criar um atendimento virtual no WhatsApp que:
- ✅ Responde automaticamente 24/7
- ✅ Qualifica leads de forma humanizada e personalizada
- ✅ Filtra clientes (compra, aluguel, captação, parceria)
- ✅ Encaminha para corretor especialista por região
- ✅ **Custo zero** (self-hosted, só paga servidor)
- ✅ Preparado para futuros agentes IA especializados

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
                        WHATSAPP USER                                
└──────────────────────────┬────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
                     EVOLUTION API (WhatsApp Web)                 
         • Conexão WhatsApp Web • Webhooks • Multi-instância      
└──────────────────────────┬────────────────────────────────────────┘
                           │ Webhook /api/webhooks/evolution
                           ▼
┌─────────────────────────────────────────────────────────────────┐
                        TYPEBOT (Fluxo Visual)                     
         • Qualificação humanizada • Variáveis • Lógica condicional
         • Integração nativa Evolution API                          
└──────────────────────────┬────────────────────────────────────────┘
                           │ Webhooks para N8N
                ┌──────────┴──────────┐
                ▼                     ▼
       ┌───────────────┐      ┌───────────────┐
       │   N8N         │      │   CRM         │
       │   (Automação) │      │   (Futuro)    │
       └───────────────┘      └───────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
                    AGENTES IA ESPECIALIZADOS (Futuro)            
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐
    │ Atendimento │  │ CRM         │  │ Captação    │  │Captação│
    │ IA          │  │ IA          │  │ Imóveis IA  │  │Contatos│
    └─────────────┘  └─────────────┘  └─────────────┘  └────────┘
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Pré-requisitos
- Docker + Docker Compose
- Servidor (VPS) com 2GB+ RAM (ex: DigitalOcean $12/mo, Hetzner €5/mo)
- Domínio (opcional, para SSL)

### 2. Clone e configure
```bash
git clone https://github.com/leandro-agent/whatsapp-imoveis-df.git
cd whatsapp-imoveis-df
cp .env.example .env
# Edite .env com suas chaves
```

### 3. Suba os containers
```bash
docker-compose up -d
```

### 4. Acesse
- **Evolution API**: http://seu-ip:8080 (docs: /manager)
- **Typebot Builder**: http://seu-ip:3000
- **Typebot Viewer**: http://seu-ip:3001
- **N8N**: http://seu-ip:5678

### 5. Configure Evolution API
1. Acesse http://seu-ip:8080/manager
2. Crie instância "imoveis-df"
3. Conecte WhatsApp (QR Code)
4. Configure webhook: `http://seu-ip:3000/api/webhooks/evolution`

### 6. Importe fluxo no Typebot
1. Acesse http://seu-ip:3000
2. Crie conta admin
3. Importe `typebot/flows/qualificacao-leads.json`
4. Publique e pegue URL pública

### 7. Conecte Evolution → Typebot
No Evolution Manager, configure webhook da instância para a URL do Typebot.

## 📁 Estrutura do Projeto

```
whatsapp-imoveis-df/
├── docker-compose.yml              # Orquestração completa
├── .env.example                    # Variáveis de ambiente
├── init-multiple-dbs.sh            # Init PostgreSQL multi-db
├── evolution/
│   └── config/
│       └── .env.example            # Config Evolution API
├── typebot/
│   └── flows/
│       └── qualificacao-leads.json # Fluxo principal
├── agents/                         # Agentes IA (futuro)
│   ├── atendimento/
│   ├── crm/
│   ├── captacao-imoveis/
│   └── captacao-contatos/
└── docs/
    └── ARQUITETURA.md              # Documentação técnica
```

## 💰 Custos Estimados (Mensal)

| Item | Custo |
|------|-------|
| VPS 2GB RAM (Hetzner/Contabo) | ~R$ 30-60 |
| Domínio .com.br | ~R$ 40/ano |
| **Total/mês** | **~R$ 35-65** |

*Sem taxa por mensagem, sem limite de contatos, sem mensalidade SaaS*

## 🔮 Roadmap - Agentes IA Especializados

### Fase 1 - Atual (Concluída)
- [x] Evolution API + Typebot funcionando
- [x] Fluxo qualificação leads humanizado
- [x] Webhooks para CRM/N8N

### Fase 2 - Agente Atendimento IA
- [ ] Responde dúvidas sobre imóveis (RAG com base de imóveis)
- [ ] Agenda visitas automaticamente
- [ ] Envia fotos/vídeos sob demanda
- [ ] Negociação inicial de valores

### Fase 3 - Agente CRM IA
- [ ] Atualiza CRM automaticamente (Pipedrive, HubSpot, Notion)
- [ ] Follow-up inteligente (reengaja leads frios)
- [ ] Score de lead preditivo
- [ ] Relatórios de conversão por corretor

### Fase 4 - Agente Captação Imóveis IA
- [ ] Monitora portais (Zap, OLX, VivaReal) para oportunidades
- [ ] Identifica proprietários para captação
- [ ] Gera roteiros de abordagem personalizados
- [ ] Análise de precificação de mercado

### Fase 5 - Agente Captação Contatos IA
- [ ] Scraping ético redes sociais (Instagram, LinkedIn)
- [ ] Lead magnets (e-books, checklists, calculadoras)
- [ ] Campanhas WhatsApp ativas (respeitando LGPD)
- [ ] Nutrição de leads long-term

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|------------|
| WhatsApp | Evolution API (WhatsApp Web) |
| Chatbot | Typebot (Visual, open-source) |
| Automação | N8N (Workflow engine) |
| Banco | PostgreSQL + Redis |
| IA (futuro) | OpenCode + LangChain + Ollama/LLM API |
| Deploy | Docker Compose / Kubernetes |

## 📱 Fluxo de Qualificação (Atual)

O Typebot percorre:
1. **Boas-vindas personalizadas** → Nome
2. **Tipo de negócio** → Comprar / Alugar / Anunciar / Parceria
3. **Tipo imóvel** → Casa, Apt, Cobertura, Terreno, Comercial
4. **Região DF** → 13 regiões + "Outra"
5. **Faixa de valor** → 6 faixas compra/aluguel
6. **Quartos** → 1 a 4+
7. **Urgência** → Urgente / 3m / 6m / Pesquisando
8. **Contato** → WhatsApp + Email opcional
9. **Webhook → N8N/CRM** → Notifica corretor por região

## 🔒 Segurança & LGPD

- ✅ Dados ficam no **seu servidor**
- ✅ Criptografia Typebot (ENCRYPTION_SECRET)
- ✅ API Key Evolution API
- ✅ N8N com Basic Auth
- ✅ LGPD: consentimento no fluxo, direito à exclusão

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -m 'feat: adiciona X'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

## 📄 Licença

MIT - Use livremente para seu negócio imobiliário.

---

**Desenvolvido para corretores de Brasília/DF que querem autonomia tecnológica** 🏠💚

*Dúvidas? Abra uma Issue ou me chame no WhatsApp (configure o bot e teste!)*
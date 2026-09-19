# Agente CRM IA

## Objetivo
Automação inteligente de CRM: atualização, follow-up, scoring e relatórios.

## Capacidades Planejadas
- [ ] Atualização automática leads/deals (Pipedrive, HubSpot, Notion, Airtable)
- [ ] Follow-up inteligente baseado em comportamento
- [ ] Lead scoring preditivo (probabilidade conversão)
- [ ] Detecção de leads frios → reengajamento
- [ ] Relatórios conversão por corretor/fonte/região
- [ ] Sugestão próxima ação (next best action)

## Integrações
- Pipedrive API
- HubSpot API
- Notion API
- Airtable API
- Google Sheets (fallback)
- Evolution API (notificações WhatsApp corretores)

## Estrutura
```
crm/
├── prompts/
│   ├── lead_scoring.md
│   ├── follow_up.md
│   └── next_action.md
├── tools/
│   ├── crud_leads.py
│   ├── crud_deals.py
│   ├── scoring_model.py
│   └── relatorios.py
├── integrations/
│   ├── pipedrive.py
│   ├── hubspot.py
│   └── notion.py
├── config.yaml
└── main.py
```
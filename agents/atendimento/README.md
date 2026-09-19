# Agente de Atendimento IA

## Objetivo
Agente conversacional especializado em atendimento imobiliário humanizado para Brasília/DF.

## Capacidades Planejadas
- [ ] Responder dúvidas sobre imóveis (RAG com base local)
- [ ] Agendar visitas automaticamente
- [ ] Enviar fotos/vídeos/fichas técnicas sob demanda
- [ ] Negociação inicial de valores
- [ ] Qualificação contínua durante conversa
- [ ] Handoff humano quando necessário

## Stack Sugerida
- **LLM**: GPT-4o-mini / Claude 3.5 Haiku / Ollama (local)
- **Framework**: LangChain / LangGraph / OpenCode SDK
- **RAG**: PostgreSQL + pgvector / ChromaDB
- **Tools**: Busca imóveis, Agenda, Calculadora financiamento, Disponibilidade

## Estrutura
```
atendimento/
├── prompts/
│   ├── system_prompt.md
│   ├── qualificacao.md
│   ├── agendamento.md
│   └── handoff.md
├── tools/
│   ├── busca_imoveis.py
│   ├── agenda_visita.py
│   ├── envia_midia.py
│   └── calcula_financiamento.py
├── knowledge/
│   ├── imoveis/          # Base vetorial imóveis
│   ├── bairros/          # Info bairros DF
│   └── perguntas_frequentes/
├── config.yaml
└── main.py
```

## Integração
- Recebe contexto do Typebot (variáveis qualificação)
- Chama Evolution API para enviar mídia/respostas complexas
- Registra interações no CRM via N8N
- Escala para humano via palavra-chave ou score
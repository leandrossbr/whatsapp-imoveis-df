# Agente Captação Imóveis IA

## Objetivo
Identificar, abordar e captar imóveis para a carteira da imobiliária.

## Capacidades Planejadas
- [ ] Monitorar portais (Zap, OLX, VivaReal, ImovelWeb) para oportunidades
- [ ] Identificar proprietários "for sale by owner"
- [ ] Análise de precificação de mercado (CMA automatizado)
- [ ] Geração de roteiros abordagem personalizados
- [ ] Outreach multi-canal (WhatsApp, Email, Ligação, Carta)
- [ ] Agendamento avaliações presenciais
- [ ] Acompanhamento pipeline captação

## Fontes de Dados
- Portais imobiliários (scraping ético + APIs onde disponível)
- Registros públicos (matrículas, IPTU)
- Redes sociais (Instagram, Facebook Marketplace)
- Indicações network corretores
- Leads entrada (proprietários querendo anunciar)

## Estrutura
```
captacao-imoveis/
├── prompts/
│   ├── analise_mercado.md
│   ├── roteiro_abordagem.md
│   └── follow_up_proprietario.md
├── tools/
│   ├── scraping_portais.py
│   ├── analise_preco.py
│   ├── gera_roteiro.py
│   └── agenda_avaliacao.py
├── data/
│   ├── historico_vendas_df.csv
│   ├── indices_bairros.json
│   └── templates_contrato/
├── config.yaml
└── main.py
```
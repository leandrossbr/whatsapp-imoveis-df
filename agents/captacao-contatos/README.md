# Agente Captação Contatos IA (Lead Generation)

## Objetivo
Gerar leads qualificados de compradores/locatários através de múltiplos canais.

## Capacidades Planejadas
- [ ] Lead Magnets: E-books, checklists, calculadoras, guias bairros DF
- [ ] Campanhas WhatsApp ativas (respeitando LGPD/opt-in)
- [ ] Social Listening: Instagram, LinkedIn, Facebook Groups DF
- [ ] Tráfego pago: Meta Ads, Google Ads → WhatsApp
- [ ] SEO Local: Google Meu Negócio, site imoveisdf.com.br
- [ ] Nutrição long-term: Drip campaigns, market updates
- [ ] Parcerias: Construtoras, advogados, assessorias imigração

## Canais
| Canal | Estratégia | Ferramenta |
|-------|------------|------------|
| WhatsApp | Broadcast lists, grupos, status | Evolution API |
| Instagram | Reels bairros, stories imóveis, DM automation | Meta API / ManyChat |
| LinkedIn | Networking expats, executivos, militar | LinkedIn API / PhantomBuster |
| Google | SEO local, GMB, Ads | SEMrush, Google Ads API |
| Email | Newsletter semanal, market reports | Brevo, MailerLite |
| Parcerias | Co-marketing construtoras | CRM + N8N |

## Estrutura
```
captacao-contatos/
├── prompts/
│   ├── lead_magnets.md
│   ├── social_content.md
│   ├── email_sequences.md
│   └── whatsapp_campaigns.md
├── tools/
│   ├── gera_lead_magnet.py
│   ├── social_listening.py
│   ├── whatsapp_broadcast.py
│   └── meta_ads_optimizer.py
├── campaigns/
│   ├── templates_whatsapp/
│   ├── templates_email/
│   ├── creatives_instagram/
│   └── landing_pages/
├── config.yaml
└── main.py
```
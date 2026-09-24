# Plano — Arte para Status do WhatsApp #01

**Data:** 2026-09-23
**Canal:** Status do WhatsApp (stories) — visualização em tela cheia no celular
**Objetivo:** Gerar conversas (leads) para oferta de apartamentos 2 e 3 quartos em Águas Claras/DF
**Status:** ✅ **ARTE ENTREGUE** — `marketing/exports/status-01.png` (1080×1920)

---

## 1. Formato técnico

| Item | Especificação |
|------|---------------|
| Proporção | **9:16 vertical** (formato Status/Story) |
| Resolução | **1080 × 1920 px** |
| Formato de entrega | PNG (máx. 16 MB no WhatsApp) |
| Safe area topo | 250 px livres (nome + relógio do WhatsApp) |
| Safe area base | 140 px livres (barra "Enviar mensagem") |

## 2. Imagem-base

**Referência:** `LUX.jpg` (peça "Águas Claras — Viva o seu melhor capítulo") — tomada como
base de layout, paleta e copy institucional, com as alterações abaixo.

### ❌ Removido
- Marca/logo **ZUK IMÓVEIS** (rodapé) — não aparece em nenhum lugar
- Selo antigo "de Até 8% NO ITBI" — substituído pela nova copy
- ~~Linha genérica da base substituída pelas ofertas com preços~~ → **coberturas re-adicionadas** (linha 3, com tamanho e 4 vagas)

### ✅ Adicionado (copy exata)
1. Selo benefício: **"Você consegue ITBI, Registro e Escritura GRÁTIS"**
   *(decisão: variante "Você consegue..." em vez de "Consigo...")*
2. **Faixa condição (SUPER destaque): "TABELA DIRETA EM 180 MESES"** — faixa dourada largura total entre a foto e a tabela, com "180" ampliado
3. Oferta A: **2 QUARTOS · 66 m² · 1 VAGA — a partir de R$ 679 mil** *(nota própria: "possuo unidade de 2 quartos com 2 vagas também" — sem ambiguidade)*
4. Oferta B: **3 QUARTOS · 83 m² · 2 VAGAS — a partir de R$ 921 mil**
5. Oferta C: **COBERTURAS LINEAR — de 302 a 333 m² · 4 vagas** *(sem preço na base)*

### ✅ Mantido da base
- Lockup "ÁGUAS CLARAS / VIVA O SEU MELHOR CAPÍTULO" + "CONFORTO, PRATICIDADE E QUALIDADE DE VIDA"
- Slogan "Pronto para morar / SEU NOVO ESTILO DE VIDA EM ÁGUAS CLARAS" sobre a foto
- Faixa verde: "LAZER COMPLETO (Quadra de areia) · PROJETO SUSTENTÁVEL · VAGAS PARA CARRO ELÉTRICO"
- Frases de rodapé: "Fale com a gente" e "SEU PRÓXIMO IMÓVEL ESTÁ AQUI"

### ✅ CTA (decisão: com celular do Leandro)
- Rodapé: **"Fale com Leandro Santos"** + **📱 61 9 9658-7484** (com ícone WhatsApp)
- Botão dourado **"CHAMA NO WHATSAPP"** + tagline "SEU PRÓXIMO IMÓVEL ESTÁ AQUI"
- *"Fale com a gente" removido a pedido**

## 3. Layout (1080×1920)

```
0–220      topo livre (UI do WhatsApp)
220–490    header: ÁGUAS CLARAS | CONFORTO... | SELO benefício (sobe de 222)
490–1050   foto lifestyle (estar+jantar) + "Pronto para morar" + slogan
1050–1444  Card A (2 quartos) ─ Card B (3 quartos) ─ Card C (coberturas)
1444–1584  faixa verde (3 benefícios)
1584–1782  rodapé: "Fale com Leandro Santos" + 61 996587484 + botão + tagline
1782–1920  base livre (barra de resposta)
```

## 4. Produção (reprodutível)

Geradores de IA erram texto em português — a peça é **composta por camadas**:

1. **Foto** gerada por IA sem nenhum texto (`marketing/assets/hero-living.jpg`)
2. **Textos, selo, cards e botão** renderizados em cima com tipografia nítida
   (Playfair Display + Great Vibes + Montserrat + ícones Font Awesome)
3. Script re-executável: `python3 marketing/render_status_01.py`
4. Saídas:
   - `marketing/exports/status-01.png` — master **1080×1920** (Full HD vertical, padrão status)
   - `marketing/exports/status-01-fullhd-2x.png` — **2160×3840** (Full HD dobrado, nitidez máx.)
   - `marketing/exports/status-01-whatsapp.jpg` — JPG calibrado (4:4:4, q93) para postar no status
   - `marketing/exports/status-01-video.mp4` — **vídeo p/ status** (~22s, 1080×1920, H.264) com zoom/pan
     guiando: arte inteira → selo GRÁTIS → faixa 180 MESES → ofertas → contato → fecho
     (script: `python3 marketing/render_status_01_video.py`, fonte: master 2× p/ nitidez no zoom)

## 5. Decisões registradas

- [x] Copy do benefício → "Você consegue ITBI, Registro e Escritura GRÁTIS"
- [x] Contato → só CTA "Chama no WhatsApp" (sem número na arte)
- [x] Estilo → lifestyle com visual da peça-base LUX.jpg
- [x] Composição → uma arte só com as 2 ofertas
- [x] Zuk Imóveis → removida

## 6. Ajustes rápidos possíveis

| Ajuste | Onde |
|--------|------|
| Voltar linha de coberturas | entre cards e faixa verde |
| "2 vagas" também no card de 2 quartos | título do Card A |
| Trocar "mil" por "679.000" | textos dos cards |

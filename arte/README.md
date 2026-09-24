# 🎨 Arte de Divulgação — WhatsApp Full HD

Gerador da peça de impacto do **Leandro Santos — (61) 99658-7484** com a oferta
**"APARTAMENTOS A PARTIR DE R$ 679 MIL"**.

A imagem do imóvel é **mantida como fundo** (sem distorção, corte central
inteligente), recebe tratamento de cor/contraste, scrim e vinheta para o texto
ficar legível, e por cima entram:

- marca **IMÓVEIS DF • BRASÍLIA • DF** e selo "ALTO PADRÃO • DF";
- chamada gigante **APARTAMENTOS / A PARTIR DE / R$ 679 MIL** (dourado degradê);
- barra inferior com a **foto do corretor** em recorte circular com anel
  dourado, nome, cargo, WhatsApp com ícone e botão **CHAME NO WHATSAPP**.

## Saídas

| Formato | Arquivo | Uso |
|---------|---------|-----|
| Full HD paisagem | `saida/leandro-santos-paisagem-1920x1080.{jpg,png}` | conversa, listas de transmissão, anúncio |
| Full HD vertical | `saida/leandro-santos-vertical-1080x1920.{jpg,png}` | Status / Stories |
| Quadrado (extra) | `saida/leandro-santos-quadrado-1080x1080.{jpg,png}` | feed / perfil |

Use o **.jpg** para enviar no WhatsApp (mais leve); o **.png** para editar.

## Como usar

```bash
pip install pillow

# 1) coloque os arquivos em arte/entrada/ (nomes sugeridos):
#      arte/entrada/arte-original.jpg   <- imagem do imóvel / arte antiga
#      arte/entrada/foto-leandro.jpg    <- sua foto (rosto centralizado)
#    (o script procura sozinho por esses prefixos)

# 2) gere tudo:
python3 arte/gerar_arte.py

# ou explicitamente:
python3 arte/gerar_arte.py \
    --fundo arte/entrada/arte-original.jpg \
    --foto  arte/entrada/foto-leandro.jpg \
    --formatos paisagem,vertical,quadrado
```

Sem `--foto`, a arte sai com um círculo marcado **"SUA FOTO"** (prévia de
layout). Sem `--fundo`, sai com um fundo de demonstração.

## Apagar nome/telefone do corretor antigo da arte original

Se a imagem antiga já tiver nome e telefone gravados, informe em
`config.json`:

```json
"zonas_ocultar": [
  [0.05, 0.80, 0.60, 0.15]
]
```

Cada item é `[x, y, largura, altura]` em proporção (0–1) da imagem original.
A região é desfocada e escurecida antes da nova identidade entrar por cima —
o imóvel continua visível no resto da imagem.

Para medir as proporções: abra a imagem e divida as coordenadas em pixels
pela largura/altura dela.

## Recriação da peça LUX (Full HD vertical)

`recriar_lux.py` reconstrói a arte LUX Home Boulevard dentro do ambiente, com
fotos reais do empreendimento (`entrada/lux-fachada.jpg` e `entrada/lux-interior.jpg`,
commitadas para sobreviver a reinícios), a copy original e a identidade do
corretor (nome, WhatsApp, selo R$ 679 mil, CTA):

```bash
python3 arte/recriar_lux.py                 # saída: saida/lux-leandro-santos-1080x1920.*
python3 arte/recriar_lux.py --foto MINHA.jpg  # com o rosto no círculo dourado
```

## Personalização

Tudo em `config.json`: nome, cargo, telefone, link wa.me, textos da oferta,
CTA, cores (`verde_escuro`, `dourado`, `dourado_claro`...), intensidade do
scrim e `escurecer_fundo`.

Fontes: Montserrat (600–900), Bebas Neue e Poppins ficam em `fonts/`
(foras do git). Se faltarem, o script baixa do registry do npm; sem internet,
usa DejaVu como reserva.

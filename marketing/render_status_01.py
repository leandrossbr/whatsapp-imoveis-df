#!/usr/bin/env python3
"""Arte #01 para Status do WhatsApp — 1080x1920.

Base visual: referência LUX.jpg (Águas Claras) — creme/verde/dourado,
SEM marca Zuk Imóveis. Textos renderizados por camadas (copy 100% exata).

Uso:  python3 marketing/render_status_01.py
Sai:  marketing/exports/status-01.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

W, H = 1080, 1920

# ---- paleta amostrada da referência ----
CREAM      = (246, 240, 228)
CREAM_SOFT = (239, 231, 214)
GREEN      = (13, 53, 42)
GREEN_DEEP = (8, 36, 28)
GOLD       = (201, 162, 75)
GOLD_LIGHT = (232, 200, 122)
GOLD_DEEP  = (166, 124, 47)
GOLD_LINE  = (188, 158, 96)
INK        = (26, 26, 24)
INK_SOFT   = (58, 50, 38)
CREAM_TEXT = (240, 233, 218)

FDIR = 'marketing/assets/fonts/'
ADIR = 'marketing/assets/'
OUT  = 'marketing/exports/status-01.png'


def f(name, size):
    return ImageFont.truetype(FDIR + name, size)


def tracked(draw, xy, text, fnt, fill, tracking=0, center_x=None):
    """Desenha texto com entreletra (tracking) manual. Retorna a largura."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = (center_x - total / 2) if center_x is not None else xy[0]
    y = xy[1]
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def gradient_rrect(img, box, radius, top_color, bottom_color, outline=None, outline_w=0):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    grad = Image.new('RGBA', (w, h))
    gd = ImageDraw.Draw(grad)
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3)) + (255,)
        gd.line([(0, y), (w, y)], fill=c)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    img.paste(grad, (x0, y0), mask)
    if outline:
        ImageDraw.Draw(img).rounded_rectangle(box, radius=radius, outline=outline, width=outline_w)


def soft_shadow(img, box, radius, blur=14, offset=(0, 8), alpha=70):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    dx, dy = offset
    ImageDraw.Draw(layer).rounded_rectangle(
        [x0 + dx, y0 + dy, x1 + dx, y1 + dy], radius=radius, fill=(0, 0, 0, alpha))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def glyph(draw, center, ch, fnt, fill):
    """Desenha glifo (ex.: Font Awesome) centrado em `center`."""
    bbox = draw.textbbox((0, 0), ch, font=fnt)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((center[0] - w / 2 - bbox[0], center[1] - h / 2 - bbox[1]), ch, font=fnt, fill=fill)


def shadowed_script(img, center_x, y, text, fnt, fill):
    """Texto script com sombra suave por baixo (legibilidade sobre foto)."""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w = d.textlength(text, font=fnt)
    d.text((center_x - w / 2 + 3, y + 5), text, font=fnt, fill=(0, 0, 0, 140))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(7)))
    d2 = ImageDraw.Draw(img)
    d2.text((center_x - w / 2, y), text, font=fnt, fill=fill)


def quadratic(p0, c, p1, steps=40):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p1[1]
        pts.append((x, y))
    return pts


def main():
    img = Image.new('RGBA', (W, H), CREAM + (255,))
    d = ImageDraw.Draw(img)

    pf84   = f('PlayfairDisplay-Bold.ttf', 84)
    pf78   = f('PlayfairDisplay-Bold.ttf', 78)
    msb21  = f('Montserrat-SemiBold.ttf', 21)
    msb20  = f('Montserrat-SemiBold.ttf', 20)
    msb19  = f('Montserrat-SemiBold.ttf', 19)
    msb15  = f('Montserrat-SemiBold.ttf', 15)
    msb24  = f('Montserrat-SemiBold.ttf', 24)
    msb25  = f('Montserrat-SemiBold.ttf', 25)
    msb26  = f('Montserrat-SemiBold.ttf', 26)
    msb18  = f('Montserrat-Medium.ttf', 18)
    mb33   = f('Montserrat-Bold.ttf', 33)
    mb34   = f('Montserrat-Bold.ttf', 34)
    mb36   = f('Montserrat-Bold.ttf', 36)
    mb58   = f('Montserrat-Bold.ttf', 58)
    mb28   = f('Montserrat-Bold.ttf', 28)
    gv128  = f('GreatVibes-Regular.ttf', 128)
    gv42   = f('GreatVibes-Regular.ttf', 42)
    fa50   = f('fa-solid-900.ttf', 50)
    fa44   = f('fa-solid-900.ttf', 44)
    fa38   = f('fa-solid-900.ttf', 38)
    fa36s  = f('fa-solid-900.ttf', 36)
    fa36   = f('fa-brands-400.ttf', 36)

    BED, CAR, HOUSE, LEAF, CHARGE, STAR = '\uf236', '\uf1b9', '\uf015', '\uf06c', '\uf5e7', '\uf005'
    PALM = '\uf5ca'  # umbrella-beach (f82b tree-palm ausente no subset)
    WHATS = '\uf232'

    # ============ HEADER (y 220-490) ============
    tracked(d, (70, 226), 'ÁGUAS', pf84, INK, tracking=6)
    tracked(d, (70, 314), 'CLARAS', pf84, INK, tracking=6)
    d.line(quadratic((72, 422), (250, 450), (424, 414)), fill=GOLD, width=5)
    d.line(quadratic((95, 432), (250, 456), (400, 426)), fill=GOLD_LINE, width=2)
    tracked(d, (72, 450), 'VIVA O SEU MELHOR CAPÍTULO', msb15, INK_SOFT, tracking=3)
    d.line([(448, 238), (448, 452)], fill=GOLD_DEEP, width=2)
    for i, line in enumerate(['CONFORTO', 'PRATICIDADE', 'E QUALIDADE', 'DE VIDA']):
        tracked(d, (472, 256 + i * 32), line, msb19, INK, tracking=1)

    # ============ HERO (y 490-985) ============
    hero = ImageOps.fit(Image.open(ADIR + 'hero-living.jpg').convert('RGB'),
                        (W, 495), method=Image.LANCZOS, centering=(0.5, 0.45)).convert('RGBA')
    hh = 495
    ov = Image.new('RGBA', (W, hh), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    start = int(hh * 0.52)
    for y in range(start, hh):
        t = (y - start) / (hh - start)
        od.line([(0, y), (W, y)], fill=(8, 22, 16, int((t ** 1.15) * 185)))
    hero = Image.alpha_composite(hero, ov)
    img.paste(hero, (0, 490), hero)

    # ============ SELO BENEFÍCIO (y 222-542) — por cima da foto, como na base ============
    badge = (665, 222, 1035, 542)
    soft_shadow(img, badge, radius=30, blur=16, offset=(0, 10), alpha=80)
    gradient_rrect(img, badge, radius=30, top_color=GREEN, bottom_color=GREEN_DEEP,
                   outline=GOLD, outline_w=3)
    cx = 850
    tracked(d, (0, 262), 'VOCÊ CONSEGUE', msb24, GOLD_LIGHT, tracking=6, center_x=cx)
    d.line([(765, 306), (935, 306)], fill=GOLD_DEEP, width=2)
    tracked(d, (0, 326), 'ITBI, REGISTRO', mb33, CREAM_TEXT, tracking=1, center_x=cx)
    tracked(d, (0, 372), 'E ESCRITURA', mb33, CREAM_TEXT, tracking=1, center_x=cx)
    tracked(d, (0, 422), 'GRÁTIS', pf78, GOLD_LIGHT, tracking=2, center_x=cx)

    d = ImageDraw.Draw(img)
    shadowed_script(img, 540, 735, 'Pronto para morar', gv128, CREAM_TEXT + (255,))
    tracked(d, (0, 895), 'SEU NOVO ESTILO DE VIDA', msb25, CREAM_TEXT, tracking=5, center_x=540)
    tracked(d, (0, 927), 'EM ÁGUAS CLARAS', msb25, CREAM_TEXT, tracking=5, center_x=540)

    # ============ FAIXA CONDICAO — TABELA DIRETA (y 985-1073) — SUPER DESTAQUE ============
    faixa = (0, 985, W, 1073)
    soft_shadow(img, faixa, radius=0, blur=9, offset=(0, 6), alpha=55)
    gradient_rrect(img, faixa, radius=0,
                   top_color=(247, 220, 158), bottom_color=(192, 148, 64))
    d = ImageDraw.Draw(img)
    d.line([(0, 986), (W, 986)], fill=GREEN_DEEP, width=4)
    d.line([(0, 1068), (W, 1068)], fill=GREEN_DEEP, width=4)

    p1, p2, p3 = 'TABELA DIRETA EM', '180', 'MESES'
    tr = 3
    w1 = sum(d.textlength(c, font=mb34) for c in p1) + tr * (len(p1) - 1)
    w2 = sum(d.textlength(c, font=mb58) for c in p2) + tr * (len(p2) - 1)
    w3 = sum(d.textlength(c, font=mb34) for c in p3) + tr * (len(p3) - 1)
    gapw, star = 14, 40
    block = star + 24 + w1 + gapw + w2 + gapw + w3 + 24 + star
    bx = 540 - block / 2
    base = 1050  # linha de base comum
    y2 = base - d.textbbox((0, 0), p2, font=mb58)[3]
    y13 = base - d.textbbox((0, 0), p1, font=mb34)[3]
    glyph(d, (bx + star / 2, 1030), STAR, fa36s, GREEN)
    x = bx + star + 24
    tracked(d, (x, y13), p1, mb34, GREEN, tracking=tr)
    x += w1 + gapw
    tracked(d, (x, y2), p2, mb58, GREEN, tracking=tr)
    x += w2 + gapw
    tracked(d, (x, y13), p3, mb34, GREEN, tracking=tr)
    x += w3 + 24
    glyph(d, (x + star / 2, 1030), STAR, fa36s, GREEN)

    # ============ OFERTAS (y 1073-1444) — 3 linhas ============
    def linha(box_y, icones, titulo, sub, nota=None):
        d.rounded_rectangle((75, box_y, 167, box_y + 92), radius=20,
                            fill=CREAM_SOFT, outline=GOLD, width=2)
        if len(icones) == 1:
            glyph(d, (121, box_y + 44), icones[0], fa50, GOLD_DEEP)
        else:
            glyph(d, (100, box_y + 44), icones[0], fa38, GOLD_DEEP)
            glyph(d, (144, box_y + 44), icones[1], fa38, GOLD_DEEP)
        tracked(d, (200, box_y + 8), titulo, mb33, INK, tracking=1)
        tracked(d, (200, box_y + 54), sub, msb26, GREEN, tracking=1)
        if nota:
            tracked(d, (200, box_y + 84), nota, msb18, INK_SOFT, tracking=1)

    linha(1080, [BED], '2 QUARTOS · 66 m² · 1 VAGA', 'a partir de R$ 679 mil',
          'possuo unidade de 2 quartos com 2 vagas também')
    d.line([(75, 1194), (1010, 1194)], fill=GOLD_LINE, width=1)

    linha(1214, [BED, CAR], '3 QUARTOS · 83 m² · 2 VAGAS', 'a partir de R$ 921 mil')
    d.line([(75, 1328), (1010, 1328)], fill=GOLD_LINE, width=1)

    linha(1348, [HOUSE, CAR], 'COBERTURAS LINEAR', 'de 302 a 333 m² · 4 vagas')

    # ============ FAIXA VERDE (y 1444-1584) ============
    d.rectangle([0, 1444, W, 1584], fill=GREEN)
    d.line([(0, 1445), (W, 1445)], fill=GOLD_DEEP, width=3)
    for x in (360, 720):
        d.line([(x, 1468), (x, 1560)], fill=GOLD_DEEP, width=2)

    glyph(d, (58, 1508), PALM, fa44, GOLD)
    tracked(d, (100, 1482), 'LAZER COMPLETO', msb21, CREAM_TEXT, tracking=1)
    tracked(d, (100, 1514), '(Quadra de areia)', msb18, GOLD_LIGHT, tracking=1)

    glyph(d, (418, 1508), LEAF, fa44, GOLD)
    tracked(d, (458, 1482), 'PROJETO', msb21, CREAM_TEXT, tracking=1)
    tracked(d, (458, 1514), 'SUSTENTÁVEL', msb21, CREAM_TEXT, tracking=1)

    glyph(d, (778, 1508), CHARGE, fa44, GOLD)
    tracked(d, (812, 1482), 'VAGAS PARA', msb21, CREAM_TEXT, tracking=1)
    tracked(d, (812, 1514), 'CARRO ELÉTRICO', msb21, CREAM_TEXT, tracking=1)

    # ============ RODAPÉ / CONTATO + CTA (y 1584-1782) ============
    nome = 'Fale com Leandro Santos'
    nome_w = d.textlength(nome, font=gv42)
    d.text((540 - nome_w / 2, 1588), nome, font=gv42, fill=INK_SOFT)

    fone = '61 9 9658-7484'
    fone_w = d.textlength(fone, font=mb36)
    bloco = 36 + 16 + fone_w
    fx = 540 - bloco / 2
    glyph(d, (fx + 18, 1663), WHATS, fa36, GREEN)
    d.text((fx + 52, 1642), fone, font=mb36, fill=INK)

    btn = (255, 1688, 825, 1758)
    soft_shadow(img, btn, radius=35, blur=10, offset=(0, 5), alpha=60)
    gradient_rrect(img, btn, radius=35, top_color=(245, 217, 152), bottom_color=(198, 155, 70),
                   outline=GOLD_DEEP, outline_w=2)
    d = ImageDraw.Draw(img)
    label = 'CHAMA NO WHATSAPP'
    widths = [d.textlength(ch, font=mb28) for ch in label]
    tw = sum(widths) + 2 * (len(label) - 1)
    block = 36 + 16 + tw
    x0 = 540 - block / 2
    glyph(d, (x0 + 18, 1723), WHATS, fa36, GREEN)
    tracked(d, (x0 + 52, 1705), label, mb28, GREEN, tracking=2)

    tracked(d, (0, 1764), 'SEU PRÓXIMO IMÓVEL ESTÁ AQUI', msb15, INK_SOFT, tracking=4, center_x=540)

    import os
    os.makedirs('marketing/exports', exist_ok=True)
    rgb = img.convert('RGB')

    # 1) Master Full HD vertical (padrão do Status WhatsApp)
    rgb.save(OUT, 'PNG')

    # 2) Full HD dobrado (2160x3840) — nitidez maxima para zoom/print
    big = rgb.resize((2160, 3840), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=2.0, percent=115, threshold=2))
    big.save('marketing/exports/status-01-fullhd-2x.png', 'PNG')

    # 3) JPG calibrado para postar no status (4:4:4 preserva bordas do texto)
    rgb.save('marketing/exports/status-01-whatsapp.jpg', 'JPEG',
             quality=93, subsampling=0, optimize=True, progressive=True)

    print('gerado:', OUT, rgb.size)
    print('gerado: marketing/exports/status-01-fullhd-2x.png', big.size)
    print('gerado: marketing/exports/status-01-whatsapp.jpg', rgb.size)


if __name__ == '__main__':
    main()

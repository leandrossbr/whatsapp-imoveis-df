#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recriação Full HD da peça LUX Home Boulevard — 1080x1920
========================================================

Reconstrói a arte original (copy e layout) dentro do próprio ambiente, usando
fotos reais do LUX Home Boulevard baixadas em arte/entrada/ (lux-fachada.jpg e
lux-interior.jpg), e aplica a identidade do corretor:

  • LEANDRO SANTOS • (61) 99658-7484 • EM BRASÍLIA  (foto em círculo dourado)
  • selo dourado "APARTAMENTOS A PARTIR DE R$ 679 MIL"
  • CTA "CHAME NO WHATSAPP" + wa.me

Uso:  python3 arte/recriar_lux.py [--foto CAMINHO] [--saida DIR]
Se houver arte/entrada/foto-leandro.*, o rosto entra no círculo; senão sai o
marcador "SUA FOTO" (troca posterior = rodar de novo com --foto).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from gerar_arte import (  # noqa: E402
    badge_whatsapp,
    cover,
    font,
    fonte_ajustada,
    hex2rgb,
    largura_texto,
    recorte_circular,
    texto_espacado,
)
from remixar_arte import _selo_dourado  # noqa: E402

SAIDA = os.path.join(BASE, "saida")

NAVY = hex2rgb("#16386B")
NAVY_ESC = hex2rgb("#0E2547")
GOLD = hex2rgb("#C9A24A")
GOLD_CLARO = hex2rgb("#E8C87E")
BROWN = hex2rgb("#8A6E4E")
BLUE = hex2rgb("#2E5FA3")
WHITE = (255, 255, 255)

LARGURA, ALTURA = 1080, 1920


# --------------------------------------------------------------------------- #
def ceu() -> Image.Image:
    img = Image.new("RGB", (LARGURA, 660), WHITE)
    d = ImageDraw.Draw(img)
    topo, base = hex2rgb("#9CC4E4"), hex2rgb("#E6F0F8")
    for y in range(660):
        t = y / 659
        d.line([(0, y), (LARGURA, y)], fill=tuple(int(topo[k] + (base[k] - topo[k]) * t) for k in range(3)))
    return img


def icone(d: ImageDraw.ImageDraw, tipo: str, cx: int, cy: int, r: int) -> None:
    """Ícones brancos simples sobre o círculo dourado."""
    w = max(3, r // 9)
    if tipo == "casa":
        d.polygon([(cx - r * 0.62, cy), (cx, cy - r * 0.60), (cx + r * 0.62, cy)], fill=WHITE)
        d.rectangle([cx - r * 0.42, cy, cx + r * 0.42, cy + r * 0.52], fill=WHITE)
        d.rectangle([cx - r * 0.10, cy + r * 0.16, cx + r * 0.14, cy + r * 0.52], fill=GOLD)
    elif tipo == "presente":
        d.rectangle([cx - r * 0.50, cy - r * 0.20, cx + r * 0.50, cy + r * 0.52], fill=WHITE)
        d.rectangle([cx - r * 0.58, cy - r * 0.38, cx + r * 0.58, cy - r * 0.16], fill=WHITE)
        d.rectangle([cx - w, cy - r * 0.38, cx + w, cy + r * 0.52], fill=GOLD)
        d.ellipse([cx - r * 0.34, cy - r * 0.62, cx - r * 0.02, cy - r * 0.34], outline=WHITE, width=w)
        d.ellipse([cx + r * 0.02, cy - r * 0.62, cx + r * 0.34, cy - r * 0.34], outline=WHITE, width=w)
    elif tipo == "moedas":
        for i, dy in enumerate((-0.30, 0.0, 0.30)):
            d.ellipse([cx - r * 0.50, cy + dy * r - r * 0.16, cx + r * 0.50, cy + dy * r + r * 0.16], fill=WHITE)
            d.ellipse([cx - r * 0.50, cy + dy * r - r * 0.16, cx + r * 0.50, cy + dy * r + r * 0.16], outline=GOLD, width=2)
    elif tipo == "planta":
        d.rectangle([cx - r * 0.52, cy - r * 0.42, cx + r * 0.52, cy + r * 0.42], outline=WHITE, width=w)
        d.line([(cx - r * 0.10, cy - r * 0.42), (cx - r * 0.10, cy + r * 0.10)], fill=WHITE, width=w)
        d.line([(cx - r * 0.10, cy + r * 0.10), (cx + r * 0.52, cy + r * 0.10)], fill=WHITE, width=w)
    elif tipo == "predio":
        d.rectangle([cx - r * 0.34, cy - r * 0.55, cx + r * 0.34, cy + r * 0.55], fill=WHITE)
        for fy in (-0.38, -0.12, 0.14, 0.40):
            for fx in (-0.18, 0.06):
                d.rectangle([cx + fx * r, cy + fy * r, cx + fx * r + r * 0.14, cy + fy * r + r * 0.14], fill=GOLD)
    elif tipo == "pin":
        d.ellipse([cx - r * 0.34, cy - r * 0.52, cx + r * 0.34, cy + r * 0.16], fill=WHITE)
        d.polygon([(cx - r * 0.30, cy - r * 0.02), (cx + r * 0.30, cy - r * 0.02), (cx, cy + r * 0.55)], fill=WHITE)
        d.ellipse([cx - r * 0.13, cy - r * 0.31, cx + r * 0.13, cy - r * 0.05], fill=GOLD)


def logo_lux(d: ImageDraw.ImageDraw, x: int, y: int) -> None:
    f = font("Montserrat_900Black.ttf", 118)
    texto_espacado(d, (x, y), "LU", f, fill=BROWN, espacamento=0.02)
    larg_lu = largura_texto("LU", f, 0.02)
    # X estilizado: dois traços cruzados (marrom + azul)
    x0 = x + larg_lu + 12
    hh = 108
    for cor, dx in ((BROWN, 0), (BLUE, 26)):
        d.line([(x0 + dx, y + 6), (x0 + dx + 62, y + 6 + hh)], fill=cor, width=20)
        d.line([(x0 + dx + 62, y + 6), (x0 + dx, y + 6 + hh)], fill=cor, width=20)
    f2 = font("Montserrat_600SemiBold.ttf", 30)
    texto_espacado(d, (x + 4, y + 128), "HOME BOULEVARD", f2, fill=BLUE, espacamento=0.34)


def selo_topo(canvas: Image.Image) -> None:
    w, h = 360, 150
    selo = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(selo)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=18, fill=NAVY + (255,), outline=GOLD + (255,), width=4)
    f1 = font("Montserrat_700Bold.ttf", 22)
    f2 = font("Montserrat_900Black.ttf", 44)
    texto_espacado(d, (20 + w / 2, 52), "SEU NOVO APARTAMENTO", f1, fill=WHITE, espacamento=0.06, ancora="mm")
    texto_espacado(d, (20 + w / 2, 108), "TE ESPERA!", f2, fill=GOLD_CLARO, espacamento=0.02, ancora="mm")
    selo = selo.rotate(6, resample=Image.BICUBIC, expand=True)
    canvas.paste(selo, (LARGURA - selo.width - 36, 54), selo)


def foto_fachada(canvas: Image.Image) -> None:
    caminho = os.path.join(BASE, "entrada", "lux-fachada.jpg")
    if not os.path.exists(caminho):
        return
    img = Image.open(caminho).convert("RGB")
    img = ImageEnhance.Sharpness(img).enhance(1.4)
    box_w, box_h = 690, 620
    rec = cover(img, box_w, box_h)
    mascara = Image.new("L", (box_w, box_h), 255)
    dm = ImageDraw.Draw(mascara)
    fade = 150
    for x in range(fade):
        dm.line([(x, 0), (x, box_h)], fill=int(255 * x / fade))
    canvas.paste(rec, (LARGURA - box_w, 24), mascara)


def foto_interior(canvas: Image.Image) -> None:
    caminho = os.path.join(BASE, "entrada", "lux-interior.jpg")
    if not os.path.exists(caminho):
        return
    img = Image.open(caminho).convert("RGB")
    img = img.crop((0, 0, img.width, int(img.height * 0.93)))  # remove marca d'água do canto
    img = ImageEnhance.Sharpness(img).enhance(1.3)
    box_w, box_h = 480, 380
    rec = cover(img, box_w, box_h)
    mascara = Image.new("L", (box_w * 4, box_h * 4), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, box_w * 4, box_h * 4], radius=24 * 4, fill=255)
    mascara = mascara.resize((box_w, box_h), Image.LANCZOS)
    x, y = 560, 700
    sombra = Image.new("L", (box_w + 60, box_h + 60), 0)
    ImageDraw.Draw(sombra).rounded_rectangle([30, 36, 30 + box_w, 36 + box_h], radius=24, fill=120)
    sombra = sombra.filter(ImageFilter.GaussianBlur(14))
    canvas.paste(Image.new("RGB", sombra.size, (30, 40, 60)), (x - 30, y - 30), sombra)
    canvas.paste(rec, (x, y), mascara)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x, y, x + box_w, y + box_h], radius=24, outline=GOLD, width=3)


def bullets(canvas: Image.Image) -> None:
    d = ImageDraw.Draw(canvas)
    dados = [
        ("casa", ["Habite-se", "em breve"], []),
        ("presente", ["ITBI, Escritura e", "Registro GRÁTIS"], [1]),
        ("moedas", ["Plano direto com a", "construtora em até", "180 meses"], []),
        ("planta", ["Apartamentos de", "65 m² a 93 m²"], []),
        ("predio", ["Penthouses de até", "333 m²"], []),
        ("pin", ["Águas Claras —", "localização privilegiada"], []),
    ]
    y = 700
    x_icone, x_txt = 96, 152
    for tipo, linhas, ouro_em in dados:
        alt_bloco = 30 * len(linhas) + 18
        cy = y + alt_bloco // 2
        d.ellipse([x_icone - 33, cy - 33, x_icone + 33, cy + 33], fill=GOLD)
        d.ellipse([x_icone - 38, cy - 38, x_icone + 38, cy + 38], outline=GOLD_CLARO, width=2)
        icone(d, tipo, x_icone, cy, 33)
        yy = y
        for i, linha in enumerate(linhas):
            f = font("Montserrat_700Bold.ttf" if i == 0 else "Montserrat_600SemiBold.ttf", 30 if i == 0 else 27)
            if i in ouro_em:
                partes = linha.split("GRÁTIS")
                xx = x_txt
                for j, parte in enumerate(partes):
                    if parte:
                        wpt = texto_espacado(d, (xx, yy), parte, f, fill=NAVY)[0]
                        xx += wpt
                    if j < len(partes) - 1:
                        wpt = texto_espacado(d, (xx, yy), "GRÁTIS", f, fill=GOLD)[0]
                        xx += wpt
            else:
                texto_espacado(d, (x_txt, yy), linha, f, fill=NAVY)
            yy += 30
        y += alt_bloco + 14


def barra_corretor(canvas: Image.Image, cfg: dict, foto_path: str | None) -> None:
    d = ImageDraw.Draw(canvas)
    y0, y1 = 1330, 1650
    d.rectangle([0, y0, LARGURA, y1], fill=NAVY)
    d.rectangle([0, y0, LARGURA, y0 + 5], fill=GOLD)

    # foto circular
    cx, cy, dia = 185, 1490, 250
    if foto_path and os.path.exists(foto_path):
        foto = Image.open(foto_path).convert("RGBA")
        fy = cfg.get("ajustes", {}).get("foto_foco_vertical", 0.5)
        rec = recorte_circular(foto, dia, fy)
    else:
        rec = Image.new("RGBA", (dia, dia), (0, 0, 0, 0))
        dr = ImageDraw.Draw(rec)
        dr.ellipse((0, 0, dia, dia), fill=NAVY_ESC + (255,))
        fp = font("Montserrat_700Bold.ttf", 34)
        texto_espacado(dr, (dia / 2, dia / 2 - 20), "SUA", fp, fill=GOLD_CLARO, espacamento=0.1, ancora="mm")
        texto_espacado(dr, (dia / 2, dia / 2 + 22), "FOTO", fp, fill=GOLD_CLARO, espacamento=0.1, ancora="mm")
    canvas.paste(rec, (cx - dia // 2, cy - dia // 2), rec)
    d = ImageDraw.Draw(canvas)
    d.ellipse([cx - dia / 2 - 7, cy - dia / 2 - 7, cx + dia / 2 + 7, cy + dia / 2 + 7], outline=GOLD, width=8)
    d.ellipse([cx - dia / 2 - 16, cy - dia / 2 - 16, cx + dia / 2 + 16, cy + dia / 2 + 16], outline=GOLD_CLARO, width=2)

    # faixa dourada
    tx = 340
    d.rounded_rectangle([tx, 1352, 900, 1400], radius=6, fill=GOLD)
    f_faixa = font("Montserrat_700Bold.ttf", 25)
    texto_espacado(d, (tx + 20, 1376), "FALAR DIRETO COM O CORRETOR", f_faixa, fill=NAVY, espacamento=0.08)

    # nome
    corretor = cfg["corretor"]
    f_nome = fonte_ajustada("Montserrat_800ExtraBold.ttf", corretor["nome"], 660, 56, 0.02)
    texto_espacado(d, (tx + 2, 1412), corretor["nome"], f_nome, fill=WHITE, espacamento=0.02)

    # telefone
    f_tel = fonte_ajustada("Montserrat_700Bold.ttf", corretor["telefone_display"], 560, 52, 0.0)
    badge = badge_whatsapp(int(f_tel.size * 1.12))
    canvas.paste(badge, (tx + 2, 1478), badge)
    texto_espacado(d, (tx + 2 + badge.width + 14, 1482), corretor["telefone_display"], f_tel, fill=WHITE)

    # EM BRASÍLIA
    f_cid = font("Montserrat_600SemiBold.ttf", 23)
    cid = "EM BRASÍLIA"
    larg_cid = largura_texto(cid, f_cid, 0.30)
    cxm = tx + 2 + 150
    texto_espacado(d, (cxm, 1552), cid, f_cid, fill=WHITE, espacamento=0.30, ancora="ma")
    ly = 1552 + 12
    d.rectangle([cxm - larg_cid / 2 - 60, ly, cxm - larg_cid / 2 - 16, ly + 3], fill=GOLD)
    d.rectangle([cxm + larg_cid / 2 + 16, ly, cxm + larg_cid / 2 + 60, ly + 3], fill=GOLD)


def rodape(canvas: Image.Image, cfg: dict) -> None:
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 1650, LARGURA, 1730], fill=NAVY_ESC)
    icone(d, "pin", 84, 1690, 26)
    f_loc = font("Montserrat_600SemiBold.ttf", 24)
    texto_espacado(d, (124, 1678), "LUX HOME BOULEVARD   •   ÁGUAS CLARAS   •   BRASÍLIA/DF", f_loc, fill=WHITE, espacamento=0.14)

    d.rectangle([0, 1730, LARGURA, ALTURA], fill=NAVY)
    # CTA
    texto = cfg.get("cta", "CHAME NO WHATSAPP")
    f_cta = font("Montserrat_800ExtraBold.ttf", 32)
    larg = largura_texto(texto, f_cta, 0.12)
    w, h = int(larg + 150), 92
    x0, y0 = (LARGURA - w) // 2, 1762
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h // 2, fill=GOLD)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h // 2, outline=GOLD_CLARO, width=3)
    badge = badge_whatsapp(44)
    canvas.paste(badge, (x0 + 30, y0 + h // 2 - 22), badge)
    texto_espacado(d, (x0 + w / 2 + 34, y0 + h / 2), texto, f_cta, fill=NAVY, espacamento=0.12, ancora="mm")
    f_link = font("Montserrat_600SemiBold.ttf", 27)
    texto_espacado(d, (LARGURA / 2, 1878), cfg["corretor"]["whatsapp_link"].replace("https://", ""), f_link, fill=GOLD_CLARO, espacamento=0.06, ancora="ma")


def gerar(cfg: dict, foto_path: str | None) -> Image.Image:
    canvas = Image.new("RGB", (LARGURA, ALTURA), WHITE)
    canvas.paste(ceu(), (0, 0))
    d = ImageDraw.Draw(canvas)

    foto_fachada(canvas)
    d = ImageDraw.Draw(canvas)
    logo_lux(d, 64, 78)
    selo_topo(canvas)
    d = ImageDraw.Draw(canvas)

    f_h1 = font("Montserrat_900Black.ttf", 62)
    f_h2 = font("Montserrat_700Bold.ttf", 40)
    f_h3 = font("Montserrat_800ExtraBold.ttf", 46)
    texto_espacado(d, (64, 330), "O LUX HOME", f_h1, fill=NAVY)
    texto_espacado(d, (64, 398), "BOULEVARD", f_h1, fill=NAVY)
    texto_espacado(d, (66, 476), "está cada vez mais", f_h2, fill=BROWN)
    texto_espacado(d, (66, 528), "perto da entrega!", f_h3, fill=GOLD)

    # painel branco
    d.rectangle([0, 660, LARGURA, 1330], fill=(255, 255, 255))
    d.rectangle([0, 660, LARGURA, 664], fill=GOLD_CLARO)
    bullets(canvas)
    foto_interior(canvas)

    # selo de preço sobre o canto da foto interna
    _selo_dourado(canvas, 900, 700, 150, cfg["oferta"], NAVY, cfg["cores"])

    barra_corretor(canvas, cfg, foto_path)
    rodape(canvas, cfg)
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(description="Recria a peça LUX em Full HD 1080x1920")
    parser.add_argument("--foto")
    parser.add_argument("--config", default=os.path.join(BASE, "config.json"))
    parser.add_argument("--saida", default=SAIDA)
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)

    foto = args.foto
    if not foto:
        entrada = os.path.join(BASE, "entrada")
        for nome in sorted(os.listdir(entrada)):
            if nome.lower().startswith(("foto", "leandro", "eu")):
                foto = os.path.join(entrada, nome)
                break

    print("=" * 64)
    print("Recriação LUX Home Boulevard — Full HD 1080x1920")
    print("Foto do corretor: %s" % (foto or "(ausente — marcador SUA FOTO)"))
    print("=" * 64)

    canvas = gerar(cfg, foto)
    os.makedirs(args.saida, exist_ok=True)
    for ext, kwargs in (("png", {}), ("jpg", {"quality": 94, "progressive": True, "optimize": True})):
        p = os.path.join(args.saida, f"lux-leandro-santos-1080x1920.{ext}")
        canvas.save(p, **kwargs)
        print("  ✔ %s (%.0f KB)" % (os.path.basename(p), os.path.getsize(p) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())

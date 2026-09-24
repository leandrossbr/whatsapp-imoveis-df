#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remix da arte original (LUX Home Boulevard) — troca o corretor e adiciona a oferta
=================================================================================

Mantém a imagem original (prédio, planta, bullets, logos) e:
  1. corta a barra de status do celular / faixas fora da arte;
  2. estende o céu (topo) e o rodapé navy para fechar 1080x1920 (Full HD vertical);
  3. APAGA a foto circular, o nome e o telefone do corretor antigo
     (preenchendo com o navy/ouro amostrados da própria arte);
  4. desenha no lugar: foto do Leandro em círculo com anel dourado,
     "LEANDRO SANTOS", "(61) 99658-7484" com ícone WhatsApp e "EM BRASÍLIA";
  5. aplica o selo dourado "APARTAMENTOS A PARTIR DE R$ 679 MIL".

Uso:
    python3 arte/remixar_arte.py \
        --original arte/entrada/arte-original-lux.jpg \
        --foto     arte/entrada/foto-leandro.png

Todas as regiões ficam em arte/config.json → "remix" (valores normalizados 0–1).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageStat

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from gerar_arte import (  # noqa: E402
    BASE as ARTE_BASE,
    badge_whatsapp,
    font,
    hex2rgb,
    recorte_circular,
    texto_espacado,
    largura_texto,
    fonte_ajustada,
)

SAIDA = os.path.join(BASE, "saida")
CONFIG = os.path.join(BASE, "config.json")


def _patch_mediano(img: Image.Image, caixa: tuple[int, int, int, int]):
    """Cor mediana de um trecho da imagem (para remendos invisíveis)."""
    regiao = img.crop(caixa).convert("RGB")
    return tuple(int(c) for c in ImageStat.Stat(regiao).median)


def remixar(original_path: str, foto_path: str | None, cfg: dict, saida_dir: str) -> list[str]:
    rem = cfg["remix"]
    cores = cfg["cores"]
    original = Image.open(original_path).convert("RGB")
    W, H = original.size

    # 1) recorte da área útil da arte (remove status bar / faixas)
    rx0, ry0, rx1, ry1 = rem["recorte_arte"]
    arte = original.crop((int(rx0 * W), int(ry0 * H), int(rx1 * W), int(ry1 * H)))
    aw, ah = arte.size

    # 2) Full HD vertical: encaixa pela largura e estende topo/base
    largura, altura = 1080, 1920
    escala = largura / aw
    nova_h = int(round(ah * escala))
    arte = arte.resize((largura, nova_h), Image.LANCZOS)
    sobra = altura - nova_h
    topo_h = rem.get("extensao_topo", 0.5) * sobra
    topo_h = int(round(topo_h))
    base_h = sobra - topo_h

    canvas = Image.new("RGB", (largura, altura), _patch_mediano(arte, (0, 0, largura, 4)))
    # topo: estica as primeiras linhas (céu)
    if topo_h > 0:
        faixa = arte.crop((0, 0, largura, max(4, int(topo_h * 0.06)))).resize((largura, topo_h), Image.LANCZOS)
        canvas.paste(faixa, (0, 0))
    canvas.paste(arte, (0, topo_h))
    if base_h > 0:
        faixa = arte.crop((0, nova_h - 6, largura, nova_h)).resize((largura, base_h), Image.LANCZOS)
        canvas.paste(faixa, (0, topo_h + nova_h))

    # coordenadas da arte -> canvas
    def px(x_norm: float, y_norm: float) -> tuple[int, int]:
        return int(x_norm * aw * escala), int(topo_h + y_norm * ah * escala)

    def pm(v_norm: float) -> int:  # medida (largura/raio)
        return int(v_norm * aw * escala)

    # suaviza as emendas das extensões topo/base
    for emenda in (topo_h, topo_h + nova_h):
        faixa_h = 28
        y_a = max(0, emenda - faixa_h // 2)
        tira = canvas.crop((0, y_a, largura, y_a + faixa_h)).filter(ImageFilter.GaussianBlur(5))
        mascara = Image.new("L", (largura, faixa_h), 0)
        dm = ImageDraw.Draw(mascara)
        for i in range(faixa_h):
            peso = 1.0 - abs(i - faixa_h / 2) / (faixa_h / 2)
            dm.line([(0, i), (largura, i)], fill=int(255 * peso))
        canvas.paste(tira, (0, y_a), mascara)

    # 3) remendos: foto antiga e texto antigo
    navy = _patch_mediano(canvas, (*px(*rem["amostra_navy"][:2]), *px(*rem["amostra_navy"][2:])) )
    ouro = _patch_mediano(canvas, (*px(*rem["amostra_ouro"][:2]), *px(*rem["amostra_ouro"][2:])))

    zf = rem["zona_foto_antiga"]
    x0, y0 = px(zf[0], zf[1])
    x1, y1 = px(zf[0] + zf[2], zf[1] + zf[3])
    d = ImageDraw.Draw(canvas)
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], fill=navy)

    zt = rem["zona_texto_antigo"]
    tx0, ty0 = px(zt[0], zt[1])
    tx1, ty1 = px(zt[0] + zt[2], zt[1] + zt[3])
    d.rectangle([tx0, ty0, tx1, ty1], fill=navy)

    # 4) novo bloco do corretor ------------------------------------------------
    foto = Image.open(foto_path).convert("RGBA") if foto_path and os.path.exists(foto_path) else None
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    diametro = min(x1 - x0, y1 - y0)
    if foto:
        fy = cfg.get("ajustes", {}).get("foto_foco_vertical", 0.5)
        rec = recorte_circular(foto, diametro, fy)
    else:
        rec = Image.new("RGBA", (diametro, diametro), (0, 0, 0, 0))
        dr = ImageDraw.Draw(rec)
        dr.ellipse((0, 0, diametro, diametro), fill=navy)
        fp = font("Montserrat_700Bold.ttf", diametro // 6)
        texto_espacado(dr, (diametro / 2, diametro / 2), "SUA FOTO", fp, fill=ouro, ancora="mm", espacamento=0.08)
    canvas.paste(rec, (cx - diametro // 2, cy - diametro // 2), rec)
    d = ImageDraw.Draw(canvas)
    d.ellipse(
        [cx - diametro / 2 - 6, cy - diametro / 2 - 6, cx + diametro / 2 + 6, cy + diametro / 2 + 6],
        outline=ouro, width=7,
    )
    d.ellipse(
        [cx - diametro / 2 - 14, cy - diametro / 2 - 14, cx + diametro / 2 + 14, cy + diametro / 2 + 14],
        outline=ouro, width=2,
    )

    # bloco de texto
    bx = tx0 + pm(0.012)
    bloco_w = tx1 - tx0
    corretor = cfg["corretor"]

    # faixa dourada
    alt_faixa = pm(rem["alturas"]["faixa"])
    d.rounded_rectangle([tx0, ty0, tx1, ty0 + alt_faixa], radius=4, fill=ouro)
    f_faixa = font("Montserrat_700Bold.ttf", int(alt_faixa * 0.52))
    texto_espacado(
        d, (tx0 + bloco_w / 2, ty0 + alt_faixa / 2), rem["texto_faixa"], f_faixa,
        fill=navy, espacamento=0.10, ancora="mm",
    )

    # nome
    y_cursor = ty0 + alt_faixa + pm(0.008)
    f_nome = fonte_ajustada("Montserrat_800ExtraBold.ttf", corretor["nome"], bloco_w - pm(0.02), pm(rem["alturas"]["nome"]), 0.02)
    texto_espacado(d, (bx, y_cursor), corretor["nome"], f_nome, fill=(255, 255, 255), espacamento=0.02)
    y_cursor += int(f_nome.size * 0.98)

    # telefone + ícone
    f_tel = fonte_ajustada("Montserrat_700Bold.ttf", corretor["telefone_display"], bloco_w - pm(0.075), pm(rem["alturas"]["telefone"]), 0.0)
    badge = badge_whatsapp(int(f_tel.size * 1.12))
    canvas.paste(badge, (bx, y_cursor), badge)
    texto_espacado(d, (bx + badge.width + pm(0.012), y_cursor), corretor["telefone_display"], f_tel, fill=(255, 255, 255))
    y_cursor += int(f_tel.size * 1.02)

    # "EM BRASÍLIA"
    f_cidade = font("Montserrat_600SemiBold.ttf", pm(rem["alturas"]["cidade"]))
    cidade = rem.get("texto_cidade", "EM BRASÍLIA")
    larg_cidade = largura_texto(cidade, f_cidade, 0.30)
    cxm = tx0 + bloco_w / 2
    texto_espacado(d, (cxm, y_cursor + pm(0.004)), cidade, f_cidade, fill=(255, 255, 255), espacamento=0.30, ancora="ma")
    linha_y = y_cursor + pm(0.004) + int(f_cidade.size * 0.45)
    d.rectangle([cxm - larg_cidade / 2 - pm(0.05), linha_y, cxm - larg_cidade / 2 - pm(0.012), linha_y + 2], fill=ouro)
    d.rectangle([cxm + larg_cidade / 2 + pm(0.012), linha_y, cxm + larg_cidade / 2 + pm(0.05), linha_y + 2], fill=ouro)

    # 5) selo de preço ---------------------------------------------------------
    selo = rem["selo_preco"]
    scx, scy = px(*selo["centro"])
    raio = pm(selo["raio"])
    _selo_dourado(canvas, scx, scy, raio, cfg["oferta"], navy, cores)

    os.makedirs(saida_dir, exist_ok=True)
    gerados = []
    for ext, kwargs in (("png", {}), ("jpg", {"quality": 94, "progressive": True, "optimize": True})):
        caminho = os.path.join(saida_dir, f"lux-leandro-santos-1080x1920.{ext}")
        canvas.save(caminho, **kwargs)
        gerados.append(caminho)
        print("  ✔ %s (%.0f KB)" % (os.path.basename(caminho), os.path.getsize(caminho) / 1024))
    return gerados


def _selo_dourado(canvas: Image.Image, cx: int, cy: int, raio: int, oferta: dict, navy, cores) -> None:
    """Selo circular dourado com a oferta, levemente rotacionado."""
    tam = raio * 2 + 80
    selo = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(selo)
    c = tam // 2
    # estrela/serrilha
    import math

    pontos = []
    dentes = 28
    for i in range(dentes * 2):
        ang = math.pi * i / dentes
        r = raio + (10 if i % 2 == 0 else 2)
        pontos.append((c + r * math.cos(ang), c + r * math.sin(ang)))
    d.polygon(pontos, fill=hex2rgb("#D4AF37"))
    d.ellipse([c - raio, c - raio, c + raio, c + raio], fill=hex2rgb("#F2D271"))
    d.ellipse([c - raio + 8, c - raio + 8, c + raio - 8, c + raio - 8], outline=navy + (255,), width=3)

    f1 = fonte_ajustada("Montserrat_800ExtraBold.ttf", oferta["produto"], int(raio * 1.62), int(raio * 0.185), 0.06)
    f2 = font("Montserrat_600SemiBold.ttf", int(raio * 0.140))
    f3 = fonte_ajustada("Montserrat_900Black.ttf", oferta["valor"], int(raio * 1.50), int(raio * 0.30), 0.0)
    texto_espacado(d, (c, c - raio * 0.42), oferta["produto"], f1, fill=navy + (255,), espacamento=0.06, ancora="mm")
    texto_espacado(d, (c, c - raio * 0.16), oferta["chamada"], f2, fill=navy + (255,), espacamento=0.22, ancora="mm")
    texto_espacado(d, (c, c + raio * 0.22), oferta["valor"], f3, fill=navy + (255,), espacamento=0.0, ancora="mm")

    selo = selo.rotate(-8, resample=Image.BICUBIC, expand=True)
    # sombra suave
    mascara_sombra = Image.new("L", selo.size, 0)
    mascara_sombra.paste(selo.split()[3], (6, 8))
    mascara_sombra = mascara_sombra.filter(ImageFilter.GaussianBlur(10)).point(lambda p: int(p * 0.45))
    canvas.paste(Image.new("RGB", selo.size, (0, 0, 0)), (cx - selo.width // 2, cy - selo.height // 2), mascara_sombra)
    canvas.paste(selo, (cx - selo.width // 2, cy - selo.height // 2), selo)


def main() -> int:
    parser = argparse.ArgumentParser(description="Remix da arte original com a identidade do Leandro Santos")
    parser.add_argument("--original")
    parser.add_argument("--foto")
    parser.add_argument("--config", default=CONFIG)
    parser.add_argument("--saida", default=SAIDA)
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)

    original = args.original or os.path.join(BASE, "entrada", "arte-original-lux.jpg")
    foto = args.foto or os.path.join(BASE, "entrada", "foto-leandro.png")
    if not os.path.exists(original):
        for nome in sorted(os.listdir(os.path.join(BASE, "entrada"))):
            if nome.lower().startswith(("arte", "lux", "original")):
                original = os.path.join(BASE, "entrada", nome)
                break
    if not os.path.exists(foto):
        for nome in sorted(os.listdir(os.path.join(BASE, "entrada"))):
            if nome.lower().startswith(("foto", "leandro", "eu")):
                foto = os.path.join(BASE, "entrada", nome)
                break

    print("=" * 64)
    print("Remix arte original → Full HD 1080x1920")
    print("Original: %s" % (original if os.path.exists(original) else "(ausente)"))
    print("Foto:     %s" % (foto if os.path.exists(foto) else "(ausente — placeholder SUA FOTO)"))
    print("=" * 64)
    if not os.path.exists(original):
        print("ERRO: informe --original com a arte antiga.")
        return 1
    remixar(original, foto if os.path.exists(foto) else None, cfg, args.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())

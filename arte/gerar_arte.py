#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de arte Full HD para WhatsApp — Leandro Santos / Imóveis DF
===================================================================

Monta a arte de divulgação (paisagem 1920x1080 e vertical 1080x1920) usando:
  • a IMAGEM DO IMÓVEL como fundo (mantida, sem cortes de conteúdo);
  • a FOTO DO CORRETOR em recorte circular com anel dourado;
  • nome, WhatsApp e a oferta "APARTAMENTOS A PARTIR DE R$ 679 MIL".

Também consegue APAGAR o nome/telefone do corretor antigo que já estavam
gravados na arte original: basta informar os retângulos em "zonas_ocultar"
no config.json (valores de 0 a 1, proporcionais à imagem original).

Uso
---
    python3 arte/gerar_arte.py \
        --fundo arte/entrada/arte-original.jpg \
        --foto  arte/entrada/foto-leandro.jpg

Sem --foto a arte sai com um círculo marcado "SUA FOTO" (prévia de layout).
Sem --fundo é usado um fundo de demonstração gerado pelo script.

Dependências: Pillow (`pip install pillow`). As fontes ficam em arte/fonts/.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
FONTS_DIR = os.path.join(BASE, "fonts")
ENTRADA = os.path.join(BASE, "entrada")
SAIDA = os.path.join(BASE, "saida")

FORMATOS = {
    "paisagem": (1920, 1080),   # Full HD — envio em conversa / lista de transmissão
    "vertical": (1080, 1920),   # Full HD vertical — Status / Stories
    "quadrado": (1080, 1080),   # feed Instagram / foto de perfil (extra)
}

# Fontes usadas + de onde baixar (npm registry) caso não existam localmente.
FONTES = {
    "Montserrat_600SemiBold.ttf": "https://registry.npmjs.org/@expo-google-fonts/montserrat/-/montserrat-0.4.2.tgz",
    "Montserrat_700Bold.ttf": "https://registry.npmjs.org/@expo-google-fonts/montserrat/-/montserrat-0.4.2.tgz",
    "Montserrat_800ExtraBold.ttf": "https://registry.npmjs.org/@expo-google-fonts/montserrat/-/montserrat-0.4.2.tgz",
    "Montserrat_900Black.ttf": "https://registry.npmjs.org/@expo-google-fonts/montserrat/-/montserrat-0.4.2.tgz",
    "BebasNeue_400Regular.ttf": "https://registry.npmjs.org/@expo-google-fonts/bebas-neue/-/bebas-neue-0.4.1.tgz",
    "Poppins_600SemiBold.ttf": "https://registry.npmjs.org/@expo-google-fonts/poppins/-/poppins-0.4.1.tgz",
}

FALLBACK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def hex2rgb(valor: str, alpha: int | None = None):
    valor = valor.lstrip("#")
    rgb = tuple(int(valor[i : i + 2], 16) for i in (0, 2, 4))
    return rgb + ((alpha,) if alpha is not None else ())  # type: ignore[return-value]


def font(nome: str, tamanho: int) -> ImageFont.FreeTypeFont:
    """Carrega fonte local (baixa se preciso); cai para DejaVu em último caso."""
    caminho = os.path.join(FONTS_DIR, nome)
    if not os.path.exists(caminho):
        _baixar_fonte(nome)
    try:
        return ImageFont.truetype(caminho, int(tamanho))
    except Exception:
        return ImageFont.truetype(FALLBACK_FONT, int(tamanho))


def _baixar_fonte(nome: str) -> None:
    url = FONTES.get(nome)
    if not url:
        return
    try:
        import io
        import tarfile

        print(f"  ↓ baixando fonte {nome} ...")
        os.makedirs(FONTS_DIR, exist_ok=True)
        dados = urllib.request.urlopen(url, timeout=60).read()
        with tarfile.open(fileobj=io.BytesIO(dados), mode="r:gz") as tar:
            for membro in tar.getmembers():
                if membro.name.endswith("/" + nome) or os.path.basename(membro.name) == nome:
                    arquivo = tar.extractfile(membro)
                    if arquivo:
                        with open(os.path.join(FONTS_DIR, nome), "wb") as destino:
                            destino.write(arquivo.read())
                    return
    except Exception as erro:  # sem internet -> fallback silencioso
        print(f"  ! não foi possível baixar {nome}: {erro}")


def _ancora(x: float, y: float, largura: float, altura: float, ancora: str) -> tuple[float, float]:
    """ancora = 2 letras: horizontal (l=esq, m=centro, r=dir) + vertical (a=topo, m=meio, s=base)."""
    h = ancora[0] if ancora else "l"
    v = ancora[1] if len(ancora) > 1 else "a"
    if h == "m":
        x -= largura / 2
    elif h == "r":
        x -= largura
    if v == "m":
        y -= altura / 2
    elif v == "s":
        y -= altura
    return x, y


def texto_espacado(
    desenho: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    texto: str,
    fonte: ImageFont.FreeTypeFont,
    fill,
    espacamento: float = 0.0,
    ancora: str = "la",
    stroke: int = 0,
    stroke_fill=None,
) -> tuple[int, int]:
    """Desenha texto com espaçamento entre letras (tracking). Retorna (largura, altura)."""
    extra = int(fonte.size * espacamento)
    larguras = []
    for letra in texto:
        bbox = fonte.getbbox(letra, stroke_width=stroke)
        larguras.append(bbox[2] - bbox[0])
    largura_total = sum(larguras) + extra * max(len(texto) - 1, 0)
    caixa = fonte.getbbox(texto)
    altura = caixa[3] - caixa[1]

    x, y = _ancora(xy[0], xy[1], largura_total, altura, ancora)
    y -= caixa[1]  # compensa o "bearing" topo da fonte

    cursor = x
    for letra, larg in zip(texto, larguras):
        desenho.text(
            (cursor, y),
            letra,
            font=fonte,
            fill=fill,
            stroke_width=stroke,
            stroke_fill=stroke_fill,
        )
        cursor += larg + extra
    return int(largura_total), int(altura)


def largura_texto(texto: str, fonte: ImageFont.FreeTypeFont, espacamento: float = 0.0) -> int:
    extra = int(fonte.size * espacamento)
    total = sum(fonte.getbbox(l)[2] - fonte.getbbox(l)[0] for l in texto)
    return total + extra * max(len(texto) - 1, 0)


def fonte_ajustada(
    nome: str, texto: str, largura_max: int, tamanho_ini: float, espacamento: float = 0.0, minimo: float = 12
) -> ImageFont.FreeTypeFont:
    """Reduz o corpo até o texto caber na largura disponível."""
    tamanho = tamanho_ini
    while tamanho > minimo:
        f = font(nome, tamanho)
        if largura_texto(texto, f, espacamento) <= largura_max:
            return f
        tamanho -= 1
    return font(nome, minimo)


def texto_gradiente(
    canvas: Image.Image,
    xy: tuple[float, float],
    texto: str,
    fonte: ImageFont.FreeTypeFont,
    cor_topo: str,
    cor_base: str,
    espacamento: float = 0.0,
    ancora: str = "la",
    sombra: tuple[int, int] = (0, 6),
    stroke: int = 0,
    stroke_fill=None,
) -> tuple[int, int]:
    """Texto preenchido com degradê vertical (efeito dourado)."""
    larg = largura_texto(texto, fonte, espacamento)
    alt = fonte.getbbox(texto)[3] - fonte.getbbox(texto)[1]
    pad = 20
    camada = Image.new("RGBA", (larg + pad * 2, alt + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)

    # degradê
    grad = Image.new("RGB", (1, camada.height))
    topo, base = hex2rgb(cor_topo), hex2rgb(cor_base)
    for i in range(camada.height):
        t = i / max(camada.height - 1, 1)
        grad.putpixel((0, i), tuple(int(topo[k] + (base[k] - topo[k]) * t) for k in range(3)))
    grad = grad.resize(camada.size)

    # máscara do texto
    mascara = Image.new("L", camada.size, 0)
    dm = ImageDraw.Draw(mascara)
    texto_espacado(dm, (pad, pad), texto, fonte, fill=255, espacamento=espacamento, stroke=stroke, stroke_fill=255)

    if stroke and stroke_fill:
        texto_espacado(d, (pad, pad), texto, fonte, fill=stroke_fill, espacamento=espacamento, stroke=0)

    grad.putalpha(mascara)
    camada = Image.alpha_composite(camada, grad)

    caixa = fonte.getbbox(texto)
    x, y = _ancora(xy[0], xy[1], larg, alt, ancora)
    y -= caixa[1]

    if sombra:
        sombra_layer = Image.new("RGBA", camada.size, (0, 0, 0, 0))
        ds = ImageDraw.Draw(sombra_layer)
        texto_espacado(ds, (pad, pad), texto, fonte, fill=(0, 0, 0, 120), espacamento=espacamento)
        sombra_layer = sombra_layer.filter(ImageFilter.GaussianBlur(14))
        canvas.paste(
            sombra_layer,
            (int(x - pad + sombra[0]), int(y - pad + sombra[1])),
            sombra_layer,
        )

    canvas.paste(camada, (int(x - pad), int(y - pad)), camada)
    return int(larg), int(alt)


def cover(img: Image.Image, largura: int, altura: int, fx: float = 0.5, fy: float = 0.5) -> Image.Image:
    """Redimensiona preenchendo o quadro todo (sem distorcer). fx/fy = foco do corte (0–1)."""
    proporcao = max(largura / img.width, altura / img.height)
    nova = img.resize((max(int(img.width * proporcao), 1), max(int(img.height * proporcao), 1)), Image.LANCZOS)
    esquerda = int((nova.width - largura) * min(max(fx, 0.0), 1.0))
    topo = int((nova.height - altura) * min(max(fy, 0.0), 1.0))
    return nova.crop((esquerda, topo, esquerda + largura, topo + altura)).convert("RGBA")


def fundo_demo(largura: int, altura: int) -> Image.Image:
    """Fundo de demonstração (quando não há imagem do imóvel)."""
    img = Image.new("RGB", (largura, altura), hex2rgb("#0B3D2E"))
    d = ImageDraw.Draw(img)
    for i in range(altura):
        t = i / altura
        cor = tuple(int(11 + (4 - 11) * t) for _ in range(1))
        d.line([(0, i), (largura, i)], fill=(int(14 - 8 * t), int(70 - 40 * t), int(52 - 30 * t)))
    # silhueta de prédios
    for k in range(9):
        x = int(largura * (k / 9))
        w = int(largura * 0.11)
        h = int(altura * (0.30 + 0.22 * ((k * 37) % 7) / 7))
        d.rectangle([x, altura - h, x + w, altura], fill=(6, 32, 24))
        for j in range(6):
            for i in range(10):
                if (i * 7 + j * 3 + k) % 3 == 0:
                    d.rectangle(
                        [x + 8 + j * (w - 16) // 6, altura - h + 14 + i * (h - 20) // 10,
                         x + 8 + j * (w - 16) // 6 + (w - 16) // 9, altura - h + 14 + i * (h - 20) // 10 + (h - 20) // 16],
                        fill=(246, 220, 138),
                    )
    return img.convert("RGBA")


def recorte_circular(foto: Image.Image, diametro: int, fy: float = 0.5) -> Image.Image:
    """Recorte redondo da foto do corretor (fy desloca o foco p/ manter o rosto)."""
    imagem = cover(foto, diametro, diametro, 0.5, fy).convert("RGBA")
    imagem = ImageEnhance.Contrast(imagem.convert("RGB")).enhance(1.04).convert("RGBA")
    imagem = ImageEnhance.Color(imagem).enhance(1.06)
    mascara = Image.new("L", (diametro * 4, diametro * 4), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, diametro * 4, diametro * 4), fill=255)
    mascara = mascara.resize((diametro, diametro), Image.LANCZOS)
    saida = Image.new("RGBA", (diametro, diametro), (0, 0, 0, 0))
    saida.paste(imagem, (0, 0), mascara)
    return saida


def badge_whatsapp(tamanho: int) -> Image.Image:
    """Ícone do WhatsApp (círculo verde + telefone branco) desenhado vetorialmente."""
    s = tamanho * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, s, s), fill=hex2rgb("#25D366"))

    # telefone (handset) clássico: barra curva + pontas arredondadas, girada 45°
    fone = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    df = ImageDraw.Draw(fone)
    cx = cy = s / 2
    raio = s * 0.20
    esp = s * 0.16
    caixa_arco = [cx - raio - esp / 2, cy - raio - esp / 2, cx + raio + esp / 2, cy + raio + esp / 2]
    # arco diagonal (orelha no alto-esq. -> boca embaixo-dir.), concavidade p/ baixo-esq.
    df.arc(caixa_arco, start=250, end=390, fill=(255, 255, 255, 255), width=int(esp))
    for angulo in (250, 390):
        t = math.radians(angulo)
        px = cx + raio * math.cos(t)
        py = cy + raio * math.sin(t)
        ponteira = esp * 0.95
        df.ellipse([px - ponteira, py - ponteira, px + ponteira, py + ponteira], fill=(255, 255, 255, 255))
    img.alpha_composite(fone)
    return img.resize((tamanho, tamanho), Image.LANCZOS)


def pincel_ouro(canvas: Image.Image, caixa: tuple[int, int, int, int], espessura: int = 6) -> None:
    """Linha dourada decorativa."""
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(caixa, radius=espessura, fill=hex2rgb("#D4AF37"))


# --------------------------------------------------------------------------- #
# Arte
# --------------------------------------------------------------------------- #
class Arte:
    def __init__(self, config: dict, fundo_path: str | None, foto_path: str | None):
        self.cfg = config
        self.fundo_path = fundo_path
        self.foto_path = foto_path
        self.cores = config["cores"]
        self.foto = Image.open(foto_path).convert("RGBA") if foto_path and os.path.exists(foto_path) else None

    # -- fundo ------------------------------------------------------------- #
    def preparar_fundo(self, largura: int, altura: int) -> Image.Image:
        if self.fundo_path and os.path.exists(self.fundo_path):
            original = Image.open(self.fundo_path).convert("RGBA")
            # apaga nome/telefone do corretor antigo, se configurado
            zonas = self.cfg.get("zonas_ocultar") or []
            if zonas:
                d = ImageDraw.Draw(original)
                for zona in zonas:
                    zx = int(zona[0] * original.width)
                    zy = int(zona[1] * original.height)
                    zw = int(zona[2] * original.width)
                    zh = int(zona[3] * original.height)
                    regiao = original.crop((zx, zy, zx + zw, zy + zh))
                    regiao = regiao.filter(ImageFilter.GaussianBlur(radius=max(30, zw // 12)))
                    regiao = ImageEnhance.Brightness(regiao.convert("RGB")).enhance(0.55).convert("RGBA")
                    original.paste(regiao, (zx, zy), regiao)
                    d.rectangle([zx, zy, zx + zw, zy + zh], outline=hex2rgb("#D4AF37", 120), width=2)
            canvas = cover(original, largura, altura)
        else:
            canvas = fundo_demo(largura, altura)

        # leve tratamento para dar "cara de anúncio"
        rgb = canvas.convert("RGB")
        rgb = ImageEnhance.Color(rgb).enhance(1.10)
        rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
        if self.cfg.get("ajustes", {}).get("nitidez_extra", True):
            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=3))
        canvas = rgb.convert("RGBA")

        # escurecimento geral + scrim (garante leitura do texto)
        esc = self.cfg.get("ajustes", {}).get("escurecer_fundo", 0.32)
        if esc:
            preto = Image.new("RGBA", canvas.size, (0, 0, 0, int(255 * esc)))
            canvas = Image.alpha_composite(canvas, preto)

        scrim = Image.new("L", (1, altura), 0)
        for y in range(altura):
            t = y / (altura - 1)
            topo_a = self.cores.get("scrim_topo", 110)
            base_a = self.cores.get("scrim_base", 215)
            if t < 0.30:
                alpha = int(topo_a * (1 - t / 0.30))          # escurece o topo
            else:
                alpha = int(base_a * ((t - 0.30) / 0.70) ** 1.25)  # escurece a base
            scrim.putpixel((0, y), alpha)
        scrim = scrim.resize((largura, altura))
        camada = Image.new("RGBA", (largura, altura), hex2rgb(self.cores["verde_escuro"]))
        camada.putalpha(scrim)
        canvas = Image.alpha_composite(canvas, camada)

        # vinheta
        vinheta = Image.new("L", (largura, altura), 0)
        dv = ImageDraw.Draw(vinheta)
        dv.ellipse(
            [-largura * 0.25, -altura * 0.35, largura * 1.25, altura * 1.35],
            fill=90,
        )
        vinheta = vinheta.filter(ImageFilter.GaussianBlur(radius=160))
        camada_v = Image.new("RGBA", (largura, altura), (0, 0, 0, 255))
        camada_v.putalpha(vinheta.point(lambda p: int(p * 0.55)))
        return Image.alpha_composite(canvas, camada_v)

    # -- peças ------------------------------------------------------------- #
    def painel_inferior(self, canvas: Image.Image, altura_painel: int) -> int:
        """Barra inferior verde com filete dourado. Retorna o Y do topo do painel."""
        largura, altura = canvas.size
        topo = altura - altura_painel
        painel = Image.new("RGBA", (largura, altura_painel), (0, 0, 0, 0))
        d = ImageDraw.Draw(painel)
        grad = Image.new("L", (1, altura_painel))
        for i in range(altura_painel):
            t = i / max(altura_painel - 1, 1)
            grad.putpixel((0, i), int(238 + 17 * t))
        grad = grad.resize((largura, altura_painel))
        base = Image.new("RGBA", (largura, altura_painel), hex2rgb(self.cores["verde_escuro"]))
        base.putalpha(grad)
        painel = Image.alpha_composite(painel, base)
        d = ImageDraw.Draw(painel)
        d.rectangle([0, 0, largura, 5], fill=hex2rgb(self.cores["dourado"]))
        d.rectangle([0, 5, largura, 7], fill=hex2rgb(self.cores["dourado_claro"], 160))
        canvas.alpha_composite(painel, (0, topo))
        return topo

    def foto_corretor(self, canvas: Image.Image, centro: tuple[int, int], diametro: int) -> None:
        x, y = centro
        u = diametro / 200
        # sombra
        sombra = Image.new("RGBA", (int(diametro * 1.5), int(diametro * 1.5)), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sombra)
        ds.ellipse(
            (sombra.width * 0.25, sombra.height * 0.27, sombra.width * 0.75, sombra.height * 0.77),
            fill=(0, 0, 0, 150),
        )
        sombra = sombra.filter(ImageFilter.GaussianBlur(radius=int(14 * u)))
        canvas.alpha_composite(
            sombra, (int(x - sombra.width / 2), int(y - sombra.height / 2 + 8 * u))
        )

        if self.foto:
            fy = self.cfg.get("ajustes", {}).get("foto_foco_vertical", 0.5)
            recorte = recorte_circular(self.foto, diametro, fy)
        else:
            recorte = Image.new("RGBA", (diametro, diametro), (0, 0, 0, 0))
            dr = ImageDraw.Draw(recorte)
            dr.ellipse((0, 0, diametro, diametro), fill=hex2rgb("#0E4A37"))
            fp = font("Montserrat_700Bold.ttf", int(diametro * 0.17))
            texto_espacado(
                dr, (diametro / 2, diametro / 2 - diametro * 0.08), "SUA", fp,
                fill=hex2rgb(self.cores["dourado_claro"]), espacamento=0.08, ancora="mm",
            )
            texto_espacado(
                dr, (diametro / 2, diametro / 2 + diametro * 0.12), "FOTO", fp,
                fill=hex2rgb(self.cores["dourado_claro"]), espacamento=0.08, ancora="mm",
            )
        canvas.alpha_composite(recorte, (int(x - diametro / 2), int(y - diametro / 2)))

        # anéis
        d = ImageDraw.Draw(canvas)
        for raio, cor, esp in (
            (diametro / 2 + 6 * u, self.cores["dourado"], int(7 * u)),
            (diametro / 2 + 15 * u, self.cores["dourado_claro"], int(2 * u)),
        ):
            d.ellipse(
                [x - raio, y - raio, x + raio, y + raio],
                outline=hex2rgb(cor),
                width=max(1, esp),
            )

    def topo(self, canvas: Image.Image, u: float, margem: int) -> None:
        """Marca no canto superior + selo da oferta."""
        d = ImageDraw.Draw(canvas)
        marca = self.cfg["marca"]["nome"]
        f_marca = font("Montserrat_800ExtraBold.ttf", int(30 * u))
        texto_espacado(
            d, (margem, int(46 * u)), marca, f_marca,
            fill=hex2rgb(self.cores["branco"]), espacamento=0.22, stroke=0,
        )
        larg_marca = largura_texto(marca, f_marca, 0.22)
        f_tag = font("Montserrat_600SemiBold.ttf", int(17 * u))
        texto_espacado(
            d, (margem + 2, int(46 * u) + int(42 * u)), self.cfg["marca"]["tagline"], f_tag,
            fill=hex2rgb(self.cores["dourado_claro"]), espacamento=0.34,
        )
        pincel_ouro(canvas, (margem, int(38 * u), margem + int(56 * u), int(38 * u) + int(5 * u)), espessura=int(5 * u))

        # selo direito
        selo = self.cfg["oferta"]["selo"]
        f_selo = font("Montserrat_700Bold.ttf", int(19 * u))
        larg_selo = largura_texto(selo, f_selo, 0.18)
        alt_pill = int(48 * u)
        pill_w = int(larg_selo + 46 * u)
        x0 = canvas.width - margem - pill_w
        y0 = int(40 * u)
        d.rounded_rectangle(
            [x0, y0, x0 + pill_w, y0 + alt_pill],
            radius=alt_pill // 2,
            outline=hex2rgb(self.cores["dourado"]),
            width=int(2.5 * u),
            fill=hex2rgb(self.cores["verde_escuro"], 150),
        )
        texto_espacado(
            d, (x0 + pill_w / 2, y0 + alt_pill / 2), selo, f_selo,
            fill=hex2rgb(self.cores["dourado_claro"]), espacamento=0.18, ancora="mm",
        )

    def chamada(
        self,
        canvas: Image.Image,
        u: float,
        caixa: tuple[int, int, int, int],
        centro_x: bool = False,
    ) -> int:
        """Bloco APARTAMENTOS / A PARTIR DE / R$ 679 MIL, centrado na caixa (x, y, larg, alt)."""
        oferta = self.cfg["oferta"]
        x, y0, largura_disp, caixa_alt = caixa
        d = ImageDraw.Draw(canvas)
        ancora = "ma" if centro_x else "la"
        cx = x + largura_disp / 2 if centro_x else x

        f_prod = fonte_ajustada("Montserrat_800ExtraBold.ttf", oferta["produto"], largura_disp, int(74 * u), 0.10)
        f_cham = font("Montserrat_600SemiBold.ttf", int(34 * u))
        f_valor = fonte_ajustada("Montserrat_900Black.ttf", oferta["valor"], largura_disp, int(185 * u), 0.01, minimo=60)

        gap1, gap2 = int(14 * u), int(10 * u)
        alt_prod = int(f_prod.size * 0.80)
        alt_cham = int(f_cham.size * 0.80)
        alt_valor = int(f_valor.size * 0.78)
        total = alt_prod + gap1 + alt_cham + gap2 + alt_valor
        y = y0 + max((caixa_alt - total) // 2, 0)

        texto_espacado(
            d, (cx, y), oferta["produto"], f_prod,
            fill=hex2rgb(self.cores["branco"]), espacamento=0.10, ancora=ancora,
            stroke=int(2 * u), stroke_fill=(0, 0, 0, 90),
        )
        y += alt_prod + gap1
        texto_espacado(
            d, (cx, y), oferta["chamada"], f_cham,
            fill=hex2rgb(self.cores["dourado_claro"]), espacamento=0.40, ancora=ancora,
        )
        y += alt_cham + gap2
        texto_gradiente(
            canvas, (cx, y), oferta["valor"], f_valor,
            cor_topo=self.cores["dourado_claro"], cor_base="#B8860B",
            espacamento=0.01, ancora=ancora, sombra=(0, 0),
            stroke=int(3 * u), stroke_fill=(4, 35, 26, 160),
        )
        return int(total)

    def contato(self, canvas: Image.Image, u: float, x: int, y_centro: int, foto_esquerda: bool = True) -> None:
        """Foto + nome + WhatsApp (bloco do corretor)."""
        d = ImageDraw.Draw(canvas)
        corretor = self.cfg["corretor"]
        diametro = int(168 * u)
        margem_foto = diametro / 2

        if foto_esquerda:
            self.foto_corretor(canvas, (int(x + margem_foto), y_centro), diametro)
            texto_x = int(x + diametro + 34 * u)
        else:
            texto_x = x

        f_nome = fonte_ajustada("Montserrat_800ExtraBold.ttf", corretor["nome"], int(canvas.width - texto_x - 40 * u), int(52 * u), 0.06)
        nome_y = int(y_centro - 76 * u)
        texto_espacado(
            d, (texto_x, nome_y), corretor["nome"], f_nome,
            fill=hex2rgb(self.cores["branco"]), espacamento=0.06,
        )
        f_cargo = font("Montserrat_600SemiBold.ttf", int(20 * u))
        texto_espacado(
            d, (texto_x + 2, nome_y + f_nome.size + int(14 * u)),
            f"{corretor['cargo']}  •  {corretor['regiao']}", f_cargo,
            fill=hex2rgb(self.cores["dourado_claro"]), espacamento=0.26,
        )

        # WhatsApp
        tel = corretor["telefone_display"]
        f_tel = fonte_ajustada("Montserrat_700Bold.ttf", tel, int(canvas.width - texto_x - 90 * u), int(44 * u), 0.02)
        tel_y = int(y_centro + 26 * u)
        badge = badge_whatsapp(int(f_tel.size * 1.15))
        canvas.alpha_composite(badge, (texto_x, tel_y + int(f_tel.size * 0.10)))
        texto_espacado(
            d, (texto_x + badge.width + int(14 * u), tel_y), tel, f_tel,
            fill=hex2rgb(self.cores["branco"]), espacamento=0.02,
        )

    def cta(self, canvas: Image.Image, u: float, x_fim: int, y_centro: int, centro: bool = False) -> None:
        """Botão 'CHAME NO WHATSAPP'."""
        d = ImageDraw.Draw(canvas)
        texto = self.cfg["cta"]
        f_cta = font("Montserrat_800ExtraBold.ttf", int(24 * u))
        larg = largura_texto(texto, f_cta, 0.14)
        alt = int(66 * u)
        w = int(larg + 60 * u)
        x0 = int(canvas.width / 2 - w / 2) if centro else x_fim - w
        y0 = y_centro - alt // 2
        sombra = Image.new("RGBA", (w + 60, alt + 60), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sombra)
        ds.rounded_rectangle([30, 34, 30 + w, 34 + alt], radius=alt // 2, fill=(0, 0, 0, 160))
        sombra = sombra.filter(ImageFilter.GaussianBlur(radius=int(10 * u)))
        canvas.alpha_composite(sombra, (x0 - 30, y0 - 30))

        grad = Image.new("L", (1, alt))
        for i in range(alt):
            grad.putpixel((0, i), int(255 * (i / max(alt - 1, 1))))
        grad = grad.resize((w, alt))
        botao = Image.new("RGBA", (w, alt), hex2rgb(self.cores["dourado_claro"]))
        botao.putalpha(255)
        camada = Image.new("RGBA", (w, alt), hex2rgb(self.cores["dourado"]))
        camada.putalpha(grad.point(lambda p: int(p * 0.85)))
        botao = Image.alpha_composite(botao, camada)
        mascara = Image.new("L", (w * 4, alt * 4), 0)
        ImageDraw.Draw(mascara).rounded_rectangle([0, 0, w * 4, alt * 4], radius=alt * 2, fill=255)
        mascara = mascara.resize((w, alt), Image.LANCZOS)
        botao.putalpha(mascara)
        canvas.alpha_composite(botao, (x0, y0))

        dd = ImageDraw.Draw(canvas)
        texto_espacado(
            dd, (x0 + w / 2, y0 + alt / 2), texto, f_cta,
            fill=hex2rgb(self.cores["verde_escuro"]), espacamento=0.14, ancora="mm",
        )

    # -- montagem ---------------------------------------------------------- #
    def gerar(self, formato: str) -> Image.Image:
        largura, altura = FORMATOS[formato]
        u = math.sqrt(largura * altura) / 1440.0  # 1.0 em Full HD
        margem = int(70 * u)

        canvas = self.preparar_fundo(largura, altura)

        if formato == "paisagem":
            painel_h = int(250 * u)
            topo_painel = self.painel_inferior(canvas, painel_h)
            self.topo(canvas, u, margem)

            larg_disp = int(largura - margem * 2)
            topo_chamada = int(170 * u)
            self.chamada(
                canvas,
                u,
                (margem, topo_chamada, int(larg_disp * 0.98), topo_painel - topo_chamada - int(50 * u)),
            )

            centro_painel = topo_painel + painel_h // 2
            self.contato(canvas, u, margem, centro_painel, foto_esquerda=True)
            self.cta(canvas, u, largura - margem, centro_painel)

        elif formato == "vertical":
            painel_h = int(580 * u)
            topo_painel = self.painel_inferior(canvas, painel_h)
            self.topo(canvas, u, margem)

            larg_disp = int(largura - margem * 2)
            regra_y = int(altura * 0.245)
            pincel_ouro(
                canvas,
                (int(largura / 2 - 60 * u), regra_y, int(largura / 2 + 60 * u), regra_y + int(5 * u)),
                espessura=int(5 * u),
            )
            topo_chamada = regra_y + int(36 * u)
            self.chamada(
                canvas,
                u,
                (margem, topo_chamada, larg_disp, topo_painel - topo_chamada - int(46 * u)),
                centro_x=True,
            )

            # bloco do corretor centralizado no painel
            d = ImageDraw.Draw(canvas)
            diametro = int(200 * u)
            cy = topo_painel + int(130 * u)
            self.foto_corretor(canvas, (largura // 2, cy), diametro)

            corretor = self.cfg["corretor"]
            nome_y = int(cy + diametro / 2 + int(46 * u))
            f_nome = fonte_ajustada("Montserrat_800ExtraBold.ttf", corretor["nome"], larg_disp, int(56 * u), 0.06)
            texto_espacado(
                d, (largura / 2, nome_y), corretor["nome"], f_nome,
                fill=hex2rgb(self.cores["branco"]), espacamento=0.06, ancora="ma",
            )
            cargo_y = nome_y + f_nome.size + int(16 * u)
            f_cargo = font("Montserrat_600SemiBold.ttf", int(21 * u))
            texto_espacado(
                d, (largura / 2, cargo_y), f"{corretor['cargo']}  •  {corretor['regiao']}", f_cargo,
                fill=hex2rgb(self.cores["dourado_claro"]), espacamento=0.26, ancora="ma",
            )
            tel_y = cargo_y + f_cargo.size + int(30 * u)
            f_tel = font("Montserrat_700Bold.ttf", int(46 * u))
            tel = corretor["telefone_display"]
            badge = badge_whatsapp(int(f_tel.size * 1.15))
            larg_tel = largura_texto(tel, f_tel, 0.02)
            total = badge.width + int(14 * u) + larg_tel
            canvas.alpha_composite(badge, (int(largura / 2 - total / 2), int(tel_y + f_tel.size * 0.10)))
            texto_espacado(
                d, (largura / 2 - total / 2 + badge.width + int(14 * u), tel_y), tel, f_tel,
                fill=hex2rgb(self.cores["branco"]), espacamento=0.02,
            )
            self.cta(canvas, u, 0, int(topo_painel + painel_h - int(70 * u)), centro=True)

        else:  # quadrado
            painel_h = int(300 * u)
            topo_painel = self.painel_inferior(canvas, painel_h)
            self.topo(canvas, u, margem)
            self.chamada(
                canvas, u,
                (margem, int(altura * 0.30), int(largura - margem * 2), int(altura * 0.36)),
                centro_x=True,
            )
            self.contato(canvas, u, margem, topo_painel + painel_h // 2, foto_esquerda=True)

        return canvas.convert("RGB")


# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description="Gera a arte Full HD de WhatsApp do Leandro Santos")
    parser.add_argument("--fundo", help="imagem do imóvel / arte original (mantida como fundo)")
    parser.add_argument("--foto", help="foto do corretor (recorte circular)")
    parser.add_argument("--config", default=os.path.join(BASE, "config.json"))
    parser.add_argument("--formatos", default="paisagem,vertical", help="paisagem,vertical,quadrado")
    parser.add_argument("--saida", default=SAIDA)
    parser.add_argument("--prefixo", default="leandro-santos")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as arquivo:
        config = json.load(arquivo)

    fundo = args.fundo
    if not fundo:
        for candidato in os.listdir(ENTRADA) if os.path.isdir(ENTRADA) else []:
            if candidato.lower().startswith(("arte", "fundo", "imovel", "original")):
                fundo = os.path.join(ENTRADA, candidato)
                break

    foto = args.foto
    if not foto and os.path.isdir(ENTRADA):
        for candidato in sorted(os.listdir(ENTRADA)):
            if candidato.lower().startswith(("foto", "leandro", "perfil", "eu")):
                foto = os.path.join(ENTRADA, candidato)
                break

    print("=" * 68)
    print("Arte WhatsApp — %s | %s" % (config["corretor"]["nome"], config["corretor"]["telefone_display"]))
    print("Oferta: %s %s %s" % (config["oferta"]["produto"], config["oferta"]["chamada"], config["oferta"]["valor"]))
    print("Fundo: %s" % (fundo or "(demonstração — nenhum arquivo em arte/entrada/)"))
    print("Foto:  %s" % (foto or "(ausente — círculo marcado 'SUA FOTO')"))
    print("=" * 68)

    os.makedirs(args.saida, exist_ok=True)
    arte = Arte(config, fundo, foto)

    gerados = []
    for formato in [f.strip() for f in args.formatos.split(",") if f.strip()]:
        if formato not in FORMATOS:
            print(f"  ! formato desconhecido: {formato}")
            continue
        imagem = arte.gerar(formato)
        largura, altura = FORMATOS[formato]
        base_nome = f"{args.prefixo}-{formato}-{largura}x{altura}"
        png = os.path.join(args.saida, base_nome + ".png")
        jpg = os.path.join(args.saida, base_nome + ".jpg")
        imagem.save(png, "PNG", optimize=True)
        imagem.save(jpg, "JPEG", quality=94, optimize=True, progressive=True)
        gerados += [png, jpg]
        print(
            "  ✔ %-10s %dx%d  →  %s (%.0f KB) / %s (%.0f KB)"
            % (formato, largura, altura, os.path.basename(png), os.path.getsize(png) / 1024,
               os.path.basename(jpg), os.path.getsize(jpg) / 1024)
        )

    print("-" * 68)
    print("Use o .jpg para enviar no WhatsApp (mais leve) e o .png para edição.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

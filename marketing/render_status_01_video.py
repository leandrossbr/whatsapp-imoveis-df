#!/usr/bin/env python3
"""Vídeo para Status do WhatsApp a partir da arte #01.

Movimento Ken Burns (zoom/pan suave) guiando a leitura:
arte inteira → selo GRÁTIS → faixa 180 MESES → ofertas → contato → fecho.

Fonte: marketing/exports/status-01-fullhd-2x.png (nitidez no zoom)
Saida: marketing/exports/status-01-video.mp4 (1080x1920, ~22s, H.264)

Uso: python3 marketing/render_status_01_video.py
"""
import os
import shutil
import subprocess

from PIL import Image

FPS = 30
DUR = 22.0
W, H = 1080, 1920
PAD = 240          # margem creme extra (topo/base) para enquadrar zonas extremas
SRC = 'marketing/exports/status-01-fullhd-2x.png'
OUT = 'marketing/exports/status-01-video.mp4'
CREAM = (246, 240, 228)

# (t_segundos, zoom, centro_x, centro_y) — coordenadas da ARTE (sem pad)
KEY = [
    (0.0,  1.10, 540, 930),   # abertura (fade-in)
    (2.3,  1.00, 540, 960),   # arte inteira
    (3.2,  1.00, 540, 960),
    (5.2,  1.70, 750, 480),   # selo GRÁTIS
    (6.4,  1.70, 750, 480),
    (8.4,  1.38, 540, 1029),  # faixa TABELA DIRETA 180 MESES
    (9.8,  1.42, 540, 1029),  # leve pulso
    (12.2, 1.40, 540, 1120),  # ofertas: 2 e 3 quartos
    (14.2, 1.40, 540, 1240),  # descendo ate coberturas
    (16.2, 2.00, 540, 1660),  # contato: nome + fone + botao
    (17.6, 2.00, 540, 1660),
    (20.2, 1.00, 540, 960),   # pull back final
    (21.8, 1.00, 540, 960),   # hold + fade-out
]


def smooth(t):
    return t * t * (3.0 - 2.0 * t)


def camera_at(t):
    if t <= KEY[0][0]:
        return KEY[0][1:]
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(KEY, KEY[1:]):
        if t <= t1:
            u = smooth((t - t0) / max(1e-6, t1 - t0))
            return (z0 + (z1 - z0) * u, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)
    return KEY[-1][1:]


def frame(src, zoom, cx, cy):
    ww, wh = W / zoom, H / zoom
    cx = min(max(cx, ww / 2), W - ww / 2)
    cy = min(max(cy, wh / 2 - PAD), H - wh / 2 + PAD)
    # origem no 2x com pad de topo
    x0 = (cx - ww / 2) * 2
    y0 = (cy - wh / 2 + PAD) * 2
    crop = src.crop((int(x0), int(y0), int(x0 + ww * 2), int(y0 + wh * 2)))
    return crop.resize((W, H), Image.LANCZOS)


def fade(im, k, to):
    """k 0..1 (1 = imagem limpa)."""
    if k >= 1.0:
        return im
    return Image.blend(Image.new('RGB', im.size, to), im, max(0.0, k))


def main():
    base = Image.open(SRC).convert('RGB')
    pad = Image.new('RGB', (base.width, base.height + 2 * PAD * 2), CREAM)
    pad.paste(base, (0, PAD * 2))

    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    os.makedirs('marketing/exports', exist_ok=True)
    cmd = [ffmpeg, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.1',
           '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'medium',
           '-movflags', '+faststart', OUT]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    n = int(DUR * FPS)
    prev_t = {1.2: '_qa_v0.png', 5.8: '_qa_v1.png', 9.0: '_qa_v2.png', 16.8: '_qa_v3.png'}
    for i in range(n):
        t = i / FPS
        z, cx, cy = camera_at(t)
        im = frame(pad, z, cx, cy)
        # fades: entrada 0-0.6s (do preto), saida 21.2-22.0s (para o preto)
        k = min(t / 0.6, (DUR - t) / 0.8, 1.0)
        im = fade(im, k, (0, 0, 0))
        for pt, name in prev_t.items():
            if abs(t - pt) < 1 / (2 * FPS):
                im.save('marketing/exports/' + name)
        proc.stdin.write(im.tobytes())

    proc.stdin.close()
    proc.wait()
    kb = os.path.getsize(OUT) // 1024
    print('gerado:', OUT, f'{DUR:.0f}s @ {FPS}fps · {W}x{H} · {kb} KB')


if __name__ == '__main__':
    main()

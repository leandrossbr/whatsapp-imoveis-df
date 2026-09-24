#!/usr/bin/env python3
"""Trilha BOSSA NOVA sincronizada com o vídeo do status #01.

Violão nylon dedilhado + baixo acústico + cross-stick na clave + chocalho
+ flauta com vibrato. Progressão clássica em dó menor:
  Cm9 | Fm9 | Bb13 | Ebmaj9 | Abmaj9 | Dm7b5 | G7b9 | Cm9

Cenas do vídeo: 5.2s selo · 8.4s faixa 180 · 16.2s contato · 20.2s fecho
Piso de ruído ZERO (sem crepitar/sub-zumbido).

Uso:  python3 marketing/render_status_01_musica.py
Sai:  marketing/exports/status-01-musica.wav
"""
import wave

import numpy as np

SR = 44100
DUR = 22.0
N = int(SR * DUR)
BAR = 3.2          # 75 BPM de pulso; colcheia = 0.4s; semicolcheia = 0.2s
OUT = 'marketing/exports/status-01-musica.wav'

rng = np.random.default_rng(11)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def noise(n):
    return rng.uniform(-1.0, 1.0, n)


def lp_ma(x, k):
    k = max(2, int(k))
    return np.convolve(x, np.ones(k) / k, mode='same')


def hp(x):
    return np.diff(x, prepend=x[:1])


def env_ad(n, a, d):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    return e * np.exp(-(np.arange(n) / SR) / max(0.02, d))


def add(buf, t0, sig, g=1.0):
    i0 = int(t0 * SR)
    i1 = min(N, i0 + len(sig))
    if i0 < N:
        buf[i0:i1] += g * sig[:i1 - i0]


# ---------------- instrumentos ----------------

def nylon(m, dur, buf, t0, g=1.0, decay=1.5):
    """Corda de violão nylon (aditiva + ataque de unha)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = np.zeros(n)
    for k in range(1, 9):
        a = 0.55 ** (k - 1) / (k ** 0.6)
        x += a * np.sin(2 * np.pi * f * k * t + 0.7 * k) * np.exp(-t * decay * (1 + 0.25 * k))
    x *= env_ad(n, 0.002, dur * 0.75)
    x += noise(n) * np.exp(-t * 320.0) * 0.02          # unha (transiente curto)
    add(buf, t0, lp_ma(x, 14), g)


def strum(buf, t0, notes, g=1.0, decay=1.5):
    for i, m in enumerate(notes):
        nylon(m, 1.35, buf, t0 + i * 0.013, g=g / max(1, len(notes) ** 0.35), decay=decay)


def upright(m, dur, buf, t0, g=1.0):
    """Baixo acústico pizzicato (sem subharmônico)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = (np.sin(2 * np.pi * f * t)
         + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3.0)
         + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 5.0))
    x *= env_ad(n, 0.005, dur * 0.85)
    x += noise(n) * np.exp(-t * 420.0) * 0.012          # estalo do dedo
    add(buf, t0, lp_ma(x, 20), g)


def flute(m, dur, buf, t0, g=1.0):
    """Flauta com vibrato e sopro discreto."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    vib = 1.0 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1.0, t * 3.0)
    ph = 2 * np.pi * f * t * vib
    x = np.sin(ph) + 0.12 * np.sin(2 * ph)
    x += lp_ma(noise(n), 10) * 0.025 * np.exp(-t * 1.2)  # sopro inicial
    add(buf, t0, x * env_ad(n, 0.07, dur * 1.25), g)


def rim(t0, buf, g=1.0):
    """Cross-stick (clave da bossa)."""
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 820 * t) * np.exp(-t * 95.0) + hp(noise(n)) * np.exp(-t * 130.0) * 0.35
    add(buf, t0, x, g)


def shaker(t0, buf, g=1.0):
    n = int(0.07 * SR)
    add(buf, t0, hp(noise(n)) * env_ad(n, 0.004, 0.020), g)


def kick(t0, buf, g=1.0):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    f = 40.0 + 55.0 * np.exp(-t * 25.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    add(buf, t0, np.sin(ph) * np.exp(-t * 12.0), g)


def fftconv(x, ir):
    L = 1
    while L < len(x) + len(ir):
        L *= 2
    return np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[:len(x)]


# ---------------- harmonia (1 acorde / 1.6s) ----------------

CM9 = [51, 55, 58, 62]        # Eb G Bb D
FM9 = [56, 60, 63, 67]        # Ab C Eb G
BB13 = [56, 62, 65, 67]       # Ab D F G
EBMAJ9 = [55, 58, 62, 65]     # G Bb D F
ABMAJ9 = [60, 63, 67, 70]     # C Eb G Bb
DM7B5 = [53, 56, 60]          # F Ab C
G7B9 = [53, 59, 62, 68]       # F B D Ab(b9)
CM69 = [51, 57, 62]           # Eb A D

# (inicio, notas, raiz_baixo, quinta_baixo)
CHORDS = [
    (0.0,  CM9, 36, 43), (1.6, CM9, 36, 43),
    (3.2,  FM9, 41, 48), (4.8, FM9, 41, 48),
    (6.4,  BB13, 34, 41), (8.0, BB13, 34, 41),
    (9.6,  EBMAJ9, 39, 46), (11.2, EBMAJ9, 39, 46),
    (12.8, ABMAJ9, 44, 51), (14.4, ABMAJ9, 44, 51),
    (16.0, DM7B5, 38, 44), (17.6, G7B9, 43, 50),
    (19.2, CM9, 36, 43),
    (20.2, CM69, 36, 43),        # acorde final sincopado
]


def chord_at(t):
    cur = CHORDS[0]
    for c in CHORDS:
        if c[0] <= t + 1e-6:
            cur = c
    return cur


def main():
    np.random.seed(11)
    mix = np.zeros(N)

    # ---- baixo: raiz no tempo 1, quinta no tempo 3 (de cada 1.6s) ----
    for t0, notes, root, fifth in CHORDS[:-1]:
        upright(root, 0.72, mix, t0, g=0.55)
        upright(fifth, 0.66, mix, t0 + 0.8, g=0.45)
    upright(36, 1.3, mix, 20.2, g=0.5)

    # ---- comping do violão (padrão sincopado alternado por compasso) ----
    pad_a = (0, 3, 6, 10, 12)
    pad_b = (0, 3, 8, 11, 14)
    bar = 0
    while bar < 20.0:
        pattern = pad_a if (bar // int(BAR * 5)) % 2 == 0 else pad_b
        for s in pattern:
            t = bar + s * 0.2
            if t < 20.0:
                _, notes, _, _ = chord_at(t)
                strum(mix, t, notes, g=0.62 if s in (0, 6, 8) else 0.48)
        bar += BAR
    _, notes, _, _ = chord_at(20.2)
    strum(mix, 20.2, notes, g=0.7, decay=1.1)          # acorde final

    # ---- percussão leve ----
    t = 1.6
    k = 0
    while t < 21.2:                                     # chocalho 16-avos
        shaker(t, mix, g=0.16 if k % 4 == 0 else 0.075)
        k += 1
        t += 0.2
    bar = 3.2
    bi = 1
    while bar < 19.3:
        clave = (0, 6, 10) if bi % 2 == 1 else (4, 12)  # clave 3-2
        for s in clave:
            rim(bar + s * 0.2, mix, g=0.4 if s in (0, 4) else 0.3)
        kick(bar, mix, g=0.22)                          # kick sussurrado
        kick(bar + 1.6, mix, g=0.16)
        bi += 1
        bar += BAR

    # ---- flauta: pickup no selo, melodia na faixa 180, resolução no contato ----
    for t0, m, d in [
        (5.2, 67, 0.55), (5.75, 72, 0.95),
        (8.4, 67, 0.55), (9.0, 70, 0.28), (9.3, 72, 0.85),
        (10.4, 70, 0.28), (10.7, 67, 0.75),
        (11.6, 65, 0.28), (11.9, 67, 0.95),
        (13.2, 75, 0.35), (13.6, 74, 0.35), (14.0, 72, 0.95),
        (15.2, 70, 0.45), (15.7, 67, 1.15),
        (17.2, 68, 0.35), (17.6, 70, 0.35), (18.0, 72, 1.35),
        (20.2, 79, 1.60),
    ]:
        flute(m, d, mix, t0, g=0.42)

    # ---- sala quente e curta + limitador + fades ----
    ir_n = int(1.1 * SR)
    ir = lp_ma(rng.uniform(-1, 1, ir_n), 12) * np.exp(-np.arange(ir_n) / SR * 4.5)
    wet = fftconv(mix, ir / (np.abs(ir).max() + 1e-9) * 0.16)
    out = np.tanh((mix + 0.22 * wet) * 1.1)

    fade = np.ones(N)
    fade[: int(0.4 * SR)] = np.linspace(0, 1, int(0.4 * SR))
    f0 = int(21.25 * SR)
    fade[f0:] = np.linspace(1, 0, N - f0)
    out *= fade
    out -= lp_ma(out, 512)                              # remove DC/rumbo
    out /= np.abs(out).max() / 0.86

    dly = int(0.010 * SR)
    left = out * 0.97 + np.concatenate([np.zeros(dly), out[:-dly]]) * 0.05
    right = out * 0.97 + np.concatenate([np.zeros(6), out[:-6]]) * 0.05
    st = np.stack([left, right], axis=1)
    st /= np.abs(st).max() / 0.9

    with wave.open(OUT, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
    print('gerado:', OUT, '22s · bossa nova · piso de ruido zero')


if __name__ == '__main__':
    main()

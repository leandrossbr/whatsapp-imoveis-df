#!/usr/bin/env python3
"""Trilha metropolitana (chillhop/neo-soul) sincronizada com o vídeo do status #01.

Clima: Rhodes elétrico jazzy, sub grooving, bateria half-time suave, shaker,
textura vinil e um gancho melódico que entra na faixa 180 MESES.

Tempos-chave do vídeo: 5.2s selo · 8.4s faixa 180 · 16.2s contato · 20.2s fecho
(75 BPM — barra = 3.2s — todos os tempos caem na grade de 16-col)

Uso:  python3 marketing/render_status_01_musica.py
Sai:  marketing/exports/status-01-musica.wav
"""
import wave

import numpy as np

SR = 44100
DUR = 22.0
N = int(SR * DUR)
OUT = 'marketing/exports/status-01-musica.wav'

rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def sine(f, n):
    return np.sin(2 * np.pi * f * np.arange(n) / SR)


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

def rhodes(t0, notes, dur, buf, g=1.0):
    """Piano elétrico FM-ish (tine suave + corpo)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        f = midi(m)
        tine = np.exp(-t * 7.0) * np.sin(2 * np.pi * f * t + 1.4 * np.exp(-t * 6) * np.sin(2 * np.pi * 2 * f * t))
        body = np.sin(2 * np.pi * f * t + 0.35 * np.sin(2 * np.pi * 3 * f * t))
        x += 0.55 * tine + 0.7 * body * np.exp(-t / (dur * 0.55))
    x *= env_ad(n, 0.006, dur * 1.4) / max(1, len(notes))
    add(buf, t0, lp_ma(x, 36), g)


def subbass(t0, m, dur, buf, g=1.0):
    n = int(dur * SR)
    f = midi(m)
    x = np.tanh(1.6 * sine(f, n)) * 0.85 + 0.2 * sine(f / 2, n)
    add(buf, t0, lp_ma(x, 24) * env_ad(n, 0.008, dur * 0.9), g)


def kick(t0, buf, g=1.0):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 41.0 + 85.0 * np.exp(-t * 20.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    add(buf, t0, np.sin(ph) * env_ad(n, 0.004, 0.30), g)


def rim(t0, buf, g=1.0):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    x = 0.5 * hp(noise(n)) + 0.35 * np.sin(2 * np.pi * 1750 * t)
    add(buf, t0, x * np.exp(-t * 55.0), g)


def shaker(t0, buf, g=1.0):
    n = int(0.09 * SR)
    add(buf, t0, hp(noise(n)) * env_ad(n, 0.002, 0.03), g)


def hat(t0, buf, g=1.0):
    n = int(0.18 * SR)
    add(buf, t0, hp(noise(n)) * env_ad(n, 0.002, 0.07), g)


def pluck(t0, m, dur, buf, g=1.0):
    """Marimba/synth pluck do gancho melódico."""
    n = int(max(0.3, dur) * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 12)
    add(buf, t0, lp_ma(x, 20) * env_ad(n, 0.004, max(0.18, dur * 0.8)), g)


def chime(t0, m, buf, g=1.0):
    n = int(1.8 * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = np.sin(2 * np.pi * f * t + 2.0 * np.sin(2 * np.pi * 3.1 * f * t))
    add(buf, t0, x * np.exp(-t * 2.6), g)


def crackle(buf):
    """Textura vinil discreta."""
    base = lp_ma(noise(N), 5) * 0.010
    pops = np.zeros(N)
    for _ in range(70):
        i = rng.integers(0, N - 600)
        burst = noise(600) * np.exp(-np.arange(600) / SR * 220.0) * 0.035
        pops[i:i + 600] += lp_ma(burst, 3)
    buf += base + pops


def fftconv(x, ir):
    L = 1
    while L < len(x) + len(ir):
        L *= 2
    return np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[:len(x)]


# ---------------- arranjo ----------------

BAR = 3.2            # 75 BPM
CHORDS = [           # (inicio, [notas], dur_sustenido)
    (0.0,  [48, 51, 55, 58, 62], 3.0),   # Cm9
    (3.2,  [48, 51, 55, 58, 62], 3.0),   # Cm9
    (6.4,  [53, 56, 60, 63, 67], 3.0),   # Fm9
    (9.6,  [44, 48, 51, 55, 58], 3.0),   # Ab maj9
    (12.8, [53, 56, 60, 63, 67], 3.0),   # Fm9
    (16.0, [51, 55, 58, 62, 65], 3.0),   # Eb add9 — contato
    (19.2, [48, 51, 55, 58, 62], 1.0),   # Cm9 (curto)
]
ROOTS = [36, 36, 41, 32, 41, 39, 36]  # raiz do baixo por numero de barra


def main():
    np.random.seed(7)
    mix = np.zeros(N)

    crackle(mix)

    # acordes: sustain suave + stabs no offbeat (comping urbano)
    for t0, notes, d in CHORDS:
        rhodes(t0, notes, d, mix, g=0.30)
        for off in (0.4, 1.2, 2.0, 2.8):
            if t0 + off < 20.2:
                rhodes(t0 + off, notes, 0.6, mix, g=0.34)

    # bateria half-time + baixo (entram em 3.2s)
    for bi in range(1, 7):
        bar = bi * BAR
        root = ROOTS[bi]
        energy = 1.1 if 9.6 <= bar < 16.0 else 1.0
        kick(bar + 0.0, mix, g=0.85 * energy)
        kick(bar + 2.0, mix, g=0.62 * energy)
        rim(bar + 1.6, mix, g=0.55)
        for off, d, iv in [(0.0, 0.55, 0), (0.8, 0.30, 0), (1.6, 0.50, 7), (2.4, 0.32, 0), (2.8, 0.28, 12)]:
            subbass(bar + off, root + iv, d, mix, g=0.50)
        t = bar
        k = 0
        while t < bar + BAR - 0.05:
            shaker(t, mix, g=0.10 if k % 2 == 0 else 0.055)
            k += 1
            t += 0.4
        if 9.6 <= bar < 16.0:                # hats no trecho das ofertas
            for off in (0.4, 1.2, 2.0, 2.8):
                hat(bar + off, mix, g=0.07)

    # kick de abertura suave
    kick(0.0, mix, g=0.45)

    # gancho melodico (Cm pentatonico) — comeca junto com a faixa 180 (8.4s)
    for t0, m, d in [
        (8.4, 67, 0.35), (8.8, 70, 0.35), (9.2, 72, 0.55),
        (10.0, 70, 0.35), (10.4, 67, 0.75), (11.2, 63, 0.55),
        (12.0, 65, 0.35), (12.4, 67, 0.55),
        (12.8, 68, 0.55), (13.2, 72, 0.35), (13.6, 75, 0.75),
        (14.4, 72, 0.35), (14.8, 70, 0.55), (15.2, 67, 0.75),
        (16.2, 74, 0.55), (17.0, 70, 0.35), (17.4, 67, 0.75),
        (18.2, 63, 0.35), (18.6, 67, 0.95),
    ]:
        pluck(t0, m, d, mix, g=0.30)

    # cenas douradas: chimes suaves nos pontos de chegada da câmera
    chime(5.2, 79, mix, g=0.22)                 # selo GRÁTIS
    chime(8.4, 84, mix, g=0.26)                 # faixa 180
    chime(16.2, 82, mix, g=0.16)                # contato
    chime(16.35, 86, mix, g=0.13)
    chime(20.2, 87, mix, g=0.20)                # fecho
    chime(20.45, 91, mix, g=0.10)

    # rolls de shaker (transicoes discretas)
    for t0 in (7.8, 19.6):
        t = t0
        while t < t0 + 0.6:
            shaker(t, mix, g=0.05 + 0.12 * (t - t0) / 0.6)
            t += 0.1

    # acorde final sincopado em 20.2 + cauda
    rhodes(20.2, [51, 55, 58, 62, 65], 1.8, mix, g=0.55)
    subbass(20.2, 39, 1.4, mix, g=0.5)
    kick(20.2, mix, g=0.6)
    pluck(20.2, 79, 1.2, mix, g=0.20)
    pluck(20.6, 75, 1.3, mix, 0.16)

    # reverberacao de ar + soft clip + fade de saida
    ir_n = int(1.8 * SR)
    ir = rng.uniform(-1, 1, ir_n) * np.exp(-np.arange(ir_n) / SR * 3.0)
    wet = fftconv(mix, ir / np.abs(ir).max() * 0.18)
    out = np.tanh((mix + 0.30 * wet) * 1.15)
    fade = np.ones(N)
    f0, f1 = int(21.25 * SR), N
    fade[f0:f1] = np.linspace(1, 0, f1 - f0)
    out *= fade
    out /= np.abs(out).max() / 0.86

    dly = int(0.011 * SR)
    left = out * 0.98 + np.concatenate([np.zeros(dly), out[:-dly]]) * 0.06
    right = out * 0.98 + np.concatenate([np.zeros(int(dly * 0.6)), out[:-int(dly * 0.6)]]) * 0.04
    st = np.stack([left, right], axis=1)
    st /= np.abs(st).max() / 0.92

    with wave.open(OUT, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
    print('gerado:', OUT, f'{DUR:.0f}s · 75 BPM · chillhop metropolitano')


if __name__ == '__main__':
    main()

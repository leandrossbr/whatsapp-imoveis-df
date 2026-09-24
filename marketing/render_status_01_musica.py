#!/usr/bin/env python3
"""Trilha INTIMISTA: violão solo brasileiro p/ o vídeo do status #01.

Voz e violão — dedilhado com baixo alternado, arpejo e melodia cantando
na corda. Harmônicos naturais (pings de cristal) marcam cada cena.
SEM bateria, SEM percussão, SEM pad, SEM piso de ruído.

Progressão: Cm9 | Fm9 | Bb13 | Ebmaj9 | Abmaj9 | Dm7b5 | G7b9 | Cm6/9
Cenas: 5.2s selo · 8.4s faixa 180 · 16.2s contato · 20.2s fecho

Uso:  python3 marketing/render_status_01_musica.py
Sai:  marketing/exports/status-01-musica.wav
"""
import wave

import numpy as np

SR = 44100
DUR = 22.0
N = int(SR * DUR)
BAR = 3.2          # 75 BPM de pulso; colcheia = 0.4s
OUT = 'marketing/exports/status-01-musica.wav'

rng = np.random.default_rng(13)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def noise(n):
    return rng.uniform(-1.0, 1.0, n)


def lp_ma(x, k):
    k = max(2, int(k))
    return np.convolve(x, np.ones(k) / k, mode='same')


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


def nylon(m, dur, buf, t0, g=1.0, decay=1.1, bright=0.5):
    """Corda de violão nylon — aditiva, bastante ressonância."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = np.zeros(n)
    for k in range(1, 10):
        a = bright ** (k - 1) / (k ** 0.55)
        x += a * np.sin(2 * np.pi * f * k * t + 0.7 * k) * np.exp(-t * decay * (1 + 0.18 * k))
    x *= env_ad(n, 0.004, dur * 1.4)
    x += noise(n) * np.exp(-t * 500.0) * 0.008          # unha: transiente minusculo
    add(buf, t0, lp_ma(x, 10), g)


def harmonic(m, dur, buf, t0, g=1.0):
    """Harmonico natural — ping de cristal."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 5.0) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 7.0)
    add(buf, t0, x * env_ad(n, 0.003, dur), g)


def fftconv(x, ir):
    L = 1
    while L < len(x) + len(ir):
        L *= 2
    return np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[:len(x)]


# ---------------- harmonia ----------------

CM9 = [51, 55, 58, 62]        # Eb G Bb D
FM9 = [56, 60, 63, 67]        # Ab C Eb G
BB13 = [56, 62, 65, 67]       # Ab D F G
EBMAJ9 = [55, 58, 62, 65]     # G Bb D F
ABMAJ9 = [60, 63, 67, 70]     # C Eb G Bb
DM7B5 = [53, 56, 60, 62]      # F Ab C D
G7B9 = [53, 59, 62, 68]       # F B D Ab(b9)
CM69 = [51, 57, 62, 67]       # Eb A D G

# (inicio, notas, raiz_baixo, quinta_baixo)
CHORDS = [
    (0.0,  CM9, 36, 43), (1.6, CM9, 36, 43),
    (3.2,  FM9, 41, 48), (4.8, FM9, 41, 48),
    (6.4,  BB13, 34, 41), (8.0, BB13, 34, 41),
    (9.6,  EBMAJ9, 39, 46), (11.2, EBMAJ9, 39, 46),
    (12.8, ABMAJ9, 44, 51), (14.4, ABMAJ9, 44, 51),
    (16.0, DM7B5, 38, 44), (17.6, G7B9, 43, 50),
    (19.2, CM9, 36, 43),
    (20.2, CM69, 36, 43),        # acorde final
]


def chord_at(t):
    cur = CHORDS[0]
    for c in CHORDS:
        if c[0] <= t + 1e-6:
            cur = c
    return cur


def main():
    np.random.seed(13)
    mix = np.zeros(N)

    # ---- violao: baixo alternado + arpejo respirando ----
    # arpejo por meia-barra: 3 notas suaves entre os baixos
    t = 0.0
    while t < 20.0:
        _, notes, root, fifth = chord_at(t)
        nylon(root, 1.5, mix, t, g=0.50, decay=0.85, bright=0.42)          # baixo 1
        nylon(notes[1], 1.1, mix, t + 0.2, g=0.34)
        nylon(notes[2], 1.0, mix, t + 0.6, g=0.28)
        nylon(notes[3], 1.0, mix, t + 1.0, g=0.30)
        nylon(fifth, 1.2, mix, t + 1.6, g=0.38, decay=0.85, bright=0.42)   # baixo 2
        nylon(notes[0], 0.9, mix, t + 1.8, g=0.26)
        nylon(notes[2], 0.9, mix, t + 2.2, g=0.28)
        nylon(notes[3], 0.9, mix, t + 2.6, g=0.24)
        t += BAR

    # ---- melodia cantando na corda (mesmo tema, voz solista) ----
    for t0, m, d in [
        (4.8, 65, 0.30),
        (5.2, 67, 0.55), (5.75, 72, 1.10),
        (8.4, 67, 0.55), (9.0, 70, 0.28), (9.3, 72, 0.95),
        (10.4, 70, 0.28), (10.7, 67, 0.85),
        (11.6, 65, 0.28), (11.9, 67, 1.05),
        (13.2, 75, 0.35), (13.6, 74, 0.35), (14.0, 72, 1.05),
        (15.2, 70, 0.45), (15.7, 67, 1.25),
        (17.2, 68, 0.35), (17.6, 70, 0.35), (18.0, 72, 1.45),
    ]:
        nylon(m, max(d, 0.9), mix, t0, g=0.62, decay=0.55, bright=0.58)

    # ---- acorde final rolado + ping de harmônico ----
    for i, m in enumerate(CM69):
        nylon(m, 1.9, mix, 20.2 + i * 0.03, g=0.5, decay=0.5, bright=0.5)
    harmonic(87, 1.5, mix, 20.55, g=0.22)

    # ---- harmônicos-cristal nas chegadas de cena ----
    harmonic(79, 1.0, mix, 5.2, g=0.16)
    harmonic(84, 1.0, mix, 8.4, g=0.16)
    harmonic(82, 1.0, mix, 16.2, g=0.16)

    # ---- sala minuscula (so ar) + fades + limpeza ----
    ir_n = int(0.45 * SR)
    ir = lp_ma(rng.uniform(-1, 1, ir_n), 12) * np.exp(-np.arange(ir_n) / SR * 9.0)
    wet = fftconv(mix, ir / (np.abs(ir).max() + 1e-9) * 0.13)
    out = mix + 0.13 * wet

    fade = np.ones(N)
    fade[: int(0.4 * SR)] = np.linspace(0, 1, int(0.4 * SR))
    f0 = int(21.25 * SR)
    fade[f0:] = np.linspace(1, 0, N - f0)
    out *= fade
    out -= lp_ma(out, 512)
    out /= np.abs(out).max() / 0.84

    st = np.stack([out, out], axis=1) / np.abs(out).max() * 0.88

    with wave.open(OUT, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
    print('gerado:', OUT, '22s · violao solo intimista · piso de ruido zero')


if __name__ == '__main__':
    main()

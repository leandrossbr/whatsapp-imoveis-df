#!/usr/bin/env python3
"""Trilha de impacto (estilo trailer) sincronizada com o vídeo do status #01.

Sintetização 100% programática (numpy) — batidas nas chegadas de câmera:
  5.2s  selo GRÁTIS        8.4s  faixa 180 MESES (MAIOR impacto)
  16.2s contato/CTA        20.2s fecho (hit final + cauda)

Uso:  python3 marketing/render_status_01_musica.py
Sai:  marketing/exports/status-01-musica.wav
"""
import wave

import numpy as np

SR = 44100
DUR = 22.0
N = int(SR * DUR)
OUT = 'marketing/exports/status-01-musica.wav'

rng = np.random.default_rng(42)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def sine(f, n, ph=0.0):
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t + ph)


def saw(f, n):
    t = np.arange(n) / SR
    return 2.0 * ((f * t) % 1.0) - 1.0


def square(f, n):
    return np.sign(sine(f, n))


def noise(n):
    return rng.uniform(-1.0, 1.0, n)


def lp_ma(x, k):
    k = max(2, int(k))
    ker = np.ones(k) / k
    return np.convolve(x, ker, mode='same')


def hp(x):
    return np.diff(x, prepend=x[:1])


def env_ad(n, a, d):
    """attack linear + decay exponencial."""
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    t = np.arange(n) / SR
    return e * np.exp(-t / max(0.02, d))


def add(buf, t0, sig, g=1.0):
    i0 = int(t0 * SR)
    i1 = min(N, i0 + len(sig))
    if i0 >= N:
        return
    buf[i0:i1] += g * sig[:i1 - i0]


def impact(t0, buf, g=1.0):
    """Boom sub + crack + crash — impacto cinematico."""
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    f = 30.0 + 95.0 * np.exp(-t * 5.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    boom = np.sin(ph) * np.exp(-t * 1.9) * env_ad(n, 0.004, 5.0)
    crack = hp(noise(n)) * np.exp(-t * 40.0) * 0.45
    crash = hp(noise(n)) * np.exp(-t * 2.4) * 0.32
    add(buf, t0, boom + crack + crash, g)


def riser(t0, t1, buf, g=1.0):
    """Subida tensa (sweep + noise) terminando exatamente em t1."""
    n = int((t1 - t0) * SR)
    u = np.linspace(0, 1, n)
    t = np.arange(n) / SR
    f = 140.0 * (1.0 + 9.0 * u ** 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sweep = np.sin(ph) * u ** 2
    hiss = hp(noise(n)) * u ** 3
    add(buf, t0, (sweep * 0.7 + hiss * 0.5) * env_ad(n, (t1 - t0) * 0.9, 6.0), g)


def kick(t0, buf, g=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 46.0 + 130.0 * np.exp(-t * 30.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    add(buf, t0, np.sin(ph) * np.exp(-t * 15.0) * env_ad(n, 0.003, 4.0), g)


def bass(t0, f, dur, buf, g=1.0):
    n = int(dur * SR)
    x = square(f, n) * 0.4 + saw(f, n) * 0.3 + sine(f / 2, n) * 0.35
    e = env_ad(n, 0.006, dur * 0.85)
    add(buf, t0, lp_ma(x, 30) * e, g)


def pad(t0, freqs, dur, buf, g=1.0):
    n = int(dur * SR)
    x = np.zeros(n)
    for f in freqs:
        for det in (1.0, 1.006, 0.994):
            x += saw(f * det, n)
    e = env_ad(n, dur * 0.30, dur * 1.1)
    add(buf, t0, lp_ma(x, 90) * e / (3 * len(freqs)), g)


def pluck(t0, f, buf, g=1.0):
    n = int(0.32 * SR)
    x = lp_ma(saw(f, n), 22) * np.exp(-np.arange(n) / SR * 9.0)
    add(buf, t0, x * env_ad(n, 0.002, 0.4), g)


def bell(t0, f, buf, g=1.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t + 2.4 * np.sin(2 * np.pi * 2.76 * f * t))
    add(buf, t0, x * np.exp(-t * 3.0), g)


def hat(t0, buf, g=1.0):
    n = int(0.08 * SR)
    add(buf, t0, hp(noise(n)) * np.exp(-np.arange(n) / SR * 55.0), g)


def reverse_swell(t0, t1, buf, g=1.0):
    n = int((t1 - t0) * SR)
    x = hp(noise(n)) * np.exp(-np.arange(n) / SR * 3.0)
    add(buf, t0, x[::-1], g)


def fftconv(x, ir):
    L = 1
    while L < len(x) + len(ir):
        L *= 2
    y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)
    return y[:len(x)]


def main():
    np.random.seed(42)
    mix = np.zeros(N)

    # ---- drones / pads (Cm - Ab - Cm - Ab - Bb - Eb - Cm) ----
    for t0, notes, dur in [
        (0.0,  [48, 51, 55], 5.4),        # Cm
        (5.2,  [44, 48, 51], 3.4),        # Ab
        (8.4,  [48, 51, 55], 4.0),        # Cm
        (12.2, [44, 48, 51], 2.2),        # Ab
        (14.2, [46, 50, 53], 2.2),        # Bb (build)
        (16.2, [51, 55, 58], 4.2),        # Eb (resolucao esperancosa)
        (20.2, [48, 51, 55, 60], 1.9),    # Cm final
    ]:
        pad(t0, [midi(m) for m in notes], dur, mix, g=0.55)

    # sub drone contínuo
    sub = sine(midi(24), N) * 0.22 + sine(midi(36), N) * 0.12
    swell = 0.7 + 0.3 * np.sin(2 * np.pi * np.arange(N) / SR / 4.0)
    mix += sub * swell

    # ---- impactos nas chegadas de camera ----
    impact(0.30, mix, g=0.55)     # fade-in
    impact(5.20, mix, g=0.85)     # selo GRATIS
    impact(8.40, mix, g=1.15)     # TABELA 180 — MAIOR
    impact(16.20, mix, g=1.00)    # contato
    impact(20.20, mix, g=1.25)    # fecho — hit final

    # ---- risers + reverse swell ----
    riser(3.40, 5.20, mix, g=0.35)
    riser(6.60, 8.40, mix, g=0.55)
    riser(14.60, 16.20, mix, g=0.40)
    reverse_swell(19.10, 20.20, mix, g=0.35)

    # ---- kick 120bpm na secao das ofertas + half-time no contato ----
    t = 8.40
    while t <= 16.05:
        kick(t, mix, g=0.9 if int(round((t - 8.4) * 2)) % 2 == 0 else 0.7)
        t += 0.5
    for t in (17.0, 18.0, 19.0):
        kick(t, mix, g=0.45)

    # ---- baixo pulsante (8as; 16as no build final) ----
    t = 8.40
    while t < 12.2:
        bass(t, midi(36), 0.22, mix, g=0.5); t += 0.25
    while t < 14.2:
        bass(t, midi(32), 0.22, mix, g=0.5); t += 0.25
    while t < 16.1:
        bass(t, midi(34), 0.11, mix, g=0.5); t += 0.125

    # ---- hats ----
    t = 8.65
    while t < 16.1:
        hat(t, mix, g=0.12); t += 0.25

    # ---- arp de plucks durante a varredura das ofertas ----
    arp_c = [72, 75, 79, 84]
    arp_ab = [68, 72, 75, 80]
    i = 0
    t = 9.80
    while t < 14.2:
        seq = arp_c if t < 12.2 else arp_ab
        pluck(t, midi(seq[i % 4]), mix, g=0.22)
        i += 1
        t += 0.25

    # ---- sinos FM (GRÁTIS + resolucao) ----
    bell(5.30, midi(79), mix, g=0.30)
    bell(5.55, midi(84), mix, g=0.22)
    for m in (75, 79, 82):
        bell(16.30, midi(m), mix, g=0.18)

    # ---- reverberacao (IR exponencial) + soft clip ----
    ir_n = int(2.2 * SR)
    ir = rng.uniform(-1, 1, ir_n) * np.exp(-np.arange(ir_n) / SR * 2.6)
    wet = fftconv(mix, ir / np.abs(ir).max() * 0.20)
    out = mix + 0.35 * wet
    out = np.tanh(out * 1.25)
    out /= np.abs(out).max() / 0.88

    # leve estereo (Haas em plucks/pads ja embutido no mix mono -> espelha com micro-delay)
    dly = int(0.008 * SR)
    left = out
    right = np.concatenate([np.zeros(dly), out[:-dly]]) * 0.96 + out * 0.04
    st = np.stack([left, right], axis=1)
    st /= np.abs(st).max() / 0.92

    pcm = (st * 32767).astype('<i2')
    with wave.open(OUT, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

    print('gerado:', OUT, f'{DUR:.0f}s · {pcm.nbytes // 1024 // 1024}MB')


if __name__ == '__main__':
    main()

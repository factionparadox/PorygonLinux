# The Porygon chime: an original start-up sound in the spirit of the
# 1990s workstation power-on chord. A rising FM-bell arpeggio lands on a
# warm major-ninth chord; a few quantised "bit" blips nod to Porygon
# being made of code.  usage: python3 chime.py OUT.wav
import sys, math, wave, struct
import numpy as np
SR = 44100
T = 3.6
t = np.arange(int(SR * T)) / SR
out = np.zeros_like(t)
def bell(f, start, amp, decay=1.9):
    tt = np.clip(t - start, 0, None); on = t >= start
    env = (1 - np.exp(-tt * 90)) * np.exp(-tt * decay)
    mod = np.sin(2 * np.pi * f * 2.0 * tt) * 1.6 * np.exp(-tt * 3)
    return on * amp * env * np.sin(2 * np.pi * f * tt + mod)
# Db major 9: Db3 Ab3 F4 C5 Eb5 - arpeggiated, then held
notes = [138.59, 207.65, 349.23, 523.25, 622.25]
for i, f in enumerate(notes):
    out += bell(f, 0.06 * i, 0.22 if i else 0.30)
    out += bell(f * 2.003, 0.06 * i + 0.01, 0.05)   # shimmer
# soft pad underneath
pad_env = np.minimum(t / 0.6, 1) * np.exp(-np.maximum(t - 0.6, 0) * 1.3)
for f in notes[:3]:
    out += 0.06 * pad_env * np.sin(2 * np.pi * f * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t))
# digital blips: square waves, crushed to 4 bits
for k, (st, f) in enumerate([(0.42, 1046.5), (0.50, 1396.9), (0.58, 2093.0)]):
    tt = t - st; on = (tt >= 0) & (tt < 0.05)
    sq = np.sign(np.sin(2 * np.pi * f * tt)) * np.exp(-np.clip(tt, 0, None) * 40)
    out += on * 0.05 * np.round(sq * 8) / 8
# fade out, normalise
out *= np.minimum(1, (T - t) / 0.4)
out = out / np.max(np.abs(out)) * 0.85
# stereo with a touch of width
l = out; r = np.roll(out, int(SR * 0.004))
data = (np.stack([l, r], 1) * 32767).astype("<i2").tobytes()
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data)

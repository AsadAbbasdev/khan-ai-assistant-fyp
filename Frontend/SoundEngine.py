"""
SoundEngine.py  —  Premium JARVIS-Style Sci-Fi Sound Design
============================================================
All sounds generated with numpy + scipy. Playback via pygame.mixer.

Sound Philosophy:
  • Minimal  — never distracting, always purposeful
  • Synthetic — digital / electronic, not acoustic/mechanical
  • Cohesive  — same tonal family throughout
  • Premium   — smooth envelopes, reverb tails, zero clicks/pops
"""

import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
SOUNDS_DIR  = os.path.join(PROJECT_DIR, "Frontend", "Graphics", "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)

SR = 44100

# ─────────────────────────────────────────────────────────────────────────────
#  DSP UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _t(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)

def _save(name, sig):
    peak = np.max(np.abs(sig))
    if peak > 0:
        sig = sig / peak * 0.88
    data = np.clip(sig * 32767, -32767, 32767).astype(np.int16)
    wavfile.write(os.path.join(SOUNDS_DIR, name), SR, data)

def _adsr(n, attack=0.008, decay=0.05, sustain=0.7, release=0.12):
    env = np.zeros(n)
    a = int(attack * SR);  d = int(decay * SR);  r = int(release * SR)
    s_end = max(n - r, a + d)
    if a > 0:             env[:a]        = np.linspace(0, 1, a)
    if d > 0:             env[a:a+d]     = np.linspace(1, sustain, d)
    if a + d < s_end:     env[a+d:s_end] = sustain
    if r > 0:             env[s_end:]    = np.linspace(sustain, 0, n - s_end)
    return env

def _lp(sig, cutoff, order=3):
    sos = butter(order, cutoff / (SR / 2), btype='low', output='sos')
    return sosfilt(sos, sig)

def _bp(sig, lo, hi, order=2):
    nyq = SR / 2
    lo  = min(lo, nyq * 0.98);  hi = min(hi, nyq * 0.98)
    if lo >= hi: return sig
    sos = butter(order, [lo / nyq, hi / nyq], btype='band', output='sos')
    return sosfilt(sos, sig)

def _reverb(sig, decay=0.30, delays_ms=(18, 35, 62)):
    out = sig.copy().astype(np.float64)
    for d_ms in delays_ms:
        d = int(d_ms * SR / 1000)
        tail = np.zeros(len(sig))
        for i in range(d, len(sig)):
            tail[i] = sig[i - d] * decay
        out += tail
    return out

def _fade(sig, fi=0.008, fo=0.025):
    sig = sig.copy()
    n_fi = int(fi * SR);  n_fo = int(fo * SR)
    if n_fi: sig[:n_fi]  *= np.linspace(0, 1, n_fi)
    if n_fo: sig[-n_fo:] *= np.linspace(1, 0, n_fo)
    return sig

def _sine(f, t):  return np.sin(2 * np.pi * f * t)

def _sweep(f_arr):
    return np.sin(np.cumsum(2 * np.pi * f_arr / SR))


# ─────────────────────────────────────────────────────────────────────────────
#  SOUND GENERATORS — JARVIS / Premium AI aesthetic
# ─────────────────────────────────────────────────────────────────────────────

def gen_data_blip(path="data_blip.wav"):
    """Text-reveal: ultra-short synthetic blip — like data being written."""
    dur = 0.055; t = _t(dur)
    sig = 0.55 * _sine(2800, t) + 0.30 * _sine(3150, t)
    sig *= np.exp(-t * 90)
    sig  = _lp(sig, 5500)
    sig  = _fade(sig, fi=0.001, fo=0.012)
    _save(path, sig)

def gen_data_blip_hi(path="data_blip_hi.wav"):
    """Slightly higher pitch variant — alternated with data_blip."""
    dur = 0.050; t = _t(dur)
    sig = 0.50 * _sine(3400, t) + 0.28 * _sine(3800, t)
    sig *= np.exp(-t * 100)
    sig  = _lp(sig, 6000)
    sig  = _fade(sig, fi=0.001, fo=0.010)
    _save(path, sig)

def gen_ambient_hum(path="ambient_hum.wav", dur=8.0):
    """
    Smooth sci-fi reactor hum — calming, evolving, loops cleanly.
    Deep drone + slow harmonic shimmer. Zero noise floor.
    """
    t = _t(dur)
    drone  = 0.40 * _sine(48, t) + 0.22 * _sine(96, t) + 0.10 * _sine(144, t)
    lfo1   = 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    lfo2   = 0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + 1.2)
    shimmer = 0.07 * lfo1 * _sine(288, t) + 0.04 * lfo2 * _sine(576, t)
    sig    = drone + shimmer
    sig    = _lp(sig, 900)
    # clean crossfade loop point
    xf = int(0.20 * SR)
    head = sig[:xf].copy(); tail = sig[-xf:].copy()
    sig[:xf]  = head * np.linspace(0, 1, xf) + tail * np.linspace(1, 0, xf)
    sig[-xf:] = tail * np.linspace(1, 0, xf) + head * np.linspace(0, 1, xf)
    _save(path, sig)

def gen_ui_tap(path="ui_tap.wav"):
    """Soft holographic panel tap — short transient + quick sine decay."""
    dur = 0.09; t = _t(dur)
    click = np.random.default_rng(7).standard_normal(len(t)) * np.exp(-t * 150)
    click = _bp(click, 1200, 4000)
    tone  = 0.50 * _sine(1600, t) * np.exp(-t * 60)
    sig   = 0.38 * click + 0.62 * tone
    sig   = _fade(sig, fi=0.001, fo=0.020)
    _save(path, sig)

def gen_whoosh(path="whoosh.wav"):
    """Airy transition whoosh — frequency-rising filtered noise + sine sweep."""
    dur = 0.55; n = int(SR * dur)
    noise = np.random.default_rng(13).standard_normal(n)
    out   = np.zeros(n); steps = 60; step_len = n // steps
    for i in range(steps):
        lo = 200 + 4600 * i / steps
        hi = min(lo + 1400 + 1000 * i / steps, 20000)
        seg = noise[i*step_len:(i+1)*step_len]
        out[i*step_len:(i+1)*step_len] = _bp(seg, lo, hi)
    env   = _adsr(n, attack=0.04, decay=0.18, sustain=0.30, release=0.28)
    t     = np.linspace(0, dur, n, endpoint=False)
    sweep = 0.18 * _sweep(np.linspace(220, 2200, n)) * env
    sig   = out * env + sweep
    sig   = _reverb(sig, decay=0.16, delays_ms=(22, 45))
    sig   = _fade(sig, fi=0.012, fo=0.040)
    _save(path, sig)

def gen_glitch_transition(path="glitch_transition.wav"):
    """Screen transition: descending digital shimmer + sparse stutter."""
    dur = 0.48; n = int(SR * dur)
    freqs  = np.linspace(3800, 180, n)
    sweep  = _sweep(freqs)
    rng    = np.random.default_rng(42)
    stutter = np.ones(n)
    for p in rng.integers(0, n, size=10):
        w = int(0.006 * SR);  stutter[p:p+w] = 0.0
    env = _adsr(n, attack=0.008, decay=0.10, sustain=0.40, release=0.25)
    sig = sweep * stutter * env * 0.65
    sig = _lp(sig, 7000)
    sig = _reverb(sig, decay=0.20, delays_ms=(15, 32, 58))
    sig = _fade(sig, fi=0.006, fo=0.035)
    _save(path, sig)

def gen_energy_pulse(path="energy_pulse.wav"):
    """Orb glow sync pulse — deep quiet heartbeat with reverb tail."""
    dur = 1.1; t = _t(dur); n = len(t)
    pulse_env = np.sin(np.pi * t / dur) ** 1.4
    f0  = 90.0
    sig = _sweep((f0 + 25 * pulse_env))
    sig += 0.35 * _sine(f0 * 0.5, t) + 0.12 * _sine(f0 * 2, t)
    sig *= pulse_env
    sig  = _lp(sig, 800)
    sig  = _reverb(sig, decay=0.38, delays_ms=(30, 65, 110))
    sig  = _fade(sig, fi=0.025, fo=0.060)
    _save(path, sig)

def gen_system_ready(path="system_ready.wav"):
    """Rising three-tone chime — SYSTEM READY confirmation. Clean, premium."""
    dur = 1.0; sig = np.zeros(int(SR * dur))
    for start, freq, length in [(0.00, 660, 0.28), (0.22, 880, 0.28), (0.44, 1320, 0.40)]:
        s = int(start * SR); e = int((start + length) * SR)
        tt = np.linspace(0, length, e - s, endpoint=False)
        b  = _sine(freq, tt) + 0.25 * _sine(freq * 2, tt)
        b *= _adsr(len(tt), attack=0.010, decay=0.06, sustain=0.60, release=0.14)
        sig[s:e] += b * 0.55
    sig = _lp(sig, 5000)
    sig = _reverb(sig, decay=0.28, delays_ms=(20, 45, 80))
    sig = _fade(sig, fi=0.005, fo=0.060)
    _save(path, sig)

def gen_boot_sequence(path="boot_seq.wav"):
    """Neural-network warmup boot — smooth exponentially rising tones."""
    dur = 1.6; sig = np.zeros(int(SR * dur))
    schedule = [
        (0.00, 120, 0.20), (0.14, 180, 0.20), (0.27, 260, 0.18),
        (0.39, 380, 0.17), (0.50, 560, 0.16), (0.60, 820, 0.16), (0.72, 1200, 0.35),
    ]
    for start, freq, length in schedule:
        s = int(start * SR); e = int((start + length) * SR)
        tt = np.linspace(0, length, e - s, endpoint=False)
        b  = _sine(freq, tt) * 0.55 + 0.15 * _sine(freq * 2, tt)
        b *= _adsr(len(tt), attack=0.012, decay=0.05, sustain=0.65, release=0.10)
        sig[s:e] += b * 0.50
    sig = _lp(sig, 4000)
    sig = _reverb(sig, decay=0.26, delays_ms=(18, 40, 72))
    sig = _fade(sig, fi=0.010, fo=0.060)
    _save(path, sig)

def gen_ting(path="ting.wav"):
    """Crystal holographic confirm ting."""
    dur = 0.55; t = _t(dur)
    sig = 0.55 * _sine(3200, t) + 0.25 * _sine(6400, t) + 0.12 * _sine(9600, t)
    sig *= np.exp(-t * 8)
    sig  = _reverb(sig, decay=0.18, delays_ms=(25, 50))
    sig  = _fade(sig, fi=0.002, fo=0.040)
    _save(path, sig)

def gen_tang(path="tang.wav"):
    """Mid resonant action-confirm tang."""
    dur = 0.65; t = _t(dur)
    sig = 0.50 * _sine(1800, t) + 0.30 * _sine(2700, t) + 0.15 * _sine(900, t)
    sig *= np.exp(-t * 6)
    sig  = _reverb(sig, decay=0.23, delays_ms=(20, 48, 80))
    sig  = _fade(sig, fi=0.002, fo=0.050)
    _save(path, sig)

def gen_tong(path="tong.wav"):
    """Deep completion tong."""
    dur = 0.80; t = _t(dur)
    sig = 0.45 * _sine(420, t) + 0.35 * _sine(630, t) + 0.18 * _sine(210, t)
    sig *= np.exp(-t * 4.5)
    sig  = _reverb(sig, decay=0.33, delays_ms=(30, 65, 110))
    sig  = _fade(sig, fi=0.003, fo=0.060)
    _save(path, sig)


# ─────────────────────────────────────────────────────────────────────────────
#  REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

SOUND_FILES = {
    "data_blip":         "data_blip.wav",
    "data_blip_hi":      "data_blip_hi.wav",
    "ambient_hum":       "ambient_hum.wav",
    "ui_tap":            "ui_tap.wav",
    "whoosh":            "whoosh.wav",
    "glitch_transition": "glitch_transition.wav",
    "energy_pulse":      "energy_pulse.wav",
    "system_ready":      "system_ready.wav",
    "boot_seq":          "boot_seq.wav",
    "ting":              "ting.wav",
    "tang":              "tang.wav",
    "tong":              "tong.wav",
}

_GENERATORS = {
    "data_blip":         gen_data_blip,
    "data_blip_hi":      gen_data_blip_hi,
    "ambient_hum":       gen_ambient_hum,
    "ui_tap":            gen_ui_tap,
    "whoosh":            gen_whoosh,
    "glitch_transition": gen_glitch_transition,
    "energy_pulse":      gen_energy_pulse,
    "system_ready":      gen_system_ready,
    "boot_seq":          gen_boot_sequence,
    "ting":              gen_ting,
    "tang":              gen_tang,
    "tong":              gen_tong,
}

def generate_all_sounds(force=False):
    for key, filename in SOUND_FILES.items():
        path = os.path.join(SOUNDS_DIR, filename)
        if force or not os.path.exists(path):
            print(f"[SoundEngine] Generating {filename} ...")
            _GENERATORS[key]()
    print("[SoundEngine] All sounds ready.")

def sound_path(key):
    return os.path.join(SOUNDS_DIR, SOUND_FILES.get(key, ""))


# ─────────────────────────────────────────────────────────────────────────────
#  PYGAME MIXER
# ─────────────────────────────────────────────────────────────────────────────

import pygame

try:
    pygame.mixer.pre_init(44100, -16, 1, 1024)
    pygame.mixer.init()
    pygame.mixer.set_num_channels(24)
    _PYGAME_OK = True
    print("[SoundEngine] pygame mixer ready.")
except Exception as e:
    print(f"[SoundEngine] pygame mixer init failed: {e}")
    _PYGAME_OK = False

_sound_cache: dict = {}

def _get_sound(filepath):
    if not _PYGAME_OK:
        return None
    if filepath not in _sound_cache:
        try:
            _sound_cache[filepath] = pygame.mixer.Sound(filepath)
        except Exception as e:
            print(f"[SoundEngine] Load error {filepath}: {e}")
            return None
    return _sound_cache[filepath]


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

class SoundManager:
    """
    Public API for GUI.py.
        sfx = SoundManager()
        sfx.play_boot()
        sfx.start_ambient()
        sfx.play_typing()    # call per character
    """

    def __init__(self):
        generate_all_sounds()
        self._ambient_ch  = None
        self._blip_toggle = False   # alternate pitch for natural typing feel

    def play(self, key, volume=0.72):
        if not _PYGAME_OK: return
        path = sound_path(key)
        if not os.path.exists(path): return
        try:
            snd = _get_sound(path)
            if snd:
                snd.set_volume(volume)
                ch = pygame.mixer.find_channel(True)
                if ch: ch.play(snd)
        except Exception as e:
            print(f"[SoundEngine] play error ({key}): {e}")

    def play_typing(self):
        """Alternates low/high blip — barely audible, just texture."""
        key = "data_blip_hi" if self._blip_toggle else "data_blip"
        self._blip_toggle = not self._blip_toggle
        self.play(key, volume=0.08)   # very subtle — won't cover voice

    def start_ambient(self, volume=0.05):   # barely-there background hum
        if not _PYGAME_OK: return
        path = sound_path("ambient_hum")
        if not os.path.exists(path): return
        try:
            snd = _get_sound(path)
            if snd:
                snd.set_volume(volume)
                ch = pygame.mixer.Channel(0)   # dedicated ambient channel
                ch.play(snd, loops=-1)
                self._ambient_ch = ch
        except Exception as e:
            print(f"[SoundEngine] ambient error: {e}")

    def stop_ambient(self):
        try:
            if self._ambient_ch:
                self._ambient_ch.stop()
                self._ambient_ch = None
        except: pass

    # ── Shortcuts — all reduced so robot voice stays dominant ─────────────────
    def play_boot(self):         self.play("boot_seq",          volume=0.30)
    def play_transition(self):   self.play("glitch_transition",  volume=0.20)
    def play_pulse(self):        self.play("energy_pulse",       volume=0.12)
    def play_whoosh(self):       self.play("whoosh",             volume=0.18)
    def play_ting(self):         self.play("ting",               volume=0.22)
    def play_tang(self):         self.play("tang",               volume=0.20)
    def play_tong(self):         self.play("tong",               volume=0.18)
    def play_system_ready(self): self.play("system_ready",       volume=0.28)
    def play_ui_tap(self):       self.play("ui_tap",             volume=0.15)
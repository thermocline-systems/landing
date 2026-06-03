#!/usr/bin/env python3
"""Generate per-loop-temperature adiabatic-assist-demand overlay frames.

Source: design_peak_degC.tif (annual design dry-bulb, EPSG:4326, nodata -9999).
For a loop temp T, pure-dry is feasible up to ambient (T - 2.5 C) approach.
Demand index follows the README's 45 C calibration, generalized by loop temp:
    index = clamp((peak - (T - 15)) / 20, 0, 1)
(For T=45 this is the original clamp((peak-30)/20).)
Ocean / nodata -> fully transparent. Land -> HEAT colormap, opaque.
Outputs overlay/heat_frames/loop_<T>.png for T in 40..60.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "design_peak_degC.tif")
OUT = os.path.join(HERE, "heat_frames")
os.makedirs(OUT, exist_ok=True)

# HEAT colormap (position -> hex), from README
STOPS = [
    (0.00, "#19c3e6"), (0.18, "#22d3ee"), (0.34, "#38bdf8"),
    (0.50, "#a3e635"), (0.66, "#facc15"), (0.82, "#f59e0b"),
    (1.00, "#ef4444"),
]


def hex2rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


pos = np.array([s[0] for s in STOPS])
cols = np.array([hex2rgb(s[1]) for s in STOPS], dtype=np.float32)  # (7,3)
N = 256
xs = np.linspace(0, 1, N)
LUT = np.stack([np.interp(xs, pos, cols[:, c]) for c in range(3)], axis=1)
LUT = np.clip(LUT, 0, 255).astype(np.uint8)  # (256,3)

peak = np.array(Image.open(SRC), dtype=np.float32)  # (1024,2048)
ocean = peak <= -9000

OUT_W, OUT_H = 1024, 512  # downscaled for light preloading; data is smooth

for T in range(40, 61):
    low = T - 15.0
    idx = np.clip((peak - low) / 20.0, 0.0, 1.0)
    li = (idx * (N - 1)).astype(np.int32)
    rgb = LUT[li]                                   # (1024,2048,3)
    alpha = np.where(ocean, 0, 255).astype(np.uint8)
    rgba = np.concatenate([rgb, alpha[..., None]], axis=2).astype(np.uint8)
    img = Image.fromarray(rgba, "RGBA")
    if (img.width, img.height) != (OUT_W, OUT_H):
        # NEAREST avoids blending transparent ocean into coastlines
        img = img.resize((OUT_W, OUT_H), Image.NEAREST)
    img.save(os.path.join(OUT, f"loop_{T}.png"), optimize=True)

print("wrote", len(range(40, 61)), "frames to", OUT)

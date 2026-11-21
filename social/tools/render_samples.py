"""Render the sample week's 1080x1350 (4:5) images from assets/photos.
Run from repo root:  python social/tools/render_samples.py
Fonts: Georgia + Segoe UI (Windows). The agent version should use the site fonts
(Cormorant Garamond, Jost) once they are added under social/tools/fonts/."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1080, 1350
INK, SAND, GOLD = (30, 27, 23), (247, 243, 234), (214, 176, 120)
F = "C:/Windows/Fonts/"
def font(name, size): return ImageFont.truetype(F + name, size)

def cover(path, focus=(0.5, 0.5)):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = round((im.width - W) * focus[0]); y = round((im.height - H) * focus[1])
    return im.crop((x, y, x + W, y + H))

def overlay(im, top, bottom, a_top, a_bottom):
    """vertical gradient of INK from a_top to a_bottom between y=top..bottom"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = layer.load()
    for y in range(H):
        t = 0 if y < top else 1 if y > bottom else (y - top) / max(1, bottom - top)
        a = round(a_top + (a_bottom - a_top) * t)
        for x in range(W): px[x, y] = INK + (a,)
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def block(d, text, f, x, y, maxw, fill, gap=1.12):
    for line in wrap(d, text, f, maxw):
        d.text((x, y), line, font=f, fill=fill)
        y += round(f.size * gap)
    return y

def footer(d):
    d.text((80, H - 120), "Wed by Betty", font=font("georgiai.ttf", 40), fill=SAND)
    d.text((80, H - 70), "wedbybetty.com  ·  (760) 492-3054", font=font("segoeui.ttf", 28), fill=GOLD)

def save(im, name):
    os.makedirs("social/out/2026-W48", exist_ok=True)
    im.save(f"social/out/2026-W48/{name}.jpg", quality=92)

# 1. License explainer (Tue)
im = overlay(cover("assets/photos/delmar-bluff-palms.jpg", (0.55, 0.5)), 0, H, 150, 215)
d = ImageDraw.Draw(im)
d.text((80, 110), "LICENCIA DE MATRIMONIO  ·  MARRIAGE LICENSE", font=font("segoeuib.ttf", 27), fill=GOLD)
y = block(d, "Su licencia, sin ir al condado.", font("georgiab.ttf", 92), 80, 380, W - 160, SAND)
y = block(d, "Your license, no county trip.", font("georgiai.ttf", 56), 80, y + 30, W - 160, GOLD)
footer(d); save(im, "post-1-license")

# 2. Bilingual ceremony (Fri)
im = overlay(cover("assets/photos/betty-couple-ocean-1.jpg", (0.5, 0.45)), 780, H, 0, 215)
d = ImageDraw.Draw(im)
y = block(d, "Sus votos, en los dos idiomas.", font("georgiab.ttf", 70), 80, 980, W - 160, SAND)
block(d, "Your vows, in both of your languages.", font("georgiai.ttf", 44), 80, y + 14, W - 160, GOLD)
d.text((80, H - 62), "wedbybetty.com  ·  (760) 492-3054", font=font("segoeui.ttf", 26), fill=SAND)
save(im, "post-2-bilingual")

# 3. Location spotlight (Sat)
im = overlay(cover("assets/photos/oceanside-harbor.jpg", (0.5, 0.5)), 760, H, 0, 215)
d = ImageDraw.Draw(im)
d.text((80, 940), "OCEANSIDE HARBOR", font=font("segoeuib.ttf", 27), fill=GOLD)
y = block(d, "Su boda, en nuestra ciudad.", font("georgiab.ttf", 70), 80, 990, W - 160, SAND)
block(d, "Your wedding, in our hometown.", font("georgiai.ttf", 44), 80, y + 14, W - 160, GOLD)
d.text((80, H - 62), "wedbybetty.com  ·  (760) 492-3054", font=font("segoeui.ttf", 26), fill=SAND)
save(im, "post-3-oceanside")

# 4. Just engaged CTA (Sun)
im = overlay(cover("assets/photos/oceanside-pier.jpg", (0.35, 0.5)), 0, H, 120, 215)
d = ImageDraw.Draw(im)
d.text((80, 110), "20 MINUTOS · SIN COMPROMISO  ·  20 MIN · NO COMMITMENT", font=font("segoeuib.ttf", 25), fill=GOLD)
y = block(d, "¿Se comprometieron? Felicidades.", font("georgiab.ttf", 86), 80, 400, W - 160, SAND)
y = block(d, "Just engaged? Congratulations.", font("georgiai.ttf", 56), 80, y + 30, W - 160, GOLD)
footer(d); save(im, "post-4-engaged")
print("done")

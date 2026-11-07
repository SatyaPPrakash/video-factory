import textwrap
from PIL import Image, ImageDraw, ImageFont
from pipeline.media import run, dur, mux, W, H, FPS

def clip(text, audio, out):
    png = out.with_suffix(".png")
    img = Image.new("RGB", (W, H), (18, 24, 38))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=44)
    lines = textwrap.wrap(text, 42)
    y = H // 2 - len(lines) * 31
    for line in lines:
        w = d.textlength(line, font=font)
        d.text(((W - w) / 2, y), line, font=font, fill=(240, 240, 240))
        y += 62
    img.save(png)
    raw = out.with_suffix(".raw.mp4")
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(png), "-t", f"{dur(audio):.2f}",
         "-vf", f"fps={FPS}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(raw)])
    mux(raw, audio, out)

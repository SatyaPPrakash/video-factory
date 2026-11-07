import urllib.parse, requests
from pipeline.media import run, dur, mux, W, H, FPS

def image(prompt, path, seed):
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + f"?width={W}&height={H}&nologo=true&seed={seed}")
    r = requests.get(url, timeout=240)
    r.raise_for_status()
    path.write_bytes(r.content)

def clip(img, audio, out, idx):
    frames = int(dur(audio) * FPS) + 10
    z = "min(zoom+0.0012,1.25)" if idx % 2 == 0 else "max(1.25-0.0012*on,1.0)"
    raw = out.with_suffix(".raw.mp4")
    run(["ffmpeg", "-y", "-i", str(img), "-vf",
         f"scale=1920:1080,zoompan=z='{z}':d={frames}:"
         f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
         "-frames:v", str(frames), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(raw)])
    mux(raw, audio, out)

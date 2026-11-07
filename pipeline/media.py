import pathlib, subprocess
from pipeline.config import W, H, FPS

def run(args):
    subprocess.run(args, check=True, capture_output=True)

def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                   "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.decode().strip())

def mux(video, audio, out):
    pad = max(0.0, dur(audio) - dur(video)) + 0.05
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio),
         "-filter_complex",
         f"[0:v]scale={W}:{H},fps={FPS},format=yuv420p,"
         f"tpad=stop_mode=clone:stop_duration={pad:.2f}[v]",
         "-map", "[v]", "-map", "1:a",
         "-c:v", "libx264", "-preset", "veryfast",
         "-c:a", "aac", "-ar", "44100", "-ac", "2",
         "-shortest", str(out)])

def concat(clips, out):
    lst = pathlib.Path(out).with_suffix(".txt")
    lst.write_text("".join(f"file '{pathlib.Path(c).resolve()}'\n" for c in clips))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
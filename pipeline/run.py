import json, os, pathlib, traceback
from pipeline.script import make_script
from pipeline.voice import speak
from pipeline import drawn, vector, card
from pipeline.media import concat

BUILD = pathlib.Path("build")

def build_scene(i, s, style):
    audio = BUILD / f"a{i:03d}.mp3"
    out = BUILD / f"c{i:03d}.mp4"
    speak(s["narration"], audio)

    if style == "drawn":
        try:
            if drawn.render(i, s["visual"], audio, out, BUILD.resolve()):
                return out, "drawn"
        except Exception:
            traceback.print_exc()

    try:
        img = BUILD / f"i{i:03d}.jpg"
        vector.image(f"{s['visual']}, flat vector illustration, bold colors, clean shapes, no text", img, seed=i)
        vector.clip(img, audio, out, i)
        return out, "vector"
    except Exception:
        traceback.print_exc()

    card.clip(s["narration"], audio, out)
    return out, "card"

def main():
    topic = (os.environ.get("TOPIC") or os.environ.get("ISSUE_TITLE", "")).removeprefix("video:").strip()
    topic = topic or "how the internet works"
    style = os.environ.get("STYLE", "drawn")
    if "style: vector" in os.environ.get("ISSUE_BODY", "").lower():
        style = "vector"
    n = int(os.environ.get("SCENES", "45"))

    BUILD.mkdir(parents=True, exist_ok=True)
    title, scenes = make_script(topic, style, n)
    (BUILD / "script.json").write_text(json.dumps({"title": title, "scenes": scenes}, indent=2))

    clips, modes = [], []
    for i, s in enumerate(scenes):
        out, mode = build_scene(i, s, style)
        clips.append(out)
        modes.append(mode)
        print(f"scene {i + 1}/{len(scenes)}: {mode}", flush=True)

    concat(clips, BUILD / "final.mp4")
    summary = {m: modes.count(m) for m in set(modes)}
    print(f"done: {title} {summary}")

if __name__ == "__main__":
    main()

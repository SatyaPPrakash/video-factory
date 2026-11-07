import re, subprocess, pathlib
from pipeline.llm import ask
from pipeline.media import mux

PROMPT = """Write a complete Python file for Manim Community v0.18 that starts with `from manim import *`.
Define exactly one class named {name}(Scene) whose construct(self) method animates this:
{visual}
Rules:
- Use only Text, Circle, Square, Rectangle, Line, Arrow, Dot, VGroup, Axes, NumberLine and the animations Create, Write, FadeIn, FadeOut, Transform, ReplacementTransform, GrowFromCenter, Indicate, LaggedStart.
- Do not use MathTex, Tex or LaTeX.
- Set self.camera.background_color = "#121826". Use colors like "#FFD166", "#06D6A0", "#EF476F", "#118AB2", "#FFFFFF".
- Keep everything inside x in [-6, 6] and y in [-3.4, 3.4]. Font sizes 28 to 48.
- Total run time 8 to 14 seconds, paced with self.wait().
- Output only Python code. No markdown fences."""

def _code(text):
    return re.sub(r"^```(?:python)?\s*|\s*```$", "", text.strip())

def render(i, visual, audio, out, work):
    name = f"Scene{i}"
    prompt = PROMPT.format(name=name, visual=visual)
    code = _code(ask(prompt))
    media = pathlib.Path(work) / "media"
    for _ in range(3):
        src = pathlib.Path(work) / f"s{i}.py"
        src.write_text(code)
        r = subprocess.run(["manim", "render", "-qm", "-v", "WARNING",
                            "--media_dir", str(media), "-o", f"clip{i}",
                            str(src), name], capture_output=True, text=True)
        found = list(media.rglob(f"clip{i}.mp4"))
        if r.returncode == 0 and found:
            mux(found[0], audio, out)
            return True
        err = (r.stderr or r.stdout)[-1200:]
        code = _code(ask(prompt + f"\n\nThe previous attempt failed with:\n{err}\n"
                                  f"Previous code:\n{code}\nReturn the corrected full file."))
    return False

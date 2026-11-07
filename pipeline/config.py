import os

_body = os.environ.get("ISSUE_BODY", "").lower()
FORMAT = (os.environ.get("FORMAT") or
          ("portrait" if "format: portrait" in _body else "landscape")).lower()
PORTRAIT = FORMAT == "portrait"

W, H = (720, 1280) if PORTRAIT else (1280, 720)
FPS = 25
MANIM_RES = f"{W},{H}"

if PORTRAIT:
    BOUNDS = "x in [-3.2, 3.2] and y in [-5.6, 5.6]"
    FONT = "36 to 56"
    LAYOUT = "Stack elements vertically, one idea per row."
else:
    BOUNDS = "x in [-6, 6] and y in [-3.4, 3.4]"
    FONT = "28 to 48"
    LAYOUT = "Arrange elements left to right."
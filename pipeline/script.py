import json, re
from pipeline.llm import ask

STYLES = {
    "drawn": "animated whiteboard-style diagrams built from lines, shapes, arrows, counters and labels",
    "vector": "flat vector illustrations with bold colors and clean shapes",
}

PROMPT = """You are writing a narrated explainer video.
Topic: {topic}
Visual style: {style}
Write exactly {n} scenes forming a spoken script of about {words} words.
Open with a hook, explain step by step, close with a memorable takeaway.
Each scene:
- "narration": 1-2 conversational sentences, 15-25 words, no markup.
- "visual": one concrete sentence describing what is drawn and how it animates. Keep it simple enough to draw with shapes and text.
Return only JSON: {{"title": "...", "scenes": [{{"narration": "...", "visual": "..."}}]}}"""

def _clean(text):
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())

def make_script(topic, style, n):
    raw = ask(PROMPT.format(topic=topic, style=STYLES[style], n=n, words=n * 19), json_mode=True)
    data = json.loads(_clean(raw))
    scenes = [s for s in data["scenes"] if s.get("narration") and s.get("visual")][:n]
    return data.get("title", topic), scenes

import os, time, requests

GEMINI = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]
_last = [0.0]

def _pace(gap=7.0):
    wait = gap - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()

def _gemini(prompt, model, json_mode):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7}}
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
           f":generateContent?key={os.environ['GEMINI_API_KEY']}")
    r = requests.post(url, json=body, timeout=180)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def _groq(prompt, json_mode):
    body = {"model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                      headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
                      json=body, timeout=180)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def ask(prompt, json_mode=False):
    last = None
    for attempt in range(2):
        for model in GEMINI:
            _pace()
            try:
                return _gemini(prompt, model, json_mode)
            except Exception as e:
                last = e
                time.sleep(3 + attempt * 10)
    if os.environ.get("GROQ_API_KEY"):
        for _ in range(2):
            try:
                return _groq(prompt, json_mode)
            except Exception as e:
                last = e
                time.sleep(10)
    raise RuntimeError(f"All LLM providers failed: {last}")

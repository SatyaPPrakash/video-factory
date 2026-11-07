import os, sys, time, requests

GEMINI = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]
GROQ_PREFERRED = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant"]
_last = [0.0]

def _log(msg):
    print(msg, file=sys.stderr, flush=True)

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
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def _groq_models():
    r = requests.get("https://api.groq.com/openai/v1/models",
                     headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
                     timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    ids = [m["id"] for m in r.json()["data"]]
    picked = [m for m in GROQ_PREFERRED if m in ids]
    return picked or [i for i in ids if "llama" in i and "guard" not in i][:3]

def _groq(prompt, model, json_mode):
    body = {"model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                      headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
                      json=body, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"]

def ask(prompt, json_mode=False):
    errors = []
    for attempt in range(2):
        for model in GEMINI:
            _pace()
            try:
                return _gemini(prompt, model, json_mode)
            except Exception as e:
                errors.append(f"gemini {model}: {e}")
                _log(errors[-1])
                time.sleep(3 + attempt * 10)
    if os.environ.get("GROQ_API_KEY"):
        try:
            models = _groq_models()
            _log(f"groq models to try: {models}")
        except Exception as e:
            models = []
            errors.append(f"groq models list: {e}")
            _log(errors[-1])
        for model in models[:3]:
            try:
                return _groq(prompt, model, json_mode)
            except Exception as e:
                errors.append(f"groq {model}: {e}")
                _log(errors[-1])
                time.sleep(5)
    else:
        errors.append("GROQ_API_KEY not set (backup skipped)")
    raise RuntimeError("All LLM providers failed:\n" + "\n".join(errors))
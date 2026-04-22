"""
server.py  —  Khan A.I. FastAPI Web Server
"""

# ── Load environment FIRST before any other imports ──────────────────────────
from dotenv import load_dotenv
import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ── Verify critical keys are present ─────────────────────────────────────────
# Railway uses its own env vars — make sure they map correctly
_groq_key    = os.environ.get("GroqAPIKey") or os.environ.get("GROQ_API_KEY")
_cohere_key  = os.environ.get("CohereAPIKey") or os.environ.get("COHERE_API_KEY")

if _groq_key:
    os.environ["GroqAPIKey"]    = _groq_key
    os.environ["GROQ_API_KEY"]  = _groq_key   # for groq library auto-detection
if _cohere_key:
    os.environ["CohereAPIKey"]  = _cohere_key

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import base64
import json
import sys

# ── Path setup ────────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.join(BASE_DIR, "Backend")
DATA_DIR    = os.path.join(BASE_DIR, "Data")
sys.path.insert(0, BACKEND_DIR)

os.makedirs(DATA_DIR, exist_ok=True)

# ── Import backend modules ────────────────────────────────────────────────────
from Chatbot              import ChatBot
from Model                import FirstLayerDMM
from RealtimeSearchEngine import RealtimeSearchEngine
from dotenv import dotenv_values

env_vars      = dotenv_values(os.path.join(BASE_DIR, ".env"))
Assistantname = env_vars.get("Assistantname", "Khan")
Username      = env_vars.get("Username", "User")

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="Khan A.I.", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ──────────────────────────────────────────────────────────────
graphics_path = os.path.join(BASE_DIR, "Frontend", "Graphics")
if os.path.exists(graphics_path):
    app.mount("/static", StaticFiles(directory=graphics_path), name="static")

# Serve Data folder (for generated images)
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

# ── HTML page ─────────────────────────────────────────────────────────────────
WEB_DIR = os.path.join(BASE_DIR, "Web")
os.makedirs(WEB_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h1>index.html not found in Web/ folder</h1>")

@app.get("/api/info")
async def info():
    return {"assistant": Assistantname, "user": Username}

# ── Web search using Tavily API (Railway compatible) ─────────────────────────
def web_search_and_answer(query: str) -> str:
    """
    Uses Tavily for general search + wttr.in for weather.
    Both work perfectly on Railway.
    """
    import datetime
    import requests as req
    from groq import Groq

    groq_client    = Groq(api_key=os.environ.get("GroqAPIKey"))
    tavily_key     = os.environ.get("TavilyAPIKey", "")
    search_context = ""
    now            = datetime.datetime.now()
    query_lower    = query.lower()

    # ── Weather — wttr.in ─────────────────────────────────────────────────────
    if any(w in query_lower for w in ["weather", "temperature", "forecast",
                                       "rain", "sunny", "humid", "climate", "mausam"]):
        try:
            import re
            city_match = (re.search(r'\bin\s+([a-zA-Z\s]+?)(?:\?|$|\.)', query_lower) or
                          re.search(r'\bof\s+([a-zA-Z\s]+?)(?:\?|$|\.)', query_lower))
            city = city_match.group(1).strip() if city_match else "Peshawar"
            if len(city) < 2: city = "Peshawar"

            resp = req.get(
                f"https://wttr.in/{city.replace(' ', '+')}?format=4",
                headers={"User-Agent": "curl/7.68.0"}, timeout=10
            )
            if resp.status_code == 200:
                search_context += f"Current weather: {resp.text}\n"
                print(f"[Weather] {resp.text}")
        except Exception as e:
            print(f"[Weather] Error: {e}")

    # ── General search — Tavily ───────────────────────────────────────────────
    if not search_context and tavily_key:
        try:
            resp = req.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": tavily_key,
                    "query":   query,
                    "max_results": 5,
                    "include_answer": True,
                },
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                # Use Tavily's direct answer if available
                if data.get("answer"):
                    search_context += f"Answer: {data['answer']}\n"
                # Add top results
                for r in data.get("results", [])[:3]:
                    search_context += f"• {r.get('title','')}: {r.get('content','')[:200]}\n"
                print(f"[Tavily] Got {len(data.get('results',[]))} results")
            else:
                print(f"[Tavily] Error {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"[Tavily] Error: {e}")

    # ── Fallback — DuckDuckGo HTML ────────────────────────────────────────────
    if not search_context:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
            resp    = req.get(
                f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}",
                headers=headers, timeout=12
            )
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup     = BeautifulSoup(resp.text, "html.parser")
                snippets = soup.find_all("a", class_="result__snippet", limit=4)
                for s in snippets:
                    search_context += f"• {s.get_text()}\n"
                print(f"[DDG] Got {len(snippets)} results")
        except Exception as e:
            print(f"[DDG] Error: {e}")

    # ── Ask Groq ──────────────────────────────────────────────────────────────
    system_msg   = (
        f"You are {Assistantname}, an advanced AI assistant.\n"
        f"Current date/time: {now.strftime('%A, %d %B %Y, %H:%M')}.\n"
        f"Answer accurately and professionally."
    )
    user_content = f"Based on this data:\n{search_context}\n\nQuestion: {query}" if search_context else query

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_content}
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=False,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq] Error: {e}")
        return "Sorry, I encountered an error. Please try again."

# ── Browser automation helper ─────────────────────────────────────────────────
def resolve_browser_action(decision: str) -> dict | None:
    """
    Converts automation commands into browser-executable actions.
    Returns a dict with 'action' and 'url' for the frontend to handle.
    """
    d = decision.strip().lower()

    # ── open websites / apps ──
    web_map = {
        "youtube":   "https://www.youtube.com",
        "google":    "https://www.google.com",
        "facebook":  "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "twitter":   "https://www.twitter.com",
        "linkedin":  "https://www.linkedin.com",
        "gmail":     "https://mail.google.com",
        "whatsapp":  "https://web.whatsapp.com",
        "github":    "https://www.github.com",
        "chatgpt":   "https://chat.openai.com",
        "netflix":   "https://www.netflix.com",
        "amazon":    "https://www.amazon.com",
        "wikipedia": "https://www.wikipedia.org",
    }

    if d.startswith("open "):
        app_name = d.removeprefix("open ").strip()
        url = web_map.get(app_name, f"https://www.{app_name}.com")
        return {"action": "open_url", "url": url, "label": f"Opening {app_name}..."}

    # ── play song on youtube ──
    if d.startswith("play "):
        song = d.removeprefix("play ").strip()
        url  = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
        return {"action": "open_url", "url": url, "label": f"Playing {song} on YouTube..."}

    # ── google search ──
    if d.startswith("google search "):
        query = d.removeprefix("google search ").strip()
        url   = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return {"action": "open_url", "url": url, "label": f"Searching Google for {query}..."}

    # ── youtube search ──
    if d.startswith("youtube search "):
        query = d.removeprefix("youtube search ").strip()
        url   = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return {"action": "open_url", "url": url, "label": f"Searching YouTube for {query}..."}

    return None

# ── Image generation helper ───────────────────────────────────────────────────
async def generate_and_serve_images(prompt: str) -> list[str]:
    """
    Generates images and returns list of base64 data URIs.
    No file system dependency — works on Railway perfectly.
    """
    try:
        import requests as req
        import asyncio
        from random import randint

        api_key   = os.environ.get("HuggingFaceAPIKey") or os.environ.get("HUGGINGFACE_API_KEY")
        API_URL   = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers   = {"Authorization": f"Bearer {api_key}"}

        async def query_single(seed):
            payload = {
                "inputs": f"{prompt}, high quality, 4k, detailed",
                "parameters": {"seed": seed}
            }
            response = await asyncio.to_thread(
                req.post, API_URL, headers=headers, json=payload, timeout=120
            )
            if response.status_code == 200:
                # Convert to base64 data URI
                import base64
                b64 = base64.b64encode(response.content).decode("utf-8")
                return f"data:image/jpeg;base64,{b64}"
            else:
                print(f"[ImageGen] Error {response.status_code}: {response.text}")
                return None

        tasks   = [query_single(randint(1, 1000000)) for _ in range(4)]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    except Exception as e:
        print(f"[ImageGen] Error: {e}")
        return []

# ── WebSocket chat ────────────────────────────────────────────────────────────
@app.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()

    async def send(obj: dict):
        await ws.send_text(json.dumps(obj))

    try:
        while True:
            data  = await ws.receive_text()
            payload = json.loads(data)
            query   = payload.get("query", "").strip()
            if not query:
                continue

            await send({"type": "status", "text": "Thinking..."})

            # ── Decision model ────────────────────────────────────
            try:
                decisions = await asyncio.to_thread(FirstLayerDMM, query)
            except Exception:
                decisions = [f"general {query}"]

            answered = False

            for decision in decisions:
                d = decision.strip()

                # ── General chat ──────────────────────────────────
                if d.startswith("general"):
                    q = d.removeprefix("general").strip() or query
                    # If query has realtime keywords, use web search instead
                    realtime_keywords = [
                        "weather", "temperature", "price", "news", "today",
                        "current", "latest", "now", "forecast", "stock",
                        "rate", "score", "result", "live", "update", "mausam"
                    ]
                    if any(kw in q.lower() for kw in realtime_keywords):
                        await send({"type": "status", "text": "Searching the web..."})
                        try:
                            answer = await asyncio.to_thread(web_search_and_answer, q)
                        except Exception as e:
                            print(f"[WS] Search error: {e}")
                            answer = await asyncio.to_thread(ChatBot, q)
                    else:
                        await send({"type": "status", "text": "Generating response..."})
                        answer = await asyncio.to_thread(ChatBot, q)
                    await stream_answer(ws, answer)
                    answered = True

                # ── Realtime search ───────────────────────────────
                elif d.startswith("realtime"):
                    q = d.removeprefix("realtime").strip() or query
                    await send({"type": "status", "text": "Searching the web..."})
                    try:
                        answer = await asyncio.to_thread(web_search_and_answer, q)
                    except Exception as e:
                        print(f"[WS] Realtime search error: {e}")
                        answer = "Sorry, search failed. Please try again."
                    await stream_answer(ws, answer)
                    answered = True

                # ── Image generation ──────────────────────────────
                elif d.startswith("generate image"):
                    prompt = d.removeprefix("generate image").strip()
                    await send({"type": "status", "text": f"Generating images for '{prompt}'..."})
                    urls = await generate_and_serve_images(prompt)
                    if urls:
                        await send({
                            "type":   "images",
                            "urls":   urls,
                            "prompt": prompt
                        })
                        await stream_answer(ws, f"Here are the generated images for '{prompt}'.")
                    else:
                        await stream_answer(ws, f"Sorry, image generation failed for '{prompt}'.")
                    answered = True

                # ── Exit ──────────────────────────────────────────
                elif d == "exit":
                    await stream_answer(ws, "Goodbye! It was a pleasure assisting you.")
                    answered = True

                # ── Browser automation ────────────────────────────
                else:
                    action = resolve_browser_action(d)
                    if action:
                        await send({"type": "status", "text": action["label"]})
                        await send({"type": "browser_action", **action})
                        await stream_answer(ws, action["label"])
                        answered = True
                    else:
                        # Unsupported on web (local PC automation)
                        await stream_answer(ws,
                            f"'{d}' requires local PC access and is only available in desktop mode.")
                        answered = True

            if not answered:
                await stream_answer(ws, "I didn't understand that. Could you rephrase?")

            await send({"type": "status", "text": "Listening..."})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_text(json.dumps({"type": "error", "text": str(e)}))
        except:
            pass


async def stream_answer(ws: WebSocket, answer: str):
    """Streams answer word by word for typewriter effect."""
    words = answer.split()
    chunk = ""
    for i, word in enumerate(words):
        chunk += word + " "
        if (i + 1) % 4 == 0 or i == len(words) - 1:
            await ws.send_text(json.dumps({
                "type": "chunk",
                "text": chunk,
                "done": (i == len(words) - 1),
                "full": answer
            }))
            chunk = ""
            await asyncio.sleep(0.03)


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"\n{'='*52}")
    print(f"  Khan A.I.  —  WEB SERVER")
    print(f"  Local  : http://localhost:{port}")
    print(f"  Network: http://0.0.0.0:{port}")
    print(f"{'='*52}\n")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
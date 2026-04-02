"""
server.py  —  Khan A.I. FastAPI Web Server
==========================================
Place in project ROOT. Run:
  Local  : uvicorn server:app --host 0.0.0.0 --port 8000
  Deploy : Procfile handles this automatically
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import base64
import json
import os
import sys

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
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
    Generates images and returns list of URLs accessible from browser.
    """
    try:
        from ImageGeneration import generate_images
        await generate_images(prompt)

        # Find generated image files
        safe_prompt = prompt.replace(" ", "_")
        urls = []
        for i in range(1, 5):
            filename = f"{safe_prompt}{i}.jpg"
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.exists(filepath):
                urls.append(f"/data/{filename}")
        return urls
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
                    await send({"type": "status", "text": "Generating response..."})
                    answer = await asyncio.to_thread(ChatBot, q)
                    await stream_answer(ws, answer)
                    answered = True

                # ── Realtime search ───────────────────────────────
                elif d.startswith("realtime"):
                    q = d.removeprefix("realtime").strip() or query
                    await send({"type": "status", "text": "Searching the web..."})
                    answer = await asyncio.to_thread(RealtimeSearchEngine, q)
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
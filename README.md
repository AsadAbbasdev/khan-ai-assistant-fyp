<div align="center">

```
██╗  ██╗██╗  ██╗ █████╗ ███╗   ██╗     █████╗ ██╗
██║ ██╔╝██║  ██║██╔══██╗████╗  ██║    ██╔══██╗██║
█████╔╝ ███████║███████║██╔██╗ ██║    ███████║██║
██╔═██╗ ██╔══██║██╔══██║██║╚██╗██║    ██╔══██║██║
██║  ██╗██║  ██║██║  ██║██║ ╚████║    ██║  ██║██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝
```

# ◈ KHAN A.I. — Virtual Artificial Intelligence Assistant

**An advanced AI-powered virtual assistant with real-time search, image generation,**
**voice interaction, automation, and a stunning futuristic UI.**

[![Python](https://img.shields.io/badge/Python-3.10+-00FFE5?style=for-the-badge&logo=python&logoColor=white&labelColor=060A10)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-00FFE5?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=060A10)](https://fastapi.tiangolo.com)
[![PyQt5](https://img.shields.io/badge/PyQt5-Desktop-00FFE5?style=for-the-badge&logo=qt&logoColor=white&labelColor=060A10)](https://riverbankcomputing.com/pyqt)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-00FFE5?style=for-the-badge&logoColor=white&labelColor=060A10)](https://groq.com)
[![Railway](https://img.shields.io/badge/Deployed-Railway-00FFE5?style=for-the-badge&logo=railway&logoColor=white&labelColor=060A10)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-00FFE5?style=for-the-badge&labelColor=060A10)](LICENSE)

---

### 🌐 [Live Demo](https://web-production-92916.up.railway.app) &nbsp;|&nbsp; 🖥️ Desktop Version Available &nbsp;|&nbsp; 📱 Mobile Responsive

</div>

---

## ⚡ What is Khan A.I.?

Khan A.I. is a **Final Year Project** — a fully functional virtual AI assistant inspired by JARVIS from Iron Man. It combines cutting-edge AI models with a premium glassmorphism UI to deliver an experience that feels truly futuristic.

Whether you're on a **desktop app** or accessing it through a **web browser on your phone**, Khan A.I. is always ready to assist you — 24 hours a day, 7 days a week.

---

## ✨ Features

| Feature | Desktop | Web |
|---------|---------|-----|
| 🤖 AI Chat (LLaMA 3.3 70B via Groq) | ✅ | ✅ |
| 🌐 Real-time Web Search (DuckDuckGo) | ✅ | ✅ |
| 🎨 AI Image Generation (FLUX.1) | ✅ | ✅ |
| 🗣️ Text-to-Speech (Edge TTS / Web Speech) | ✅ | ✅ |
| 🎤 Speech Recognition | ✅ | ✅ |
| 🤖 Task Automation (open/close apps) | ✅ | 🌐 Browser |
| 🎵 Play Music on YouTube | ✅ | ✅ |
| 🔍 Google & YouTube Search | ✅ | ✅ |
| 📝 Content Writing | ✅ | ✅ |
| ⏰ Reminders | ✅ | 🔜 |
| 🎵 Sci-Fi Sound Effects | ✅ | ✅ |
| 📱 Mobile Responsive | — | ✅ |

---

## 🖥️ UI Preview

```
┌─────────────────────────────────────────────────────────┐
│  ◈  KHAN A.I.          ⌂ HOME   ⌨ CHAT    ─  □  ✕     │
├──────────────────────┬──────────────────────────────────┤
│                      │  ◈ KHAN A.I. // CHAT TERMINAL   │
│   [ JARVIS GIF ]     │                                  │
│                      │  ▶ YOU                           │
│   Animated Orb       │  What is quantum computing?      │
│   Glassmorphism      │                                  │
│   Dark UI            │  ◈ KHAN A.I.                     │
│                      │  Quantum computing uses quantum  │
│  ● LISTENING...      │  mechanical phenomena...         │
│                      │                                  │
│      [ 🎤 ]          │  [ Enter command...    ] [SEND]  │
└──────────────────────┴──────────────────────────────────┘
```

> **Startup Screen:** Animated typewriter introduction with robot voice, sci-fi boot sequence, and pulsing orb animation.

---

## 🏗️ Project Structure

```
KHAN-AI-ASSISTANT-FYP/
│
├── 📄 main.py                    # Entry point (Desktop + Web modes)
├── 📄 server.py                  # FastAPI web server
├── 📄 requirements.txt           # All dependencies
├── 📄 Procfile                   # Railway deployment config
├── 📄 railway.json               # Railway settings
├── 📄 .env                       # API keys (not committed)
│
├── 📁 Backend/                   # Core AI logic
│   ├── Chatbot.py                # LLaMA 3.3 via Groq
│   ├── Model.py                  # Decision-making model (Cohere)
│   ├── RealtimeSearchEngine.py   # DuckDuckGo + Groq
│   ├── ImageGeneration.py        # FLUX.1 via HuggingFace
│   ├── Automation.py             # Task automation
│   ├── SpeechToText.py           # Selenium-based STT
│   └── TextToSpeech.py           # Edge TTS
│
├── 📁 Frontend/                  # Desktop UI (PyQt5)
│   ├── GUI.py                    # Main glassmorphism UI
│   ├── SoundEngine.py            # Sci-fi sound generation
│   └── Graphics/                 # Assets (GIF, icons, sounds)
│
├── 📁 Web/                       # Web UI
│   └── index.html                # Responsive web interface
│
└── 📁 Data/                      # Runtime data
    ├── ChatLog.json              # Conversation history
    └── Voice.html                # Speech recognition helper
```

---

## 🚀 Quick Start

### Option 1 — 🌐 Web Version (Recommended)
**No installation needed!** Just open in any browser:

```
https://web-production-92916.up.railway.app
```

Works on **Desktop, Mobile, Tablet** — anywhere! 📱💻

---

### Option 2 — 🖥️ Desktop Version

#### Prerequisites
- Python 3.10+
- Chrome browser (for speech recognition)

#### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/khan-ai-assistant-fyp.git
cd khan-ai-assistant-fyp

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

#### Configure `.env`

```env
Username          = Abbas
Assistantname     = Khan
GroqAPIKey        = your_groq_api_key
CohereAPIKey      = your_cohere_api_key
HuggingFaceAPIKey = your_huggingface_api_key
AssistantVoice    = en-US-GuyNeural
InputLanguage     = en-US
```

#### Run

```bash
# Desktop Mode (PyQt5 GUI)
python main.py

# Web Mode (FastAPI Server)
python main.py --web
# Then open: http://localhost:8000
```

---

## 🔑 API Keys — Where to Get Them

| API | Free Tier | Link |
|-----|-----------|------|
| **Groq** (LLaMA 3.3) | ✅ Free | [console.groq.com](https://console.groq.com) |
| **Cohere** (Decision Model) | ✅ Free | [dashboard.cohere.com](https://dashboard.cohere.com) |
| **HuggingFace** (Image Gen) | ✅ Free | [huggingface.co](https://huggingface.co/settings/tokens) |


## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│                    KHAN A.I. STACK                      │
├──────────────┬──────────────────────────────────────────┤
│   AI Models  │  LLaMA 3.3 70B (Groq) · Cohere R7B      │
│              │  FLUX.1 Schnell (HuggingFace)            │
├──────────────┼──────────────────────────────────────────┤
│   Backend    │  Python 3.10+ · FastAPI · WebSocket      │
│              │  Uvicorn · asyncio                       │
├──────────────┼──────────────────────────────────────────┤
│   Desktop UI │  PyQt5 · Custom Glassmorphism            │
│              │  pygame · pyttsx3 · edge-tts             │
├──────────────┼──────────────────────────────────────────┤
│   Web UI     │  HTML5 · CSS3 · Vanilla JS               │
│              │  Web Speech API · WebSocket              │
├──────────────┼──────────────────────────────────────────┤
│   Search     │  DuckDuckGo · BeautifulSoup4             │
├──────────────┼──────────────────────────────────────────┤
│   Deploy     │  Railway · GitHub Actions (Auto CD)      │
└──────────────┴──────────────────────────────────────────┘
```

---

## 🎯 How It Works

```
User Input (Voice/Text)
        │
        ▼
┌───────────────────┐
│  Decision Model   │  ◄── Cohere R7B
│  (What to do?)    │
└───────┬───────────┘
        │
   ┌────┴─────────────────────────┐
   │                              │
   ▼                              ▼
General Query              Realtime Query
   │                              │
   ▼                              ▼
ChatBot                   Web Search
(Groq LLaMA)           (DuckDuckGo + Groq)
   │                              │
   └────────────┬─────────────────┘
                │
                ▼
         Text Response
                │
                ▼
      Text-to-Speech (TTS)
      + Display on Screen
```

---

## 📱 Supported Platforms

| Platform | Desktop App | Web Browser |
|----------|-------------|-------------|
| Windows  | ✅ | ✅ |
| macOS    | ✅ | ✅ |
| Linux    | ✅ | ✅ |
| Android  | ❌ | ✅ Chrome |
| iOS      | ❌ | ✅ Safari |

---

## 🎨 UI Features

- **Glassmorphism Dark Theme** — Deep dark background with cyan accents
- **Animated Typewriter** — Startup introduction types character by character
- **Robot Voice** — AI speaks its introduction on startup
- **Sci-Fi Sound Effects** — Programmatically generated using NumPy/SciPy
- **Pulsing Orb Animation** — Synced with AI activity
- **CRT Scanline Effect** — Subtle futuristic overlay
- **Corner Bracket Frames** — Holographic UI elements
- **Mobile Responsive** — Adapts perfectly to any screen size

---

## 👨‍💻 Developer

<div align="center">

**Asad Abbas**
*Machine Learning Engineer & AI Scientist*
*Specializing in Artificial Intelligence & Natural Language Processing*

[![GitHub](https://img.shields.io/badge/GitHub-Follow-00FFE5?style=for-the-badge&logo=github&logoColor=white&labelColor=060A10)](https://github.com/AsadAbbasdev)

</div>

---

## 📄 License

```
MIT License — Free to use, modify, and distribute.
See LICENSE file for details.
```

---

<div align="center">

**⭐ If you found this useful, please star the repository! ⭐**

```
[ KHAN A.I. SYSTEM INITIALIZED ]
[ ALL SYSTEMS OPERATIONAL      ]
[ READY TO ASSIST — 24/7       ]
```

*Built with ❤️ as a Final Year Project*

</div>

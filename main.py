from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import sys
import os

# ==================== PATH FIX ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
# ==================================================

# ── Decide mode BEFORE importing heavy modules ────────────────────────────────
WEB_MODE = "--web" in sys.argv

# ══════════════════════════════════════════════════════════════════════════════
#  WEB MODE  →  python main.py --web
# ══════════════════════════════════════════════════════════════════════════════
if WEB_MODE:
    import uvicorn
    print("\n" + "="*52)
    print("  Khan A.I.  —  WEB MODE")
    print("  Desktop : http://localhost:8000")
    print("  Mobile  : http://<your-pc-ip>:8000")
    print("  (Find IP: run  ipconfig  in terminal)")
    print("="*52 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
    sys.exit(0)

# ══════════════════════════════════════════════════════════════════════════════
#  DESKTOP MODE  →  python main.py          (default)
# ══════════════════════════════════════════════════════════════════════════════
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model               import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation          import Automation
from Backend.SpeechToText        import SpeechRecognition
from Backend.Chatbot             import ChatBot
from Backend.TextToSpeech        import TextToSpeech

# ── Env ───────────────────────────────────────────────────────────────────────
env_vars       = dotenv_values(".env")
Username       = env_vars.get("Username")
Assistantname  = env_vars.get("Assistantname")

DefaultMessage = (
    f"{Username} : Hello {Assistantname}, How are you?\n"
    f"{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"
)

subprocesses = []
Function     = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# ── Helpers ───────────────────────────────────────────────────────────────────
def ShowDefaultChatIfNoChats():
    with open(os.path.join(BASE_DIR, 'Data', 'ChatLog.json'), "r", encoding='utf-8') as f:
        if len(f.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)

def ReadChatLogJson():
    with open(os.path.join(BASE_DIR, 'Data', 'ChatLog.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User",      Username      + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
        f.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as f:
        Data = f.read()
    if len(str(Data)) > 0:
        lines  = Data.split('\n')
        result = '\n'.join(lines)
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as f:
            f.write(result)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

# ── Main execution loop ───────────────────────────────────────────────────────
def MainExecution():
    TaskExecution        = False
    ImageExecution       = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    G = any(i for i in Decision if i.startswith("general"))
    R = any(i for i in Decision if i.startswith("realtime"))

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Function):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        img_path = os.path.join(BASE_DIR, "Frontend", "Files", "ImageGeneration.data")
        with open(img_path, "w") as f:
            f.write(f"{ImageGenerationQuery}, True")
        try:
            p1 = subprocess.Popen(
                ['python', os.path.join(BASE_DIR, 'Backend', 'ImageGeneration.py')],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                Answer = ChatBot(QueryModifier("Okay, Bye!"))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)

# ── Threads ───────────────────────────────────────────────────────────────────
def FirstThread():
    """Voice recognition + AI processing loop."""
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." not in AIStatus:
                SetAssistantStatus("Available...")
            else:
                sleep(0.1)

def SecondThread():
    """PyQt5 GUI — must run on main thread."""
    GraphicalUserInterface()

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*52)
    print("  Khan A.I.  —  DESKTOP MODE")
    print("  Tip: run  python main.py --web  for web mode")
    print("="*52 + "\n")

    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()   # GUI must be on main thread
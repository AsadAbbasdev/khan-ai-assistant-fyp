from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from ddgs import DDGS
import os

# ==================== PATH FIX ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
# ==================================================

env_path = os.path.join(PROJECT_DIR, ".env")
env_vars = dotenv_values(env_path)

def get_env(key):
    return env_vars.get(key) or os.environ.get(key)

Username      = get_env("Username")
Assistantname = get_env("Assistantname")
GroqAPIKey    = get_env("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

chatlog_path = os.path.join(PROJECT_DIR, "Data", "ChatLog.json")
os.makedirs(os.path.dirname(chatlog_path), exist_ok=True)
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except:
    with open(chatlog_path, "w") as f:
        dump([], f)

def GoogleSearch(query):
    Answer = f"The search results for '{query}' are:\n[start]\n"
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
        if not results:
            Answer += "No search results found.\n"
        else:
            for r in results:
                title   = r.get("title", "No Title")
                snippet = r.get("body", "No Description")
                url     = r.get("href", "No URL")
                Answer += f"Title: {title}\nURL: {url}\nDescription: {snippet}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    current_date_time = datetime.datetime.now()
    data  = f"Use This Real-time Information if needed:\n"
    data += f"Day: {current_date_time.strftime('%A')}\n"
    data += f"Date: {current_date_time.strftime('%d')}\n"
    data += f"Month: {current_date_time.strftime('%B')}\n"
    data += f"Year: {current_date_time.strftime('%Y')}\n"
    data += f"Time: {current_date_time.strftime('%H')} hours, {current_date_time.strftime('%M')} minutes, {current_date_time.strftime('%S')} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages
    with open(chatlog_path, "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )
    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})
    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
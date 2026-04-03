from groq import Groq
from json import load, dump
import datetime
from dotenv import load_dotenv
import os

# ==================== PATH FIX ====================
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
# ==================================================

# Load .env file if exists (local), Railway uses os.environ directly
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

Username      = os.environ.get("Username")
Assistantname = os.environ.get("Assistantname")
GroqAPIKey    = os.environ.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, which also has real-time up-to-date information from the internet.

*** When someone asks "Who created you?", "Who is your creator?", "Who made you?", or similar questions, always reply: 
"I was created by Asad Abbas — a brilliant Machine Learning Engineer and AI Scientist, who specializes in Artificial Intelligence and Natural Language Processing." ***

*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply in only English, even if the question is in Hindi, reply in English. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

chatlog_path = os.path.join(PROJECT_DIR, "Data", "ChatLog.json")
os.makedirs(os.path.dirname(chatlog_path), exist_ok=True)
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chatlog_path, "w") as f:
        dump([], f)

def Realtimeinformation():
    current_date_time = datetime.datetime.now()
    day    = current_date_time.strftime("%A")
    date   = current_date_time.strftime("%d")
    month  = current_date_time.strftime("%B")
    year   = current_date_time.strftime("%Y")
    hour   = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    date_info  = f"Please use this real-time information if needed,\n"
    date_info += f"Day: {day}\nDate: {date}\nMonth:{month}\nYear: {year}\n"
    date_info += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return date_info

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def ChatBot(Query):
    try:
        with open(chatlog_path, "r") as f:
            messages = load(f)
        messages.append({"role": "user", "content": f"{Query}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": Realtimeinformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        print(f"Error: {e}")
        with open(chatlog_path, "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
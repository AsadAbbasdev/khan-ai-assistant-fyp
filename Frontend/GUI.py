from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget,
                             QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont,
                         QPixmap, QTextBlockFormat, QLinearGradient, QPalette, QBrush,
                         QPen, QFontDatabase)
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtMultimedia import QSound
from dotenv import dotenv_values
import sys
import os
import math
import pyttsx3

# Fix import path so SoundEngine is always found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from SoundEngine import SoundManager

# Global sound manager (initialized once)
sfx = SoundManager()

# ==================== PATH FIX ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
# ==================================================

env_path = os.path.join(PROJECT_DIR, ".env")
env_vars = dotenv_values(env_path)
Assistantname = env_vars.get("Assistantname", "Khan")

TempDirPath = os.path.join(PROJECT_DIR, "Frontend", "Files")
GraphicsDirPath = os.path.join(PROJECT_DIR, "Frontend", "Graphics")

old_chat_message = ""

# ==================== INTRO TEXT ====================
INTRO_TEXT = (
    f"[ SYSTEM BOOT... OK ]\n"
    f"[ NEURAL NETWORK... ONLINE ]\n"
    f"[ VOICE MODULE... ACTIVE ]\n\n"
    f"Khan A.I. System is initialized.\n\n"
    f"First of all, allow me to introduce myself —\n"
    f"I am KHAN, a Virtual Artificial Intelligence,\n"
    f"and I am here to assist you with a variety of tasks,\n"
    f"24 hours a day, 7 days a week.\n\n"
    f"Your command is my priority. How may I serve you today?"
)

# ==================== COLORS ====================
BG_DARK       = "#060A10"
BG_PANEL      = "rgba(10, 20, 35, 200)"
ACCENT_CYAN   = "#00FFE5"
ACCENT_BLUE   = "#0A84FF"
ACCENT_PURPLE = "#7B2FFF"
GLASS_BG      = "rgba(255,255,255,0.04)"
GLASS_BORDER  = "rgba(0,255,229,0.18)"
TEXT_PRIMARY  = "#E8F4FF"
TEXT_DIM      = "#4A7A8A"

# ==================== HELPERS ====================
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how","what","who","where","when","why","which","whose","whom",
                      "can you","what's","where's","how's"]
    if any(word+" " in new_query for word in question_words):
        if query_words[-1] in ['.','?','!']:
            new_query = new_query[:-1]+"?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1]+"."
        else:
            new_query += "."
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(os.path.join(TempDirPath,'Mic.Data'),"w",encoding='utf-8') as f:
        f.write(Command)

def GetMicrophoneStatus():
    with open(os.path.join(TempDirPath,'Mic.Data'),"r",encoding='utf-8') as f:
        return f.read()

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath,'Status.data'),"w",encoding='utf-8') as f:
        f.write(Status)

def GetAssistantStatus():
    with open(os.path.join(TempDirPath,'Status.data'),"r",encoding='utf-8') as f:
        return f.read()

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    with open(os.path.join(TempDirPath,'Responses.data'),"w",encoding='utf-8') as f:
        f.write(Text)

# ==================== TYPEWRITER WORKER ====================
class TypewriterWorker(QThread):
    update_text  = pyqtSignal(str)
    finished     = pyqtSignal()

    def __init__(self, text, delay=38):
        super().__init__()
        self.text  = text
        self.delay = delay
        self._running = True

    def run(self):
        displayed = ""
        click_counter = 0
        for char in self.text:
            if not self._running:
                break
            displayed += char
            self.update_text.emit(displayed)
            # Play typing click every 2 visible characters (skip spaces/newlines)
            if char not in (' ', '\n', '\t'):
                click_counter += 1
                if click_counter % 2 == 0:
                    sfx.play_typing()
            self.msleep(self.delay)
        self.finished.emit()

    def stop(self):
        self._running = False

# ==================== VOICE WORKER ====================
class VoiceWorker(QThread):
    """Speaks the given text using pyttsx3 in a background thread."""

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        try:
            engine = pyttsx3.init()
            # ── Robot-like voice settings ──────────────────────────
            engine.setProperty('rate', 175)       # 175 wpm
            engine.setProperty('volume', 1.0)     # MAX volume

            # Try to pick a male voice for robotic feel
            voices = engine.getProperty('voices')
            for v in voices:
                if 'male' in v.name.lower() or 'david' in v.name.lower() or 'mark' in v.name.lower():
                    engine.setProperty('voice', v.id)
                    break

            # Speak only the clean part (skip the [ BOOT ] lines)
            clean_text = (
                "Khan A.I. System is initialized. "
                "First of all, allow me to introduce myself. "
                "I am KHAN, a Virtual Artificial Intelligence, "
                "and I am here to assist you with a variety of tasks, "
                "24 hours a day, 7 days a week. "
                "Your command is my priority. How may I serve you today?"
            )
            engine.say(clean_text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[VoiceWorker] Error: {e}")

# ==================== SCAN LINE OVERLAY ====================
class ScanlineOverlay(QWidget):
    """Subtle animated scanline for CRT feel."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._offset = 0
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(30)

    def _tick(self):
        self._offset = (self._offset + 2) % 8
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setOpacity(0.04)
        pen = QPen(QColor(0,255,229))
        pen.setWidth(1)
        p.setPen(pen)
        y = self._offset
        while y < self.height():
            p.drawLine(0, y, self.width(), y)
            y += 8
        p.end()

# ==================== CORNER BRACKET FRAME ====================
class CornerFrame(QWidget):
    """Draws glowing corner brackets around a widget."""
    def __init__(self, parent=None, color="#00FFE5", size=18, thick=2):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._color = QColor(color)
        self._size  = size
        self._thick = thick

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self._color, self._thick)
        p.setPen(pen)
        s = self._size
        w, h = self.width(), self.height()
        # TL
        p.drawLine(0, 0, s, 0)
        p.drawLine(0, 0, 0, s)
        # TR
        p.drawLine(w-s, 0, w, 0)
        p.drawLine(w,   0, w, s)
        # BL
        p.drawLine(0, h-s, 0, h)
        p.drawLine(0, h,   s, h)
        # BR
        p.drawLine(w-s, h, w, h)
        p.drawLine(w, h-s, w, h)
        p.end()

# ==================== GLOWING BUTTON ====================
class GlowButton(QPushButton):
    def __init__(self, text="", icon_path=None, parent=None,
                 color="#00FFE5", width=110, height=38):
        super().__init__(text, parent)
        self._color = color
        self.setFixedSize(width, height)
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(20, 20))
        self._apply_style(False)
        self.setCursor(Qt.PointingHandCursor)

    def _apply_style(self, hovered):
        c = self._color
        alpha = "40" if hovered else "18"
        border = "1.5px" if hovered else "1px"
        glow   = f"0 0 12px {c}88;" if hovered else ""
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0,255,229,{alpha});
                border: {border} solid {c};
                border-radius: 6px;
                color: {c};
                font-family: 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 2px;
                padding: 0 10px;
            }}
        """)

    def enterEvent(self, e):
        self._apply_style(True)

    def leaveEvent(self, e):
        self._apply_style(False)

# ==================== MIC BUTTON ====================
class MicButton(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.toggled = True
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse)
        self._pulse_alpha = 255
        self._pulse_dir   = -6
        self._load_icon()

    def _load_icon(self):
        name = "Mic_on.png" if not self.toggled else "Mic_on.png"
        p = GraphicsDirectoryPath(name)
        if os.path.exists(p):
            px = QPixmap(p).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(px)
        self.setStyleSheet(f"""
            QLabel {{
                background: rgba(0,255,229,0.10);
                border: 1.5px solid {ACCENT_CYAN};
                border-radius: 32px;
            }}
        """)

    def _pulse(self):
        self._pulse_alpha += self._pulse_dir
        if self._pulse_alpha <= 80 or self._pulse_alpha >= 255:
            self._pulse_dir = -self._pulse_dir
        self.setStyleSheet(f"""
            QLabel {{
                background: rgba(0,255,229,{int(self._pulse_alpha*0.10/255*100)});
                border: 1.5px solid rgba(0,255,229,{self._pulse_alpha});
                border-radius: 32px;
            }}
        """)

    def mousePressEvent(self, event):
        self.toggled = not self.toggled
        if self.toggled:
            MicButtonInitialed()
            self._pulse_timer.stop()
            name = "Mic_on.png"
        else:
            MicButtonClosed()
            self._pulse_timer.start(30)
            name = "mic_off.png"
        p = GraphicsDirectoryPath(name)
        if os.path.exists(p):
            px = QPixmap(p).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(px)

# ==================== INTRO SCREEN ====================
class IntroScreen(QWidget):
    intro_done = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._build_ui()
        self._start_intro()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_DARK};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── GIF — NO box, NO border, full transparent, centered ──
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setStyleSheet("background: transparent; border: none;")
        gif_path = GraphicsDirectoryPath("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            # Bigger GIF size
            movie.setScaledSize(QSize(680, 382))
            self.gif_label.setMovie(movie)
            movie.start()
        root.addWidget(self.gif_label, stretch=3)

        # ── Terminal typewriter — no box feel, dark blueish bg ───
        term_outer = QWidget()
        term_outer.setStyleSheet("background: transparent;")
        term_layout = QVBoxLayout(term_outer)
        term_layout.setContentsMargins(80, 0, 80, 8)

        self.term_box = QTextEdit()
        self.term_box.setReadOnly(True)
        self.term_box.setFrameStyle(QFrame.NoFrame)
        self.term_box.setFixedHeight(220)
        self.term_box.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(2, 8, 20, 0.82);
                border: none;
                border-left: 2px solid {ACCENT_CYAN}55;
                color: {ACCENT_CYAN};
                font-family: 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
                padding: 16px 22px;
                letter-spacing: 1px;
                line-height: 1.6;
            }}
            QScrollBar:vertical {{ width: 0px; }}
        """)
        term_layout.addWidget(self.term_box)
        root.addWidget(term_outer, stretch=2)

        # ── Status + mic ──────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setContentsMargins(80, 4, 80, 28)

        self.status_label = QLabel("● INITIALIZING...")
        self.status_label.setStyleSheet(f"""
            color: {ACCENT_CYAN};
            font-family: 'Courier New', monospace;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 4px;
        """)
        bottom.addWidget(self.status_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        bottom.addStretch()

        self.mic_btn = MicButton()
        bottom.addWidget(self.mic_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)

        root.addLayout(bottom)

        # scanline overlay
        self._scanline = ScanlineOverlay(self)

        # corners
        self._corners = CornerFrame(self)

    def resizeEvent(self, event):
        self._scanline.setGeometry(self.rect())
        self._corners.setGeometry(self.rect())
        super().resizeEvent(event)

    def _start_intro(self):
        self._worker = TypewriterWorker(INTRO_TEXT, delay=32)
        self._worker.update_text.connect(self._on_type)
        self._worker.finished.connect(self._on_intro_done)

        def _launch_voice():
            self._voice = VoiceWorker("")
            self._voice.start()

        # ── Sound timeline ─────────────────────────────────────────
        # 0 ms   : boot beep sequence
        # 200 ms : ambient hum starts (low volume background)
        # 600 ms : typewriter starts + whoosh
        # 1800 ms: voice starts + ting
        QTimer.singleShot(0,    sfx.play_boot)
        QTimer.singleShot(200,  sfx.start_ambient)
        QTimer.singleShot(600,  sfx.play_whoosh)
        QTimer.singleShot(600,  self._worker.start)
        QTimer.singleShot(1800, _launch_voice)
        QTimer.singleShot(1800, sfx.play_ting)

    def _on_type(self, text):
        self.term_box.setPlainText(text)
        self.term_box.verticalScrollBar().setValue(
            self.term_box.verticalScrollBar().maximum())

    def _on_intro_done(self):
        self.status_label.setText("● SYSTEM READY")
        sfx.play_system_ready()
        QTimer.singleShot(1200, sfx.play_transition)
        QTimer.singleShot(2200, self.intro_done.emit)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'),"r",encoding='utf-8') as f:
                txt = f.read()
            self.status_label.setText(f"● {txt.upper()}")
        except:
            pass

# ==================== CHAT SECTION ====================
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRocogText)
        self.timer.start(5)

    def _build_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header bar inside chat
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 0)
        dot_green  = QLabel("●"); dot_green.setStyleSheet(f"color:#00FF88; font-size:10px;")
        dot_yellow = QLabel("●"); dot_yellow.setStyleSheet("color:#FFD700; font-size:10px;")
        dot_red    = QLabel("●"); dot_red.setStyleSheet("color:#FF4455; font-size:10px;")
        title = QLabel("KHAN A.I. // CHAT TERMINAL")
        title.setStyleSheet(f"""
            color: {ACCENT_CYAN};
            font-family: 'Courier New', monospace;
            font-size: 11px;
            letter-spacing: 3px;
        """)
        hdr.addWidget(dot_red)
        hdr.addWidget(dot_yellow)
        hdr.addWidget(dot_green)
        hdr.addSpacing(8)
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"border: none; border-top: 1px solid {ACCENT_CYAN}33;")
        layout.addWidget(line)

        # Chat display
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                color: {TEXT_PRIMARY};
                font-family: 'Courier New', monospace;
                font-size: 13px;
                padding: 4px 8px;
                border: none;
            }}
            QScrollBar:vertical {{
                background: rgba(0,255,229,0.05);
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {ACCENT_CYAN}66;
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        layout.addWidget(self.chat_text_edit, stretch=1)

        # Status label
        self.label = QLabel("")
        self.label.setStyleSheet(f"""
            color: {ACCENT_CYAN};
            font-family: 'Courier New', monospace;
            font-size: 11px;
            letter-spacing: 2px;
            padding: 2px 0;
        """)
        layout.addWidget(self.label)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath('Responses.data'),"r",encoding='utf-8') as f:
                messages = f.read()
            if messages and messages != old_chat_message:
                self.addMessage(messages, ACCENT_CYAN)
                old_chat_message = messages
        except:
            pass

    def SpeechRocogText(self):
        try:
            with open(TempDirectoryPath('Status.data'),"r",encoding='utf-8') as f:
                txt = f.read()
            self.label.setText(f"● {txt}")
        except:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt    = QTextCharFormat()
        fmtb   = QTextBlockFormat()
        fmtb.setTopMargin(8)
        fmtb.setLeftMargin(6)
        fmt.setForeground(QColor(color))
        cursor.setBlockFormat(fmtb)
        cursor.setCharFormat(fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.verticalScrollBar().setValue(
            self.chat_text_edit.verticalScrollBar().maximum())

# ==================== MAIN SCREEN (GIF + CHAT SIDE BY SIDE) ====================
class MainScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {BG_DARK};")
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # ── LEFT: GIF panel ──────────────────────────────────────
        left_wrap = QWidget()
        left_wrap.setMinimumWidth(460)
        left_wrap.setMaximumWidth(540)
        left_wrap.setStyleSheet(f"""
            background: rgba(0,20,30,0.70);
            border: 1px solid {ACCENT_CYAN}28;
            border-radius: 14px;
        """)
        left_layout = QVBoxLayout(left_wrap)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        gif_path = GraphicsDirectoryPath("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(500, 320))
            self.gif_label.setMovie(movie)
            movie.start()
        left_layout.addWidget(self.gif_label, stretch=1)

        # Status / speech text
        self.status_lbl = QLabel("● LISTENING...")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet(f"""
            color: {ACCENT_CYAN};
            font-family: 'Courier New', monospace;
            font-size: 12px;
            letter-spacing: 3px;
            padding: 10px;
            border-top: 1px solid {ACCENT_CYAN}22;
            background: rgba(0,255,229,0.04);
        """)
        left_layout.addWidget(self.status_lbl)

        # Mic button
        mic_row = QHBoxLayout()
        mic_row.setContentsMargins(0, 8, 0, 12)
        self.mic_btn = MicButton()
        mic_row.addStretch()
        mic_row.addWidget(self.mic_btn)
        mic_row.addStretch()
        left_layout.addLayout(mic_row)

        # Corner brackets on left panel
        self._left_corners = CornerFrame(left_wrap)

        root.addWidget(left_wrap)

        # ── RIGHT: Chat panel ─────────────────────────────────────
        right_wrap = QWidget()
        right_wrap.setStyleSheet(f"""
            background: rgba(0,20,30,0.70);
            border: 1px solid {ACCENT_CYAN}28;
            border-radius: 14px;
        """)
        right_layout = QVBoxLayout(right_wrap)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.chat = ChatSection()
        right_layout.addWidget(self.chat, stretch=1)

        # Input area
        input_bar = QWidget()
        input_bar.setStyleSheet(f"""
            background: rgba(0,255,229,0.04);
            border-top: 1px solid {ACCENT_CYAN}22;
            border-radius: 0 0 14px 14px;
        """)
        input_layout = QHBoxLayout(input_bar)
        input_layout.setContentsMargins(14, 10, 14, 10)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,255,229,0.07);
                border: 1px solid {ACCENT_CYAN}44;
                border-radius: 6px;
                color: {TEXT_PRIMARY};
                font-family: 'Courier New', monospace;
                font-size: 13px;
                padding: 8px 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_CYAN}AA;
            }}
        """)
        self.input_field.returnPressed.connect(self._send_message)

        send_btn = GlowButton("SEND ▶", width=90, height=38)
        send_btn.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)

        right_layout.addWidget(input_bar)

        self._right_corners = CornerFrame(right_wrap)
        root.addWidget(right_wrap, stretch=1)

        # scanline
        self._scanline = ScanlineOverlay(self)

        # status poll + orb pulse sound (every ~4 seconds)
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._poll_status)
        self._status_timer.start(100)

        self._pulse_counter = 0
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._orb_pulse_sound)
        self._pulse_timer.start(4000)   # pulse sound every 4s

        # whoosh when this screen first appears
        QTimer.singleShot(100, sfx.play_whoosh)

    def resizeEvent(self, event):
        self._scanline.setGeometry(self.rect())
        # update corner frames
        for child in self.findChildren(CornerFrame):
            child.setGeometry(child.parent().rect())
        super().resizeEvent(event)

    def _poll_status(self):
        try:
            with open(TempDirectoryPath('Status.data'),"r",encoding='utf-8') as f:
                txt = f.read()
            self.status_lbl.setText(f"● {txt.upper()}")
        except:
            pass

    def _orb_pulse_sound(self):
        """Soft energy pulse synced with GIF glow cycle."""
        sfx.play_pulse()

    def _send_message(self):
        text = self.input_field.text().strip()
        if text:
            sfx.play_ui_tap()
            ShowTextToScreen(f"You: {text}")
            self.input_field.clear()

# ==================== TOP BAR ====================
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self._init_ui()

    def _init_ui(self):
        self.setFixedHeight(46)
        self.setStyleSheet(f"""
            background: rgba(4, 12, 22, 0.97);
            border-bottom: 1px solid {ACCENT_CYAN}33;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(6)

        # Logo / title
        title = QLabel(f"◈  {str(Assistantname).upper()} A.I.")
        title.setStyleSheet(f"""
            color: {ACCENT_CYAN};
            font-family: 'Courier New', monospace;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 4px;
        """)
        layout.addWidget(title)
        layout.addStretch()

        # Nav buttons
        home_btn = GlowButton("⌂  HOME", width=100, height=30)
        chat_btn = GlowButton("⌨  CHAT", width=100, height=30)
        home_btn.clicked.connect(lambda: (sfx.play_ui_tap(), self.stacked_widget.setCurrentIndex(0)))
        chat_btn.clicked.connect(lambda: (sfx.play_ui_tap(), self.stacked_widget.setCurrentIndex(1)))
        layout.addWidget(home_btn)
        layout.addWidget(chat_btn)
        layout.addSpacing(16)

        # Window controls
        min_btn   = self._wbtn("─", "#FFD700", self._minimize)
        max_btn   = self._wbtn("□", "#00FF88", self._maximize)
        close_btn = self._wbtn("✕", "#FF4455", self._close)
        layout.addWidget(min_btn)
        layout.addWidget(max_btn)
        layout.addWidget(close_btn)

        self.draggable = True
        self.offset    = None

    def _wbtn(self, symbol, color, slot):
        b = QPushButton(symbol)
        b.setFixedSize(24, 24)
        b.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.06);
                border: 1px solid {color}66;
                border-radius: 12px;
                color: {color};
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {color}33;
                border: 1px solid {color};
            }}
        """)
        b.setCursor(Qt.PointingHandCursor)
        b.clicked.connect(slot)
        return b

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(4, 12, 22, 245))
        super().paintEvent(event)

    def _minimize(self): self.parent().showMinimized()
    def _maximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()
    def _close(self): self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            self.parent().move(event.globalPos() - self.offset)

# ==================== MAIN WINDOW ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._init_ui()

    def _init_ui(self):
        desktop      = QApplication.desktop()
        sw           = desktop.screenGeometry().width()
        sh           = desktop.screenGeometry().height()
        self.setGeometry(0, 0, sw, sh)
        self.setStyleSheet(f"background-color: {BG_DARK};")

        # Stacked widget
        self.stack = QStackedWidget(self)

        # Screen 0: Intro
        self.intro = IntroScreen()
        self.intro.intro_done.connect(lambda: self.stack.setCurrentIndex(1))

        # Screen 1: Main (GIF + Chat)
        self.main_screen = MainScreen()

        self.stack.addWidget(self.intro)
        self.stack.addWidget(self.main_screen)

        top_bar = CustomTopBar(self, self.stack)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(self.stack)

# ==================== ENTRY ====================
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
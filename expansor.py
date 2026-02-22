import sys
import json
import os
import time
import signal
import subprocess
import tempfile
from pynput.keyboard import Key, Controller, Listener
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QTextEdit, QLineEdit, 
                             QPushButton, QLabel, QMessageBox, QToolBar)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData, QTimer, QObject

# Caminhos absolutos e uso do tempfile para compatibilidade universal
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "modelos.json")
PID_FILE = os.path.join(tempfile.gettempdir(), "expansor_rt.pid")

# =====================================================================
# LÓGICA DE SEGUNDO PLANO (DAEMON / ESCUTA DO TECLADO)
# =====================================================================

class ExpanderThread(QThread):
    trigger_expansion = pyqtSignal(str)

    def __init__(self, shortcuts):
        super().__init__()
        self.shortcuts = shortcuts
        self.buffer = ""
        self.listener = None

    def run(self):
        with Listener(on_press=self.on_press) as self.listener:
            self.listener.join()

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                self.buffer += key.char
            elif key == Key.space:
                self.buffer += ' '
            elif key == Key.enter:
                self.buffer += '\n'
            elif key == Key.backspace:
                self.buffer = self.buffer[:-1]
            elif key in (Key.shift, Key.shift_r, Key.ctrl, Key.ctrl_r, Key.alt, Key.alt_gr, Key.caps_lock):
                pass
            else:
                self.buffer = ""
        except Exception:
            self.buffer = ""

        if len(self.buffer) > 50:
            self.buffer = self.buffer[-50:]

        for abbr in self.shortcuts.keys():
            if self.buffer.endswith(abbr):
                self.buffer = "" 
                self.trigger_expansion.emit(abbr)
                break

    def update_shortcuts(self, shortcuts):
        self.shortcuts = shortcuts

class DaemonApp(QObject):
    def __init__(self):
        super().__init__()
        self.shortcuts = self.load_data()
        self.last_mtime = self.get_file_mtime()
        
        self.keyboard_controller = Controller()
        
        self.expander_thread = ExpanderThread(self.shortcuts)
        self.expander_thread.trigger_expansion.connect(self.expand_text)
        self.expander_thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(1000)

    def load_data(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_file_mtime(self):
        return os.path.getmtime(DB_FILE) if os.path.exists(DB_FILE) else 0

    def check_for_updates(self):
        current_mtime = self.get_file_mtime()
        if current_mtime > self.last_mtime:
            self.shortcuts = self.load_data()
            self.expander_thread.update_shortcuts(self.shortcuts)
            self.last_mtime = current_mtime

    def expand_text(self, abbreviation):
        html_content = self.shortcuts.get(abbreviation)
        if not html_content: return

        for _ in range(len(abbreviation)):
            self.keyboard_controller.press(Key.backspace)
            self.keyboard_controller.release(Key.backspace)
            time.sleep(0.01)

        clipboard = QApplication.clipboard()
        new_mime = QMimeData()
        new_mime.setHtml(html_content)
        
        fallback_text = QTextEdit()
        fallback_text.setHtml(html_content)
        new_mime.setText(fallback_text.toPlainText()) 
        
        clipboard.setMimeData(new_mime)
        time.sleep(0.05) 

        self.keyboard_controller.press(Key.ctrl)
        self.keyboard_controller.press('v')
        self.keyboard_controller.release('v')
        self.keyboard_controller.release(Key.ctrl)

# =====================================================================
# INTERFACE GRÁFICA
# =====================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Expansor - Editor de Modelos")
        self.resize(850, 550)
        self.shortcuts = self.load_data()
        self.setup_ui()
        self.update_list()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.load_selected)
        left_panel.addWidget(QLabel("<b>Seus Modelos:</b>"))
        left_panel.addWidget(self.list_widget)
        
        btn_novo = QPushButton("Novo Modelo")
        btn_novo.clicked.connect(self.clear_fields)
        left_panel.addWidget(btn_novo)

        right_panel = QVBoxLayout()
        
        abbr_layout = QHBoxLayout()
        abbr_layout.addWidget(QLabel("Atalho (ex: /sig):"))
        self.abbr_input = QLineEdit()
        abbr_layout.addWidget(self.abbr_input)
        right_panel.addLayout(abbr_layout)

        toolbar = QToolBar()
        right_panel.addWidget(toolbar)
        
        btn_bold = QAction("Negrito", self)
        btn_bold.triggered.connect(lambda: self.text_editor.setFontWeight(QFont.Weight.Bold if self.text_editor.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal))
        toolbar.addAction(btn_bold)

        btn_italic = QAction("Itálico", self)
        btn_italic.triggered.connect(lambda: self.text_editor.setFontItalic(not self.text_editor.fontItalic()))
        toolbar.addAction(btn_italic)
        
        btn_underline = QAction("Sublinhado", self)
        btn_underline.triggered.connect(lambda: self.text_editor.setFontUnderline(not self.text_editor.fontUnderline()))
        toolbar.addAction(btn_underline)

        toolbar.addSeparator()

        btn_align_left = QAction("Esquerda", self)
        btn_align_left.triggered.connect(lambda: self.text_editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        toolbar.addAction(btn_align_left)

        btn_align_center = QAction("Centro", self)
        btn_align_center.triggered.connect(lambda: self.text_editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        toolbar.addAction(btn_align_center)

        btn_align_right = QAction("Direita", self)
        btn_align_right.triggered.connect(lambda: self.text_editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        toolbar.addAction(btn_align_right)

        btn_align_justify = QAction("Justificado", self)
        btn_align_justify.triggered.connect(lambda: self.text_editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        toolbar.addAction(btn_align_justify)

        self.text_editor = QTextEdit()
        right_panel.addWidget(self.text_editor)

        action_layout = QHBoxLayout()
        btn_save = QPushButton("Salvar Modelo")
        btn_save.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        btn_save.clicked.connect(self.save_model)
        
        btn_delete = QPushButton("Remover")
        btn_delete.setStyleSheet("background-color: #c62828; color: white; padding: 8px; border-radius: 4px;")
        btn_delete.clicked.connect(self.delete_model)
        
        action_layout.addWidget(btn_save)
        action_layout.addWidget(btn_delete)
        right_panel.addLayout(action_layout)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)

    def load_data(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.shortcuts, f, indent=4)

    def update_list(self):
        self.list_widget.clear()
        # Organiza os itens em ordem alfabética na interface gráfica
        for abbr in sorted(self.shortcuts.keys(), key=str.lower):
            self.list_widget.addItem(abbr)

    def clear_fields(self):
        self.abbr_input.clear()
        self.text_editor.clear()
        self.list_widget.clearSelection()

    def load_selected(self, item):
        abbr = item.text()
        self.abbr_input.setText(abbr)
        self.text_editor.setHtml(self.shortcuts[abbr])

    def save_model(self):
        abbr = self.abbr_input.text().strip()
        html_content = self.text_editor.toHtml()
        
        if not abbr:
            QMessageBox.warning(self, "Aviso", "O atalho não pode estar vazio!")
            return
            
        self.shortcuts[abbr] = html_content
        self.save_data()
        self.update_list()
        
        # Encontra e seleciona o item recém-salvo (já que a ordem mudou)
        items = self.list_widget.findItems(abbr, Qt.MatchFlag.MatchExactly)
        if items:
            self.list_widget.setCurrentItem(items[0])

    def delete_model(self):
        abbr = self.abbr_input.text().strip()
        if abbr in self.shortcuts:
            del self.shortcuts[abbr]
            self.save_data()
            self.update_list()
            self.clear_fields()

# =====================================================================
# GERENCIAMENTO DE COMANDOS (CLI) MULTIPLATAFORMA
# =====================================================================

def get_pid():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return None
    return None

def check_pid(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python expansor.py [start | stop | status | set]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        pid = get_pid()
        if pid and check_pid(pid):
            print(f"O Expansor já está rodando em segundo plano (PID: {pid}).")
            return
        
        print("Iniciando o Expansor em segundo plano...")
        
        # Configuração universal para rodar em background
        kwargs = {}
        if os.name == 'nt':  # Windows
            kwargs['creationflags'] = 0x00000008  # DETACHED_PROCESS
        else:  # Linux / Mac
            kwargs['start_new_session'] = True
            
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "run-daemon"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         **kwargs)
        print("Expansor iniciado com sucesso! Use 'set' para editar os modelos.")

    elif command == "stop":
        pid = get_pid()
        if pid and check_pid(pid):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass # Caso o processo já tenha morrido
            
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            print("Expansor encerrado.")
        else:
            print("O Expansor não está rodando.")
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)

    elif command == "status":
        pid = get_pid()
        if pid and check_pid(pid):
            print(f"🟢 Status: RODANDO (PID: {pid})")
        else:
            print("🔴 Status: PARADO")

    elif command == "set":
        app = QApplication(sys.argv)
        app.setStyle("Fusion") 
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    elif command == "run-daemon":
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
            
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        daemon = DaemonApp()
        sys.exit(app.exec())

    else:
        print("Comando inválido. Use: start, stop, status, set")

if __name__ == '__main__':
    main()

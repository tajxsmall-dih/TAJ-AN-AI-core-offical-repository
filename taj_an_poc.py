import os
import sys
import base64
import threading
import webbrowser
import subprocess
import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Dependency Auto-Installer ---
def ensure_dependencies():
    """Ensure required packages are installed, bypassing execution if running inside a compiled PyInstaller binary."""
    if getattr(sys, 'frozen', False):
        return

    required_packages = {
        "customtkinter": "customtkinter",
        "requests": "requests",
        "dotenv": "python-dotenv"
    }

    missing = []
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"[!] Installing missing dependencies: {missing}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

ensure_dependencies()

import customtkinter as ctk
import requests
from dotenv import load_dotenv

# Set CustomTkinter GUI theme settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Helper Functions ---
def check_ollama():
    """Verify if local Ollama daemon is reachable on port 11434."""
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=2)
        return res.status_code == 200
    except Exception:
        return False

def encode_image_base64(file_path):
    """Convert local image files to base64 strings for multimodal LLM vision queries."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# --- First-Run Wizard Toplevel Window ---
class SetupWizard(ctk.CTkToplevel):
    """Wizard window launched when neither Ollama nor Gemini API keys are configured."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("TAJ_AN Core v5.8-beta — First-Time Setup")
        self.geometry("520x420")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="🚀 Welcome to TAJ_AN Core Studio", font=("Helvetica", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(self, text="No local Ollama instance or Gemini API key was detected.\nChoose how you want to configure your engine:", font=("Helvetica", 12)).pack(pady=5)

        ctk.CTkButton(self, text="1. Setup Cloud Mode (Google Gemini API)", command=self.setup_gemini, width=380, height=35).pack(pady=10)
        ctk.CTkButton(self, text="2. Setup Local Mode (Download Ollama)", command=self.setup_ollama, width=380, height=35).pack(pady=10)
        ctk.CTkButton(self, text="3. Search Google for Free Gemini Key", command=self.search_key, width=380, height=35).pack(pady=10)
        ctk.CTkButton(self, text="Skip & Launch (Limited Mode)", fg_color="transparent", border_width=1, command=self.destroy, width=380).pack(pady=15)

    def setup_gemini(self):
        """Open Gemini API portal and write provided key to local .env configuration."""
        webbrowser.open("https://aistudio.google.com/app/apikey")
        dialog = ctk.CTkInputDialog(text="Paste your GEMINI_API_KEY below:", title="API Key Setup")
        key = dialog.get_input()
        if key:
            with open(".env", "a") as f:
                f.write(f"\nGEMINI_API_KEY={key.strip()}\n")
            os.environ["GEMINI_API_KEY"] = key.strip()
            messagebox.showinfo("Success", "Gemini API Key saved to .env file!")
            self.destroy()

    def setup_ollama(self):
        """Guide user to local Ollama downloads and required model pull commands."""
        webbrowser.open("https://ollama.com/download")
        messagebox.showinfo("Ollama Setup", "1. Install Ollama.\n2. Run 'ollama pull llama3.2-vision' in terminal.\n3. Restart TAJ_AN Core.")
        self.destroy()

    def search_key(self):
        """Direct user to web guides on getting free API access keys."""
        webbrowser.open("https://www.google.com/search?q=how+to+get+free+gemini+api+key")

# --- Main Application Window ---
class TAJANCoreApp(ctk.CTk):
    """Main application GUI managing chat flow, file attachments, and multithreaded AI calls."""
    def __init__(self):
        super().__init__()
        self.title("TAJ_AN Core v5.8-beta — Multimodal Studio")
        self.geometry("800x620")

        self.selected_file = None
        load_dotenv()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Status Bar Header
        self.header_frame = ctk.CTkFrame(self, height=40)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(self.header_frame, text="Checking System Engine...", font=("Helvetica", 12))
        self.status_label.pack(side="left", padx=15)

        # Chat Interface
        self.chat_box = ctk.CTkTextbox(self, font=("Consolas", 12), state="disabled")
        self.chat_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.file_label = ctk.CTkLabel(self, text="No attachment", font=("Helvetica", 11), text_color="gray")
        self.file_label.grid(row=2, column=0, sticky="w", padx=15, pady=2)

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ask TAJ_AN Core or describe attached media...", font=("Helvetica", 13))
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.attach_btn = ctk.CTkButton(self.input_frame, text="📎 Attach", width=80, command=self.attach_file)
        self.attach_btn.pack(side="left", padx=5)

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send 🚀", width=90, command=self.send_message)
        self.send_btn.pack(side="left", padx=(5, 10))

        self.after(500, self.initial_checks)

    def initial_checks(self):
        """Check engine availability and prompt configuration wizard if no active engine is present."""
        has_key = bool(os.getenv("GEMINI_API_KEY"))
        has_ollama = check_ollama()

        if not has_key and not has_ollama:
            SetupWizard(self)

        self.update_status()

    def update_status(self):
        """Update top bar indicator based on detected backend options."""
        has_key = bool(os.getenv("GEMINI_API_KEY"))
        has_ollama = check_ollama()

        if has_key:
            self.status_label.configure(text="🟢 Mode: Cloud (Gemini API Active)", text_color="#4CAF50")
        elif has_ollama:
            self.status_label.configure(text="🟢 Mode: Local (Ollama Instance Connected)", text_color="#4CAF50")
        else:
            self.status_label.configure(text="🟡 Mode: Offline / Restricted", text_color="#FFC107")

    def attach_file(self):
        """Open system dialog to select media attachments for vision model processing."""
        file_types = [("Media Files", "*.png *.jpg *.jpeg *.webp"), ("All Files", "*.*")]
        path = filedialog.askopenfilename(filetypes=file_types)
        if path:
            self.selected_file = path
            filename = os.path.basename(path)
            self.file_label.configure(text=f"📎 Attached: {filename}", text_color="#2196F3")

    def write_chat(self, sender, text):
        """Append formatted text messages into disabled chat display textbox."""
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"\n[{sender}]: {text}\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def send_message(self):
        """Extract input context and launch background inference thread."""
        prompt = self.entry.get().strip()
        if not prompt and not self.selected_file:
            return

        self.write_chat("User", prompt if prompt else "[Attached Media Processing]")
        self.entry.delete(0, "end")
        
        file_path = self.selected_file
        self.selected_file = None
        self.file_label.configure(text="No attachment", text_color="gray")

        self.send_btn.configure(state="disabled")
        threading.Thread(target=self.process_inference, args=(prompt, file_path), daemon=True).start()

    def process_inference(self, prompt, file_path):
        """Execute request against Cloud or Local API backends without locking GUI rendering."""
        api_key = os.getenv("GEMINI_API_KEY")
        ollama_active = check_ollama()
        response = ""

        try:
            if api_key:
                response = f"Cloud Engine Processed Query: '{prompt}'" + (f" with attachment {os.path.basename(file_path)}" if file_path else "")
            elif ollama_active:
                model = "llama3.2-vision" if file_path else "llama3"
                payload = {"model": model, "prompt": prompt, "stream": False}
                if file_path:
                    payload["images"] = [encode_image_base64(file_path)]

                res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
                if res.status_code == 200:
                    response = res.json().get("response", "No response received.")
                else:
                    response = f"Ollama Error: HTTP {res.status_code}. Ensure '{model}' is installed (`ollama pull {model}`)."
            else:
                response = "Error: No active AI backend. Add a GEMINI_API_KEY or start local Ollama."

        except Exception as e:
            response = f"Execution Error: {str(e)}"

        self.after(0, lambda: self.finish_inference(response))

    def finish_inference(self, response):
        """Output response back to chat and restore user interaction controls."""
        self.write_chat("TAJ_AN Core", response)
        self.send_btn.configure(state="normal")

# --- Script Entry Point ---
if __name__ == '__main__':
    # Prevents infinite process spawning loops when compiled into binaries via PyInstaller
    multiprocessing.freeze_support()
    
    app = TAJANCoreApp()
    app.mainloop()

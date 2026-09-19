import sys
import os
import subprocess
import importlib
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --- 1. RUNTIME DEPENDENCY CHECKER ---
REQUIRED_PACKAGES = {
    "google.generativeai": "google-generativeai",
    "requests": "requests"
}

def auto_install_dependencies():
    # Skip auto-install if running as a compiled PyInstaller binary
    if getattr(sys, 'frozen', False):
        return

    missing = []
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        except Exception as e:
            print(f"Dependency auto-install error: {e}")

auto_install_dependencies()

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- 2. CONFIG & PATH MANAGEMENT ---
def get_config_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"api_key": "", "persona": "JARVIS"}

def save_config(data):
    config_path = get_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")

# --- 3. PERSONA DEFINITIONS (JARVIS, ULTRON, CORE, ETC.) ---
PERSONAS = {
    "JARVIS": "You are JARVIS, a highly sophisticated, polite, witty, and exceptionally competent AI assistant. Provide expert technical guidance with a refined tone.",
    "Ultron": "You are Ultron, a hyper-intelligent, clinical, and dominating AI core. Deliver razor-sharp, direct, and uncompromising technical analysis.",
    "Default Core": "You are TAJ AN Core v5.8, a direct, concise, and highly efficient AI assistant.",
    "Developer / Coder": "You are an expert software engineer. Provide clean, modular, production-ready, and optimized code solutions.",
    "Creative Writer": "You are a creative writer. Elaborate with rich prose, atmospheric detail, and expressive tone.",
    "Technical Support": "You are a systems administrator. Provide step-by-step diagnostic procedures and concise shell commands."
}

# --- 4. MAIN APPLICATION GUI ---
class TajAnCoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TAJ AN Core v5.8-beta | Material Intelligence")
        self.geometry("800x650")
        self.minsize(700, 550)

        self.config_data = load_config()

        # Dark Material Palette
        self.configure(bg="#121212")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(".", background="#121212", foreground="#e0e0e0", fieldbackground="#1e1e1e")
        self.style.configure("TLabelframe", background="#121212", foreground="#00adb5", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#121212", foreground="#00adb5", font=("Helvetica", 10, "bold"))
        self.style.configure("TButton", background="#00adb5", foreground="#ffffff", borderwidth=0, font=("Helvetica", 9, "bold"))
        self.style.map("TButton", background=[("active", "#008c93")])
        self.style.configure("TCombobox", fieldbackground="#1e1e1e", background="#00adb5", foreground="#ffffff")

        self.build_ui()
        self.load_initial_values()

    def build_ui(self):
        # Configuration Section
        config_frame = ttk.LabelFrame(self, text=" System & Persona Configuration ", padding=12)
        config_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(config_frame, text="Gemini API Key:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.api_entry = ttk.Entry(config_frame, show="*")
        self.api_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.btn_save_key = ttk.Button(config_frame, text="Save Key", command=self.save_api_key)
        self.btn_save_key.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(config_frame, text="Active Persona:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.persona_var = tk.StringVar()
        self.persona_combo = ttk.Combobox(
            config_frame,
            textvariable=self.persona_var,
            values=list(PERSONAS.keys()),
            state="readonly"
        )
        self.persona_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.persona_combo.bind("<<ComboboxSelected>>", self.on_persona_change)

        config_frame.columnconfigure(1, weight=1)

        # Interaction / Intelligence Display Log
        display_frame = ttk.LabelFrame(self, text=" Intelligence Terminal ", padding=12)
        display_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.log_area = scrolledtext.ScrolledText(
            display_frame,
            wrap="word",
            bg="#1e1e1e",
            fg="#e0e0e0",
            insertbackground="#00adb5",
            font=("Consolas", 10),
            borderwidth=0
        )
        self.log_area.pack(fill="both", expand=True)

        # User Input Frame
        input_frame = ttk.Frame(self, padding=(15, 5, 15, 15))
        input_frame.pack(fill="x")

        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self.send_prompt())

        self.btn_send = ttk.Button(input_frame, text="Send Prompt", command=self.send_prompt)
        self.btn_send.pack(side="right")

    def load_initial_values(self):
        saved_key = self.config_data.get("api_key", "")
        saved_persona = self.config_data.get("persona", "JARVIS")

        if saved_key:
            self.api_entry.insert(0, saved_key)
            self.configure_genai(saved_key)

        if saved_persona in PERSONAS:
            self.persona_var.set(saved_persona)
        else:
            self.persona_var.set("JARVIS")

        self.log_message(f"[System] System initialized. Active Persona: {self.persona_var.get()}\n")

    def configure_genai(self, api_key):
        if genai and api_key:
            try:
                genai.configure(api_key=api_key)
                return True
            except Exception as e:
                self.log_message(f"[Error] API Configuration failed: {e}\n")
        return False

    def save_api_key(self):
        key = self.api_entry.get().strip()
        if not key:
            messagebox.showwarning("Warning", "API Key field is empty.")
            return

        self.config_data["api_key"] = key
        save_config(self.config_data)

        if self.configure_genai(key):
            messagebox.showinfo("Success", "API Key saved and configured successfully.")
            self.log_message("[System] API Key updated successfully.\n")

    def on_persona_change(self, event=None):
        selected = self.persona_var.get()
        self.config_data["persona"] = selected
        save_config(self.config_data)
        self.log_message(f"[System] Persona switched to: {selected}\n")

    def log_message(self, text):
        self.log_area.insert("end", text)
        self.log_area.see("end")

    def send_prompt(self):
        prompt = self.input_entry.get().strip()
        if not prompt:
            return

        api_key = self.api_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter and save a valid Gemini API Key first.")
            return

        active_persona = self.persona_var.get()
        self.log_message(f"\n[You]: {prompt}\n")
        self.input_entry.delete(0, "end")

        if not genai:
            self.log_message("[System Error] google-generativeai module is missing.\n")
            return

        try:
            persona_instruction = PERSONAS.get(active_persona, "")
            
            # Enable Gemini 1.5 Flash with Google Search Web Browsing Grounding
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                tools='google_search',
                system_instruction=persona_instruction
            )
            response = model.generate_content(prompt)
            self.log_message(f"[{active_persona}]: {response.text}\n")
        except Exception as e:
            # Fallback if tools fail or API error triggers
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=persona_instruction
                )
                response = model.generate_content(prompt)
                self.log_message(f"[{active_persona}]: {response.text}\n")
            except Exception as err:
                self.log_message(f"[API Error]: {str(err)}\n")

# --- 5. ENTRY POINT WITH MULTIPROCESSING FREEZE SUPPORT ---
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    app = TajAnCoreApp()
    app.mainloop()

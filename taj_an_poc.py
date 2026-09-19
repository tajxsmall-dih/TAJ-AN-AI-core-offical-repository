import sys
import os
import subprocess
import importlib
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

# --- 1. RUNTIME DEPENDENCY CHECKER ---
REQUIRED_PACKAGES = {
    "google.generativeai": "google-generativeai",
    "requests": "requests"
}

def auto_install_dependencies():
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

# --- 3. PERSONA DEFINITIONS ---
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
        self.geometry("850x700")
        self.minsize(700, 550)

        self.attached_file_path = None
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

        self.setup_app_icon()
        self.build_ui()
        self.load_initial_values()

    def setup_app_icon(self):
        # Create a fallback programmatic icon if no .png/.ico file is found on disk
        try:
            icon_img = tk.PhotoImage(width=32, height=32)
            for x in range(32):
                for y in range(32):
                    if 4 <= x <= 27 and 4 <= y <= 27:
                        icon_img.put("#00adb5", (x, y))
            self.iconphoto(True, icon_img)
        except Exception:
            pass

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

        # Interaction Display Log
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

        # User Input & File Attachment Frame
        input_frame = ttk.Frame(self, padding=(15, 5, 15, 15))
        input_frame.pack(fill="x")

        self.btn_attach = ttk.Button(input_frame, text="📎 Attach", command=self.attach_file)
        self.btn_attach.pack(side="left", padx=(0, 5))

        self.lbl_attachment = ttk.Label(input_frame, text="", font=("Helvetica", 8, "italic"))
        self.lbl_attachment.pack(side="left", padx=(0, 5))

        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self.send_prompt())

        self.btn_send = ttk.Button(input_frame, text="Send Prompt", command=self.send_prompt)
        self.btn_send.pack(side="right")

    def attach_file(self):
        filepath = filedialog.askopenfilename(
            title="Select File Attachment",
            filetypes=[("All Files", "*.*"), ("Text Files", "*.txt"), ("Python Files", "*.py")]
        )
        if filepath:
            self.attached_file_path = filepath
            filename = os.path.basename(filepath)
            self.lbl_attachment.config(text=f"[{filename}]")
            self.log_message(f"[System] File attached: {filepath}\n")

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

    def local_fallback_engine(self, prompt, persona):
        """ Local Offline Fallback Intelligence Generator """
        persona_prefix = f"[{persona} - Local Engine]"
        
        # Include attached file text if attached
        file_content = ""
        if self.attached_file_path and os.path.exists(self.attached_file_path):
            try:
                with open(self.attached_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f"\n\n--- ATTACHED FILE ({os.path.basename(self.attached_file_path)}) ---\n" + f.read(2000)
            except Exception as e:
                file_content = f"\n[File Read Error: {e}]"

        combined_prompt = prompt + file_content

        response = (
            f"{persona_prefix}: API connection unavailable or model route offline.\n"
            f"Processed Local Query: '{combined_prompt[:100]}...'\n"
            f"Status: Core operational in local offline diagnostic mode."
        )
        return response

    def send_prompt(self):
        prompt = self.input_entry.get().strip()
        if not prompt:
            return

        api_key = self.api_entry.get().strip()
        active_persona = self.persona_var.get()

        self.log_message(f"\n[You]: {prompt}\n")
        self.input_entry.delete(0, "end")

        # Read attached file content if present
        file_data = ""
        if self.attached_file_path and os.path.exists(self.attached_file_path):
            try:
                with open(self.attached_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_data = f"\n\n[Attached File Content]:\n" + f.read(4000)
                self.log_message(f"[System] Appending file '{os.path.basename(self.attached_file_path)}' to payload.\n")
            except Exception as e:
                self.log_message(f"[Warning] Could not read attached file: {e}\n")
            
            # Reset attachment indicator after sending
            self.attached_file_path = None
            self.lbl_attachment.config(text="")

        full_payload = prompt + file_data

        if not genai or not api_key:
            fallback_res = self.local_fallback_engine(full_payload, active_persona)
            self.log_message(f"{fallback_res}\n")
            return

        persona_instruction = PERSONAS.get(active_persona, "")
        
        # Candidate model names to handle API version routing changes
        model_candidates = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-pro"]
        success = False

        for m_name in model_candidates:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=persona_instruction
                )
                response = model.generate_content(full_payload)
                self.log_message(f"[{active_persona}]: {response.text}\n")
                success = True
                break
            except Exception as err:
                print(f"Model {m_name} failed: {err}")
                continue

        if not success:
            # Fall back to offline local engine
            fallback_res = self.local_fallback_engine(full_payload, active_persona)
            self.log_message(f"{fallback_res}\n")

# --- 5. ENTRY POINT ---
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    app = TajAnCoreApp()
    app.mainloop()

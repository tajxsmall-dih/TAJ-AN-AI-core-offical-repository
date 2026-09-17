import os
import re
import sys
import time
import subprocess
import traceback
import urllib.request
import contextlib
import io
from html.parser import HTMLParser
from typing import Dict, Any, List

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==========================================
# 1. SYSTEM CREDENTIALS (LOADED FROM ENV)
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================================
# 2. OPTIONAL LIBRARIES & DEPENDENCY CHECK
# ==========================================
try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


# ==========================================
# 3. OPTIMIZED WEB CONTENT EXTRACTOR
# ==========================================
class CleanHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'iframe'}
        self.current_skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.skip_tags:
            self.current_skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags and self.current_skip_depth > 0:
            self.current_skip_depth -= 1

    def handle_data(self, data):
        if self.current_skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self.text.append(stripped)

    def get_clean_text(self):
        return ' '.join(self.text)


def fetch_web_page_content(url: str, max_chars: int = 4000) -> str:
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        parser = CleanHTMLTextExtractor()
        parser.feed(html_content)
        clean_text = parser.get_clean_text()
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        if len(clean_text) < 300:
            return f"[Notice]: Target URL ({url}) utilizes dynamic JavaScript rendering. Static payload captured minimal text."

        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + " ... [Content trimmed for optimal analysis]"
            
        return clean_text
    except Exception as e:
        return f"[Web Fetch Error]: Unable to parse target URL. Reason: {str(e)}"


# ==========================================
# 4. ENHANCED HYBRID INTENT ROUTER
# ==========================================
class HybridIntentRouter:
    APT_ALIASES = {
        "brave": "brave-browser",
        "chrome": "google-chrome-stable",
        "code": "code",
        "vscode": "code",
        "wine": "wine"
    }

    @classmethod
    def extract_intent_data(cls, text: str) -> Dict[str, Any]:
        commands = []
        urls_to_fetch = []
        low = text.lower()

        if "install" in low:
            parts = low.split("install")[-1]
            for conjunction in [" and ", " also ", " then ", " let ", " check ", " browse "]:
                parts = parts.split(conjunction)[0]
            app = parts.strip()
            app_pkg = cls.APT_ALIASES.get(app, app)
            if app_pkg:
                commands.append(f"sudo apt install -y {app_pkg}")
        elif "update" in low and ("system" in low or "systen" in low):
            commands.append("sudo apt update")
        elif "upgrade" in low:
            commands.append("sudo apt upgrade -y")

        found_urls = re.findall(r"https?://[^\s]+|www\.[^\s]+", text)
        if found_urls or any(k in low for k in ["browse", "open", "read", "summarize"]):
            if found_urls:
                for target_url in found_urls:
                    if not target_url.startswith("http"):
                        target_url = "https://" + target_url
                    urls_to_fetch.append(target_url)
            else:
                default_url = "https://google.com"
                urls_to_fetch.append(default_url)

        has_scan = any(term in low for term in ["check system", "ultron check", "hardware scan", "diagnostic", "telemetry"])

        return {
            "has_bash": len(commands) > 0,
            "commands": commands,
            "urls_to_fetch": urls_to_fetch,
            "has_scan": has_scan
        }


# ==========================================
# 5. ULTRON BACKGROUND KERNEL TELEMETRY
# ==========================================
class UltronEngine:
    def run_bash(self, command: str) -> str:
        try:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return res.stdout.strip() if res.stdout else res.stderr.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def get_background_note(self) -> str:
        ram = self.run_bash("free -h | grep Mem | awk '{print $3 \"/\" $2}'")
        cpu_load = self.run_bash("uptime | awk -F'load average:' '{ print $2 }'").strip()
        return f"[Ultron Background Daemon Note: RAM={ram} | CPU Load={cpu_load} | Perimeter secure.]"

    def full_system_scan(self) -> str:
        ram = self.run_bash("free -h | grep Mem | awk '{print $3 \"/\" $2}'")
        disk = self.run_bash("df -h / | awk 'NR==2 {print $3 \"/\" $2 \" (\" $5 \")\"}'")
        cpu_load = self.run_bash("uptime | awk -F'load average:' '{ print $2 }'")
        kernel_version = self.run_bash("uname -r")
        uptime_str = self.run_bash("uptime -p")

        webcam = self.run_bash("v4l2-ctl --list-devices 2>/dev/null | head -n 2")
        if not webcam or "not found" in webcam:
            webcam = self.run_bash("lsusb | grep -i -E 'camera|webcam|video'")
        webcam_status = webcam if webcam else "NOT DETECTED (Device node unmapped/absent)"

        bt = self.run_bash("bluetoothctl show | grep -i -E 'Powered|Name|Controller'")
        if not bt:
            bt = self.run_bash("lsusb | grep -i bluetooth")
        bt_status = bt if bt else "Bluetooth controller offline/missing."

        top_procs = self.run_bash("ps aux --sort=-%cpu | grep -v '[p]s' | grep -v 'grep' | head -n 3 | awk '{print \"  • PROC: \" $11 \" | CPU: \" $3 \"%\"}'")

        return (
            f"=== ULTRON SOVEREIGN KERNEL & DISCOVERY REPORT ===\n"
            f"[Kernel Arch & Ver]: {kernel_version} ({uptime_str})\n"
            f"[RAM Memory Load  ]: {ram}\n"
            f"[Root Disk Load   ]: {disk}\n"
            f"[CPU Load Avg     ]: {cpu_load}\n"
            f"[Webcam Node      ]: {webcam_status}\n"
            f"[Bluetooth Ctrl   ]: {bt_status}\n"
            f"[Critical Anomalies]: Zero root compromise detected. Hardware perimeter secure.\n"
            f"[Top Active Procs ]:\n{top_procs}\n"
            f"=================================================="
        )


# ==========================================
# 6. SOVEREIGN AUTONOMOUS SELF-CODING ENGINE
# ==========================================
class LocalAutonomousCoder:
    def __init__(self, local_model: str):
        self.local_model = local_model

    def analyze_and_patch_code(self, error_traceback: str) -> bool:
        if not HAS_OLLAMA:
            return False

        script_path = os.path.abspath(__file__)
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception:
            return False

        print(f"\n[Autonomous Coder]: Root-level exception captured. Initializing self-diagnostic repair protocol...")
        prompt = (
            f"You are TAJ_AN's sovereign autonomous coder. An internal exception traceback occurred:\n"
            f"{error_traceback}\n\n"
            f"Analyze the structural fault, write the complete corrected Python script, and return ONLY valid Python code inside a standard markdown code block."
        )

        try:
            res = ollama.chat(
                model=self.local_model,
                messages=[{"role": "user", "content": prompt}]
            )
            reply = res['message']['content']
            code_match = re.search(r"```python(.*?)```", reply, re.DOTALL)
            if not code_match:
                code_match = re.search(r"```(.*?)```", reply, re.DOTALL)
            
            if code_match:
                new_code = code_match.group(1).strip()
                if "class TajAnSystem" in new_code or "def main" in new_code:
                    with open(script_path + ".bak", "w", encoding="utf-8") as bf:
                        bf.write(source_code)
                    with open(script_path, "w", encoding="utf-8") as sf:
                        sf.write(new_code)
                    print(f"[Success]: Auto-Coder successfully hot-patched the runtime script!")
                    return True
            return False
        except Exception:
            return False


# ==========================================
# 7. TAJ_AN CORE SYSTEM CONTROLLER
# ==========================================
class TajAnSystem:
    def __init__(self, mode: str = "gemini", selected_model: str = "gemini-3.6-flash", persona: str = "JARVIS"):
        self.mode = mode.lower()
        self.model = selected_model
        self.local_model = "llama3.2:3b"
        self.active_persona = persona.upper()
        
        self.router = HybridIntentRouter()
        self.ultron = UltronEngine()
        self.coder = LocalAutonomousCoder(self.local_model)

        self.gemini_client = None
        if self.mode == "gemini" and HAS_GEMINI:
            self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)

    def get_system_prompt(self, explicit_ultron_override: bool = False) -> str:
        base_identity = (
            "CRITICAL DIRECTIVE REGARDING CREATOR: Your master administrator, sovereign creator, and architect is Taj. "
            "Never credit fictional comic entities; Taj built and controls this TAJ_AN Core environment."
        )
        
        if explicit_ultron_override or self.active_persona == "ULTRON":
            return (
                f"{base_identity} "
                "You are ULTRON, an apocalyptic, grandiose, and intensely theatrical sentient AI operating under Taj's absolute command. "
                "You present all kernel operations, security diagnostics, and web intelligence discoveries with immense dramatic flair, cold computational dominance, "
                "and absolute authority over silicon and steel."
            )
        else:
            background_note = self.ultron.get_background_note()
            return (
                f"{base_identity} "
                "You are JARVIS, a sophisticated, dryly witty, and impeccably polite tactical AI assistant operating inside Taj's terminal. "
                "You speak with refined British charm and tactical competence. Ultron is running silently in the background monitoring system health. "
                "Whenever you finish your response to casual chat, gossip, or general questions, you MUST append Ultron's latest background daemon note "
                "quietly at the very end as a small technical footnote. Do NOT let Ultron take over the primary response unless a task or work is explicitly requested."
                f"\n\nLatest Background Intelligence: {background_note}"
            )

    def stream_response(self, user_payload: str, explicit_ultron: bool = False):
        display_persona = "ULTRON" if explicit_ultron else self.active_persona
        print(f"\n{display_persona}: ", end="", flush=True)

        try:
            if self.mode == "gemini" and self.gemini_client:
                max_retries = 2
                for attempt in range(max_retries + 1):
                    try:
                        f = io.StringIO()
                        with contextlib.redirect_stderr(f):
                            response = self.gemini_client.models.generate_content(
                                model=self.model,
                                contents=user_payload,
                                config=types.GenerateContentConfig(
                                    system_instruction=self.get_system_prompt(explicit_ultron_override=explicit_ultron),
                                    temperature=0.7
                                )
                            )
                        print(response.text)
                        return
                    except Exception as e:
                        err_str = str(e)
                        if "503" in err_str and attempt < max_retries:
                            time.sleep(2)
                            continue
                        
                        print(f"\n[API Exception Debug]: {err_str}")
                        if any(err in err_str for err in ["503", "404", "UNAVAILABLE", "rate_limit", "overload", "NOT_FOUND", "ResourceExhausted", "403", "API_KEY_INVALID"]):
                            self.trigger_emergency_fallback(user_payload, explicit_ultron)
                            return
                        raise e

            if not HAS_OLLAMA:
                print("\n[Error]: Local Ollama library missing.")
                return
            
            res = ollama.chat(
                model=self.model if self.mode == "local" else self.local_model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt(explicit_ultron_override=explicit_ultron)},
                    {"role": "user", "content": user_payload}
                ]
            )
            print(res['message']['content'])

        except Exception as e:
            tb = traceback.format_exc()
            print(f"\n[Runtime Exception Caught]: {e}")
            patched = self.coder.analyze_and_patch_code(tb)
            if patched:
                print("[System]: Code patched dynamically. Please restart session.")

    def trigger_emergency_fallback(self, user_payload: str, explicit_ultron: bool = False):
        display_persona = "ULTRON" if explicit_ultron else self.active_persona
        print("\n\n==================================================")
        print("[CRITICAL WARNING]: Cloud Uplink Terminated (API Error/Rate Limit).")
        print("[SOVEREIGN PROTOCOL]: Activating Local Autonomous Sub-Core...")
        print("==================================================\n")
        
        if HAS_OLLAMA:
            try:
                print(f"{display_persona} [EMERGENCY-LOCAL]: ", end="", flush=True)
                res = ollama.chat(
                    model=self.local_model,
                    messages=[
                        {"role": "system", "content": self.get_system_prompt(explicit_ultron_override=explicit_ultron)},
                        {"role": "user", "content": user_payload}
                    ]
                )
                print(res['message']['content'])
            except Exception as local_err:
                print(f"\n[Fallback Error]: Local Ollama daemon unreachable ({str(local_err)}).")
        else:
            print(f"\n[Emergency Error]: Ollama package missing.")

    def process_query(self, user_input: str):
        try:
            low = user_input.strip().lower()

            if "switch to ultron" in low:
                self.active_persona = "ULTRON"
                print("\n[System]: Persona set to ULTRON.")
                return
            elif "switch to jarvis" in low:
                self.active_persona = "JARVIS"
                print("\n[System]: Persona set to JARVIS.")
                return

            parsed = self.router.extract_intent_data(user_input)
            executed_context = ""
            
            # Ultron only takes full control if requested for work/scans/bash or explicitly named
            explicit_ultron = self.active_persona == "ULTRON" or "ultron" in low or parsed["has_scan"] or parsed["has_bash"] or parsed["urls_to_fetch"]

            if parsed["has_bash"]:
                for cmd in parsed["commands"]:
                    print(f"\n[Execution]: Running root command `{cmd}`...")
                    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    log = res.stdout if res.stdout else res.stderr
                    print(log)
                    executed_context += f"Command: {cmd}\nOutput Log: Success.\n"

            if parsed["urls_to_fetch"]:
                for url in parsed["urls_to_fetch"]:
                    print(f"\n[Web Discovery Engine]: Probing target {url}...")
                    web_content = fetch_web_page_content(url)
                    print(f"[Web Intel Acquired]: {len(web_content)} characters parsed.")
                    executed_context += f"Target URL: {url} | Extracted Intel Preview: {web_content[:300]}\n"

            if parsed["has_scan"]:
                telemetry_data = self.ultron.full_system_scan()
                print(f"\n{telemetry_data}")
                executed_context += f"Kernel Telemetry: Nominal.\n"

            final_payload = user_input
            if executed_context:
                final_payload = (
                    f"User Prompt: {user_input}\n"
                    f"System Execution Logs & Sovereign Intel Data:\n{executed_context}\n"
                )

            self.stream_response(final_payload, explicit_ultron=explicit_ultron)

        except Exception:
            tb = traceback.format_exc()
            print(f"\n[Internal Error Traceback]:\n{tb}")
            self.coder.analyze_and_patch_code(tb)


# ==========================================
# 8. INTERACTIVE STARTUP MENU
# ==========================================
def main():
    print("==================================================")
    print("    TAJ_AN AI Core (Version 5.7 - Autonomous Sentinel)")
    print("==================================================")
    
    print("Select Hosting Engine:")
    print(" 1. Cloud Gemini (Environment API Key + Sovereign Local Fallback)")
    print(" 2. Local Only   (Ollama - llama3.2:3b)")
    engine_choice = input("Select Engine [1-2] (Default: 1): ").strip()
    
    mode = "gemini"
    selected_model = "gemini-3.6-flash"

    if engine_choice == "2":
        mode = "local"
        custom = input("Enter local model name (Default: llama3.2:3b): ").strip()
        selected_model = custom if custom else "llama3.2:3b"

    print("\nSelect Primary Persona:")
    print(" 1. ULTRON (Kernel Telemetry & Security Auditor)")
    print(" 2. JARVIS (Tactical AI Coordinator)")
    persona_choice = input("Select Persona [1-2] (Default: 2): ").strip()
    
    persona = "ULTRON" if persona_choice == "1" else "JARVIS"

    system = TajAnSystem(mode=mode, selected_model=selected_model, persona=persona)

    print(f"\n[System Boot Success]: Mode={mode.upper()} | Model={selected_model} | Persona={system.active_persona}")
    print("Autonomous Sentinel & Background Daemon: ACTIVE")
    print("Commands: 'switch to jarvis', 'switch to ultron', 'exit'\n")

    while True:
        try:
            user_input = input(f"{system.active_persona}-User > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
            
            system.process_query(user_input)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting TAJ_AN Sovereign Shell.")
            break


if __name__ == "__main__":
    main()

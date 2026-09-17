# 🚀 TAJ_AN Core v5.7 — Universal AI Engine

**TAJ_AN Core** is a cross-platform, standalone local AI wrapper engineered to bridge local LLMs (via Ollama) and cloud inference (via Google GenAI). Built with zero-dependency execution in mind, it packages complete CLI control, system-level telemetry, and task execution into native binaries for **Linux** and **Windows**.

---

## 📑 Table of Contents
* [✨ Core Capabilities](#-core-capabilities)
* [⚡ Quick Start & User Guide](#-quick-start--user-guide)
* [⚖️ Platform Deep Dive: Linux vs. Windows](#️-platform-deep-dive-linux-vs-windows)
* [⚠️ System Execution & Safety Concerns](#️-system-execution--safety-concerns)
* [🗺️ Future Roadmap](#️-future-roadmap)
* [📜 License](#-license)

---

## ✨ Core Capabilities

* **Dual-Inference Architecture:** Toggle on-the-fly between offline local models (via Ollama) and cloud-based Google GenAI models.
* **Native System Telemetry:** Inspect hardware state, memory consumption, active processes, and platform specs directly through the CLI prompt.
* **System-Level Execution:** Issue shell commands, manage background tasks, and run system utility checks directly within the environment.
* **Zero Runtime Dependencies:** Distributed as self-contained executables—no Python, virtual environments, or `pip` installations required.

---

## ⚡ Quick Start & User Guide

### 🐧 Linux Execution Guide
1. Go to the [Releases Page](https://github.com/tajxsmall-dih/TAJ-AN-AI-core-offical-repository/releases) and download `TAJ_AN_Core_v5.7_Linux`.
2. Open your terminal in the directory where the file was downloaded.
3. Grant execution permissions:
   ```bash
   chmod +x TAJ_AN_Core_v5.7_Linux
4.Run the executable:
Bash

./TAJ_AN_Core_v5.7_Linux
🪟 Windows Execution Guide

    1.Download TAJ_AN_Core_v5.7_Windows.exe from Releases.

   2.(Optional) Create a .env file in the same folder to store your cloud API key:
    Code snippet

    GEMINI_API_KEY=your_api_key_here
3.Open PowerShell or Command Prompt, navigate to the download folder, and launch:
DOS

.\TAJ_AN_Core_v5.7_Windows.exe
⚖️ Platform Deep Dive: Linux vs. WindowsFeature / Metric🐧 Linux (Recommended)🪟 WindowsSystem TelemetryLow-overhead inspection via /proc, lscpu, and free -m.Queries via WMI/CIM and systeminfo sub-processes.Command ExecutionNative Bash pipeline support with full UNIX utility piping.Command Prompt (cmd.exe) and PowerShell sub-shell execution.Memory FootprintExtremely low baseline memory overhead (~15–30 MB).Slightly higher RAM footprint due to Windows sub-system calls.Local LLM IntegrationDirect daemon interaction via systemctl / ollama.service.Background service connection via Windows task tray process.🟢 Pros & 🔴 Cons🐧 Linux🟢 Pros: Blazing fast startup, lower memory consumption, native pipe handling, direct daemon control.🔴 Cons: Requires manual execution permission (chmod +x), user must manage terminal paths.🪟 Windows🟢 Pros: Double-click launcher convenience, familiar user environment, built-in PowerShell access.🔴 Cons: Windows SmartScreen / Antivirus warnings on unsigned binaries, higher system resource baseline.⚠️ System Execution & Safety ConcernsBecause TAJ_AN Core provides direct system-level capabilities, keep the following security guidelines in mind:Sandboxed Shell Execution: Always verify system commands before granting automated execution rights within scripts.Environment File Security: Store your .env file in a secure location and never commit API keys or secret credentials to public repositories.Elevated Privileges: Avoid running the application as root (Linux) or Administrator (Windows) unless explicit elevated system changes are required.🗺️ Future Roadmap[ ] Desktop GUI Wrapper: Cross-platform visual interface using PyWebView / Electron.[ ] Smart Model Router: Automatic query routing to local or cloud models based on task complexity.[ ] Local Storage History: SQLite-backed context logging for persistent sessions.[ ] Plugin Framework: User-extensible system utility scripts and automation hooks.📜 LicenseDistributed under the MIT License.EOF

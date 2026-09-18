# 🚀 TAJ_AN Core v5.8-beta — Universal AI Engine Studio

**TAJ_AN Core** is a lightweight, cross-platform local AI assistant wrapper designed to seamlessly bridge local LLMs (via Ollama) and cloud inference (via Google GenAI). Compiled into standalone, zero-dependency executables for both **Windows** and **Linux**.

---

## ✨ What's New in v5.8-beta (GUI Release)

* **Interactive CustomTkinter GUI:** Full dark-mode visual desktop interface.
* **Multimodal Vision Engine:** Direct support for images using local `llama3.2-vision` models or Gemini cloud APIs.
* **First-Run Setup Wizard:** Automatically pops up on first launch to assist with API keys and local Ollama setup.
* **Non-Blocking Multithreading:** Keeps the user interface smooth and responsive during long AI generation tasks.

---

## 📦 Version Availability & Legacy CLI Access

| Release | Version | Interface | Target Hardware |
| :--- | :--- | :--- | :--- |
| **Current Headline** | **v5.8-beta** | CustomTkinter GUI | Modern Desktop / Workstations |
| **Legacy Fallback** | **v5.7.0** | Minimal CLI Shell | Low-spec Machines / Headless Linux |

---

## ⚡ Quick Start Guide

### 🪟 Windows Setup
1. Download `TAJ_AN_Core_v5.8-beta_Windows.exe` from [Releases](https://github.com/tajxsmall-dih/TAJ-AN-AI-core-offical-repository/releases).
2. Double-click to launch the application. The Setup Wizard will assist with setup if no API key or local model is found.

### 🐧 Linux Setup
1. Download `TAJ_AN_Core_v5.8-beta_Linux` from [Releases](https://github.com/tajxsmall-dih/TAJ-AN-AI-core-offical-repository/releases).
2. Make it executable and run:
   ```bash
   chmod +x TAJ_AN_Core_v5.8-beta_Linux
   ./TAJ_AN_Core_v5.8-beta_Linux
📜 License

Distributed under the MIT License.


---

### Step 4: Commit, Rebase Sync, and Push Release Tag

Run this one-liner to sync local commits with remote changes, push everything to `main`, and publish tag **`v5.8-beta`** to trigger GitHub Actions:

```bash
git add . && git commit -m "feat: upgrade core to v5.8-beta GUI studio with vision support" && git pull --rebase origin main && git push origin main && git tag v5.8-beta && git push origin v5.8-beta
EOf

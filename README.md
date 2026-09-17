# TAJ_AN AI Core (v5.7)

An autonomous sentinel CLI featuring hybrid routing between Cloud Gemini models and local Ollama sub-cores.

## Security & API Key Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and add your key:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

## Running
```bash
python taj_an_poc.py
```

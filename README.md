# Aqsa Portfolio Assistant (Streamlit + Gemini)

A friendly chatbot that answers **only** from Aqsa Shah's portfolio data (in `aqsa_profile.yaml`).
UI is built with **Streamlit**; AI is **Gemini** via the `google-generativeai` SDK.

## 1) Setup

```bash
# Python 3.10+ recommended
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Add your key
cp .env.example .env
# then put your real key in .env
```

## 2) Run locally

```bash
streamlit run app.py
```

Open the local URL Streamlit prints.

## 3) Deploy (Streamlit Community Cloud)

1. Push this folder to a **public GitHub repo**.
2. Go to https://share.streamlit.io (Community Cloud) → *New app*.
3. Point to your repo and set **Main file path** to `app.py`.
4. In *Advanced settings* → *Secrets*, add:
   ```
   GEMINI_API_KEY="your-real-key"
   ```
5. Deploy.

## 4) Update the bot's knowledge

Edit `aqsa_profile.yaml` and redeploy. The bot only uses facts from that file.

## 5) Troubleshooting

- **No API key** → set `GEMINI_API_KEY` either in `.env` or Streamlit secrets.
- **Model errors** → check network / quota; try `gemini-1.5-flash` first.
- **Bot making things up** → it is instructed to refuse unknowns. Ensure the fact exists in YAML.

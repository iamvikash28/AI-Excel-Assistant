# 🧭 Step-by-Step Setup in VS Code

## 1. Install prerequisites (one-time)
- Install **Python 3.10+** from https://python.org (check "Add to PATH" during install on Windows)
- Install **VS Code** from https://code.visualstudio.com
- In VS Code, install the **Python extension** (Extensions icon → search "Python" by Microsoft → Install)

## 2. Get the project files
- Unzip the project folder you downloaded and open it in VS Code:
  `File → Open Folder → select "ai-excel-assistant"`

## 3. Open the integrated terminal
`Terminal → New Terminal` (or `` Ctrl+` ``)

## 4. Create a virtual environment
```bash
python -m venv venv
```
Activate it:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

You'll see `(venv)` appear at the start of your terminal prompt — that means it's active.
In VS Code, also select this interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter" → pick the one inside `venv`.

## 5. Install dependencies
```bash
pip install -r requirements.txt
```
This installs Streamlit, Pandas, Plotly, scikit-learn, and the OpenAI/Gemini SDKs.

## 6. Get a free AI API key
**Option A — Gemini (recommended, generous free tier):**
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with a Google account → "Create API Key" → copy it

**Option B — OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create a key (requires billing set up, even for small usage)

Keep this key handy — you'll paste it into the app's sidebar (never commit it to GitHub).

## 7. Run the app
```bash
streamlit run app.py
```
This opens `http://localhost:8501` in your browser automatically. If not, click the link shown in the terminal.

## 8. Try it out
1. In the sidebar, choose **Gemini** or **OpenAI** and paste your API key
2. Upload `sample_data.xlsx` (included in the project) or your own spreadsheet
3. Try the tabs:
   - Go to **💬 Ask AI** and type: *"find duplicate customers"*
   - Try: *"predict sales for the next 30 days"*
   - Try: *"what's the average sales by region?"*
4. Or skip AI entirely and click through **Duplicates / Missing Values / Pivot Table / Charts / Predict Sales** — these work without any API key.

## 9. Stopping the app
Press `Ctrl+C` in the terminal.

## 10. Push to GitHub (for your portfolio/resume link)
```bash
git init
git add .
git commit -m "Initial commit: AI Excel Assistant"
git branch -M main
git remote add origin https://github.com/<your-username>/ai-excel-assistant.git
git push -u origin main
```
⚠️ Your `.gitignore` already excludes `venv/` and `.env` — never commit your API key.

## 11. (Optional but recommended) Deploy it live
1. Push the repo to GitHub (step 10)
2. Go to https://share.streamlit.io → "New app" → connect your GitHub repo → select `app.py`
3. In the deployed app's settings, add your API key under "Secrets" (don't hardcode it)
4. You'll get a live public URL — put this directly on your resume and LinkedIn

## Troubleshooting
| Problem | Fix |
|---|---|
| `streamlit: command not found` | Make sure `venv` is activated, then reinstall: `pip install -r requirements.txt` |
| `ModuleNotFoundError` | You're likely running the wrong Python interpreter — reselect it in VS Code (step 4) |
| Excel file won't upload | Make sure it's `.xlsx`, `.xls`, or `.csv` and not password-protected |
| AI chat says "couldn't process" | Double-check the API key was pasted correctly with no extra spaces |

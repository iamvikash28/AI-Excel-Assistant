# 📊 AI Excel Assistant

An AI-powered web app that lets you upload any Excel/CSV file and analyze it using **plain English**, or through dedicated one-click tools — no formulas or pivot-table know-how required.

Built as a portfolio project to demonstrate **data analysis (Pandas), data visualization (Plotly), basic ML forecasting (scikit-learn), and LLM integration (OpenAI/Gemini)** inside an interactive **Streamlit** UI.

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Ask AI** | Type a question like *"find duplicate customers"* or *"predict sales for next month"* — the LLM classifies your intent and runs the right analysis |
| 🧬 **Find Duplicates** | Detect duplicate rows, optionally scoped to specific columns |
| ❓ **Missing Values** | Get a full missing-data report with counts, percentages, and a chart |
| 📋 **Pivot Tables** | Build pivot tables interactively (rows, columns, values, aggregation) |
| 📈 **Charts** | Generate bar, line, scatter, pie, or histogram charts from any columns |
| 🔮 **Predict Sales** | Forecast future sales with a linear regression trend model |

All tabs work standalone with pandas/plotly/sklearn — **no API key required** except for the chat assistant.

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit
- **Data processing:** Pandas, NumPy
- **Visualization:** Plotly
- **Machine Learning:** scikit-learn (Linear Regression for forecasting)
- **AI/LLM:** OpenAI GPT-4o-mini or Google Gemini 1.5 Flash
- **File formats:** .xlsx, .xls, .csv (openpyxl)

## 🚀 Getting Started

See [SETUP.md](SETUP.md) for full step-by-step VS Code instructions.

Quick version:
```bash
git clone <your-repo-url>
cd ai-excel-assistant
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py
```

Then open the sidebar, paste a free [Gemini API key](https://aistudio.google.com/app/apikey) (or OpenAI key), and upload `sample_data.xlsx` to try it out.

## 📁 Project Structure

```
ai-excel-assistant/
├── app.py              # Streamlit UI and app logic
├── utils.py             # Core pandas/plotly/sklearn functions
├── ai_helper.py          # LLM prompt + routing logic (OpenAI/Gemini)
├── requirements.txt
├── sample_data.xlsx      # Sample dataset to demo the app
├── .env.example
└── README.md
```

## 🎯 Why I Built This

To demonstrate practical, job-ready skills for a Data Analyst / BI Analyst role:
- Cleaning and profiling real-world messy data (duplicates, missing values)
- Building pivot tables and visualizations without a BI tool
- Basic predictive analytics (trend forecasting)
- Integrating LLMs to make data analysis accessible via natural language

## Live demo
[ai-excel-assistant.streamlit.app](https://ai-excel-assistant.streamlit.app)

## 👤 Author

**Vikash Verma**
Aspiring Data Analyst | Excel · SQL · Power BI · Python | E-mail- vikashverma566@gmail.com

---

"""
AI Excel Assistant
-------------------
Upload an Excel/CSV file, then either type a question in plain English
(e.g. "find duplicate customers", "predict next month's sales") or use the
dedicated tabs to run the analysis directly.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import io

from utils import (
    find_duplicates,
    missing_value_report,
    generate_pivot,
    create_chart,
    predict_sales,
    profile_dataframe,
)
from ai_helper import route_question

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Excel Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# CUSTOM CSS — makes the default Streamlit look feel like a real product
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #4F8BF9 0%, #7C5CFC 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; }
    .main-header p { margin: 0.2rem 0 0 0; opacity: 0.9; font-size: 0.95rem; }

    .metric-card {
        background: #ffffff;
        border: 1px solid #eef0f5;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        font-weight: 500;
    }

    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📊 AI Excel Assistant</h1>
    <p>Upload a spreadsheet, then ask questions in plain English — or use the tools below.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SIDEBAR — file upload + AI provider settings
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Setup")

    provider = st.radio("AI Provider", ["Gemini", "OpenAI"], horizontal=True,
                         help="Gemini has a generous free tier — good for demos.")
    api_key = st.text_input(f"{provider} API Key", type="password",
                             help="Your key is only used for this session and never stored.")

    st.divider()
    uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "xls", "csv"])

    st.divider()
    st.caption("Built with Streamlit · Pandas · Plotly · scikit-learn · LLM (OpenAI/Gemini)")
    st.caption("💡 No API key? The Duplicates / Missing / Pivot / Chart / Predict tabs "
               "all work without AI — only the chat assistant needs a key.")

# ----------------------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            st.session_state.df = pd.read_csv(uploaded_file)
        else:
            st.session_state.df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Couldn't read that file: {e}")

df = st.session_state.df

if df is None:
    st.info("👈 Upload an Excel or CSV file from the sidebar to get started.")
    st.markdown("**Not sure what to upload?** Try any sales/customer spreadsheet with columns "
                "like `Date`, `Customer`, `Product`, `Region`, `Sales`.")
    st.stop()

# ----------------------------------------------------------------------------
# TOP METRICS
# ----------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", len(df.columns))
c3.metric("Missing Cells", f"{int(df.isnull().sum().sum()):,}")
c4.metric("Duplicate Rows", int(df.duplicated().sum()))

with st.expander("🔍 Preview data", expanded=False):
    st.dataframe(df.head(20), use_container_width=True)

st.write("")

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab_chat, tab_dup, tab_missing, tab_pivot, tab_chart, tab_predict = st.tabs(
    ["💬 Ask AI", "🧬 Duplicates", "❓ Missing Values", "📋 Pivot Table", "📈 Charts", "🔮 Predict Sales"]
)

# ---------------- TAB 1: CHAT ----------------
with tab_chat:
    st.caption("Ask things like *\"find duplicate customers\"*, *\"show missing values\"*, "
               "*\"predict sales for the next 30 days\"*, or *\"what's the average sales by region?\"*")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], str):
                st.markdown(msg["content"])
            else:
                msg["content"]()  # replay stored render function (tables/charts)

    question = st.chat_input("Type your question about the data...")

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            if not api_key:
                st.warning("Add your API key in the sidebar to use the chat assistant, "
                           "or use the dedicated tabs above.")
            else:
                with st.spinner("Thinking..."):
                    profile = profile_dataframe(df)
                    result = route_question(question, profile, provider, api_key)
                    intent = result.get("intent", "general")
                    cols = result.get("columns", {})

                    try:
                        if intent == "duplicates":
                            subset = cols.get("subset_cols") or None
                            res = find_duplicates(df, subset)
                            st.markdown(f"Found **{len(res)}** duplicate rows.")
                            st.dataframe(res, use_container_width=True)

                        elif intent == "missing":
                            res = missing_value_report(df)
                            st.markdown(f"**{len(res)}** columns have missing values.")
                            st.dataframe(res, use_container_width=True)

                        elif intent == "pivot":
                            pivot = generate_pivot(
                                df, cols.get("index_col"), cols.get("columns_col"),
                                cols.get("values_col"), cols.get("aggfunc", "sum")
                            )
                            st.dataframe(pivot, use_container_width=True)

                        elif intent == "chart":
                            fig = create_chart(
                                df, cols.get("chart_type", "bar"),
                                cols.get("x_col"), cols.get("y_col")
                            )
                            st.plotly_chart(fig, use_container_width=True)

                        elif intent == "predict":
                            hist, fcst, fig, r2 = predict_sales(
                                df, cols.get("date_col"), cols.get("values_col"), 30
                            )
                            st.markdown(f"Forecast for the next 30 days (model fit R² = {r2:.2f}):")
                            st.plotly_chart(fig, use_container_width=True)

                        else:
                            st.markdown(result.get("answer", "I'm not sure how to answer that."))

                        st.session_state.chat_history.append({"role": "assistant", "content": "✅ Done above."})

                    except Exception as e:
                        st.error(f"Something went wrong running that: {e}. "
                                 f"Try the dedicated tabs for full control.")

# ---------------- TAB 2: DUPLICATES ----------------
with tab_dup:
    st.subheader("Find Duplicate Rows")
    subset_cols = st.multiselect("Check duplicates based on specific columns (optional)",
                                  options=df.columns.tolist())
    if st.button("Find Duplicates", key="btn_dup"):
        res = find_duplicates(df, subset_cols if subset_cols else None)
        if len(res) == 0:
            st.success("No duplicates found! 🎉")
        else:
            st.warning(f"Found {len(res)} duplicate rows.")
            st.dataframe(res, use_container_width=True)
            st.download_button("Download duplicates as CSV", res.to_csv(index=False),
                                "duplicates.csv", "text/csv")

# ---------------- TAB 3: MISSING VALUES ----------------
with tab_missing:
    st.subheader("Missing Value Report")
    res = missing_value_report(df)
    if len(res) == 0:
        st.success("No missing values in this dataset! 🎉")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(res, use_container_width=True)
        with col2:
            fig = create_chart(res, "bar", "Column", "Missing Values")
            st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 4: PIVOT TABLE ----------------
with tab_pivot:
    st.subheader("Generate a Pivot Table")
    col1, col2, col3, col4 = st.columns(4)
    index_col = col1.selectbox("Rows (index)", df.columns.tolist())
    columns_col = col2.selectbox("Columns (optional)", [None] + df.columns.tolist())
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    values_col = col3.selectbox("Values", numeric_cols if numeric_cols else df.columns.tolist())
    aggfunc = col4.selectbox("Aggregation", ["sum", "mean", "count", "max", "min"])

    if st.button("Generate Pivot Table", key="btn_pivot"):
        try:
            pivot = generate_pivot(df, index_col, columns_col, values_col, aggfunc)
            st.dataframe(pivot, use_container_width=True)
            st.download_button("Download pivot as CSV", pivot.to_csv(),
                                "pivot_table.csv", "text/csv")
        except Exception as e:
            st.error(f"Couldn't build that pivot table: {e}")

# ---------------- TAB 5: CHARTS ----------------
with tab_chart:
    st.subheader("Create a Chart")
    col1, col2, col3, col4 = st.columns(4)
    chart_type = col1.selectbox("Chart type", ["bar", "line", "scatter", "pie", "histogram"])
    x_col = col2.selectbox("X-axis", df.columns.tolist())
    y_col_options = df.select_dtypes(include="number").columns.tolist()
    y_col = col3.selectbox("Y-axis", y_col_options if y_col_options else df.columns.tolist())
    color_col = col4.selectbox("Color by (optional)", [None] + df.columns.tolist())

    if st.button("Generate Chart", key="btn_chart"):
        try:
            fig = create_chart(df, chart_type, x_col, y_col, color_col)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Couldn't build that chart: {e}")

# ---------------- TAB 6: PREDICT SALES ----------------
with tab_predict:
    st.subheader("Forecast Future Sales")
    date_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    col1, col2, col3 = st.columns(3)
    date_col = col1.selectbox("Date column", date_cols)
    sales_col = col2.selectbox("Sales/Value column", numeric_cols if numeric_cols else date_cols)
    periods = col3.slider("Days to forecast", 7, 90, 30)

    if st.button("Run Forecast", key="btn_predict"):
        try:
            hist, fcst, fig, r2 = predict_sales(df, date_col, sales_col, periods)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Simple linear trend model — R² = {r2:.2f} "
                       f"(this is a lightweight demo forecast, not production-grade).")
            st.download_button("Download forecast as CSV", fcst.to_csv(index=False),
                                "forecast.csv", "text/csv")
        except Exception as e:
            st.error(f"Couldn't run forecast: {e}. Make sure you picked a valid date column "
                     f"and a numeric sales column.")

st.divider()
st.caption("AI Excel Assistant — a portfolio project demonstrating pandas, data visualization, "
           "and LLM-powered natural language data analysis.")

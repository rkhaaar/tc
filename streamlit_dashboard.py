# streamlit_dashboard.py

import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Triathlon Coach Dashboard", layout="wide")

# ---- Styling ----
st.markdown("""
<style>
body, .stApp {
    background-color: #f4f4f4;
    color: #1a1a1a;
    font-family: 'Poppins', sans-serif;
}

.sidebar .sidebar-content {
    background-color: #ffffff;
    border-right: 1px solid #ccc;
    padding-top: 2rem;
    font-size: 16px;
}

.sidebar .sidebar-content a {
    color: #333;
    text-decoration: none;
    display: flex;
    align-items: center;
    padding: 10px;
    transition: background 0.3s;
}

.sidebar .sidebar-content a:hover {
    background-color: #efefef;
    border-radius: 6px;
}

[data-testid="metric-container"] > div {
    background-color: #fff;
    border-radius: 1rem;
    padding: 1rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
    .stApp {
        font-size: 14px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---- Load Data ----
DATA_PATH = "athlete_data.json"

if not os.path.exists(DATA_PATH):
    st.error("athlete_data.json not found.")
    st.stop()

with open(DATA_PATH) as f:
    data = json.load(f)

# ---- Sidebar Navigation (Icon Based) ----
st.sidebar.markdown("### 📋 Menu")
menu = st.sidebar.radio("", [
    "🏠 Home", "📅 Training Plan", "📊 Metrics", "📖 History", "💬 Coach Chat"
], label_visibility="collapsed")

profile = data['profile']

if menu == "🏠 Home":
    st.title("Today's Overview")

    col1, col2 = st.columns(2)
    col1.metric("Athlete", profile['name'])
    col2.metric("VO2 Max", profile['vo2max'])

    st.markdown("### Today's Training")
    st.markdown(f"- {data['training_plan'][0]['sessions'][0]}")

    st.markdown("### Quick Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Weight", profile['weight_kg'])
    col2.metric("Resting HR", profile['resting_hr'])
    col3.metric("Body Fat %", profile['body_fat_pct'])

elif menu == "📅 Training Plan":
    st.subheader("📅 Weekly Training Plan")
    for week in data['training_plan']:
        st.markdown(f"**Week {week['week']} starting {week['start_date']}**")
        for session in week['sessions']:
            st.markdown(f"- {session}")

elif menu == "📊 Metrics":
    st.subheader("📊 Training Metrics Overview")
    summary = data['metrics_collected']

    flat_data = []
    for date, sessions in summary.items():
        for session in sessions:
            metrics = session['metrics']
            metrics['sport'] = session['sport']
            metrics['date'] = date
            flat_data.append(metrics)

    if flat_data:
        df = pd.DataFrame(flat_data)
        df['date'] = pd.to_datetime(df['date'])
        sports = df['sport'].unique()

        for sport in sports:
            st.markdown(f"### {sport.title()} Metrics")
            sport_df = df[df['sport'] == sport]
            with st.expander(f"{sport.title()} Summary", expanded=True):
                st.line_chart(sport_df.set_index('date')[['duration_min']], use_container_width=True)
                if 'avg_hr' in sport_df:
                    st.line_chart(sport_df.set_index('date')[['avg_hr']], use_container_width=True)
                if 'power' in sport_df:
                    st.line_chart(sport_df.set_index('date')[['power']], use_container_width=True)

elif menu == "📖 History":
    st.subheader("📖 Athlete History")
    history_file = "training_history.json"
    if os.path.exists(history_file):
        with open(history_file) as f:
            history_data = json.load(f)
        for entry in history_data:
            st.markdown(f"**{entry['date']} - {entry['summary']}**")
    else:
        st.info("No history data found.")

elif menu == "💬 Coach Chat":
    st.subheader("💬 Chat with Coach")
    chat_input = st.text_input("Ask your coach a question:")
    if chat_input:
        athlete_data = data['profile']
        prompt = f"Athlete Data: {athlete_data}\nQuestion: {chat_input}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        coach_reply = response.choices[0].text.strip()
        st.markdown(f"**Coach:** {coach_reply}")
        with open("chat_log.txt", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] You: {chat_input}\nCoach: {coach_reply}\n\n")

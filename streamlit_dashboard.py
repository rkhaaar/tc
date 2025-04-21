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
    background-color: #0e1117; /* Very dark background */
    color: #f8f9fa; /* Light text color */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Modern font */
}

.sidebar .sidebar-content {
    background-color: #161b22; /* Darker sidebar */
    border-right: 1px solid #21262d;
    padding-top: 2rem;
    font-size: 16px;
}

.sidebar .sidebar-content a {
    color: #c9d1d9;
    text-decoration: none;
    display: flex;
    align-items: center;
    padding: 10px;
    transition: background 0.3s;
}

.sidebar .sidebar-content a:hover {
    background-color: #21262d;
    border-radius: 6px;
}

.data-card {
    background-color: #1a1e24; /* Slightly lighter card background */
    color: #f8f9fa;
    border-radius: 0.75rem; /* More rounded corners */
    padding: 1.25rem; /* Increased padding */
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15); /* Subtle shadow */
}

.card-title {
    font-size: 1.15em;
    font-weight: 600; /* Semi-bold */
    margin-bottom: 0.75rem;
    color: #e0e6ed;
}

.metric-value {
    font-size: 2em;
    font-weight: bold;
    line-height: 1.1;
}

.metric-label {
    font-size: 0.9em;
    color: #adb5bd;
    margin-top: 0.25rem;
}

.status-box {
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding-top: 1rem;
}

.status-item {
    text-align: center;
}

.status-value {
    font-weight: 500; /* Slightly lighter bold */
    font-size: 1.05em;
}

.status-label {
    color: #adb5bd;
    font-size: 0.8em;
    margin-top: 0.2rem;
}

@media (max-width: 768px) {
    .status-box {
        flex-direction: column;
        align-items: stretch;
    }
    .status-item {
        margin-bottom: 0.75rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ---- Load Data ----
DATA_PATH = "athlete_data.json"

if not os.path.exists(DATA_PATH):
    st.error(f"Error: {DATA_PATH} not found. Please create this file with athlete data in JSON format.")
    st.stop()

with open(DATA_PATH) as f:
    data = json.load(f)

# ---- Sidebar Navigation (Icon Based) ----
st.sidebar.markdown("### ☰ Menu")
menu = st.sidebar.radio("", [
    "🏠 Home", "📅 Training Plan", "📊 Metrics", "📖 History", "💬 Coach Chat"
], label_visibility="collapsed")

profile = data.get('profile', {})
training_plan = data.get('training_plan', [])
metrics_collected = data.get('metrics_collected', {})

if menu == "🏠 Home":
    st.title("Today's Overview")

    # --- Today's Session Card ---
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Today\'s Session</div>', unsafe_allow_html=True)
    today_session = "Rest Day"
    if training_plan and training_plan[0].get('sessions'):
        today_session = training_plan[0]['sessions'][0]
    st.markdown(f'<div class="metric-value">{today_session}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Athlete Score Card ---
    st.markdown('<div class="data-card" style="text-align: center;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Athlete Score</div>', unsafe_allow_html=True)
    athlete_score = profile.get('athlete_score', 78)
    st.markdown(f'<div class="metric-value">{athlete_score}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Status, Duration, Effort Card ---
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Session Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-box">', unsafe_allow_html=True)

    today_status = "Rest"
    today_duration = "0 m"
    today_effort = "Easy"

    if training_plan and training_plan[0].get('sessions'):
        first_session_details = training_plan[0]['sessions'][0]
        if "Bike" in first_session_details:
            today_status = "Training"
            today_duration = "1h 30 m"
            today_effort = "Moderate"
        elif "Run" in first_session_details:
            today_status = "Training"
            today_duration = "45 min"
            today_effort = "Easy"
        # Add more conditions for other sports/sessions

    st.markdown(f'<div class="status-item"><div class="status-value">{today_status}</div><div class="status-label">Status</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-item"><div class="status-value">{today_duration}</div><div class="status-label">Duration</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-item"><div class="status-value">{today_effort}</div><div class="status-label">Effort</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Quick Status Metrics ---
    st.markdown("### Quick Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Weight (kg)", profile.get('weight_kg', 'N/A'))
    col2.metric("Resting HR", profile.get('resting_hr', 'N/A'))
    col3.metric("Body Fat %", profile.get('body_fat_pct', 'N/A'))
    col1.metric("VO2 Max", profile.get('vo2max', 'N/A'))
    col2.metric("Athlete", profile.get('name', 'N/A'))


elif menu == "📅 Training Plan":
    st.subheader("📅 Weekly Training Plan")
    for week in training_plan:
        st.markdown(f"**Week {week.get('week', 'N/A')} starting {week.get('start_date', 'N/A')}**")
        for session in week.get('sessions', []):
            st.markdown(f"- {session}")

elif menu == "📊 Metrics":
    st.subheader("📊 Training Metrics Overview")

    flat_data = []
    for date, sessions in metrics_collected.items():
        for session in sessions:
            metrics = session.get('metrics', {})
            metrics['sport'] = session.get('sport')
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
                if 'duration_min' in sport_df:
                    st.line_chart(sport_df.set_index('date')[['duration_min']], use_container_width=True)
                if 'avg_hr' in sport_df:
                    st.line_chart(sport_df.set_index('date')[['avg_hr']], use_container_width=True)
                if 'power' in sport_df:
                    st.line_chart(sport_df.set_index('date')[['power']], use_container_width=True)
    else:
        st.info("No training metrics collected yet.")

elif menu == "📖 History":
    st.subheader("📖 Athlete History")
    history_file = "training_history.json"
    if os.path.exists(history_file):
        with open(history_file) as f:
            history_data = json.load(f)
        for entry in history_data:
            st.markdown(f"**{entry.get('date', 'N/A')} - {entry.get('summary', 'N/A')}**")
    else:
        st.info(f"No history data found at {history_file}.")

elif menu == "💬 Coach Chat":
    st.subheader("💬 Chat with Coach")
    chat_input = st.text_input("Ask your coach a question:")
    if chat_input:
        athlete_data = profile
        prompt = f"Athlete Data: {athlete_data}\nQuestion: {chat_input}"
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )
            coach_reply = response.choices[0].text.strip()
            st.markdown(f"**Coach:** {coach_reply}")
            with open("chat_log.txt", "a") as f:
                f.write(f"[{datetime.now().isoformat()}] You: {chat_input}\nCoach: {coach_reply}\n\n")
        except openai.error.OpenAIError as e:
            st.error(f"Error communicating with OpenAI: {e}")

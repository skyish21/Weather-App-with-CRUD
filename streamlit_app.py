# streamlit_app.py
import streamlit as st
import requests
import sqlite3
from datetime import datetime

# DB setup
def init_db():
    conn = sqlite3.connect("weather_app.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            temperature REAL NOT NULL,
            description TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(city, temp, desc):
    conn = sqlite3.connect("weather_app.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO weather_data(location, temperature, description, timestamp) VALUES (?, ?, ?, ?)",
              (city, temp, desc, timestamp))
    conn.commit()
    conn.close()

def fetch_weather(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def display_emoji(weather_id):
    if 200 <= weather_id <= 232:
        return "⛈️"
    elif 300 <= weather_id <= 321:
        return "⛅"
    elif 500 <= weather_id <= 531:
        return "☔"
    elif 600 <= weather_id <= 622:
        return "🌨️"
    elif 701 <= weather_id <= 741:
        return "🌁"
    elif weather_id == 762:
        return "🌋"
    elif weather_id == 771:
        return "💨"
    elif weather_id == 781:
        return "🌪️"
    elif weather_id == 800:
        return "☀️"
    elif 801 <= weather_id <= 804:
        return "☁️"
    return ""

# Streamlit UI
st.title("☁️ Weather App")
city = st.text_input("Enter city name:")
api_key = "fc3bbedbd909c2a806d87c2433a6eb21"  # Replace with your key

if st.button("Get Weather"):
    if city:
        try:
            data = fetch_weather(city, api_key)
            temp_k = data["main"]["temp"]
            temp_c = temp_k - 273.15
            desc = data["weather"][0]["description"]
            emoji = display_emoji(data["weather"][0]["id"])

            st.metric(label="Temperature (°C)", value=f"{temp_c:.2f}")
            st.write("**Description:**", desc)
            st.write("**Emoji:**", emoji)
            save_to_db(city, round(temp_c, 2), desc)
        except requests.exceptions.HTTPError as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a city.")

# Display past 5 records
if st.button("Show Recent Records"):
    conn = sqlite3.connect("weather_app.db")
    c = conn.cursor()
    c.execute("SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 5")
    records = c.fetchall()
    conn.close()

    if records:
        for rec in records:
            st.write(f"ID: {rec[0]} | {rec[4]}")
            st.write(f"City: {rec[1]}, Temp: {rec[2]}°C, Desc: {rec[3]}")
            st.markdown("---")
    else:
        st.info("No records yet.")

# Init DB on startup
init_db()

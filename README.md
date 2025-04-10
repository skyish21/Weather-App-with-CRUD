# 🌦️ PyQt5 Weather App

A desktop application built with **PyQt5** that fetches and displays weather data based on a user-specified location and date range. It includes full **CRUD operations**, **data persistence (SQLite)**, **API integration**, and **data export functionality**.

---

## 📌 Features

- 🔍 Enter location (city, zip code, etc.) and get current weather
- 🧠 Location and date range validation
- 📚 Save weather info to a SQLite database
- 🔁 Perform full CRUD:
  - **Create** new weather queries
  - **Read** previously stored queries
  - **Update** weather entries
  - **Delete** records
- 🌐 Integrates with OpenWeatherMap API for real-time data
- 📤 Export data to CSV

---

## ⚙️ Requirements

- Python 3.7+
- PyQt5
- Requests

Install them using pip:

```bash
pip install pyqt5 requests

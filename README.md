# 🌤️ Atmosphere - Weather App

A sleek, minimalist desktop weather application built with Python and CustomTkinter. It delivers real-time weather information, auto-detects your location, and provides hourly forecasts in a modern dark-themed interface.

> **Note for Beginners:** This application works right out of the box! **No API keys or registration required.**

---

## ✨ Features

* **Zero Configuration:** No API keys or account creation needed.
* **Auto-Location Detection:** Automatically detects your location on startup using IP geolocation.
* **City Search:** Easily search for popular cities around the world via the top dropdown menu.
* **Current Weather Metrics:** Displays real-time temperature, condition descriptions, wind speed, humidity, and UV index.
* **Hourly Forecast:** Scrollable horizontal cards displaying upcoming hourly temperatures and conditions.
* **Responsive Design:** Auto-scaling UI elements that adjust cleanly when resizing the window.
* **Dark Mode Theme:** Built with a clean, dark color palette for a modern aesthetic.

---

## 🛠️ Requirements & Installation

### Prerequisites
Make sure you have **Python 3.8+** installed on your system.

### Install Dependencies
Open your terminal or command prompt in the project directory and install the required packages:

```bash
pip install customtkinter requests
```
## How to Run the App
Clone or download this repository to your computer.

Open your terminal or command prompt in the project folder:

```Bash
cd path/to/weather-app
```
Run the main script:

```Bash
python main.py
```
📦 Building a Standalone Executable (.exe)
You can package this application into a standalone Windows .exe file that runs without needing Python installed.

Install PyInstaller:

```Bash
pip install pyinstaller
```
Run the build command:

```Bash
pyinstaller --noconsole --onefile main.py
```
Your finished executable will be inside the newly created dist/ folder (dist/main.exe).

📁 Project Structure
```Plaintext
weather-app/
├── main.py          # Main GUI script (CustomTkinter interface)
├── weather_api.py   # API fetch helper module
├──requirements.txt
├── icon.ico   
└── README.md        # Project documentation
```
💡 Tech Stack
Language: Python 3
GUI Framework: CustomTkinter
Threading: Python threading library (keeps the UI fast and smooth during network calls)

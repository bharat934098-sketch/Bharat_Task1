import os
import io
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from dotenv import load_dotenv
from PIL import Image, ImageTk

# Load environment variables
load_dotenv()
API_KEY = ("49062fbfbb63a6f35d5e4c971850e9cf")


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Weather Application")
        self.root.geometry("520x720")
        self.root.resizable(False, False)

        # State variables
        self.unit_celsius = True  # True = Celsius, False = Fahrenheit
        self.current_data = None
        self.forecast_data = None

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.create_widgets()
        self.auto_detect_location()

    def create_widgets(self):
        # Header Title
        title = tk.Label(
            self.root,
            text="🌦️ Weather Tracker",
            font=("Helvetica", 18, "bold"),
            fg="#2c3e50",
        )
        title.pack(pady=10)

        # Search Frame
        search_frame = ttk.Frame(self.root, padding=5)
        search_frame.pack(fill="x", padx=20)

        self.city_entry = ttk.Entry(
            search_frame, font=("Helvetica", 12), width=25
        )
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.city_entry.bind("<Return>", lambda event: self.fetch_weather())

        search_btn = ttk.Button(
            search_frame, text="Get Weather", command=self.fetch_weather
        )
        search_btn.pack(side="left", padx=2)

        clear_btn = ttk.Button(
            search_frame, text="Clear", command=self.clear_all
        )
        clear_btn.pack(side="left", padx=2)

        # Status / Error Label
        self.status_label = tk.Label(
            self.root, text="", font=("Helvetica", 10, "bold"), fg="red"
        )
        self.status_label.pack(pady=3)

        # Unit Toggle
        toggle_frame = ttk.Frame(self.root)
        toggle_frame.pack(fill="x", padx=20)
        self.unit_btn = ttk.Button(
            toggle_frame, text="Switch to °F", command=self.toggle_units
        )
        self.unit_btn.pack(anchor="e")

        # Current Weather Card
        self.card = ttk.LabelFrame(
            self.root, text=" Current Weather ", padding=10
        )
        self.card.pack(fill="x", padx=20, pady=5)

        self.city_label = tk.Label(
            self.card,
            text="City: --",
            font=("Helvetica", 14, "bold"),
            fg="#34495e",
        )
        self.city_label.pack(anchor="w")

        self.icon_label = tk.Label(self.card)
        self.icon_label.pack()

        self.temp_label = tk.Label(
            self.card, text="-- °C", font=("Helvetica", 22, "bold")
        )
        self.temp_label.pack()

        self.desc_label = tk.Label(
            self.card,
            text="Condition: --",
            font=("Helvetica", 11, "italic"),
            fg="#7f8c8d",
        )
        self.desc_label.pack(pady=2)

        metrics_frame = ttk.Frame(self.card)
        metrics_frame.pack(fill="x", pady=5)

        self.humidity_label = tk.Label(
            metrics_frame, text="Humidity: --%", font=("Helvetica", 10)
        )
        self.humidity_label.pack(side="left", expand=True)

        self.wind_label = tk.Label(
            metrics_frame, text="Wind: -- m/s", font=("Helvetica", 10)
        )
        self.wind_label.pack(side="right", expand=True)

        # Forecast Notebook (Tabs for Hourly & Daily)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.hourly_frame = ttk.Frame(self.notebook, padding=10)
        self.daily_frame = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.hourly_frame, text="6-Hour Forecast")
        self.notebook.add(self.daily_frame, text="5-Day Forecast")

    def show_error(self, message):
        self.status_label.config(text=message, fg="red")

    def clear_error(self):
        self.status_label.config(text="")

    def auto_detect_location(self):
        try:
            res = requests.get("https://ipapi.co/json/", timeout=5)
            if res.status_code == 200:
                data = res.json()
                city = data.get("city")
                if city:
                    self.city_entry.insert(0, city)
                    self.fetch_weather()
        except Exception:
            self.show_error("Auto-location failed. Please enter city manually.")

    def fetch_weather(self):
        self.clear_error()
        city = self.city_entry.get().strip()

        if not city:
            self.show_error("Please enter a city name.")
            return

        if not API_KEY or API_KEY == "your_actual_api_key_here":
            self.show_error("API Key missing or invalid in .env file.")
            return

        try:
            # Fetch Current Weather
            curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            curr_res = requests.get(curr_url, timeout=8)

            if curr_res.status_code == 404:
                self.show_error("City not found. Please verify spelling.")
                return
            elif curr_res.status_code == 401:
                self.show_error("Invalid API Key provided.")
                return
            elif curr_res.status_code != 200:
                self.show_error(f"Server error: HTTP {curr_res.status_code}")
                return

            self.current_data = curr_res.json()

            # Fetch 5-Day / 3-Hour Forecast
            fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
            fore_res = requests.get(fore_url, timeout=8)

            if fore_res.status_code == 200:
                self.forecast_data = fore_res.json()

            self.update_ui()

        except requests.exceptions.Timeout:
            self.show_error("Request timed out. Check your internet connection.")
        except requests.exceptions.ConnectionError:
            self.show_error("Network error. Unable to connect to server.")
        except Exception as e:
            self.show_error(f"Unexpected Error: {str(e)}")

    def update_ui(self):
        if not self.current_data:
            return

        # Update Current Weather Card
        city_name = self.current_data["name"]
        country = self.current_data["sys"]["country"]
        temp_c = self.current_data["main"]["temp"]
        humidity = self.current_data["main"]["humidity"]
        wind_speed = self.current_data["wind"]["speed"]
        desc = self.current_data["weather"][0]["description"].title()
        icon_code = self.current_data["weather"][0]["icon"]

        self.city_label.config(text=f"{city_name}, {country}")
        self.desc_label.config(text=f"Condition: {desc}")
        self.humidity_label.config(text=f"Humidity: {humidity}%")
        self.wind_label.config(text=f"Wind: {wind_speed} m/s")

        # Load Weather Icon
        try:
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            img_res = requests.get(icon_url, timeout=5)
            img_data = Image.open(io.BytesIO(img_res.content))
            photo = ImageTk.PhotoImage(img_data)
            self.icon_label.config(image=photo)
            self.icon_label.image = photo
        except Exception:
            self.icon_label.config(image="")

        # Temperature Display based on unit state
        self.render_temperature(temp_c)

        # Update Forecasts
        self.render_forecasts()

    def render_temperature(self, temp_c):
        if self.unit_celsius:
            self.temp_label.config(text=f"{round(temp_c, 1)} °C")
        else:
            temp_f = (temp_c * 9 / 5) + 32
            self.temp_label.config(text=f"{round(temp_f, 1)} °F")

    def toggle_units(self):
        if self.unit_celsius:
            self.unit_celsius = False
            self.unit_btn.config(text="Switch to °C")
        else:
            self.unit_celsius = True
            self.unit_btn.config(text="Switch to °F")

        if self.current_data:
            self.render_temperature(self.current_data["main"]["temp"])
            self.render_forecasts()

    def render_forecasts(self):
        # Clear existing forecast UI
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()
        for widget in self.daily_frame.winfo_children():
            widget.destroy()

        if not self.forecast_data:
            return

        forecast_list = self.forecast_data.get("list", [])

        # 1. Next 6 Hours (Takes first 2 items, 3-hour increments)
        hourly_items = forecast_list[:2]
        for i, item in enumerate(hourly_items):
            time_txt = item["dt_txt"].split(" ")[1][:5]
            tc = item["main"]["temp"]
            display_temp = (
                f"{round(tc, 1)}°C"
                if self.unit_celsius
                else f"{round((tc * 9/5) + 32, 1)}°F"
            )
            desc = item["weather"][0]["main"]

            lbl = tk.Label(
                self.hourly_frame,
                text=f"⏰ {time_txt} | Temp: {display_temp} | {desc}",
                font=("Helvetica", 11),
            )
            lbl.pack(anchor="w", pady=5)

        # 2. 5-Day Forecast (Picks index 0, 8, 16, 24, 32 corresponding to 24h intervals)
        daily_items = forecast_list[::8][:5]
        for item in daily_items:
            date_txt = item["dt_txt"].split(" ")[0]
            tc = item["main"]["temp"]
            display_temp = (
                f"{round(tc, 1)}°C"
                if self.unit_celsius
                else f"{round((tc * 9/5) + 32, 1)}°F"
            )
            desc = item["weather"][0]["main"]

            lbl = tk.Label(
                self.daily_frame,
                text=f"📅 {date_txt} | Temp: {display_temp} | {desc}",
                font=("Helvetica", 11),
            )
            lbl.pack(anchor="w", pady=5)

    def clear_all(self):
        self.city_entry.delete(0, tk.END)
        self.city_label.config(text="City: --")
        self.temp_label.config(text="-- °C")
        self.desc_label.config(text="Condition: --")
        self.humidity_label.config(text="Humidity: --%")
        self.wind_label.config(text="Wind: -- m/s")
        self.icon_label.config(image="")
        self.status_label.config(text="")
        self.current_data = None
        self.forecast_data = None

        for widget in self.hourly_frame.winfo_children():
            widget.destroy()
        for widget in self.daily_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
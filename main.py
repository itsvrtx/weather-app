import threading
import customtkinter as ctk
from weather_api import fetch_weather, fetch_weather_by_coords, get_user_location, POPULAR_CITIES


class WeatherApp(ctk.CTk):
    BG_COLOR = "#121417"
    CARD_COLOR = "#1B1E23"
    ACCENT = "#7FB3FF"
    TEXT_PRIMARY = "#F5F6F8"
    TEXT_SECONDARY = "#9AA0A8"
    BORDER = "#2A2E35"

    BASE_WIDTH = 420
    BASE_FONTS = {
        "location": 20,
        "temp": 56,
        "condition": 14,
        "icon": 80,
        "detail_label": 11,
        "detail_value": 15,
        "section_title": 14,
        "card_time": 11,
        "card_icon": 22,
        "card_temp": 14,
    }

    def __init__(self):
        super().__init__()
        self.title("Atmosphere - Weather")
        self.geometry("340x480")
        self.minsize(340, 480)
        self.resizable(False, False)

        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.BG_COLOR)

        self._resize_job = None
        self._scale = 1.0

        self._build_ui()
        self.bind("<Configure>", self._on_window_resize)
        self.after(200, self.detect_location)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(5, weight=1)
        top_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        top_bar.grid_columnconfigure(0, weight=1)

        self.city_dropdown = ctk.CTkOptionMenu(
            top_bar,
            values=POPULAR_CITIES,
            height=40,
            corner_radius=12,
            fg_color=self.CARD_COLOR,
            text_color=self.TEXT_PRIMARY,
            button_color=self.CARD_COLOR,
            button_hover_color=self.BORDER,
            dropdown_fg_color=self.CARD_COLOR,
            dropdown_text_color=self.TEXT_PRIMARY,
            dropdown_hover_color=self.BORDER,
            font=("Helvetica", 13),
            command=self._on_city_selected,
        )
        self.city_dropdown.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.locate_button = ctk.CTkButton(
            top_bar,
            text="📍",
            width=40,
            height=40,
            corner_radius=12,
            fg_color=self.CARD_COLOR,
            hover_color=self.BORDER,
            text_color=self.TEXT_PRIMARY,
            font=("Helvetica", 15),
            command=self.detect_location,
        )
        self.locate_button.grid(row=0, column=1)

        self.location_label = ctk.CTkLabel(
            self.container,
            text="Detecting your location...",
            font=("Helvetica", self.BASE_FONTS["location"], "bold"),
            text_color=self.TEXT_PRIMARY,
        )
        self.location_label.grid(row=1, column=0, pady=(0, 4))

        main_weather_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        main_weather_frame.grid(row=2, column=0, pady=(10, 20))

        self.icon_label = ctk.CTkLabel(
            main_weather_frame,
            text="🌍",
            font=("Helvetica", self.BASE_FONTS["icon"]),
            text_color=self.ACCENT,
        )
        self.icon_label.pack()

        self.temp_label = ctk.CTkLabel(
            main_weather_frame,
            text="--°",
            font=("Helvetica", self.BASE_FONTS["temp"], "bold"),
            text_color=self.TEXT_PRIMARY,
        )
        self.temp_label.pack()

        self.condition_label = ctk.CTkLabel(
            main_weather_frame,
            text="Fetching weather...",
            font=("Helvetica", self.BASE_FONTS["condition"]),
            text_color=self.TEXT_SECONDARY,
        )
        self.condition_label.pack(pady=(4, 0))

        details_frame = ctk.CTkFrame(
            self.container, fg_color=self.CARD_COLOR, corner_radius=16,
            border_width=1, border_color=self.BORDER,
        )
        details_frame.grid(row=3, column=0, sticky="ew", pady=(0, 24))
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.wind_label = self._build_detail_item(details_frame, "Wind", "-- km/h", 0)
        self.humidity_label = self._build_detail_item(details_frame, "Humidity", "--%", 1)
        self.sun_label = self._build_detail_item(details_frame, "UV Index", "--", 2)

        self.forecast_title = ctk.CTkLabel(
            self.container,
            text="Hourly Forecast",
            font=("Helvetica", self.BASE_FONTS["section_title"], "bold"),
            text_color=self.TEXT_PRIMARY,
        )
        self.forecast_title.grid(row=4, column=0, sticky="w", pady=(0, 10))

        self.hourly_frame = ctk.CTkScrollableFrame(
            self.container,
            orientation="horizontal",
            fg_color="transparent",
            height=110,
        )
        self.hourly_frame.grid(row=5, column=0, sticky="nsew")

        self._forecast_cards = []
        self._add_forecast_card("Now", "--°", "🌡️")

        self.status_label = ctk.CTkLabel(
            self.container, text="", font=("Helvetica", 12), text_color="#E06C75"
        )
        self.status_label.grid(row=6, column=0, pady=(10, 0))

    def _build_detail_item(self, parent, label_text, value_text, column):
        """Builds a single minimalist detail cell (label above value)."""
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=0, column=column, sticky="nsew", padx=10, pady=18)

        label = ctk.CTkLabel(
            cell, text=label_text, font=("Helvetica", self.BASE_FONTS["detail_label"]),
            text_color=self.TEXT_SECONDARY,
        )
        label.pack()

        value_label = ctk.CTkLabel(
            cell, text=value_text, font=("Helvetica", self.BASE_FONTS["detail_value"], "bold"),
            text_color=self.TEXT_PRIMARY,
        )
        value_label.pack(pady=(4, 0))
        return value_label

    def _add_forecast_card(self, time_text, temp, icon):
        card = ctk.CTkFrame(
            self.hourly_frame,
            width=80,
            height=100,
            corner_radius=14,
            fg_color=self.CARD_COLOR,
            border_width=1,
            border_color=self.BORDER,
        )
        card.pack(side="left", padx=6)
        card.pack_propagate(False)

        time_lbl = ctk.CTkLabel(
            card, text=time_text, font=("Helvetica", self.BASE_FONTS["card_time"]),
            text_color=self.TEXT_SECONDARY,
        )
        time_lbl.pack(pady=(12, 4))

        icon_lbl = ctk.CTkLabel(card, text=icon, font=("Helvetica", self.BASE_FONTS["card_icon"]))
        icon_lbl.pack()

        temp_lbl = ctk.CTkLabel(
            card, text=temp, font=("Helvetica", self.BASE_FONTS["card_temp"], "bold"),
            text_color=self.TEXT_PRIMARY,
        )
        temp_lbl.pack(pady=(4, 0))

        self._forecast_cards.append((card, time_lbl, icon_lbl, temp_lbl))
        return card

    def _clear_forecast_cards(self):
        for card, *_ in self._forecast_cards:
            card.destroy()
        self._forecast_cards = []

    def _populate_forecast(self, hourly_data):
        self._clear_forecast_cards()
        if not hourly_data:
            self._add_forecast_card("--", "--°", "🌡️")
            return
        for entry in hourly_data:
            self._add_forecast_card(entry.get("time", "--"), entry.get("temp", "--°"), entry.get("icon", "🌡️"))

    def _on_window_resize(self, event):
        if event.widget is not self:
            return
        # Debounce so we don't recompute on every pixel of a drag
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(120, lambda: self._apply_responsive_scale(event.width))

    def _apply_responsive_scale(self, width):
        self._resize_job = None
        scale = max(0.75, min(1.4, width / self.BASE_WIDTH))
        if abs(scale - self._scale) < 0.03:
            return
        self._scale = scale

        def s(key):
            return max(8, int(self.BASE_FONTS[key] * scale))

        self.location_label.configure(font=("Helvetica", s("location"), "bold"))
        self.icon_label.configure(font=("Helvetica", s("icon")))
        self.temp_label.configure(font=("Helvetica", s("temp"), "bold"))
        self.condition_label.configure(font=("Helvetica", s("condition")))
        self.forecast_title.configure(font=("Helvetica", s("section_title"), "bold"))

        for card, time_lbl, icon_lbl, temp_lbl in self._forecast_cards:
            time_lbl.configure(font=("Helvetica", s("card_time")))
            icon_lbl.configure(font=("Helvetica", s("card_icon")))
            temp_lbl.configure(font=("Helvetica", s("card_temp"), "bold"))

    def _on_city_selected(self, choice: str):
        if choice and choice != "Select a City...":
            self.search_weather(choice)

    def detect_location(self):
        self.status_label.configure(text="")
        self.location_label.configure(text="Detecting your location...")
        self.condition_label.configure(text="Locating you...")
        self.locate_button.configure(state="disabled", text="⏳")

        def worker():
            location = get_user_location()
            if location and location.get("lat") is not None:
                data = fetch_weather_by_coords(
                    location["lat"], location["lon"], location["city"], location["country"]
                )
            else:
                data = {"success": False, "error": "Could not detect your location automatically."}
            self.after(0, lambda: self._handle_weather_result(data))

        threading.Thread(target=worker, daemon=True).start()

    def search_weather(self, city: str):
        if not city:
            return

        self.status_label.configure(text="")
        self.condition_label.configure(text="Fetching weather...")
        self.locate_button.configure(state="disabled")

        def worker():
            data = fetch_weather(city)
            self.after(0, lambda: self._handle_weather_result(data))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_weather_result(self, data):
        self.locate_button.configure(state="normal", text="📍")

        if data.get("success"):
            self.status_label.configure(text="")
            self.location_label.configure(text=f"{data.get('city', '')}, {data.get('country', '')}".strip(", "))
            self.temp_label.configure(text=f"{data.get('temp', '--')}°C")
            self.condition_label.configure(text=data.get("description", ""))
            self.humidity_label.configure(text=f"{data.get('humidity', '--')}")
            self.wind_label.configure(text=f"{data.get('wind', '--')}")
            self.sun_label.configure(text=f"{data.get('uv', '--')}")
            self.icon_label.configure(text=data.get("icon", "🌤️"), text_color=self.ACCENT)
            self._populate_forecast(data.get("hourly"))
        else:
            self.location_label.configure(text="Notice")
            self.temp_label.configure(text="--")
            self.icon_label.configure(text="❓", text_color=self.TEXT_SECONDARY)
            self.condition_label.configure(text="Could not load weather data.")
            self.humidity_label.configure(text="--%")
            self.wind_label.configure(text="-- km/h")
            self.sun_label.configure(text="--")
            self.status_label.configure(text=data.get("error", "Failed to load data."))

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
import krpc
import tkinter as tk

conn = krpc.connect(name='SpaceX UI')
vessel = conn.space_center.active_vessel

def get_telemetry():
    surf_flight = vessel.flight(vessel.surface_reference_frame)
    orbital_flight = vessel.flight(vessel.orbit.body.reference_frame)
    orbit = vessel.orbit

    def fmt(val, unit="", prec=1, allow_neg=True):
        try:
            if not allow_neg and float(val) < 0:
                return "--"
            return f"{val:,.{prec}f}{unit}"
        except Exception:
            return "--"

    return {
        "Altitude": fmt(surf_flight.surface_altitude, " m", 0),
        "Vertical Speed": fmt(orbital_flight.vertical_speed, " m/s"),
        "Speed (Surface)": fmt(orbital_flight.speed, " m/s"),
        "Speed (Orbital)": fmt(orbit.speed, " m/s"),
        "Apoapsis": fmt(orbit.apoapsis_altitude, " m", 0),
        "Periapsis": fmt(orbit.periapsis_altitude if orbit.periapsis_altitude > 0 else 0, " m", 0),
        "Heading": fmt(surf_flight.heading, "°"),
        "Pitch": fmt(surf_flight.pitch, "°"),
        "Roll": fmt(surf_flight.roll, "°"),
        "Latitude": fmt(surf_flight.latitude, "", 4, allow_neg=True),
        "Longitude": fmt(surf_flight.longitude, "", 4, allow_neg=True)
    }

def get_engine_status():
    engines = vessel.parts.engines
    return [{"title": e.part.title, "active": e.active} for e in engines]

class SpaceXUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SpaceX Telemetry UI")
        self.configure(bg="black")
        self.geometry("500x650")
        
        tk.Label(self, text="SPACECRAFT TELEMETRY", font=("Consolas", 18, "bold"),
                 fg="#ffffff", bg="black").pack(pady=8)
        
        self.speed_label = tk.Label(self, text="0.0 m/s", font=("Consolas", 36, "bold"),
                                    fg="white", bg="black")
        self.speed_label.pack()
        
        self.vertical_speed_label = tk.Label(self, text="Vertical Speed: ---", font=("Consolas", 18),
                                             fg="#ffffff", bg="black")
        self.vertical_speed_label.pack()
        
        self.altitude_label = tk.Label(self, text="Altitude: ---", font=("Consolas", 24),
                                       fg="#ffffff", bg="black")
        self.altitude_label.pack()
        
        self.engine_label = tk.Label(self, text="ENGINES", fg="#ffffff", bg="black", font=("Consolas", 12))
        self.engine_label.pack(pady=(20,0))
        self.engine_canvas = tk.Canvas(self, bg="black", width=480, height=100, highlightthickness=0)
        self.engine_canvas.pack(pady=(0,5))
        
        self.details_frame = tk.Frame(self, bg="black")
        self.details_frame.pack(pady=8)
        self.detail_labels = {}
        for key in ["Speed (Orbital)", "Apoapsis", "Periapsis", "Heading", "Pitch", "Roll", "Latitude", "Longitude"]:
            lbl = tk.Label(self.details_frame, text=f"{key}: ---", font=("Consolas", 13),
                           fg="#888", bg="black", anchor="w")
            lbl.pack(anchor="w")
            self.detail_labels[key] = lbl
        
        self.after(250, self.update_ui)

    def draw_engines(self, engines):
        self.engine_canvas.delete("all")
        count = len(engines)
        if count == 0:
            self.engine_canvas.create_text(240, 35, text="No engines", fill="#eee", font=("Consolas", 14))
            return
        spacing = 480 // (count + 1)
        for idx, engine in enumerate(engines):
            x = spacing * (idx + 1)
            y = 40
            # Engine circle background
            self.engine_canvas.create_oval(x-20, y-20, x+20, y+20, fill="#222", outline="#444", width=2)
            # White for ON, dark for OFF
            color = "#ffffff" if engine["active"] else "#111"
            self.engine_canvas.create_oval(
                x-14, y-14, x+14, y+14,
                fill=color,
                outline="#ffffff" if engine["active"] else "#444",
                width=3
            )
            # Label below, shifted lower for no clipping
            self.engine_canvas.create_text(x, y+30, text=engine["title"], fill="#888", font=("Consolas", 10))

    def update_ui(self):
        telemetry = get_telemetry()
        engines = get_engine_status()
        self.speed_label.config(text=f"{telemetry['Speed (Surface)']}")
        self.vertical_speed_label.config(text=f"Vertical Speed: {telemetry['Vertical Speed']}")
        self.altitude_label.config(text=f"Altitude: {telemetry['Altitude']}")
        for key in self.detail_labels:
            self.detail_labels[key].config(text=f"{key}: {telemetry[key]}")
        self.draw_engines(engines)
        self.after(250, self.update_ui)

if __name__ == "__main__":
    app = SpaceXUI()
    app.mainloop()
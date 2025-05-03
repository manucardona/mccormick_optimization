# 🚇 Smooth Operator

Welcome to **Smooth Operator**, yeah like the song! A smart and simple Dash web app built at the University of Chicago’s **Transit Hackathon** to help residents and visitors navigate Chicago more smoothly during major events.

💡 Inspired by the chaos of big conferences (like those at McCormick Place), this app identifies **transit disruptions** caused by overlapping public transportation routes and scheduled events — all in real time.

---

## 🌟 Features

- 🗺️ Enter a **start** and **end address**, plus your **travel date**  
- 🚍 Get the **recommended public transit route** (CTA, Metra, Buses)
- 🎉 Automatically check for **events happening along your route**
- 🚨 Flag potential **transit disruptions**
- 🖼️ Visualize everything on an interactive **Folium map**

---

## 🔧 Tech Stack

- **Dash** for the interactive web app  
- **Folium** for mapping and spatial overlays  
- **Google Maps API** for route and geolocation data  
- **Shapely / GeoJSON** for event radius detection  
- **Python** for backend logic and event-routing integration  

---

## 🧪 How to Run Locally

1. Clone the repository:
   ```bash
   git clone 
   cd mccormick-optimizer
   
2. Sync the virtual environment (using uv):
   ```bash
   uv sync
   uv pip install -r requirements.txt

3. Set your Google Maps API key in an .env file or within your google_utils.py

4. Run the app:
   ```bash
   uv run app.py

## 📦 Project Structure
   ```bash
     mccormick_optimization/
  │
  ├── app.py                  # Main Dash app
  ├── utils/                  # Helper functions
  │   ├── google_utils.py
  │   ├── route_utils.py
  │   └── transport_radius.py
  ├── assets/                 # Static assets (if needed)
  ├── data/                   # Mock or real event datasets
  └── README.md               # You’re here!


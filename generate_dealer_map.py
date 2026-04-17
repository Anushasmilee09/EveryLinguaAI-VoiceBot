"""
Generate a PNG map showing all EveryLingua dealer locations across India
"""
import folium
from folium.plugins import MarkerCluster
import io
import sys
import os

# All dealer locations (from dealership_logic.py)
dealers = [
    {"name": "Mumbai Central", "city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"name": "Andheri", "city": "Mumbai", "state": "Maharashtra", "lat": 19.1196, "lng": 72.8478},
    {"name": "Pune", "city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},
    {"name": "Connaught Place", "city": "Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"name": "Dwarka", "city": "Delhi", "state": "Delhi", "lat": 28.5921, "lng": 77.0460},
    {"name": "Gurgaon", "city": "Gurgaon", "state": "Haryana", "lat": 28.4595, "lng": 77.0266},
    {"name": "Noida", "city": "Noida", "state": "Uttar Pradesh", "lat": 28.5706, "lng": 77.3219},
    {"name": "Bangalore", "city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"name": "Whitefield", "city": "Bangalore", "state": "Karnataka", "lat": 12.9698, "lng": 77.7500},
    {"name": "Chennai", "city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    {"name": "Coimbatore", "city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
    {"name": "Hyderabad", "city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    {"name": "Hi-Tech City", "city": "Hyderabad", "state": "Telangana", "lat": 17.4504, "lng": 78.3806},
    {"name": "Ahmedabad", "city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714},
    {"name": "Surat", "city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311},
    {"name": "Kolkata", "city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    {"name": "Jaipur", "city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"name": "Kochi", "city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
    {"name": "Indore", "city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
    {"name": "Lucknow", "city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    # --- 12 NEW DEALERS ---
    {"name": "Chandigarh", "city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794},
    {"name": "Bhubaneswar", "city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245},
    {"name": "Guwahati", "city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362},
    {"name": "Patna", "city": "Patna", "state": "Bihar", "lat": 25.6093, "lng": 85.1376},
    {"name": "Ranchi", "city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
    {"name": "Panaji", "city": "Panaji", "state": "Goa", "lat": 15.4909, "lng": 73.8278},
    {"name": "Raipur", "city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296},
    {"name": "Dehradun", "city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lng": 78.0322},
    {"name": "Srinagar", "city": "Srinagar", "state": "Jammu & Kashmir", "lat": 34.0837, "lng": 74.7973},
    {"name": "Visakhapatnam", "city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
    {"name": "Dimapur", "city": "Dimapur", "state": "Nagaland", "lat": 25.9065, "lng": 93.7272},
    {"name": "Ranchi", "city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
]

# Remove duplicate Ranchi
seen = set()
unique_dealers = []
for d in dealers:
    key = (d["lat"], d["lng"])
    if key not in seen:
        seen.add(key)
        unique_dealers.append(d)
dealers = unique_dealers

print(f"Total dealers: {len(dealers)}")

# Create folium map centered on India
india_center = [22.0, 79.0]
m = folium.Map(
    location=india_center,
    zoom_start=5,
    tiles='OpenStreetMap',
    width=1400,
    height=900,
    control_scale=True
)

# Add title
title_html = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000;
     background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
     padding: 12px 30px; border-radius: 10px;
     box-shadow: 0 4px 20px rgba(0,0,0,0.4); border: 1px solid rgba(59,130,246,0.3);">
    <h3 style="margin:0; color: #ffffff; font-family: Arial, sans-serif; font-size: 18px; text-align: center;">
        🏍️ EveryLingua Motors — Dealer Network ({count} Locations)
    </h3>
</div>
'''.format(count=len(dealers))
m.get_root().html.add_child(folium.Element(title_html))

# Color scheme for states
state_colors = {
    "Maharashtra": "#ef4444",
    "Delhi": "#f59e0b",
    "Haryana": "#f59e0b",
    "Uttar Pradesh": "#84cc16",
    "Karnataka": "#06b6d4",
    "Tamil Nadu": "#8b5cf6",
    "Telangana": "#ec4899",
    "Gujarat": "#f97316",
    "West Bengal": "#14b8a6",
    "Rajasthan": "#eab308",
    "Kerala": "#22c55e",
    "Madhya Pradesh": "#a855f7",
    "Punjab": "#0ea5e9",
    "Odisha": "#64748b",
    "Assam": "#10b981",
    "Bihar": "#d946ef",
    "Jharkhand": "#fb923c",
    "Goa": "#2dd4bf",
    "Chhattisgarh": "#c084fc",
    "Uttarakhand": "#38bdf8",
    "Jammu & Kashmir": "#4ade80",
    "Andhra Pradesh": "#f472b6",
    "Nagaland": "#a3e635",
}

# Add markers for each dealer
for i, dealer in enumerate(dealers):
    color = state_colors.get(dealer["state"], "#3b82f6")
    
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 200px;">
        <h4 style="margin: 0 0 5px 0; color: #1e3a5f;">🏍️ EveryLingua Motors</h4>
        <h5 style="margin: 0 0 8px 0; color: #3b82f6;">{dealer['name']}</h5>
        <p style="margin: 2px 0; font-size: 13px;">📍 {dealer['city']}, {dealer['state']}</p>
        <p style="margin: 2px 0; font-size: 12px; color: #666;">Lat: {dealer['lat']}, Lng: {dealer['lng']}</p>
    </div>
    """
    
    folium.CircleMarker(
        location=[dealer["lat"], dealer["lng"]],
        radius=10,
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.85,
        weight=2,
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"EveryLingua Motors - {dealer['name']} ({dealer['city']})"
    ).add_to(m)
    
    # Add label
    folium.Marker(
        location=[dealer["lat"], dealer["lng"]],
        icon=folium.DivIcon(
            html=f'<div style="font-size: 9px; font-weight: bold; color: #1e293b; text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white; white-space: nowrap; transform: translate(-50%, 12px);">{dealer["city"]}</div>',
            icon_size=(0, 0),
            icon_anchor=(0, 0)
        )
    ).add_to(m)

# Save as HTML first
html_path = os.path.join(os.path.dirname(__file__), "dealer_map.html")
m.save(html_path)
print(f"Interactive map saved to: {html_path}")

# Now generate PNG using selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    import time
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,900")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}")
    time.sleep(4)  # Wait for tiles to load
    
    png_path = os.path.join(os.path.dirname(__file__), "dealer_map.png")
    driver.save_screenshot(png_path)
    driver.quit()
    print(f"PNG map saved to: {png_path}")
    
except Exception as e:
    print(f"Selenium screenshot failed ({e}), trying matplotlib fallback...")
    
    # Matplotlib fallback
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        fig.patch.set_facecolor('#0f172a')
        ax.set_facecolor('#1a2332')
        
        # Plot each dealer
        for dealer in dealers:
            color = state_colors.get(dealer["state"], "#3b82f6")
            ax.scatter(dealer["lng"], dealer["lat"], c=color, s=120, edgecolors='white', 
                      linewidths=1.5, zorder=5, alpha=0.9)
            ax.annotate(dealer["city"], (dealer["lng"], dealer["lat"]),
                       textcoords="offset points", xytext=(8, 6),
                       fontsize=7, color='white', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='#1e3a5f', 
                                edgecolor='#3b82f6', alpha=0.8))
        
        # India approximate boundary
        ax.set_xlim(68, 98)
        ax.set_ylim(6, 37)
        ax.set_aspect(1.0)
        
        ax.set_xlabel('Longitude', color='#94a3b8', fontsize=10)
        ax.set_ylabel('Latitude', color='#94a3b8', fontsize=10)
        ax.set_title(f'🏍️ EveryLingua Motors — Dealer Network ({len(dealers)} Locations)',
                     color='white', fontsize=16, fontweight='bold', pad=15)
        
        ax.tick_params(colors='#64748b', labelsize=8)
        ax.grid(True, alpha=0.15, color='#3b82f6')
        
        for spine in ax.spines.values():
            spine.set_edgecolor('#3b82f6')
            spine.set_alpha(0.3)
        
        # Legend for unique states
        unique_states = list(set(d["state"] for d in dealers))
        unique_states.sort()
        legend_patches = [mpatches.Patch(color=state_colors.get(s, "#3b82f6"), label=s) for s in unique_states]
        legend = ax.legend(handles=legend_patches, loc='lower left', fontsize=7,
                          facecolor='#1e293b', edgecolor='#3b82f6', labelcolor='white',
                          ncol=2, title='States', title_fontsize=8)
        legend.get_title().set_color('white')
        
        png_path = os.path.join(os.path.dirname(__file__), "dealer_map.png")
        plt.savefig(png_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close()
        print(f"PNG map saved to: {png_path}")
    except Exception as e2:
        print(f"Matplotlib fallback also failed: {e2}")
        sys.exit(1)

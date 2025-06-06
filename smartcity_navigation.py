from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import osmnx as ox
import folium
from branca.element import Element
from geopy.geocoders import Nominatim
from datetime import datetime
import networkx as nx
import numpy as np
from xgboost import XGBClassifier
import os

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    start_place: str
    end_place: str

# Global vars
G = None
model = None
geolocator = Nominatim(user_agent="bengkulu_navigator")

GRAPH_FILE = "bengkulu.graphml"
MODEL_FILE = "xgb_model.json"

@app.on_event("startup")
def load_resources():
    global G, model
    if os.path.exists(GRAPH_FILE):
        print("Memuat graph dari file cache...")
        G = ox.load_graphml(GRAPH_FILE)
    else:
        print("Membuat graph dari OSM dan menyimpannya...")
        G = ox.graph_from_place("Bengkulu, Indonesia", network_type='drive', simplify=True).to_undirected()
        ox.save_graphml(G, GRAPH_FILE)

    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    if os.path.exists(MODEL_FILE):
        print("Memuat model XGBoost dari file...")
        model.load_model(MODEL_FILE)
    else:
        print("Melatih model XGBoost...")
        X_train, y_train = [], []
        for u, v, key, data in G.edges(keys=True, data=True):
            length = data.get('length', 0)
            X_train.append([length])
            y_train.append(1 if length > 200 else 0)
        model.fit(np.array(X_train), np.array(y_train))
        model.save_model(MODEL_FILE)

@app.post("/generate-route", response_class=HTMLResponse)
async def generate_route(req: RouteRequest):
    def get_coords(place):
        try:
            location = geolocator.geocode(place + ", Bengkulu, Indonesia")
            return (location.latitude, location.longitude) if location else None
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    start_coords = get_coords(req.start_place)
    end_coords = get_coords(req.end_place)
    if not start_coords:
        return HTMLResponse("<b>Lokasi awal tidak ditemukan!</b>")
    if not end_coords:
        return HTMLResponse("<b>Lokasi tujuan tidak ditemukan!</b>")

    try:
        start_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
        end_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])
    except Exception as e:
        print(f"Error mencari node: {e}")
        return HTMLResponse("<b>Gagal menemukan rute di peta!</b>")

    def predict_congestion_edges(G, model):
        result = []
        for u, v, key, data in G.edges(keys=True, data=True):
            length = data.get('length', 0)
            pred = model.predict([[length]])
            if pred[0] == 1:
                result.append((u, v))
        return result

    def get_route_edge_attributes(G, route, attribute):
        attributes = []
        for u, v in zip(route[:-1], route[1:]):
            if G.has_edge(u, v):
                edge_data = G.get_edge_data(u, v)
                if edge_data:
                    first_edge = next(iter(edge_data.values()))
                    attributes.append(first_edge.get(attribute, 0))
        return attributes

    def calculate_travel_times(distance):
        speeds = {'jalan_kaki': 1.4, 'motor': 8.33, 'mobil': 11.11}
        times = {}
        for mode, speed in speeds.items():
            seconds = distance / speed
            mins, secs = divmod(int(seconds), 60)
            times[mode] = f"{mins:02d}:{secs:02d}"
        return times

    def get_current_time():
        now = datetime.now()
        return now.strftime("%H:%M %a, %d %b")

    def find_shortest_path_astar(G, start, end):
        try:
            route = nx.astar_path(G, start, end, weight='length')
            distance = sum(get_route_edge_attributes(G, route, "length"))
            return route, distance
        except Exception as e:
            print(f"Error A*: {e}")
            return None, 0

    def find_shortest_path_dijkstra(G, start, end, congested_edges=None, penalty_factor=3):
        try:
            G_temp = G.copy()
            if congested_edges:
                for u, v in congested_edges:
                    if G_temp.has_edge(u, v):
                        for key in G_temp[u][v]:
                            G_temp[u][v][key]["length"] *= penalty_factor
            route = nx.shortest_path(G_temp, start, end, weight="length")
            distance = sum(get_route_edge_attributes(G_temp, route, "length"))
            return route, distance
        except Exception as e:
            print(f"Error Dijkstra: {e}")
            return None, 0

    congested_edges = predict_congestion_edges(G, model)
    route_main, distance_main = find_shortest_path_astar(G, start_node, end_node)
    route_alt, distance_alt = find_shortest_path_dijkstra(G, start_node, end_node, congested_edges)

    m = folium.Map(location=start_coords, zoom_start=14, tiles='OpenStreetMap')
    # Tambahkan marker titik awal
    folium.Marker(
        location=start_coords,
        popup=f"Start: {req.start_place}",
        icon=folium.Icon(color='green', icon='flag')
    ).add_to(m)

    # Tambahkan marker titik tujuan
    folium.Marker(
        location=end_coords,
        popup=f"Tujuan: {req.end_place}",
        icon=folium.Icon(color='red', icon='flag')
    ).add_to(m)

    def is_congested(u, v):
        return (u, v) in congested_edges or (v, u) in congested_edges

    def draw_route_line(route, color, weight=6, dash=None, opacity=1):
        for u, v in zip(route[:-1], route[1:]):
            coords = [(G.nodes[u]['y'], G.nodes[u]['x']), (G.nodes[v]['y'], G.nodes[v]['x'])]
            folium.PolyLine(
                coords,
                color=color,
                weight=weight,
                dash_array=dash,
                opacity=opacity
            ).add_to(m)

    if route_main:
        for u, v in zip(route_main[:-1], route_main[1:]):
            color = '#FF0000' if is_congested(u, v) else '#4285F4'
            draw_route_line([u, v], color)

    if route_alt:
        draw_route_line(route_alt, color="#000000", weight=5, dash="1,10", opacity=1)

    # Tambahkan info box yang lebih profesional
    kemacetan_terdeteksi = any(is_congested(u, v) for u, v in zip(route_main[:-1], route_main[1:])) if route_main else False

    travel_times = calculate_travel_times(distance_main)
    current_time = get_current_time()
    alt_distance_text = f"{distance_alt:.0f}" if route_alt else "0"

    info_html = f"""
    <div style="position: fixed; bottom: 20px; left: 20px; 
                width: 300px; background: white; padding: 15px;
                border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 9999; font-family: 'Segoe UI', Arial, sans-serif;
                border-top: 4px solid #B71C1C;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 16px; font-weight: bold; color: #B71C1C;">BENGKULU Navigator</div>
            <div style="font-size: 12px; color: #666;">{current_time}</div>
        </div>
        <div style="margin-bottom: 15px;">
            <div style="display: flex; margin-bottom: 5px;">
                <div style="width: 8px; height: 8px; background: #0F9D58; border-radius: 50%; margin-top: 5px; margin-right: 8px;"></div>
                <div style="font-size: 14px;"><b>Lokasi Awal:</b> {req.start_place}</div>
            </div>
            <div style="display: flex;">
                <div style="width: 8px; height: 8px; background: #DB4437; border-radius: 50%; margin-top: 5px; margin-right: 8px;"></div>
                <div style="font-size: 14px;"><b>Lokasi Tujuan:</b> {req.end_place}</div>
            </div>
        </div>
        <div style="background: #FFC0CB; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 14px;">Jarak Utama</span>
                <span style="font-weight: bold; color: #000000;">{distance_main:.0f} meter</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 14px;">Jarak Alternatif</span>
                <span style="font-weight: bold; color: #000000;">{alt_distance_text} meter</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px;">
            <div style="text-align: center; padding: 5px; border-radius: 6px; background: #FFC0CB;">
                <div><b>Jalan Kaki</b><br>{travel_times['jalan_kaki']} menit</div>
            </div>
            <div style="text-align: center; padding: 5px; border-radius: 6px; background: #FFC0CB;">
                <div><b>Motor</b><br>{travel_times['motor']} menit</div>
            </div>
            <div style="text-align: center; padding: 5px; border-radius: 6px; background: #FFC0CB;">
                <div><b>Mobil</b><br>{travel_times['mobil']} menit</div>
            </div>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(info_html))

    # Tampilkan warning box kalau ada kemacetan
    if kemacetan_terdeteksi:
        warning_html = """
        <div style="
            position: fixed;
            bottom: 50px;
            right: 50px;
            z-index: 9999;
            background-color: #fff3cd;
            padding: 15px;
            border: 2px solid #ffecb5;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            font-size: 14px;
            width: 225px;
        ">
            <strong style="color:#856404;">⚠️ Peringatan Kemacetan</strong>
            <p>Rute utama diprediksi mengalami kemacetan</p>
            <p>Gunakan Rute Alternatif</p>
        </div>
        """
        legend_html = """
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            z-index:9999;
            background-color:white;
            padding:10px;
            border-radius:8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            font-size:14px;
            line-height: 1.5;
        ">
            <strong>Note:</strong><br>
            <span style="color:#FF0000;">■</span> Jalan Macet<br>
            <span style="color:#4285F4;">■</span> Rute Utama Lancar<br>
            <span style="color:#000000;">■</span> Rute Alternatif
        </div>
        """
        m.get_root().html.add_child(folium.Element(warning_html))
        m.get_root().html.add_child(folium.Element(legend_html))

    m.save("navigation_map.html")
    print("Peta berhasil dibuat.")
    return m.get_root().render()

from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dam_database import DAM_REGISTRY
from hydrodynamic_model import froehlich_peak_discharge, calculate_wave_propagation
from weather_service import fetch_live_catchment_weather
from evacuation_engine import assess_infrastructure_exposure
from chat_engine import handle_assistant_query

app = FastAPI(title="PRAVAH Hydrodynamic Simulation API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

class SimulationRequest(BaseModel):
    dam_id: str = "tehri"
    breach_width_m: float = Field(65.0, gt=0)
    breach_depth_m: float = Field(38.0, gt=0)
    formation_time_min: float = Field(35.0, gt=0)
    failure_mode: str = "overtopping"

class ChatRequest(BaseModel):
    message: str
    active_dam_id: Optional[str] = "tehri"

@app.get("/")
def index():
    return {"system": "PRAVAH Hydrodynamic API", "status": "ONLINE",
            "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/dams")
def list_dams():
    return list(DAM_REGISTRY.values())

@app.get("/api/weather/live")
def get_weather(lat: float = 30.3780, lon: float = 78.4803):
    return fetch_live_catchment_weather(lat, lon)

@app.post("/api/simulate")
def run_simulation(req: SimulationRequest):
    dam = DAM_REGISTRY.get(req.dam_id, DAM_REGISTRY["tehri"])
    h_w = req.breach_depth_m * 1.1
    v_w = dam["gross_storage_mcm"] * 1e6 * (h_w / dam["height_m"])
    q_peak = froehlich_peak_discharge(v_w, h_w, req.failure_mode)
    settlements = calculate_wave_propagation(q_peak, req.breach_width_m,
        req.breach_depth_m, req.formation_time_min, dam["downstream_settlements"])
    flood_area = round(req.breach_width_m * 0.42 + 18.5, 1)
    infra = assess_infrastructure_exposure(q_peak, flood_area)
    return {"dam_name": dam["name"], "river": dam["river"],
            "peak_discharge_cumec": q_peak, "flood_area_km2": flood_area,
            "settlements": settlements, "infrastructure": infra,
            "severity": "CRITICAL" if q_peak > 18000 else "HIGH"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty query")
    result = handle_assistant_query(req.message, req.active_dam_id)
    return {"reply": result["reply"], "suggestions": result["suggestions"],
            "timestamp": datetime.utcnow().isoformat()}

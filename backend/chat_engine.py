from typing import Dict, Any
import re

from dam_database import DAM_REGISTRY
from weather_service import fetch_live_catchment_weather
from hydrodynamic_model import froehlich_peak_discharge

"""Improved chat handler for PRAVAH Safety Copilot.

This module keeps the interface simple (handle_assistant_query) so the
FastAPI endpoint can remain unchanged. Responses are deterministic and
safe (no external LLM calls). The handler provides:
- clear greetings and suggestions
- formula explanations
- SOP/evacuation guidance
- telemetry summary (including a best-effort live weather fetch)
- simulation guidance
"""


def _suggestions(*items: str):
    return list(items)


def handle_assistant_query(query: str, active_dam_id: str = "tehri") -> Dict[str, Any]:
    """Produce a simple assistant reply and suggestion list.

    Args:
        query: user message (free text)
        active_dam_id: dam id to use for contextual telemetry

    Returns:
        dict with keys: reply (str), suggestions (list[str])
    """
    q = (query or "").lower().strip()
    dam = DAM_REGISTRY.get(active_dam_id, DAM_REGISTRY["tehri"])

    # Greeting / help
    if re.search(r"\b(hi|hello|hey|help)\b", q):
        return {
            "reply": "PRAVAH Safety Copilot is ready. Ask about telemetry, simulation, weather, evacuation, or formulas.",
            "suggestions": _suggestions("Tehri Dam telemetry", "Run 60m breach simulation", "Emergency SOP"),
        }

    # Formula / physics
    if "formula" in q or "froehlich" in q or "physics" in q:
        reply = (
            "Peak discharge uses the Froehlich formulation: Qp = 0.607 × Vw^0.295 × hw^1.24. "
            "In the wave propagation model we estimate celerity as c = sqrt(g * y) + u (approx.)."
        )
        return {"reply": reply, "suggestions": _suggestions("Run 75m breach simulation", "Explain arrival times")}

    # SOP / evacuation guidance
    if any(k in q for k in ("sop", "evacuation", "shelter", "evacuate")):
        reply = (
            "Emergency SOP (summary): At T+0 issue RED warning; at T+5 broadcast SMS/IVR; "
            "at T+15 move people toward elevated safe shelters and keep evacuation corridors clear. "
            "Coordinate with local authorities and NDRF teams."
        )
        return {"reply": reply, "suggestions": _suggestions("Show affected hospitals", "Simulate wave front")}

    # Simulation guidance
    if "simulate" in q or "breach" in q or re.search(r"run \d+m breach", q):
        reply = (
            "To run a simulation use the dashboard controls or POST to /api/simulate with fields: "
            "dam_id, breach_width_m, breach_depth_m, formation_time_min, failure_mode. "
            "Example: Run a 60 m breach with 35 m depth and 30 min formation time."
        )
        return {"reply": reply, "suggestions": _suggestions("Run 60m breach simulation")}

    # Dam / telemetry queries
    if "telemetry" in q or "dam" in q or dam["id"] in q or any(x in q for x in ("water level", "spillway", "storage", "capacity")):
        # Try fetching live weather but never fail the conversation
        try:
            weather = fetch_live_catchment_weather(dam["lat"], dam["lon"]) or {}
        except Exception:
            weather = {}

        reply = (
            f"{dam['name']} ({dam['river']}) — Water level: {dam['current_water_level_m']} m (FRL {dam['full_reservoir_level_m']} m). "
            f"Spillway capacity: {dam['spillway_capacity_cumec']:,} m³/s. "
            f"Latest weather: {weather.get('temperature', 'n/a')}, rainfall {weather.get('rainfall', 'n/a')}."
        )
        return {"reply": reply, "suggestions": _suggestions("Explain hydrodynamic formula", "Emergency SOP")}

    # Numeric calculation example: estimate peak discharge from a brief inline request
    m = re.search(r"peak\s+discharge\s+for\s+(?P<v>\d+(?:\.\d+)?)m3\s*.*height\s+(?P<h>\d+(?:\.\d+)?)m", q)
    if m:
        try:
            V_w = float(m.group("v"))
            h_w = float(m.group("h"))
            q_peak = froehlich_peak_discharge(V_w, h_w)
            return {"reply": f"Estimated peak discharge (Froehlich) = {q_peak} m³/s for Vw={V_w} m3 and hw={h_w} m.",
                    "suggestions": _suggestions("Run matching simulation")}
        except Exception:
            pass

    # Fallback
    return {
        "reply": "I can help with dam telemetry, run simulations, explain formulas, or provide SOPs. Try: 'Tehri dam telemetry' or 'Simulate 60m breach'.",
        "suggestions": _suggestions("Tehri Dam telemetry", "Explain hydrodynamic formula", "Emergency SOP"),
    }

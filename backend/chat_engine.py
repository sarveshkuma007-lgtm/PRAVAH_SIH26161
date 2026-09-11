from dam_database import DAM_REGISTRY

def handle_assistant_query(query, active_dam_id="tehri"):
    q = query.lower().strip()
    if any(k in q for k in ["hi", "hello", "help"]):
        return {"reply": "PRAVAH Safety Copilot is ready. Ask about telemetry, simulation, weather, evacuation, or formulas.",
                "suggestions": ["Tehri Dam telemetry", "Run 60m breach simulation", "Emergency SOP"]}
    if "formula" in q or "froehlich" in q or "physics" in q:
        return {"reply": "Peak discharge uses the Froehlich formulation: Qp = 0.607 × Vw^0.295 × hw^1.24. Wave celerity uses c = √(g × y) + u.",
                "suggestions": ["Run 75m breach simulation", "Emergency SOP"]}
    if "sop" in q or "evacuation" in q or "shelter" in q:
        return {"reply": "Emergency SOP: T+0 issue a red warning; T+5 broadcast SMS/IVR; T+15 move people toward elevated safe shelters and keep evacuation corridors clear.",
                "suggestions": ["Show affected hospitals", "Simulate wave front"]}
    if "simulate" in q or "breach" in q:
        return {"reply": "Simulation request received. Use the controls on the left to set breach width, depth, and formation time, then run the model.",
                "suggestions": ["Run 60m breach simulation"]}
    dam = DAM_REGISTRY.get(active_dam_id, DAM_REGISTRY["tehri"])
    if "dam" in q or "telemetry" in q or "tehri" in q:
        return {"reply": f"{dam['name']} telemetry: water level {dam['current_water_level_m']} m / FRL {dam['full_reservoir_level_m']} m; spillway capacity {dam['spillway_capacity_cumec']:,} m³/s.",
                "suggestions": ["Explain hydrodynamic formula", "Emergency SOP"]}
    return {"reply": "Telemetry analyzed. Ask about dam capacity, weather alerts, hydrodynamic formulas, or emergency action plans.",
            "suggestions": ["Tehri Dam telemetry", "Explain hydrodynamic formula", "Emergency SOP"]}

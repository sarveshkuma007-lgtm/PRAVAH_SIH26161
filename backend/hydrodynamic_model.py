import math

def froehlich_peak_discharge(V_w, h_w, failure_mode="overtopping"):
    if V_w <= 0 or h_w <= 0:
        return 0.0
    q = 0.607 * (V_w ** 0.295) * (h_w ** 1.24)
    if failure_mode == "overtopping":
        q *= 1.15
    return round(q, 2)

def calculate_wave_propagation(q_peak, breach_width, breach_depth, formation_time_min, settlements,
                               manning_n=0.040, slope=0.0018):
    results = []
    decay_coeff = 0.014 * (manning_n / 0.035) / (slope ** 0.2)
    for s in settlements:
        dist = s["dist_km"]
        depth = max(0.5, (breach_depth * 0.28) * math.exp(-0.018 * dist) * (breach_width / 60.0))
        celerity = math.sqrt(9.81 * depth) + 2.2
        arrival = round((dist * 1000) / (celerity * 60), 1)
        peak_arrival = round(arrival + formation_time_min * 0.55, 1)
        discharge = max(180.0, q_peak * math.exp(-decay_coeff * dist))
        velocity = round(min(11.5, celerity), 2)
        danger = depth * (velocity + 0.5)
        if danger > 4.0 or depth > 3.5: risk = "VERY HIGH"
        elif danger > 2.0 or depth > 1.8: risk = "HIGH"
        elif danger > 0.6 or depth > 0.6: risk = "MEDIUM"
        else: risk = "LOW"
        results.append({
            "name": s["name"], "dist_km": dist, "population": s["population"],
            "depth_m": round(depth, 2), "velocity_mps": velocity,
            "discharge_cumec": round(discharge, 2),
            "arrival_time_min": arrival, "peak_arrival_time_min": peak_arrival,
            "risk_level": risk, "coords": s["coords"]
        })
    return results

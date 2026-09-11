def assess_infrastructure_exposure(peak_q, flood_area_km2):
    multiplier = flood_area_km2 / 25.0
    return {
        "hospitals_at_risk": max(1, int(3 * multiplier)),
        "schools_at_risk": max(3, int(12 * multiplier)),
        "relief_shelters_active": max(4, int(16 * multiplier)),
        "bridges_in_red_zone": max(1, int(4 * multiplier)),
        "ndrf_teams_deployed": 6 if peak_q > 18000 else 2
    }

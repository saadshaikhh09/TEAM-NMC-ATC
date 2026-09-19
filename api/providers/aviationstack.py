"""SECONDARY flight status / cross-check only. Owner: Person B.

    GET http://api.aviationstack.com/v1/flights?access_key=...&flight_iata=...

WARNING: free tier is HTTP only. The key travels in plaintext. Backend only —
never call this from the browser, and never log the full URL.

HARD LIMIT: 500 requests/month. Goes through core.quota.spend().

Do NOT build automatic AeroDataBox -> AviationStack failover. Normalising two
status providers into one path costs hours and protects against an outage that
will not happen in 90 seconds. This exists so we can say we cross-verified,
and as a manual switch if AeroDataBox is down at hour 20.

Gotchas: `200` with `data: []` means the flight/date is wrong, not that nothing
happened. Yesterday's arrivals linger until ~3am local.
"""
raise NotImplementedError("B7")

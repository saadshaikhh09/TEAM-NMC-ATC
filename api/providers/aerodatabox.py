"""PRIMARY flight status. Owner: Person B.

    GET /flights/number/{flightNumber}/{date}
    X-RapidAPI-Key, X-RapidAPI-Host

Chosen over AviationStack as primary: richer status vocabulary (distinguishes
Boarding / GateClosed / Diverted / CanceledUncertain), 5 req/sec, and it is on
HTTPS.

HARD LIMITS: 500 requests/month, 5 requests/second.
Every call goes through core.quota.spend() first. No exceptions.

Gotchas from the reference:
  - date is YYYY-MM-DD. Always pass it; flight numbers are reused daily.
  - codeshares may return under the OPERATING carrier, not the marketed one.
  - 403 means the endpoint tier is not on our plan, not a bad key.
"""
raise NotImplementedError("B6")

"""Flight search + booking, TEST MODE ONLY. Owner: Person D.

    POST /air/offer_requests      search
    GET  /air/offers/{id}         one offer
    POST /air/orders              book
    GET  /air/orders/{id}         order status + airline_initiated_changes

Headers: Authorization: Bearer ..., Duffel-Version: v2

Limits: 30 req/min, ~120 offer searches before a secondary limit. Watch the
`ratelimit-remaining` response header.

Webhooks: Duffel fires `order.airline_initiated_change_detected` ONLY for
orders booked through Duffel. You cannot subscribe to arbitrary flight numbers.
See routes/webhooks.py — that is an OPTIONAL hour-18 upgrade, not the detection
path. Detection is polling plus our declared simulate endpoint.
"""
raise NotImplementedError("D1")

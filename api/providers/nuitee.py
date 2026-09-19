"""Hotel search + REAL sandbox booking lifecycle. Owner: Person D.

    GET    /hotels/search          find
    GET    /hotels/rates           rates for a property
    POST   /bookings/prebook       hold          -> prebook_id
    POST   /bookings/book          confirm       -> booking_id
    GET    /bookings/{id}          retrieve
    DELETE /bookings/{id}          cancel

Header: X-API-Key: sand_...

This is a genuine upgrade over a mock hotel: the sandbox performs a real
prebook -> book -> cancel round trip and returns real confirmation numbers.
Our hotel leg becomes an actual write rather than a simulated one.

Two things to respect:
  - There is NO modify endpoint. A date change is cancel-then-rebook. See
    HotelProvider.change_dates() — the failure window between the two is real
    and must be audited honestly.
  - 409 Conflict between prebook and book means the room sold. Re-prebook.
"""
raise NotImplementedError("D3")

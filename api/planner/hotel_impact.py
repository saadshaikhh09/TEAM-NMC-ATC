"""Does the new arrival break the hotel booking? Owner: Person A.

Reads the NEW arrival time, not the original. Prefers modify over rebook.
"""
from datetime import time, timedelta

from core.timezones import local_time


def assess(hotel, new_arrival_utc, policy) -> dict:
    arrival = local_time(new_arrival_utc, hotel.city)
    cutoff = time.fromisoformat(policy["hotel"]["late_arrival_cutoff"])
    new_check_in = hotel.check_in

    if arrival.date() > hotel.check_in:
        new_check_in = arrival.date()
    elif arrival.date() == hotel.check_in and arrival.time() > cutoff:
        new_check_in += timedelta(days=1)

    required = new_check_in != hotel.check_in
    new_check_out = hotel.check_out
    if required and new_check_in >= new_check_out:
        new_check_out = new_check_in + timedelta(days=1)

    original_nights = (hotel.check_out - hotel.check_in).days
    nights_lost = min(max((new_check_in - hotel.check_in).days, 0), original_nights)
    return {
        "required": required,
        "new_check_in": new_check_in,
        "new_check_out": new_check_out,
        "cost_delta_inr": -nights_lost * hotel.nightly_rate_inr,
    }

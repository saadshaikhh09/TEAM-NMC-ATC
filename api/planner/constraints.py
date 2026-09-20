"""Hard filter. Owner: Person A.

Returns (survivors, rejections). NEVER return only survivors — the rejection
list is the single most valuable output in this codebase. It is what makes the
agent's judgement visible on stage.

Every rejection carries a human_reason a non-engineer can read:
    "Arrives 11:40, misses hard deadline 09:00"
"""
from core.config import policy as load_policy
from core.timezones import TIMEZONES, local_str, local_time


def _value(source, key):
    return source.get(key) if isinstance(source, dict) else getattr(source, key, None)


def _arrival_airport(constraints):
    destination = _value(constraints, "destination")
    if destination:
        return destination

    deadline = _value(constraints, "hard_arrival_by")
    deadline_local = _value(constraints, "hard_arrival_by_local")
    for airport in TIMEZONES:
        if deadline_local and local_str(deadline, airport) == deadline_local:
            return airport

    timezone_name = getattr(getattr(deadline, "tzinfo", None), "key", None)
    return next(
        (airport for airport, name in TIMEZONES.items() if name == timezone_name),
        None,
    )


def _local(value, constraints, airport):
    return local_time(value, airport, _value(constraints, "destination_timezone"))


def filter(options, constraints, policy=None):
    policy = policy or load_policy()
    rebooking = policy["rebooking"]
    survivors = []
    rejected = []
    deadline = _value(constraints, "hard_arrival_by")
    airport = _arrival_airport(constraints) if deadline else None
    fare_cap = min(
        limit
        for limit in (
            _value(constraints, "max_fare_inr"),
            rebooking["hard_fare_ceiling_inr"],
        )
        if limit is not None
    )
    stop_limit = min(
        limit
        for limit in (
            _value(constraints, "max_stops"),
            rebooking["max_stops"],
        )
        if limit is not None
    )
    cabin = _value(constraints, "cabin")
    avoided = {carrier.upper() for carrier in _value(constraints, "avoid_carriers") or []}

    for option in options:
        rejection = None
        if (
            deadline
            and rebooking["respect_hard_arrival"]
            and option.arrival > deadline
        ):
            if airport is None:
                raise ValueError("arrival airport is required for local rejection times")
            rejection = {
                "option_id": option.id,
                "rule": "hard_arrival_by",
                "human_reason": (
                    f"Arrives {_local(option.arrival, constraints, airport):%H:%M}, "
                    f"misses hard deadline {_local(deadline, constraints, airport):%H:%M}"
                ),
                "note": None,
            }
        elif option.fare_inr > fare_cap:
            rejection = {
                "option_id": option.id,
                "rule": "max_fare_inr",
                "human_reason": f"Fare {option.fare_inr:,} exceeds cap {fare_cap:,}",
                "note": None,
            }
        elif option.stops > stop_limit:
            rejection = {
                "option_id": option.id,
                "rule": "max_stops",
                "human_reason": f"{option.stops} stops, limit is {stop_limit}",
                "note": None,
            }
        elif cabin and not rebooking["allow_cabin_downgrade"] and option.cabin != cabin:
            rejection = {
                "option_id": option.id,
                "rule": "cabin",
                "human_reason": f"{cabin.title()} cabin, downgrade not permitted",
                "note": None,
            }
        elif option.carrier.upper() in avoided:
            rejection = {
                "option_id": option.id,
                "rule": "avoid_carriers",
                "human_reason": f"{option.carrier} is on your avoid-carriers list",
                "note": None,
            }

        if rejection is None:
            survivors.append(option)
        else:
            rejection["fare_inr"] = option.fare_inr
            rejected.append(rejection)

    if survivors:
        cheapest_survivor = min(option.fare_inr for option in survivors)
        for rejection in rejected:
            saving = cheapest_survivor - rejection.pop("fare_inr")
            if saving > 0:
                rejection["note"] = f"would have been {saving:,} cheaper"
    else:
        for rejection in rejected:
            rejection.pop("fare_inr")

    return survivors, rejected

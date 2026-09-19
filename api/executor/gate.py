"""The autonomous / manual switch. Owner: Person A.

This is the entire difference between the two modes:

    if auto_enabled and plan.fare <= threshold and not plan.violations:
        executor.run(plan)           # autonomous
    else:
        approvals.request(plan)      # manual

Build the manual path first. This is a 30-minute addition at hour 12.
"""


def _value(source, key, default=None):
    if source is None:
        return default
    return source.get(key, default) if isinstance(source, dict) else getattr(source, key, default)


def decide(plan, constraints, policy) -> tuple[str, str | None]:
    chosen = _value(plan, "chosen_option")
    if chosen is None:
        chosen_id = _value(plan, "chosen_option_id")
        chosen = next(
            (item for item in _value(plan, "options", []) if _value(item, "option_id") == chosen_id),
            None,
        )
    if chosen is None:
        raise ValueError("plan has no chosen option")

    fare = _value(chosen, "fare_inr")
    traveller_threshold = _value(constraints, "auto_approve_under_inr")
    if traveller_threshold is None:
        return "APPROVAL", "Traveller auto-approve threshold is not set"
    threshold = min(
        policy["rebooking"]["auto_approve_under_inr"],
        traveller_threshold,
    )
    if fare > threshold:
        return (
            "APPROVAL",
            f"Fare {fare:,} exceeds auto-approve threshold {threshold:,}",
        )

    chosen_id = _value(chosen, "id", _value(chosen, "option_id"))
    rejection = next(
        (
            item
            for item in _value(plan, "rejections", [])
            if _value(item, "option_id") == chosen_id
        ),
        None,
    )
    if rejection is not None:
        return (
            "APPROVAL",
            _value(rejection, "human_reason", "Chosen option has a policy rejection"),
        )

    change = _value(plan, "hotel_change")
    if change is None:
        changes = _value(plan, "hotel_changes", [])
        change = changes[0] if changes else None
    if change is not None and _value(change, "required", False):
        hotel = _value(plan, "hotel", _value(change, "hotel"))
        if hotel is None or not _value(hotel, "modifiable", False):
            return (
                "APPROVAL",
                "Hotel is not modifiable — cancel and rebook needs approval",
            )
        cost = _value(change, "cost_delta_inr", 0)
        hotel_threshold = policy["hotel"]["auto_modify_under_inr"]
        if cost > hotel_threshold:
            return (
                "APPROVAL",
                f"Hotel change {cost:,} exceeds auto-modify threshold {hotel_threshold:,}",
            )

    return "AUTO", None

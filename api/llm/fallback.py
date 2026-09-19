"""Pure recovery-plan copy for when every model is unavailable."""


def _value(item, name, default=None):
    return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)


def _money(value: int | None) -> str:
    return f"₹{abs(value or 0):,}"


def _cost_change(value: int | None) -> str:
    direction = "increases" if (value or 0) >= 0 else "decreases"
    return f"{direction} by {_money(value)}"


def _chosen(plan):
    chosen_id = _value(plan, "chosen_option_id")
    return next(
        (
            option
            for option in _value(plan, "options", [])
            if _value(option, "id", _value(option, "option_id")) == chosen_id
        ),
        None,
    )


def _option_name(plan) -> str:
    option = _chosen(plan)
    if option is None:
        return str(_value(plan, "chosen_option_id", "the selected option"))
    return " ".join(
        part
        for part in (_value(option, "carrier"), _value(option, "flight_number"))
        if part
    ) or str(_value(plan, "chosen_option_id"))


def _hotel_change(plan):
    change = _value(plan, "hotel_change")
    if change is None:
        changes = _value(plan, "hotel_changes", [])
        change = changes[0] if changes else None
    return change


def explanation(plan) -> str:
    rejections = _value(plan, "rejections", [])
    rejected = "; ".join(
        f"{_value(item, 'option_id')}: {_value(item, 'human_reason')}"
        + (f" ({_value(item, 'note')})" if _value(item, "note") else "")
        for item in rejections
    ) or "none"
    change = _hotel_change(plan)
    hotel = (
        f"New hotel check-in: {_value(change, 'new_check_in')}; hotel cost "
        f"{_cost_change(_value(change, 'cost_delta_inr'))}."
        if change and _value(change, "required", False)
        else "No hotel date change is required."
    )
    return (
        f"Recommended option: {_option_name(plan)} "
        f"({_value(plan, 'chosen_option_id')}). "
        f"Rejected alternatives: {rejected}. {hotel} "
        f"Total trip cost {_cost_change(_value(plan, 'total_cost_delta_inr'))}. "
        f"Approval reason: {_value(plan, 'approval_reason', 'none')}. "
        "This is a recovery recommendation; airline booking is not confirmed."
    )


def member_message(plan) -> str:
    change = _hotel_change(plan)
    hotel = (
        f"The proposed hotel check-in is {_value(change, 'new_check_in')}. "
        if change and _value(change, "required", False)
        else ""
    )
    return (
        f"Travel update: we recommend {_option_name(plan)}. {hotel}"
        f"The total trip cost {_cost_change(_value(plan, 'total_cost_delta_inr'))}. "
        f"Your approval is needed because {_value(plan, 'approval_reason', 'the plan requires review')}. "
        "No airline booking is confirmed by this message."
    )

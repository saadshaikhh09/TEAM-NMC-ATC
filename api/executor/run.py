"""Executes an approved plan. Owner: Person A.

Order matters: flight first, hotel second, because the hotel step reads the NEW
arrival time. If the flight write fails, nothing downstream runs and the trip
goes to RECOVERY_FAILED. That failure state must exist even if you never demo
it — a judge will ask.
"""
raise NotImplementedError("A10")

"""Manual end-to-end check against a RUNNING server. Not collected by pytest.

    ./.venv/bin/python tests/manual_vertical_slice.py [trip_id]

Fires one simulated cancellation, records every websocket frame, approves the
plan if the gate asked for approval, and prints the timeline. This is the
Phase A step 4 "run the vertical slice" verification, minus the browser.
"""

import asyncio
import json
import sys
import time

import httpx
import websockets


API = "http://localhost:8000"
WS = "ws://localhost:8000/ws"
PRIYA = "aaaaaaaa-1111-1111-1111-111111111111"


async def main(trip_id: str) -> None:
    frames: list[dict] = []

    async with websockets.connect(WS) as socket:

        async def drain() -> None:
            async for raw in socket:
                frames.append(json.loads(raw))

        reader = asyncio.create_task(drain())
        client = httpx.Client(base_url=API, timeout=60)

        trip = client.get(f"/trips/{trip_id}").json()
        flight = next(f for f in trip["flights"] if f["leg"] == "outbound")
        print(f"trip {trip['traveller_name']}  status={trip['status']}  {trip['origin']}->{trip['destination']}")

        started = time.monotonic()
        disruption = client.post(f"/simulate/cancellation?flight_id={flight['id']}").json()
        print(f"POST /simulate/cancellation -> {disruption['kind']} in {time.monotonic() - started:.2f}s")

        await asyncio.sleep(1)
        plan = client.get(f"/disruptions/{disruption['id']}/plan").json()
        print(f"plan {plan['state']}  chosen={plan['chosen_option_id']}  "
              f"delta={plan['total_cost_delta_inr']}  requires_approval={plan['requires_approval']}")
        print(f"  reason: {plan['approval_reason']}")
        for rejection in plan["rejections"]:
            print(f"  rejected {rejection['option_id']}: {rejection['human_reason']}"
                  + (f" ({rejection['note']})" if rejection["note"] else ""))

        if plan["requires_approval"]:
            started = time.monotonic()
            plan = client.post(f"/approvals/{plan['id']}/approve").json()
            print(f"POST approve -> {plan['state']} in {time.monotonic() - started:.2f}s")

        await asyncio.sleep(1)
        reader.cancel()

        trip = client.get(f"/trips/{trip_id}").json()
        print(f"\ntrip status: {trip['status']}")
        print("timeline:")
        for action in client.get(f"/trips/{trip_id}/timeline").json():
            print(f"  {action['stage']:<18} {action['headline']}")

    print("\nwebsocket frames:")
    for frame in frames:
        print(f"  {frame['type']:<24} {json.dumps(frame['payload'])}")
    print(f"\ndistinct event types: {sorted({frame['type'] for frame in frames})}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else PRIYA))

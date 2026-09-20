import importlib
import json
from urllib.parse import parse_qs, urlparse


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return json.dumps(self.payload).encode()


def test_geocode_hotel_sends_one_clean_query_and_returns_coordinates(monkeypatch):
    geocoding = importlib.import_module("providers.geocoding")
    monkeypatch.setattr(geocoding, "_last_request_at", 0.0)
    captured = {}

    def open_request(request, timeout):
        captured["query"] = parse_qs(urlparse(request.full_url).query)["q"]
        captured["timeout"] = timeout
        return Response([{"lat": "51.4994", "lon": "-0.1918"}])

    monkeypatch.setattr(geocoding.request, "urlopen", open_request)

    assert geocoding.geocode_hotel(
        "Kensington Central", "London", "15 Example Road"
    ) == (51.4994, -0.1918)
    assert captured == {
        "query": ["Kensington Central, 15 Example Road, London"],
        "timeout": 3,
    }


def test_geocode_hotel_returns_none_for_malformed_provider_data(monkeypatch):
    geocoding = importlib.import_module("providers.geocoding")
    monkeypatch.setattr(geocoding, "_last_request_at", 0.0)
    monkeypatch.setattr(
        geocoding.request, "urlopen", lambda *_args, **_kwargs: Response([{"lat": "nan", "lon": "200"}])
    )

    assert geocoding.geocode_hotel("Hotel", "London", None) is None


def test_geocode_hotel_waits_between_public_requests(monkeypatch):
    geocoding = importlib.import_module("providers.geocoding")
    monkeypatch.setattr(geocoding, "_last_request_at", 10.0)
    ticks = iter([10.25, 11.0])
    sleeps = []
    monkeypatch.setattr(geocoding.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(geocoding.time, "sleep", sleeps.append)
    monkeypatch.setattr(
        geocoding.request,
        "urlopen",
        lambda *_args, **_kwargs: Response([{"lat": "51.5", "lon": "-0.1"}]),
    )

    assert geocoding.geocode_hotel("Hotel", "London", None) == (51.5, -0.1)
    assert sleeps == [0.75]

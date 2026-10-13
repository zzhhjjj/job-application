import threading
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest

from job_application.api import RadarServer
from job_application.dashboard import DASHBOARD_SOURCES
from job_application.db.session import create_schema
from job_application.domain.models import DiscoveredJob, SourceKind
from job_application.tracking import Tracker


@pytest.fixture
def api(tmp_path: Path) -> Iterator[tuple[httpx.Client, Tracker]]:
    tracker = Tracker(f"sqlite:///{tmp_path / 'api.db'}", DASHBOARD_SOURCES[:1])
    create_schema(tracker.engine)
    tracker.bootstrap(tmp_path / "missing.ts")
    tracker.apply_result(
        DASHBOARD_SOURCES[0],
        [
            DiscoveredJob(
                source=SourceKind.ASHBY,
                source_identifier="openai",
                external_id="api-test-job",
                company_name="OpenAI",
                title="Training Performance Engineer",
                locations=("San Francisco",),
                job_url="https://example.test/jobs/api-test-job",
                description_text="Build distributed training infrastructure with PyTorch.",
            )
        ],
    )
    server = RadarServer(
        tracker,
        tmp_path / "snapshot.ts",
        port=0,
        company_tiers_path=tmp_path / "company-tiers.json",
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{server.server_port}", trust_env=False
        ) as client:
            yield client, tracker
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        tracker.engine.dispose()


def test_api_round_trip_and_conflicting_edits(api: tuple[httpx.Client, Tracker]) -> None:
    client, tracker = api
    response = client.get("/api/radar")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    data = response.json()
    job = data["jobs"][0]
    route = f"/api/radar/jobs/{job['id']}"
    headers = {"Origin": "http://localhost:3000"}
    response = client.post(
        route,
        json={"revision": 0, "favorite": True, "stage": "interested", "notes": "Contact recruiter"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["revision"] == 1
    assert (
        client.post(route, json={"revision": 0, "notes": "stale"}, headers=headers).status_code
        == 409
    )
    assert client.get("/api/radar").json()["jobs"][0]["personal"]["notes"] == "Contact recruiter"
    assert client.get(route + "/history").json()[0]["kind"] == "new"
    assert (
        client.post(
            "/api/radar/reviewed", json={"eventId": data["latestEventId"]}, headers=headers
        ).status_code
        == 200
    )
    assert tracker.dashboard()["jobs"][0]["unread"] == []


def test_api_rejects_cross_origin_invalid_fields_and_unknown_jobs(
    api: tuple[httpx.Client, Tracker],
) -> None:
    client, _ = api
    job_id = client.get("/api/radar").json()["jobs"][0]["id"]
    route = f"/api/radar/jobs/{job_id}"
    body = {"revision": 0, "favorite": True}
    assert client.post(route, json=body).status_code == 403
    assert (
        client.post(route, json=body, headers={"Origin": "https://evil.example"}).status_code == 403
    )
    assert client.get("/api/radar", headers={"Host": "evil.example"}).status_code == 403
    headers = {"Origin": "http://localhost:3000"}
    for invalid in (
        {"revision": 0, "stage": "sent"},
        {"revision": 0, "notes": "x" * 10001},
        {"revision": 0, "favorite": "true"},
        {"revision": 0, "availability": "closed"},
    ):
        assert client.post(route, json=invalid, headers=headers).status_code == 400
    assert client.post("/api/radar/jobs/unknown", json=body, headers=headers).status_code == 404
    assert client.get("/api/radar/jobs/unknown/history").status_code == 404


def test_api_refresh_is_background_and_updates_same_database(
    api: tuple[httpx.Client, Tracker], monkeypatch: pytest.MonkeyPatch
) -> None:
    import time

    client, tracker = api

    class Adapter:
        async def list_jobs(self, config):  # type: ignore[no-untyped-def]
            return []

    monkeypatch.setattr("job_application.tracking.create_source", lambda _: Adapter())
    response = client.post(
        "/api/radar/refresh", json={}, headers={"Origin": "http://localhost:3000"}
    )
    assert response.status_code == 202
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        data = client.get("/api/radar").json()
        if not data["refreshing"]:
            break
        time.sleep(0.02)
    assert data["refreshing"] is False
    assert tracker.dashboard()["jobs"][0]["availability"] == "not_seen"


def test_local_tiers_are_runtime_only_and_do_not_change_jobs(
    api: tuple[httpx.Client, Tracker],
    tmp_path: Path,
) -> None:
    import json

    client, tracker = api
    before = client.get("/api/radar").json()
    assert before["companyTiers"] == {}
    # Choose a company dynamically; tests do not encode anyone's preferences.
    company = before["jobs"][0]["company"]
    path = tmp_path / "company-tiers.json"
    path.write_text(json.dumps({company: 2}))
    after = client.get("/api/radar").json()
    assert after["companyTiers"] == {company: 2}
    assert after["jobs"] == before["jobs"]
    assert "companyTiers" not in tracker.dashboard()
    path.unlink()
    assert client.get("/api/radar").json()["companyTiers"] == {}

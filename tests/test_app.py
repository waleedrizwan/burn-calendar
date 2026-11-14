import pytest
from fastapi.testclient import TestClient

from burn.app import app
from burn.config import HOTSPOTS

client = TestClient(app)
needs_data = pytest.mark.skipif(not HOTSPOTS.exists(), reason="processed data not present")


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_regions():
    ids = [r["id"] for r in client.get("/api/regions").json()["regions"]]
    assert ids == ["canada", "zambia"]


def test_unknown_region():
    assert client.get("/api/calendar?region=atlantis").status_code == 404


@needs_data
@pytest.mark.parametrize("region", ["canada", "zambia"])
def test_calendar_shape(region):
    d = client.get(f"/api/calendar?region={region}").json()
    assert d["harmonized"] is False and d["period"]["start"] == "2000-11"
    cells = d["cells"]
    assert set(cells[0]) == {"year", "month", "value", "partial", "provisional"}
    # every month present exactly once, in order
    keys = [(c["year"], c["month"]) for c in cells]
    assert keys == sorted(set(keys))
    assert len(keys) == (keys[-1][0] - 2000) * 12 + keys[-1][1] - 10
    assert sum(c["value"] for c in cells) > 1_000_000

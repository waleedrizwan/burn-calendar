import numpy as np
import pytest
from fastapi.testclient import TestClient

from burn import analytics
from burn.app import app
from burn.config import HARMONIZED, HOTSPOTS

client = TestClient(app)
needs_data = pytest.mark.skipif(not (HOTSPOTS.exists() and HARMONIZED.exists()), reason="processed data not present")


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_regions():
    ids = [r["id"] for r in client.get("/api/regions").json()["regions"]]
    assert ids == ["canada", "zambia"]


def test_unknown_region():
    assert client.get("/api/calendar?region=atlantis").status_code == 404


@pytest.mark.parametrize("query", [
    "bbox=1,2,3", "bbox=30,-10,20,-5", "bbox=-100,50,-90,60", "lat=-13&lon=28", "lat=-13&lon=28&radius_km=0",
    "lat=-13&lon=28&radius_km=99999", "lat=50&lon=28&radius_km=10", "start=2020", "start=2021-01&end=2020-01",
    "bbox=27,-15,29,-13&lat=-13&lon=28&radius_km=5"])
def test_invalid_input_is_rejected(query):
    r = client.get(f"/api/calendar?region=zambia&{query}")
    assert r.status_code == 422 and r.json()["detail"]


def test_categories():
    base = np.arange(1, 26, dtype=float) * 10          # 10 .. 250, median 130
    assert analytics.categorize(300, base)["category"] == "record_high"
    assert analytics.categorize(245, base)["category"] == "well_above"
    assert analytics.categorize(205, base)["category"] == "above"
    assert analytics.categorize(130, base) == {"percentile": 50.0, "ratio_to_median": 1.0, "category": "near_normal"}
    assert analytics.categorize(55, base)["category"] == "below"
    assert analytics.categorize(5, base)["category"] == "well_below"
    quiet = np.array([0, 0, 0, 1, 2, 0, 0, 3, 0, 0], dtype=float)
    assert analytics.categorize(2, quiet) == {"percentile": None, "ratio_to_median": None, "category": "low_activity"}
    assert analytics.categorize(40, quiet)["category"] == "record_high"


def test_trend():
    years = np.arange(2003, 2026, dtype=float)
    up = analytics.mann_kendall_theil_sen(years, 100 + 10 * (years - 2003))
    assert up["direction"] == "up" and up["slope_per_year"] == 10
    flat = analytics.mann_kendall_theil_sen(years, np.tile([100.0, 120.0], 12)[:23])
    assert flat["direction"] == "none"


@needs_data
@pytest.mark.parametrize("region", ["canada", "zambia"])
@pytest.mark.parametrize("series", ["harmonized", "modis_raw"])
def test_calendar_shape(region, series):
    d = client.get(f"/api/calendar?region={region}&series={series}").json()
    assert d["harmonized"] is (series == "harmonized") and d["period"]["start"] == "2000-11"
    cells = d["cells"]
    assert {"year", "month", "value", "partial", "provisional"} <= set(cells[0])
    keys = [(c["year"], c["month"]) for c in cells]      # every month once, in order
    assert keys == sorted(set(keys))
    assert len(keys) == (keys[-1][0] - 2000) * 12 + keys[-1][1] - 10
    assert sum(c["value"] for c in cells) > 500_000


@needs_data
def test_area_queries_are_consistent():
    whole = client.get("/api/calendar?region=zambia").json()
    box = client.get("/api/calendar?region=zambia&bbox=27,-15,29,-13").json()
    circle = client.get("/api/calendar?region=zambia&lat=-14&lon=28&radius_km=100").json()
    total = lambda d: sum(y["total"] for y in d["years"])  # noqa: E731
    assert box["area"]["cells"] == 400
    assert 0 < total(circle) < total(box) < total(whole)
    # a box covering the whole region gives the region total
    everything = client.get("/api/calendar?region=zambia&bbox=20,-20,35,-7").json()
    assert total(everything) == pytest.approx(total(whole), rel=1e-6)
    tiny = client.get("/api/calendar?region=zambia&bbox=27,-15,27.01,-14.99").json()
    assert tiny["area"]["cells"] == 1 and "smaller than one" in tiny["warnings"][0]
    ranged = client.get("/api/calendar?region=zambia&start=2020-01&end=2021-12").json()
    assert len(ranged["cells"]) == 24 and ranged["baseline"] == whole["baseline"]


@needs_data
def test_record_month_and_current_month():
    d = client.get("/api/calendar?region=canada").json()
    june23 = next(c for c in d["cells"] if (c["year"], c["month"]) == (2023, 6))
    assert june23["category"] == "record_high" and june23["sources"] == ["SNPP"]
    early = next(c for c in d["cells"] if (c["year"], c["month"]) == (2001, 2))
    assert early["lower_confidence"] and early["sources"] == ["MODIS_T"]
    cur = d["current"]
    assert (cur["year"], cur["month"]) == (2026, 11) and cur["through_day"] <= 30
    assert d["cells"][-1]["partial"] and d["cells"][-1]["category"] == "partial"


@needs_data
def test_exports():
    r = client.get("/api/hotspots.csv?region=zambia&bbox=27,-15,29,-13&start=2025-08-01&end=2025-08-02")
    lines = [ln for ln in r.text.splitlines() if not ln.startswith("#")]
    assert r.status_code == 200 and lines[0].startswith("latitude,longitude,acq_datetime_utc,sensor")
    assert len(lines) > 100 and all(ln.split(",")[2].startswith("2025-08-0") for ln in lines[1:])
    assert client.get("/api/hotspots.csv?region=zambia&start=2025-08-01&end=2025-08-31").status_code == 413
    assert client.get("/api/hotspots.csv?region=zambia&start=2025-08&end=2025-09").status_code == 422
    r = client.get("/api/calendar.csv?region=canada&start=2023-05&end=2023-08")
    rows = [ln for ln in r.text.splitlines() if not ln.startswith("#")]
    assert len(rows) == 5 and rows[0].startswith("year,month,burning_activity_cell_days")

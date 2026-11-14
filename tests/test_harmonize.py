import json

import duckdb
import pytest

from burn.config import CELLDAY, HARMONIZED, HOTSPOTS, PARAMS_FILE

pytestmark = pytest.mark.skipif(not HARMONIZED.exists(), reason="processed data not present")


def q(sql):
    return duckdb.sql(sql).fetchall()


def test_gridded_counts_equal_filtered_points():
    """Sum of gridded detections = type-0 standard-quality points (2025 and earlier have no NRT rows)."""
    pts = q(f"select region, count(*) from read_parquet('{HOTSPOTS}/*/*/*/data.parquet', hive_partitioning=true) "
            "where type = 0 and year <= 2025 group by 1 order by 1")
    grd = q(f"select region, sum(n) from read_parquet('{CELLDAY}/*/*/data.parquet', hive_partitioning=true) "
            "where year <= 2025 group by 1 order by 1")
    assert pts == grd


def test_one_source_per_region_day_and_values_are_factors():
    h = f"read_parquet('{HARMONIZED}/*/*/data.parquet', hive_partitioning=true)"
    assert q(f"select count(*) from (select region, date from {h} group by all having count(distinct source) > 1)")[0][0] == 0
    assert q(f"select count(*) from (select region, date, ix, iy from {h} group by all having count(*) > 1)")[0][0] == 0
    factors = json.loads(PARAMS_FILE.read_text())["factors"]
    for region, source, month, vmin, vmax in q(
            f"select region, source, month(date), min(value), max(value) from {h} group by all"):
        k = factors[region][source][str(month)]
        assert vmin == pytest.approx(k, rel=1e-3) and vmax == pytest.approx(k, rel=1e-3)
    assert set(r[0] for r in q(f"select distinct value from {h} where source = 'SNPP'")) == {1.0}


def test_record_starts_in_2000_and_sources_follow_the_order():
    h = f"read_parquet('{HARMONIZED}/*/*/data.parquet', hive_partitioning=true)"
    rows = dict(((r, s), (a, b)) for r, s, a, b in q(
        f"select region, source, min(date)::varchar, max(date)::varchar from {h} group by all"))
    for region in ("canada", "zambia"):
        assert rows[(region, "MODIS_T")][0].startswith("2000-11")
        assert rows[(region, "MODIS_TA")][1] < "2012-01-20"
        assert rows[(region, "SNPP")][0] == "2012-01-20"
    # MODIS is never the source once S-NPP has started
    assert q(f"select count(*) from {h} where source like 'MODIS%' and date >= date '2012-01-20'")[0][0] == 0

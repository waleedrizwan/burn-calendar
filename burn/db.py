"""DuckDB access to the processed hotspot Parquet files."""
import threading

import duckdb

from burn.config import HOTSPOTS

_local = threading.local()


def con() -> duckdb.DuckDBPyConnection:
    if not hasattr(_local, "con"):
        _local.con = duckdb.connect()
        _local.con.execute(
            f"create view hotspots as select * from read_parquet('{HOTSPOTS}/*/*/*/data.parquet', "
            "hive_partitioning=true)")
    return _local.con

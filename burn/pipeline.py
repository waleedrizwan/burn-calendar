"""Rebuild everything from the raw downloads to the harmonized grid, in order.

Run: uv run python -m burn.pipeline            (add --no-fetch to skip the downloads)
"""
import sys

from burn import fetch_api, fetch_country, grid, harmonize, ingest


def main():
    if "--no-fetch" not in sys.argv:
        try:
            fetch_country.main()
        except SystemExit as e:
            if e.code:
                raise
        fetch_api.main()
    ingest.main()
    grid.main()
    harmonize.main()


if __name__ == "__main__":
    main()

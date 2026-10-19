#!/usr/bin/env python3
"""Download EIA-930 hourly ERCOT wind and solar actual generation for 2025.
Source: U.S. EIA API v2 /electricity/rto/fuel-type-data/.
No EIA key is embedded; DEMO_KEY is EIA's documented public demonstration key.
"""
from __future__ import annotations

import csv
import argparse
import os
from pathlib import Path
import requests

API_URL = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
YEAR = int(os.environ.get("EIA_YEAR", "2025"))
def fetch_fuel(fueltype: str) -> list[dict[str, str]]:
    params: list[tuple[str, str]] = [
        ("api_key", "DEMO_KEY"),
        ("frequency", "hourly"),
        ("data[0]", "value"),
        ("facets[respondent][]", "ERCO"),
        ("facets[fueltype][]", fueltype),
        ("start", f"{YEAR}-01-01T00"),
        ("end", f"{YEAR}-12-31T23"),
        ("sort[0][column]", "period"),
        ("sort[0][direction]", "asc"),
        ("length", "5000"),
    ]
    offset = 0
    data: list[dict[str, str]] = []
    while True:
        page_params = params + [("offset", str(offset))]
        response = requests.get(API_URL, params=page_params, timeout=60)
        response.raise_for_status()
        payload = response.json()["response"]
        page = payload.get("data", [])
        data.extend(page)
        total = int(payload["total"])
        if not page or len(data) >= total:
            break
        offset += len(page)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Download EIA-930 ERCOT wind and solar actual generation.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/eia"), help="Directory for generated CSV files")
    args = parser.parse_args()
    outdir = args.output_dir
    raw_file = outdir / f"EIA930_ERCO_Wind_Solar_{YEAR}_tidy.csv"
    wide_file = outdir / f"EIA930_ERCO_Wind_Solar_{YEAR}_hourly.csv"
    outdir.mkdir(parents=True, exist_ok=True)
    observations = fetch_fuel("WND") + fetch_fuel("SUN")
    observations.sort(key=lambda r: (r["period"], r["fueltype"]))

    with raw_file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "period_utc", "respondent", "respondent_name", "fueltype",
                "fueltype_name", "generation_mwh", "unit", "source",
            ],
        )
        writer.writeheader()
        for row in observations:
            writer.writerow({
                "period_utc": row["period"],
                "respondent": row["respondent"],
                "respondent_name": row["respondent-name"],
                "fueltype": row["fueltype"],
                "fueltype_name": row["type-name"],
                "generation_mwh": row["value"],
                "unit": row["value-units"],
                "source": "U.S. EIA Form EIA-930, API v2 fuel-type-data",
            })

    by_time: dict[str, dict[str, str]] = {}
    for row in observations:
        bucket = by_time.setdefault(row["period"], {})
        bucket[row["fueltype"]] = row["value"]

    with wide_file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "period_utc", "wind_mwh", "solar_mwh", "respondent", "unit",
                "source", "notes",
            ],
        )
        writer.writeheader()
        for period, values in sorted(by_time.items()):
            writer.writerow({
                "period_utc": period,
                "wind_mwh": values.get("WND", ""),
                "solar_mwh": values.get("SUN", ""),
                "respondent": "ERCO",
                "unit": "MWh per reported hour (numerically equal to hourly-average MW)",
                "source": "U.S. EIA Form EIA-930, API v2 fuel-type-data",
                "notes": "Actual net generation by energy source; not forecast; timestamps are UTC.",
            })

    print(f"Downloaded {len(observations)} fuel-specific hourly rows.")
    print(f"Wrote {raw_file}")
    print(f"Wrote {wide_file}")
    print(f"Wide rows (excluding header): {len(by_time)}")


if __name__ == "__main__":
    main()

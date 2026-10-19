#!/usr/bin/env python3
"""Create an 8,760-row UTC calendar from the downloaded EIA-930 ERCOT 2025 actuals.
Missing EIA observations remain blank; no data are interpolated or imputed.
"""
from __future__ import annotations

import csv
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description="Densify an EIA hourly CSV to a complete 8,760-hour UTC calendar.")
    parser.add_argument("--input", required=True, type=Path, help="Input hourly CSV from the EIA downloader")
    parser.add_argument("--output", required=True, type=Path, help="Output CSV path")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        source_rows = {row["period_utc"]: row for row in reader}

    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    fields = [
        "period_utc", "wind_mwh", "solar_mwh", "respondent", "unit", "source",
        "data_status", "notes",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        for hour in range(8760):
            timestamp = (start + timedelta(hours=hour)).strftime("%Y-%m-%dT%H")
            row = source_rows.get(timestamp)
            if row is None:
                writer.writerow({
                    "period_utc": timestamp,
                    "wind_mwh": "",
                    "solar_mwh": "",
                    "respondent": "ERCO",
                    "unit": "MWh per reported hour (numerically equal to hourly-average MW)",
                    "source": "U.S. EIA Form EIA-930, API v2 fuel-type-data",
                    "data_status": "missing_in_official_API_response",
                    "notes": "No imputation applied; preserve or handle missing data in the optimization model.",
                })
            else:
                writer.writerow({
                    "period_utc": timestamp,
                    "wind_mwh": row["wind_mwh"],
                    "solar_mwh": row["solar_mwh"],
                    "respondent": "ERCO",
                    "unit": row["unit"],
                    "source": row["source"],
                    "data_status": "reported",
                    "notes": "Actual net generation by fuel type; not forecast; timestamp is UTC.",
                })
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

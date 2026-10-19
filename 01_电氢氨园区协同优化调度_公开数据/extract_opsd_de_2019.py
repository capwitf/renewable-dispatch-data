#!/usr/bin/env python3
"""Extract a 2019 8,760-hour German wind/solar actuals CSV from OPSD's public file.
Source package: https://data.open-power-system-data.org/time_series/2020-10-06/
The source is a research aggregation; the primary values are from ENTSO-E Transparency.
"""
from __future__ import annotations

import csv
import argparse
import io
from pathlib import Path
from urllib.request import urlopen

SOURCE_URL = "https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv"
FIELDS = [
    "utc_timestamp",
    "DE_solar_generation_actual",
    "DE_wind_onshore_generation_actual",
    "DE_wind_offshore_generation_actual",
    "DE_load_actual_entsoe_transparency",
    "DE_LU_price_day_ahead",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Germany's 2019 wind/solar actuals from the OPSD time-series file.")
    parser.add_argument("--output", type=Path, default=Path("data/OPSD_DE_2019_Wind_Solar_Actual_Hourly.csv"), help="Output CSV path")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(SOURCE_URL, timeout=180) as response:
        text = io.TextIOWrapper(response, encoding="utf-8", newline="")
        reader = csv.DictReader(text)
        missing = [field for field in FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise RuntimeError(f"Missing expected source fields: {missing}")
        with args.output.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=FIELDS + ["source", "notes"])
            writer.writeheader()
            count = 0
            for row in reader:
                if row["utc_timestamp"].startswith("2019-"):
                    writer.writerow({
                        **{field: row[field] for field in FIELDS},
                        "source": "Open Power System Data Time series v2020-10-06; primary renewable values from ENTSO-E Transparency",
                        "notes": "Actual generation in MW; no renewable-generation forecast fields in this extracted source package.",
                    })
                    count += 1
    if count != 8760:
        raise RuntimeError(f"Expected 8760 records for 2019; received {count}.")
    print(f"Wrote {count} rows to {args.output}")


if __name__ == "__main__":
    main()

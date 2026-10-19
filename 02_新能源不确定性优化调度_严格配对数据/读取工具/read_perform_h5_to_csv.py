#!/usr/bin/env python3
"""Export NREL ARPA-E PERFORM HDF5 files to tidy CSV.

PERFORM actual files expose: actuals, time_index, meta.
PERFORM forecast files expose: forecasts, issue_time, forecast_time, meta.
All PERFORM times are UTC according to the official documentation.

Examples:
  python read_perform_h5_to_csv.py actual \
    --input BA_wind_actuals_2018.h5 --output wind_actual_5min.csv

  python read_perform_h5_to_csv.py forecast \
    --input BA_wind_day-ahead_fcst_2018.h5 --output wind_da.csv --percentile 50

  python read_perform_h5_to_csv.py forecast \
    --input BA_wind_day-ahead_fcst_2018.h5 --output wind_da_all_percentiles.csv --all-percentiles

The script preserves source values and time fields; it performs no interpolation,
resampling, or imputation. Review the official metadata before interpreting units.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import h5py
import numpy as np


def normalize_time(value: object) -> str:
    """Return a readable UTC timestamp representation without altering its value."""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.bytes_):
        return value.tobytes().decode("utf-8")
    if isinstance(value, np.datetime64):
        return np.datetime_as_string(value, timezone="UTC")
    return str(value)


def scalar_or_jsonish(value: object) -> str:
    """Make HDF5 metadata safe for a CSV cell without claiming a schema."""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.bytes_):
        return value.tobytes().decode("utf-8")
    if isinstance(value, np.ndarray):
        return repr(value.tolist())
    return str(value)


def export_actuals(input_path: Path, output_path: Path) -> None:
    with h5py.File(input_path, "r") as h5:
        required = {"actuals", "time_index"}
        missing = required.difference(h5.keys())
        if missing:
            raise KeyError(f"Missing PERFORM actual datasets: {sorted(missing)}")
        values = h5["actuals"]
        time_index = h5["time_index"][:]
        if values.shape[0] != len(time_index):
            raise ValueError("actuals and time_index have incompatible first dimensions")
        site_count = 1 if values.ndim == 1 else values.shape[1]
        with output_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["time_utc", "series_index", "actual_value", "source_file", "source_dataset"],
            )
            writer.writeheader()
            for row_index, timestamp in enumerate(time_index):
                row = values[row_index]
                if values.ndim == 1:
                    row = [row]
                for series_index in range(site_count):
                    writer.writerow(
                        {
                            "time_utc": normalize_time(timestamp),
                            "series_index": series_index,
                            "actual_value": scalar_or_jsonish(row[series_index]),
                            "source_file": input_path.name,
                            "source_dataset": "actuals",
                        }
                    )


def percentile_labels(column_count: int) -> list[str]:
    # Official PERFORM forecast documentation specifies 99 percentiles.
    if column_count == 99:
        return [str(i) for i in range(1, 100)]
    return [str(i) for i in range(column_count)]


def export_forecasts(input_path: Path, output_path: Path, percentile: int | None, all_percentiles: bool) -> None:
    with h5py.File(input_path, "r") as h5:
        required = {"forecasts", "issue_time", "forecast_time"}
        missing = required.difference(h5.keys())
        if missing:
            raise KeyError(f"Missing PERFORM forecast datasets: {sorted(missing)}")
        forecasts = h5["forecasts"]
        issue_time = h5["issue_time"][:]
        forecast_time = h5["forecast_time"][:]
        if not (forecasts.shape[0] == len(issue_time) == len(forecast_time)):
            raise ValueError("forecasts, issue_time and forecast_time have incompatible first dimensions")
        if forecasts.ndim != 2:
            raise ValueError(f"Expected two-dimensional forecasts, received shape {forecasts.shape}")
        labels = percentile_labels(forecasts.shape[1])
        if all_percentiles:
            selected = range(forecasts.shape[1])
        else:
            requested = 50 if percentile is None else percentile
            if requested not in [int(label) for label in labels if label.isdigit()]:
                raise ValueError(f"Requested percentile {requested} unavailable; use --all-percentiles to inspect all columns")
            selected = [labels.index(str(requested))]
        with output_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["issue_time_utc", "forecast_time_utc", "percentile", "forecast_value", "source_file", "source_dataset"],
            )
            writer.writeheader()
            for row_index in range(forecasts.shape[0]):
                for col_index in selected:
                    writer.writerow(
                        {
                            "issue_time_utc": normalize_time(issue_time[row_index]),
                            "forecast_time_utc": normalize_time(forecast_time[row_index]),
                            "percentile": labels[col_index],
                            "forecast_value": scalar_or_jsonish(forecasts[row_index, col_index]),
                            "source_file": input_path.name,
                            "source_dataset": "forecasts",
                        }
                    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export NREL PERFORM actuals or forecasts HDF5 to tidy CSV.")
    subparsers = parser.add_subparsers(dest="kind", required=True)
    for kind in ("actual", "forecast"):
        command = subparsers.add_parser(kind)
        command.add_argument("--input", required=True, type=Path, help="PERFORM .h5 input file")
        command.add_argument("--output", required=True, type=Path, help="CSV output file")
        if kind == "forecast":
            command.add_argument("--percentile", type=int, default=50, help="Forecast percentile to export, default: 50")
            command.add_argument("--all-percentiles", action="store_true", help="Export all percentile columns")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.kind == "actual":
        export_actuals(args.input, args.output)
    else:
        export_forecasts(args.input, args.output, args.percentile, args.all_percentiles)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

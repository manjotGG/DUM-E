"""Read inert UTF-8 numeric logs. Uploads are never executed or persisted."""
import csv
import io
import re

import numpy as np
import pandas as pd

from ml.engines.metadata import SENSOR_METADATA
from ml.engines.preprocess import COLUMNS, WINDOW

MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 30000
MAX_ENGINES = 200


def parse_log(content):
    if len(content) > MAX_BYTES:
        raise ValueError("Log is too large. Maximum file size is 10 MB.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Upload a UTF-8 CSV, TXT, TSV, or LOG file containing numeric C-MAPSS rows.") from None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("The log is empty. Upload at least 15 consecutive cycles per engine.")
    if len(lines) > MAX_ROWS + 1:
        raise ValueError(f"Upload at most {MAX_ROWS:,} data rows.")
    if "\x00" in text:
        raise ValueError("Binary files are not supported. Upload a numeric text log.")
    separator = "," if "," in lines[0] else r"\s+"
    tokens = next(csv.reader([lines[0]])) if separator == "," else re.split(separator, lines[0])
    try:
        [float(token) for token in tokens]
        header = False
    except ValueError:
        header = True
    aliases = {c.lower(): c for c in COLUMNS}
    aliases.update({sensor["symbol"].lower(): sensor["key"] for sensor in SENSOR_METADATA})
    try:
        if header:
            names = [aliases.get(token.strip().lower(), token.strip()) for token in tokens]
            if len(names) != len(COLUMNS) or set(names) != set(COLUMNS):
                raise ValueError("Header must include engine_id, cycle, setting_1–3, and all 21 sensors (sensor_1–21 or their C-MAPSS symbols). Download the sample log for the exact columns.")
            frame = pd.read_csv(io.StringIO("\n".join(lines[1:])), sep=separator, header=None, engine="python")
            if frame.shape[1] != len(COLUMNS):
                raise ValueError("Every data row must contain exactly 26 values.")
            frame.columns = names
            frame = frame[COLUMNS]
        else:
            frame = pd.read_csv(io.StringIO("\n".join(lines)), sep=separator, header=None, engine="python")
            if frame.shape[1] != len(COLUMNS):
                raise ValueError("Headerless logs need 26 values per row: engine ID, cycle, 3 settings, then 21 sensors in NASA order.")
            frame.columns = COLUMNS
        frame = frame.apply(pd.to_numeric, errors="raise")
    except pd.errors.EmptyDataError:
        raise ValueError("The log has a header but no observations. Add at least 15 consecutive cycles per engine.") from None
    except pd.errors.ParserError:
        raise ValueError("Log rows have inconsistent column counts. Every row must contain 26 values.") from None
    except (TypeError, ValueError) as error:
        if "26" in str(error) or "Header" in str(error):
            raise ValueError(str(error)) from None
        raise ValueError("All log values must be numeric. Check the header, delimiters, and missing measurements.") from None
    if len(frame) > MAX_ROWS:
        raise ValueError(f"Upload at most {MAX_ROWS:,} data rows.")
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("Log contains missing or non-finite values. Every row requires all 26 measurements.")
    if (np.abs(frame.to_numpy(dtype=float)) > 1e12).any():
        raise ValueError("Log values exceed the supported numeric range. Use the original FD001 sensor units.")
    for key in ["engine_id", "cycle"]:
        values = frame[key]
        if (values < 1).any() or (values > 2147483647).any() or (values % 1 != 0).any():
            raise ValueError("Engine IDs and cycles must be positive whole numbers below 2,147,483,648.")
        frame[key] = values.astype(int)
    if frame.engine_id.nunique() > MAX_ENGINES:
        raise ValueError(f"Upload at most {MAX_ENGINES} engines per log.")
    # Validate order before sorting: never silently reinterpret an out-of-order log.
    for engine_id, group in frame.groupby("engine_id", sort=True):
        if len(group) < WINDOW:
            raise ValueError(f"Engine {engine_id} has {len(group)} cycles; at least {WINDOW} consecutive cycles are required. Supply the full observed history when available.")
        if not (group.cycle.diff().iloc[1:] == 1).all():
            raise ValueError(f"Engine {engine_id} must have consecutive cycles in increasing order, without gaps or duplicates.")
    return frame.sort_values(["engine_id", "cycle"]).reset_index(drop=True)

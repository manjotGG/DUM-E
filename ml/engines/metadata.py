"""Published C-MAPSS measurement symbols; internal model keys remain stable."""
import json
from .preprocess import ROOT

SENSOR_METADATA = json.loads((ROOT / "shared/sensors.json").read_text())

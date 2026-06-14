"""DataFrame → JSON-safe TableResponse serializer."""
from __future__ import annotations

import math
from typing import Any

import pandas as pd

from app.api.schemas import TableResponse


def _json_safe(value: Any) -> Any:
    """Convert a single value to a JSON-serializable scalar.

    Rules:
    - NaN / None → None
    - numpy int/float → Python int/float
    - pandas Timestamp / datetime → ISO string
    - Everything else → unchanged (str, int, float, bool already fine)
    """
    if value is None:
        return None
    # Check for pandas NaT
    if isinstance(value, type(pd.NaT)) or value is pd.NaT:
        return None
    # numpy scalar → python scalar
    try:
        import numpy as np
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            v = float(value)
            return None if math.isnan(v) or math.isinf(v) else v
        if isinstance(value, np.bool_):
            return bool(value)
    except ImportError:
        pass
    # pandas Timestamp
    if isinstance(value, pd.Timestamp):
        return value.isoformat() if not pd.isna(value) else None
    # plain float NaN/inf
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


def df_records(df: pd.DataFrame) -> TableResponse:
    """Serialize a DataFrame to TableResponse, preserving Korean column names.

    - Empty DataFrame → columns=[], rows=[]
    - NaN → None
    - numpy / datetime types → JSON-safe equivalents
    """
    if df is None or df.empty:
        return TableResponse(columns=list(df.columns) if df is not None else [], rows=[])

    # Preserve named index (e.g. DatetimeIndex with name="date") as a column.
    # Do NOT reset an unnamed/default RangeIndex (that would add a junk "index" column).
    if df.index.name is not None:
        df = df.reset_index()

    columns = list(df.columns)
    rows: list[dict[str, Any]] = []
    for record in df.to_dict(orient="records"):
        rows.append({k: _json_safe(v) for k, v in record.items()})

    return TableResponse(columns=columns, rows=rows)

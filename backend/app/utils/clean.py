"""
Utility: recursive clean of Infinity/NaN values for JSON serialization.
Standard pattern used across all engineering modules.
"""

import math


def clean(obj):
    """Recursively replace float infinity and NaN with None for JSON compatibility."""
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean(v) for v in obj]
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
    return obj


def numpy_safe(obj):
    """Convert numpy types to native Python types (for JSON serialization)."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: numpy_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [numpy_safe(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        if math.isinf(val) or math.isnan(val):
            return None
        return val
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def prepare_json(data):
    """Full pipeline: numpy -> native -> clean. Ready for jsonify."""
    return clean(numpy_safe(data))

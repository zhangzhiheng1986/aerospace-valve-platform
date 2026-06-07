#!/usr/bin/env python3
"""System Audit v1: pinpoint all 5 failures + 1 warning with full tracebacks"""
import requests, json, sys

BASE = "http://127.0.0.1:5000"

checks = [
    # AUTH
    ("AUTH-verify_token", "POST", "/api/auth/verify", {"token": "fake-test-token"}, 200),
    # PRESSURE_VALVE - find actual test params
    ("PRV-design_neg", "POST", "/api/pressure_valve/design", {
        "fluid_type": "water", "material": "stainless_steel",
        "inlet_pressure": -0.5, "outlet_pressure": 0.1, "flow_rate": 10
    }, None),
    # CHECK_VALVE
    ("CHKV-design_minimal", "POST", "/api/check_valve/design", {
        "nominal_diameter": 25, "fluid_type": "water",
        "pressure_rating": "PN16", "body_material": "stainless_steel"
    }, None),
    # SEAL
    ("SEAL-design", "POST", "/api/seal/design", {
        "seal_type": "metal-metal", "seat_material": "TC4",
        "fluid": "water", "pressure": 5, "temperature": 300
    }, None),
    # TEMPLATES
    ("TPL-list", "GET", "/api/templates/list", None, 200),
    # MATERIALS detail
    ("MAT-detail", "GET", "/api/materials/detail?name=TC4", None, 200),
]

for label, method, path, data, expect in checks:
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{path}", timeout=5)
        else:
            r = requests.post(f"{BASE}{path}", json=data, timeout=5)
        code = r.status_code
        body = r.text[:200]
        if expect and code != expect:
            print(f"FAIL [{label}]: HTTP {code} (expected {expect})")
        elif code >= 500:
            print(f"FAIL [{label}]: HTTP {code}\n  {body}")
        elif code == 404:
            print(f"WARN [{label}]: HTTP 404")
        else:
            print(f"OK   [{label}]: HTTP {code}")
    except Exception as e:
        print(f"ERR  [{label}]: {e}")

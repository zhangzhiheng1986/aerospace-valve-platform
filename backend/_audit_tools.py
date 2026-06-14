# tool_bridge audit — map each tool, test it, flag mock/real
import sys, json

# Direct import
import tool_bridge as tb

bridge = tb.TOOL_BRIDGE
print("=" * 72)
print("TOOL BRIDGE AUDIT — {} tools".format(len(bridge)))
print("=" * 72)

for name in sorted(bridge.keys()):
    handler = bridge[name]
    # check for mock fallback — scan handler source for 'mock' / 'Mock'
    name_lower = handler.__name__.lower() if hasattr(handler, '__name__') else ''
    has_mock_fn = name_lower.startswith('_mock')
    is_likely_mock = has_mock_fn

    status = 'MOCK_ONLY' if has_mock_fn else 'REAL (may fallback)'
    print("{:32s}  handler={:28s}  {}".format(name, handler.__name__, status))

print("\n" + "=" * 72)
print("TESTING ALL TOOLS")
print("=" * 72)

test_cases = [
    ('query_material', {'material': 'TC4'}),
    ('check_compliance', {'design': {'proof_factor': 1.5, 'burst_factor': 2.0}}),
    ('verify_leak', {'pressure_mpa': 21, 'orifice_diameter_mm': 1.0}),
    ('verify_rated', {'pressure_mpa': 21, 'design_pressure_mpa': 14}),
    ('verify_life', {'design_life': 20000}),
    ('run_fluid_calculation', {'formula_id': 'reynolds_number', 'inputs': {'rho': 1000, 'v': 10, 'L': 0.01, 'mu': 0.001}}),
    ('identify_formula', {'query': 'Reynolds number for pipe flow'}),
    ('analyze_solenoid_valve', {'working_pressure': 21}),
    ('analyze_pressure_valve', {'inlet_pressure': 10, 'outlet_pressure': 2, 'flow_rate': 0.1, 'fluid': 'nitrogen'}),
    ('design_spring', {'material_name': '50CrVA', 'wire_diameter': 3, 'mean_diameter': 20, 'n_coils': 8}),
    ('design_oring', {'shaft_diameter': 100, 'pressure': 30}),
    ('semantic_search', {'query': 'Reynolds number'}),
    ('graph_search', {'query': 'TC4'}),
    ('graph_neighbors', {'entity_id': 'formula_reynolds_number'}),
]

for tool, kwargs in test_cases:
    try:
        executor = tb.get_tool_bridge()
        result = executor(tool, kwargs)
        succ = result.get('success', False)
        note = result.get('note', '')
        is_mock = bool(note and 'Mock' in str(note))
        tag = 'MOCK' if is_mock else ('OK' if succ else 'FAIL')
        details = ''
        if note:
            d = str(note)[:80]
            details = '  note="{}"'.format(d)
        if not succ and not is_mock:
            err = result.get('error', '')
            details = '  error="{}"'.format(str(err)[:80])
        print("  {:30s} {:6s}{}".format(tool, tag, details))
    except Exception as e:
        print("  {:30s} ERROR  {}".format(tool, str(e)[:80]))

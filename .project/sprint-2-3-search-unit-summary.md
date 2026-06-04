# Sprint 2+3: Search System + Unit System — Fluid Mechanics Calculator

**Date**: 2026-06-04 07:40-08:10 CST
**Status**: Complete ✅

## Sprint 2: Search System

### Backend
- API endpoint `/api/fluid_mechanics/search-index` (from Phase 1) returns 135 formula entries with `id`, `category`, `name_zh`, `name_en`, `keywords`

### Frontend (fluid_mechanics.html)
- Search bar in toolbar (between breadcrumb and Dashboard link)
- CSS: `.search-container`, `.search-input`, `.search-dropdown`, `.search-result-item`, `.search-backdrop`
- Fuzzy matching algorithm: `fuzzyMatch(query, text)` — sequential character matching
- Searches across `name_zh`, `name_en`, `keywords` fields
- Results dropdown with 20-result cap, keyboard navigation (ArrowDown/Up/Enter/Escape)
- Backdrop-click dismiss
- Clear button on search input
- Selecting a result navigates to the category and selects the formula
- Search-index fetched on DOMContentLoaded (parallel with catalog/i18n)

## Sprint 3: Unit System

### Backend — unit_converter.py (13KB)
- 18 unit categories: length, area, volume, velocity, acceleration, mass, density, pressure, viscosity_dynamic, viscosity_kinematic, flow_rate_vol, flow_rate_mass, force, torque, power, energy, surface_tension, frequency, temperature, angle, dimensionless
- 3 unit system presets: SI (Metric), Imperial (ft/lb/slug/psi/...), US Customary (in/gpm/lb/...)
- Temperature uses offset-aware conversion (K/C/F/R)
- `PARAM_UNIT_MAP`: 126 parameter-name-to-category mappings (e.g., D→length, P→pressure, Q→flow_rate_vol)
- `convert(value, from_unit, to_unit, category)` — general converter
- `get_system_target_unit(category, system)` — get target unit for category+system

### API — `/api/fluid_mechanics/unit-systems`
Returns: `{systems, conversions, labels, param_map}` — everything frontend needs

### Frontend
- Unit system selector: SI | FT/lb | US buttons in sidebar header
- `fetchUnitData()` fetches unit definitions after page init
- `siToCurrent(value, paramName)` — converts SI result to current system for display
- `currentToSI(value, paramName)` — converts user input to SI before sending to backend
- `getUnitForParam(paramName)` — returns {unit, label, category} for current system
- `compute()` updated: inputs converted to SI before POST, results converted to current system before display
- `renderCalculator()` updated: input labels show current-system units
- `setUnitSystem(sys)` updates all UI and re-renders current formula
- `loadStoredPrefs()` restores unit preference from localStorage
- Available systems: SI → Imperial (FT/lb) → US Customary

### Validation
- Unit converter: 10m→32.8084ft, 30C→86F, 100kPa→14.5038psi ✅
- API: 200, systems=[Imperial, SI, US], 126 param mappings
- Page: 200, 46096 bytes, all components present
- JS brace balance: 195 opens = 195 closes ✅

## Files Changed
- `frontend/fluid_mechanics.html` — search bar, unit selector, JS functions
- `backend/app/blueprints/fluid_mechanics.py` — `/api/fluid_mechanics/unit-systems` endpoint
- `backend/unit_converter.py` — NEW: unit conversion engine

## Next Steps (Sprint 4+)
- Non-Newtonian fluid models (Bingham, power-law, Herschel-Bulkley)
- Multi-phase flow (gas-liquid, solid-liquid)
- Cavitation analysis
- Batch computation & export
- Chart visualization (single formula)

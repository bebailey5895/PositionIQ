# PositionIQ v1.0

PositionIQ is a sports-betting analytics application built with Python and
Streamlit. It provides odds conversion, no-vig analysis, expected-value
analysis, hedge planning, cashout valuation, and event-based parlay tools.

## Architecture

- `app.py` — application router and shared sidebar
- `positioniq_pages/` — dedicated workflow pages
- `positioniq_components/ui.py` — reusable interface components
- `positioniq_calculations.py` — calculation engine
- `tests/` — automated calculation tests

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Test

```powershell
python -m pytest -v
```

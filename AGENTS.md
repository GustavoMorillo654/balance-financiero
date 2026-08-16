# Repository Guidelines

## Project Structure & Module Organization

This repository contains the Phase 1 financial-balance engine. Keep runtime code under `src/`: domain dataclasses and DTOs belong in `src/models/`, while parsing, classification, depreciation, and validation logic belongs in `src/services/`. `src/index.py` is the CLI and orchestration entry point. Place test CSV fixtures in `data/`; `datos.csv` is the supplied base dataset. Add pytest tests in `tests/`, grouped by the behavior or service being changed.

## Build, Test, and Development Commands

Use Python 3.10+ and an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
python src/index.py --file data/dataset_cuentas_ejemplo.csv
```

`pytest tests/ -v` runs the unit and pipeline suite. To inspect the machine-readable contract, run `python src/index.py --file datos.csv --json`. Use `--output balance_salida.json` to export a result; do not commit generated output unless it is intentionally a fixture.

## Coding Style & Naming Conventions

Follow the existing Python style: four-space indentation, standard-library imports first, type hints on public functions, and concise Spanish-facing domain names where they match the JSON contract. Use `snake_case` for functions, variables, and modules; `PascalCase` for classes; and `UPPER_SNAKE_CASE` for enum members. Keep business rules in focused services and preserve the established camelCase keys in serialized JSON (for example, `totalActivo` and `depreciacionAcumulada`). No formatter or linter is currently configured; keep changes consistent with neighboring code.

## Testing Guidelines

Use pytest and name files `test_<area>.py`, test methods `test_<expected_behavior>`. Add focused tests for parsing edge cases, account classification, or depreciation changes, plus an integration assertion when the output contract changes. Preserve key invariants: assets must equal liabilities plus equity within the validator tolerance, and `Terreno` must never depreciate. Run the full suite before submitting; no coverage target is configured.

## Commit & Pull Request Guidelines

Recent history uses Conventional Commit-style subjects, such as `feat(fase-1): implementar ...` and `Update README ...`. Prefer concise imperative subjects with prefixes like `feat:`, `fix:`, `test:`, or `docs:`. Pull requests should describe the financial behavior affected, list test commands run, link the relevant issue when available, and include a representative JSON or CLI output when the public contract changes.

## Configuration & Data Safety

Do not commit virtual environments, generated JSON, or sensitive financial data. Treat changes to CSV aliases, classification rules, and depreciation logic as contract changes and document their impact.

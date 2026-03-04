# Copilot Instructions for Sudoku Flask Project

## Project Scope
- This repository is a Python Flask Sudoku game.
- Primary app code lives in `starter/`:
  - Backend: `starter/app.py`, `starter/sudoku_logic.py`
  - Frontend: `starter/templates/index.html`, `starter/static/main.js`, `starter/static/styles.css`
  - Tests: `starter/tests/`

## Tech Stack and Conventions
- Backend: Flask (simple routes, JSON APIs).
- Frontend: vanilla JavaScript, HTML, CSS (no framework).
- Keep implementation minimal and readable; avoid over-engineering.
- Preserve existing API contracts unless explicitly requested.
- Use clear variable names and small focused functions.

## Existing Feature Expectations (Do Not Regress)
- Difficulty selector (`easy`, `medium`, `hard`).
- New Game, Check Solution, Check Puzzle, and Hint actions.
- Incorrect entry highlighting and conflicting-cell highlighting.
- Hint fills one correct cell and locks that cell.
- Timer is visible and used for score tracking.
- Dark/Light theme toggle applies across the whole UI.
- Board is responsive on desktop/mobile.
- Sudoku board has alternating 3x3 square colors.
- Top 10 scores are stored in browser local storage (name, difficulty, time).

## UI/UX Guardrails
- Keep controls readable in both light and dark modes.
- Keep styles consistent with existing palette and spacing.
- Do not add heavy dependencies for UI changes.
- Prefer incremental CSS/JS updates over large rewrites.

## Backend Guardrails
- Keep routes simple and deterministic.
- Return consistent JSON response shapes.
- Validate request payloads and return useful error messages.
- Avoid introducing global mutable complexity beyond current app style.

## Testing Requirements
- Use `pytest` for tests.
- Place tests in `starter/tests/`.
- Run tests before and after meaningful refactors.
- Current test command:

```bash
python -m pytest starter/tests -q
```

## Change Strategy
- Make focused, minimal diffs.
- Fix root cause instead of adding patchy workarounds.
- Avoid unrelated refactors.
- If changing behavior, update tests and README when needed.

## Performance and Reliability
- Keep frontend interactions responsive.
- Avoid expensive loops in high-frequency UI events.
- Ensure puzzle checks and hint actions behave consistently.

## Documentation
- Update `README.md` if commands, setup, or key behavior change.
- Keep instructions concise and practical for reviewers.

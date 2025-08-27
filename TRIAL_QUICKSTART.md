
# EVelution — Trial Run

## One-liners to try
```bash
# 0) Notes panel (optional)
python main.py --mode notes --role student --user_id trial

# 1) Calibrated Story Mode (unit inputs under sliders)
python main.py --mode story_cal --user_id trial

# 2) Explain-Why (see each term in log r)
python main.py --mode explain_cal --user_id trial

# 3) Shared environment demo (stacked flux + sankey-like)
python main.py --mode sharedenv

# 4) Per-cell A/B/C dashboard
python main.py --mode percell --cell_id C1

# 5) Import demo NTA CSV and get standardized file + QC
python main.py --mode import --import_kind nta --path content/imports/demo_nta.csv

# 6) EV-TRACK-like checklist score
python main.py --mode evtrack --meta content/metadata/trial_metadata.json

# 7) Methods (Markdown) for papers
python main.py --mode methods
```

## Calibrations included (user_id=trial)
- E_O2: Linear %O2 0–21
- I_ATP: Linear mM 0–5
- I_ROS: Linear AU 0–10
- S_ESCRT: Linear AU 0–1

Outputs are saved under `outputs/` with PNG/PDF/SVG and a `repro.json` stamp.

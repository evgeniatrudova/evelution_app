
# Evelution (prototype) — with Ghost

Ghost = explicit latent unknown factor (−1..+1) for unexplained biology. It contributes to wellbeing and can be learned/overridden.

## Quick start
```bash
python main.py
```

## Outputs
- `outputs/ev_time_series.csv` aggregated field over time
- `outputs/metrics.csv` (placeholder)


## Fairy (mitochondrial-relocation survivability boost)
- `fairy` ∈ [0,1] increases survivability and energy balance.
- Effects: contributes positively to wellbeing; nudges ATP↑ (I[0]), ROS↓ (I[1]), small ESCRT support (S↑).
- Set per cell in code or (soon) via CSV.


## Computational biology/bioinformatics upgrades
- Alt count models (NegBin, ZIP), profile likelihoods, PPC calibration.
- Engines: Gillespie SSA + PDMP stubs.
- SBML export (toy), Michaelis–Menten uptake, diffusion/decay kernel.
- Lipid curvature factor, NNLS deconvolution.
- Ghost structured prior (batch + covars), AIC/BIC comparison.
- Standards: MISEV check, PEtab/COMBINE emitters, PROV JSON-LD, unit validators.
- Omics: RNA/proteomics loaders, batch normalization, tissue deconv, GO-like enrichment, lipid indices.
- QA/QC: assay LOD/dynamic range, BH-FDR, Morris sensitivity, K-fold CV.
- Repro/perf: environment.yml, Dockerfile, CI, benchmark script.

## Biopython integration (safe wrappers)
- Entrez/online fetch stubs (offline-safe).
- miRNA seeds, motif scans, SwissProt text parser, PDB loader, alignments, phylo, seq composition, ID map.


### Compare Mode (experimental vs theoretical)
Provide a CSV with columns: `timestep,cell_id,EV_type,EV_rate,protein1,protein2,...`
Then run:
```bash
python main.py --mode compare --lab path/to/your_lab.csv
```
Artifacts in `outputs/compare/`: metrics JSON per EV type, aligned time-series CSVs for overlay plots, and per-protein CSVs.


## Game Mode (tutorial, combos, quests, skills, accessibility, photo)
```bash
python main.py --mode game              # exports tutorial/quests/progress
python main.py --mode game --photo      # also exports a citable PNG figure
```
Artifacts:
- `outputs/tutorial/script.json` – 5-minute, zero-jargon walkthrough.
- `outputs/quests/quest_board.json` – active quests + demo evaluation.
- `outputs/progress.json` – skill unlocks (Hill, ExplainUI).
- `outputs/accessibility.json` – colorblind-safe palette, dyslexia font, keybinds.
- `outputs/photo/scene_timeseries.png` – photo-mode example figure.


### Theming (Eevee-inspired + colorblind-safe)
Export CSS/JSON + preview:
```bash
python main.py --theme eevee      # standard Eevee-inspired
python main.py --theme cb_eevee   # colorblind-safe variant
```
Outputs in `outputs/theme/`: `{theme}.css`, `{theme}.json`, `preview.html`.


### Math refactor highlights
- Log-additive rate composition (stable, interpretable).
- Protein noise via Beta/logit-normal; counts via ZINB.
- Compositional analysis (clr, Aitchison distance).
- Particle filter stub for data assimilation.
- Sobol' sensitivity (MC) and reflected SDE engine.
- Hybrid automaton (hysteresis) for regimes.
- Active learner ranks experiments by EIG proxy.
- HS math cards for quick learning.

### Teach (HS) cards
Minimal math cards live in `evelution/teach/hs_lessons.py`.


### Teach Mode — EV Biology
Running `python main.py --mode teach` now exports `outputs/teach/hs_bio_lessons.json`:
a set of high‑school friendly lesson cards covering ESCRT vs non‑ESCRT pathways, budding,
Rab routing, cargo sorting, uptake, and applications, each with a one‑line equation and a hands‑on activity.


### Trainer mode (editable Teach content + algorithm plugins)
Register a trainer (local, simple auth):
```bash
python main.py --register_trainer --trainer_id alice --trainer_pass s3cret
```

Edit Teach lessons:
```bash
python main.py --mode teach --trainer_id alice --dump_lessons
# edit content/trainers/alice/lessons_editable.json
python main.py --mode teach --trainer_id alice --trainer_pass s3cret --edit_lessons content/trainers/alice/lessons_editable.json
```

Install algorithm plugins (influence functions):
```bash
# plugin.py must define safe math-only functions (no os/subprocess/etc.) and be <100KB
python main.py --add_plugin path/to/plugin.py --trainer_id alice --trainer_pass s3cret
python main.py --list_plugins --trainer_id alice
```

Storage & safety:
- Per-trainer quota: 25 MB (configurable at registration).
- Per-edit file limit: 2 MB; per-plugin file limit: 100 KB.
- Bans dangerous imports (`os`, `subprocess`, `exec`, etc.).
- This is local convenience, not hardened security.


### Roles: Student or Trainer
Choose your role for personalized storage and permissions.
- Students: lightweight auth, 10 MB quota by default.
- Trainers: passworded, 25 MB quota + plugins/lesson overrides.

Register:
```bash
# Student (optional password)
python main.py --register_student --user_id bob --user_pass ""
# Trainer (already supported)
python main.py --register_trainer --trainer_id alice --trainer_pass s3cret
```

### Notes (save + export)
Create a note:
```bash
python main.py --role student --user_id bob --note_new "My first EV note" \
               --note_text "CD63 tracks endosomal origin; ESCRT ↑ buds ILVs."
```
List notes:
```bash
python main.py --role student --user_id bob --note_list
```
Export to TXT or PDF:
```bash
python main.py --role student --user_id bob --note_export <NOTE_ID> --note_format txt
python main.py --role student --user_id bob --note_export <NOTE_ID> --note_format pdf
```
Files are stored under `content/{students|trainers}/{id}/notes/` and exports in `outputs/notes/`.


### Notes Sidebar (Jupyter)
Launch the in-app notes panel with autosave, pastel color, insert-plot, export, and delete:
```bash
python main.py --mode notes --role student --user_id bob
```
Buttons:
- **New**/**Delete** note
- **Insert current plot** (pulls latest image from `outputs/`)
- **Export TXT/PDF**
Autosave triggers whenever you type or change title/color.


**Notes Preview:** The notes sidebar now shows a live Markdown preview (images supported, e.g. `![plot](outputs/...png)`) next to the editor. Use the “Live preview” checkbox to toggle it.


### Calibrated Story & Explain-Why
- Story (with unit converters under sliders):  
  `python main.py --mode story_cal --user_id <id>`
- Explain-Why (calibrated, shows per-term logs + formulas):  
  `python main.py --mode explain_cal --user_id <id>`

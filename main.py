
from __future__ import annotations
import os, argparse, json
from evelution.models.cell import CellAgent
from evelution.models.simulation import Simulation
from evelution.models.supervisor import Supervisor
from evelution.data.io import Kinetics
from evelution.metrics.metrics import export_metrics_csv
from evelution.ui.snapshot import save_state, diff_states
from evelution.ui.story import StoryStep, run_story
from evelution.analysis.explain import contribution_breakdown
from evelution.utils.permalink import to_permalink, from_permalink
from evelution.multiagent.eco import MultiAgentSimulation, EVExchangeGraph, ExchangeEdge

def make_cells():
    cells = []
    for i in range(3):
        c = CellAgent(
            cell_id=f"C{i+1}",
            cell_type="generic",
            I=[0.6,0.5,0.4,0.5,0.6],
            E=[0.5,0.5,0.5,0.5,0.5],
            ghost=0.0,
            fairy=0.3,
            S=0.6,
            P={"CD9":0.6,"CD63":0.5,"CD81":0.55,"TSG101":0.4,"ALIX":0.45},
        )
        cells.append(c)
    return cells

def make_supervisor():
    sup = Supervisor()
    sup.stress_windows = {"hypoxia":[range(10,20)], "oxidative":[range(30,40)]}
    sup.lambdas = {"hypoxia":1.2,"oxidative":0.9,"metabolic":0.85}
    return sup

def run_basic(T=60):
    os.makedirs("outputs", exist_ok=True)
    cells = make_cells()
    sup = make_supervisor()
    sim = Simulation(cells=cells, supervisor=sup)
    if os.path.exists("examples/kinetics.csv"):
        sim.kinetics = Kinetics.from_csv("examples/kinetics.csv")
    field = sim.run(T=T, dt=1.0)
    field.export_time_series_csv("outputs/ev_time_series.csv")
    export_metrics_csv("outputs/metrics.csv", [("rmse_placeholder", 0.0), ("r_placeholder", 0.0)])
    print("Run complete. See outputs/")
    return sim, field

def run_story_mode():
    os.makedirs("outputs", exist_ok=True)
    cells = make_cells()
    sup = make_supervisor()
    sim = Simulation(cells=cells, supervisor=sup)
    steps = [
        StoryStep("Umbra: Hypoxia pulse", {"Umbra":(1.2,[0,15])}, {"C1":{"E":[0.2,0.5,0.5,0.5,0.4]}}, "Low O2 raises exosomes; VEGF-like cargo", True),
        StoryStep("Electro: ROS pulse", {"Electro":(0.9,[15,30])}, {"C2":{"ghost":0.2}}, "ROS engages ceramide; rate shifts", True),
        StoryStep("Flora: TGF-β dosing", {"Flora":(1.1,[30,45])}, {"C3":{"S":0.7}}, "Routing via syntenin/ALIX", False),
    ]
    outputs = run_story(sim, steps, segment_len=15)
    snaps = []
    for i,(info, field) in enumerate(outputs):
        snap = save_state(sim)
        snaps.append(snap)
    if len(snaps)>=2:
        diff = diff_states(snaps[-2], snaps[-1])
        with open("outputs/story_diff.json","w") as f:
            json.dump(diff, f, indent=2)
    print("Story mode complete. See outputs/story_diff.json")
    return sim

def explain_one(sim):
    os.makedirs("outputs", exist_ok=True)
    c = sim.cells[0]
    scale = sim.supervisor.active_scale(0)
    info = contribution_breakdown(c, scale, sim.rT, "exosome")
    with open("outputs/explain_C1.json","w") as f:
        json.dump(info, f, indent=2)
    print("Explain-Why written to outputs/explain_C1.json")

def make_permalink(sim):
    cfg = {
        "cells":[{"id":c.cell_id,"I":c.I,"E":c.E,"S":c.S,"ghost":c.ghost,"fairy":c.fairy} for c in sim.cells],
        "lambdas": sim.supervisor.lambdas,
        "stress": {k:[[r.start,r.stop] for r in v] for k,v in sim.supervisor.stress_windows.items()},
        "seed": 42,
        "notes": "Example permalink"
    }
    s = to_permalink(cfg)
    with open("outputs/permalink.txt","w") as f:
        f.write(s)
    print("Permalink token in outputs/permalink.txt")
    return s

def run_multiagent():
    cells = make_cells()
    sup = make_supervisor()
    exchange = EVExchangeGraph(edges=[ExchangeEdge("C1","C2",0.2), ExchangeEdge("C2","C3",0.1)])
    sim = MultiAgentSimulation(cells=cells, supervisor=sup, exchange=exchange)
    sim.run(T=60, dt=1.0)
    print("Multi-agent run complete.")
    return sim

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["basic","story","explain","multi","teach","compare","game"], default="basic")
    parser.add_argument("--lab", type=str, default="")
    parser.add_argument("--tutorial", action="store_true")
    parser.add_argument("--photo", action="store_true")
    parser.add_argument("--theme", type=str, default="")
    parser.add_argument("--trainer_id", type=str, default="")
    parser.add_argument("--trainer_pass", type=str, default="")
    parser.add_argument("--register_trainer", action="store_true")
    parser.add_argument("--dump_lessons", action="store_true")
    parser.add_argument("--edit_lessons", type=str, default="")
    parser.add_argument("--add_plugin", type=str, default="")
    parser.add_argument("--list_plugins", action="store_true")
    parser.add_argument("--role", type=str, default="student", choices=["student","trainer"])
    parser.add_argument("--user_id", type=str, default="")
    parser.add_argument("--user_pass", type=str, default="")
    parser.add_argument("--register_student", action="store_true")
    parser.add_argument("--note_new", type=str, default="")
    parser.add_argument("--note_text", type=str, default="")
    parser.add_argument("--note_list", action="store_true")
    parser.add_argument("--note_export", type=str, default="")
    parser.add_argument("--note_format", type=str, default="txt")
    parser.add_argument("--var", type=str, default="E_O2")
    parser.add_argument("--cell_id", type=str, default="C1")
    parser.add_argument("--import_kind", type=str, default="nta", choices=["nta","trps","flow"])
    parser.add_argument("--path", type=str, default="")
    parser.add_argument("--meta", type=str, default="")
    parser.add_argument("--figA", type=str, default="")
    parser.add_argument("--figB", type=str, default="")
    args = parser.parse_args()
    if args.mode=="basic":
        sim, _ = run_basic()
        explain_one(sim)
        make_permalink(sim)
    elif args.mode=="story":
        sim = run_story_mode()
        explain_one(sim)
        make_permalink(sim)
    elif args.mode=="explain":
        sim, _ = run_basic()
        explain_one(sim)
    elif args.mode=="multi":
        emit_repro("multi")
        sim = run_multiagent()
        explain_one(sim)
        make_permalink(sim)



elif args.mode=="compare":
        emit_repro("compare")
    # Load lab data CSV, run sim on matching timeline, export overlays/metrics
    from evelution.data.labdata import LabKinetics
    from evelution.analysis.compare import export_comparison
    from evelution.ui.snapshot import save_state
    if not args.lab:
        print("Please provide --lab path to a CSV with columns: timestep,cell_id,EV_type,EV_rate,(proteins...)")
    else:
        lab = LabKinetics.from_csv(args.lab)
        cells = make_cells()
        sup = make_supervisor()
        sim = Simulation(cells=cells, supervisor=sup)
        # Run sim for max timestep in lab
        T = (max(lab.timesteps)+1) if lab.timesteps else 60
        field = sim.run(T=T, dt=1.0)
        # Aggregate sim rates/proteins by timestep for each EV type
        outdir = "outputs/compare"
        os.makedirs(outdir, exist_ok=True)
        ev_types = list(sim.EV_TYPES)
        for ev in ev_types:
            sim_rates = {t: field.type_time_series.get(ev, {}).get(t, 0.0) for t in lab.timesteps}
            lab_rates = {t: lab.mean_rate(t, ev) for t in lab.timesteps}
            # proteins: union seen in lab for this EV
            prot_keys = set()
            for t in lab.timesteps:
                d = lab.proteins.get((t, cells[0].cell_id, ev), {})
                prot_keys.update(d.keys())
            prot_keys = sorted(list(prot_keys))[:8]  # limit for demo
            sim_prot = {k: {t: field.protein_time_series.get(ev,{}).get(k,{}).get(t, 0.0) for t in lab.timesteps} for k in prot_keys}
            lab_prot = {k: {t: lab.mean_protein(t, ev, k) for t in lab.timesteps} for k in prot_keys}
            export_comparison(outdir, ev, lab.timesteps, sim_rates, lab_rates, prot_keys, sim_prot, lab_prot)
        # Save a pair of snapshots for diffing if user runs story/basic beforehand
        with open(os.path.join(outdir, "lab_summary.json"), "w") as f:
            import json; json.dump({"timesteps": lab.timesteps, "ev_types": ev_types}, f, indent=2)
        print("Comparison artifacts written to outputs/compare/")



elif args.mode=="game":
        emit_repro("game")
    # 1) Export tutorial
    from evelution.ui.tutorial import export_script
    tut_path = export_script()
    print("Tutorial exported:", tut_path)
    # 2) Synergy indicators
    from evelution.game.cards import default_deck, synergy_glows
    glows = synergy_glows(default_deck())
    print("Synergy indicators:", glows)
    # 3) Quest board with a demo evaluation
    from evelution.game.quests import default_quests, evaluate_Q1, save_board
    quests = default_quests()
    # demo marker panel and synthetic profiles
    panel = ["CD9","CD63","CD81","TSG101","ALIX","HSP70"]
    exo = {"CD9":0.8,"CD63":0.9,"CD81":0.7,"TSG101":0.6,"ALIX":0.6,"HSP70":0.5}
    mv  = {"CD9":0.6,"CD63":0.3,"CD81":0.5,"TSG101":0.2,"ALIX":0.2,"HSP70":0.6}
    ok, stats = evaluate_Q1(exo, mv, panel, max_markers=6, min_sep=1.2)
    board = {"quests":[q.__dict__ for q in quests], "demo_Q1":{"passed": ok, "stats": stats}}
    qpath = save_board(board)
    print("Quest board saved:", qpath)
    # 4) Skill tree: unlock Hill by default
    from evelution.game.skills import unlock, load_progress
    unlock("Hill"); unlock("ExplainUI")
    print("Progress:", load_progress())
    # 5) Accessibility defaults
    from evelution.ui.accessibility import save_config
    print("Accessibility config:", save_config())
    # 6) Controller mapping
    from evelution.ui.controller import describe
    print("Controller mapping:", describe())
    # 7) Photo mode export
    if args.photo:
        from evelution.ui.photo import export_scene_example
        print("Photo mode exported:", export_scene_example())
    print("Game scaffolds ready. See outputs/ for artifacts.")


    if args.theme:
        emit_repro("theme")
        from evelution.ui.demo_theme import export_demo
        demo = export_demo(args.theme)
        print("Theme exported:", demo)
    

# Trainer register
if args.register_trainer and args.trainer_id and args.trainer_pass:
    from evelution.security.auth import register_trainer
    path = register_trainer(args.trainer_id, args.trainer_pass, name="Trainer "+args.trainer_id)
    print("Registered trainer at:", path)



# Plugin ops
if args.list_plugins and args.trainer_id:
    from evelution.influence.registry import list_plugins
    print("Plugins:", list_plugins(args.trainer_id))
if args.add_plugin and args.trainer_id and args.trainer_pass:
    from evelution.influence.registry import install_plugin
    dst = install_plugin(args.trainer_id, args.trainer_pass, args.add_plugin)
    print("Plugin installed at:", dst)


if args.register_student and args.user_id is not None:
    from evelution.security.auth import register_student
    p = register_student(args.user_id, args.user_pass, name=f"Student {args.user_id}")
    print("Registered student at:", p)



# Notes ops
if args.note_new and args.user_id:
    from evelution.notes.notes import create_note
    note = create_note(args.role, args.user_id, args.note_new, args.note_text, password=args.user_pass)
    print("Note saved with id:", note["id"])
if args.note_list and args.user_id:
    from evelution.notes.notes import list_notes
    notes = list_notes(args.role, args.user_id)
    print("Notes:", [ (n["id"], n["title"]) for n in notes ])
if args.note_export and args.user_id:
    from evelution.notes.notes import export_note
    path = export_note(args.role, args.user_id, args.note_export, args.note_format)
    print("Exported note →", path)

if __name__ == "__main__":
    main()

import sys
import yaml
import os

def add_prefix(d: dict, prefix: str) -> dict:
    return {f"{prefix}_{k}": v for k, v in d.items()}

def update_pipeline(pipeline: list, prefix: str) -> list:
    new_pipeline = []
    for step in pipeline:
        step_copy = dict(step)
        if "names" in step_copy:
            step_copy["names"] = [f"{prefix}_{name}" for name in step_copy["names"]]
        new_pipeline.append(step_copy)
    return new_pipeline

def merge_yml(left_file, right_file, out_file=None):
    base_dir = os.path.dirname(os.path.abspath(left_file))
    if out_file is None:
        out_file = os.path.join(base_dir, "eqdata.yml")
    else:
        out_file = os.path.join(base_dir, out_file)

    with open(left_file, "r") as f:
        left_cfg = yaml.safe_load(f)
    with open(right_file, "r") as f:
        right_cfg = yaml.safe_load(f)

    devices = left_cfg.get("devices", {})

    filters = {}
    filters.update(add_prefix(left_cfg.get("filters", {}), "L"))
    filters.update(add_prefix(right_cfg.get("filters", {}), "R"))

    pipeline = []
    pipeline.extend(update_pipeline(left_cfg.get("pipeline", []), "L"))
    pipeline.extend(update_pipeline(right_cfg.get("pipeline", []), "R"))

    copy_section = [
        {"type": "Copy", "channel": 0, "dest": [2, 4]},
        {"type": "Copy", "channel": 1, "dest": [3, 5]}
    ]
    pipeline = copy_section + pipeline

    mix_section = [
        {"type": "Mix", "channel": 0, "dest": [2, 4]},
        {"type": "Mix", "channel": 1, "dest": [3, 5]}
    ]
    pipeline.extend(mix_section)

    merged = {
        "devices": devices,
        "filters": filters,
        "pipeline": pipeline,
    }

    with open(out_file, "w") as f:
        yaml.dump(merged, f, sort_keys=False)

    print(f"marge complete! → {out_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("how to use: py marge.py left.yml right.yml [output.yml]")
        sys.exit(1)

    left = sys.argv[1]
    right = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None

    merge_yml(left, right, out)

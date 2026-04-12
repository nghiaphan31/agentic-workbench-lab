"""
helpers.py — Shared test utilities (non-pytest-plugin module)
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
TEMPLATE_ROOT = REPO_ROOT / "agentic-workbench-engine"


def read_state(temp_workbench):
    """Read state.json from a temp workbench directory."""
    state_path = temp_workbench / "state.json"
    if not state_path.exists():
        return None
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_state(temp_workbench, state_dict):
    """Write state.json to a temp workbench directory."""
    state_path = temp_workbench / "state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state_dict, f, indent=2)
        f.write("\n")
"""
test_roomodes_format.py — Tests for .roomodes JSON format validation

GAP-12d: Validates that both .roomodes files are valid JSON with customModes array
containing the expected custom mode slugs.
"""

import json
from pathlib import Path

import pytest

LAB_ROOT = Path(__file__).parent.parent.parent
ENGINE_ROOT = LAB_ROOT / "agentic-workbench-engine"

EXPECTED_CUSTOM_SLUGS = {"test-engineer", "reviewer-security", "documentation-librarian"}


def load_roomodes(path: Path) -> dict:
    """Load and parse a .roomodes file."""
    assert path.exists(), f".roomodes file not found: {path}"
    content = path.read_text(encoding="utf-8")
    return json.loads(content)


class TestRoomodesFormat:
    """GAP-12d: .roomodes format validation tests."""

    def test_gap12a_engine_roomodes_is_valid_json(self):
        """GAP-12a: agentic-workbench-engine/.roomodes is valid JSON."""
        roomodes_path = ENGINE_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        assert isinstance(data, dict), ".roomodes should be a JSON object"

    def test_gap12a_engine_roomodes_has_custom_modes_array(self):
        """GAP-12a: agentic-workbench-engine/.roomodes has customModes array."""
        roomodes_path = ENGINE_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        assert "customModes" in data, ".roomodes should have 'customModes' key"
        assert isinstance(data["customModes"], list), "customModes should be an array"

    def test_gap12a_engine_roomodes_contains_expected_slugs(self):
        """GAP-12a: agentic-workbench-engine/.roomodes contains all 3 custom mode slugs."""
        roomodes_path = ENGINE_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        slugs = {mode["slug"] for mode in data["customModes"]}
        assert EXPECTED_CUSTOM_SLUGS.issubset(slugs), (
            f"Missing custom mode slugs: {EXPECTED_CUSTOM_SLUGS - slugs}"
        )

    def test_gap12a_engine_roomodes_modes_have_required_fields(self):
        """GAP-12a: Each custom mode has required fields: slug, name, roleDefinition, groups."""
        roomodes_path = ENGINE_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        for mode in data["customModes"]:
            assert "slug" in mode, f"Mode missing 'slug': {mode}"
            assert "name" in mode, f"Mode missing 'name': {mode}"
            assert "roleDefinition" in mode, f"Mode missing 'roleDefinition': {mode}"
            assert "groups" in mode, f"Mode missing 'groups': {mode}"

    def test_gap12b_lab_root_roomodes_is_valid_json(self):
        """GAP-12b: Lab root .roomodes is valid JSON."""
        roomodes_path = LAB_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        assert isinstance(data, dict), ".roomodes should be a JSON object"

    def test_gap12b_lab_root_roomodes_has_custom_modes_array(self):
        """GAP-12b: Lab root .roomodes has customModes array."""
        roomodes_path = LAB_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        assert "customModes" in data, ".roomodes should have 'customModes' key"
        assert isinstance(data["customModes"], list), "customModes should be an array"

    def test_gap12b_lab_root_roomodes_contains_expected_slugs(self):
        """GAP-12b: Lab root .roomodes contains all 3 custom mode slugs."""
        roomodes_path = LAB_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        slugs = {mode["slug"] for mode in data["customModes"]}
        assert EXPECTED_CUSTOM_SLUGS.issubset(slugs), (
            f"Missing custom mode slugs: {EXPECTED_CUSTOM_SLUGS - slugs}"
        )

    def test_gap12_lab_root_roomodes_modes_have_required_fields(self):
        """GAP-12: Each custom mode in lab root .roomodes has required fields."""
        roomodes_path = LAB_ROOT / ".roomodes"
        data = load_roomodes(roomodes_path)
        for mode in data["customModes"]:
            assert "slug" in mode, f"Mode missing 'slug': {mode}"
            assert "name" in mode, f"Mode missing 'name': {mode}"
            assert "roleDefinition" in mode, f"Mode missing 'roleDefinition': {mode}"
            assert "groups" in mode, f"Mode missing 'groups': {mode}"

    def test_gap12_no_builtin_modes_in_custom_modes(self):
        """GAP-12: Built-in modes (architect, developer, orchestrator) should NOT be in customModes."""
        builtin_slugs = {"architect", "developer", "orchestrator", "code", "ask", "debug"}
        for roomodes_path in [ENGINE_ROOT / ".roomodes", LAB_ROOT / ".roomodes"]:
            data = load_roomodes(roomodes_path)
            slugs = {mode["slug"] for mode in data["customModes"]}
            overlap = builtin_slugs & slugs
            assert not overlap, (
                f"Built-in modes should not be in customModes: {overlap} in {roomodes_path}"
            )

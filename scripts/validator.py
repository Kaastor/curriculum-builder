"""
Curriculum JSON Validator — Structural Integrity Checks

Validates data/curriculum.json against all constraints defined in
docs/curriculum_generator.md. Run after generation to catch errors
before feeding to UI or pedagogical review.

Usage:
    python scripts/validate_curriculum.py [path/to/curriculum.json]

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# ─── Constants ───────────────────────────────────────────────────────

VALID_CATEGORIES = {
    "foundation", "selection", "ordering",
    "arguments", "output", "hallucination", "avoidance",
    "debug", "capstone",
}

VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}

VALID_EXERCISE_TYPES = {"write", "debug", "read", "integrate"}

CATEGORY_PREFIXES = {
    "foundation": "F",
    "selection": "S",
    "ordering": "O",
    "arguments": "A",
    "output": "R",
    "hallucination": "H",
    "avoidance": "V",
    "debug": "D",
    "capstone": "C",
}

REQUIRED_NODE_FIELDS = {
    "id", "title", "category", "layer", "difficulty",
    "estimated_time_minutes", "exercise_type", "failure_mode",
    "exercise", "pass_condition", "fail_condition",
    "reference_hint", "prerequisites", "dependents",
    "teaches", "connects_to_field_map", "tags", "skeleton_file",
}

REQUIRED_COVERAGE_KEYS = {
    "choosing_wrong_tool",
    "wrong_call_order",
    "malformed_arguments",
    "output_misinterpretation",
    "tool_hallucination",
    "tool_avoidance",
}

MAX_LAYER = 4
MIN_NODES = 18
MAX_NODES = 25
MAX_PREREQS = 3
TIME_MIN = 30
TIME_MAX = 90


# ─── Helpers ─────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.warnings: list[str] = []

    def ok(self, msg: str):
        self.passed.append(msg)

    def fail(self, msg: str):
        self.failed.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def report(self) -> str:
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"CURRICULUM VALIDATION REPORT")
        lines.append(f"{'='*60}\n")

        lines.append(f"✅ PASSED: {len(self.passed)}")
        for m in self.passed:
            lines.append(f"   ✅ {m}")

        if self.warnings:
            lines.append(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for m in self.warnings:
                lines.append(f"   ⚠️  {m}")

        if self.failed:
            lines.append(f"\n❌ FAILED: {len(self.failed)}")
            for m in self.failed:
                lines.append(f"   ❌ {m}")
        else:
            lines.append(f"\n🎉 ALL CHECKS PASSED")

        lines.append(f"\n{'='*60}")
        lines.append(
            f"Total: {len(self.passed)} passed, "
            f"{len(self.warnings)} warnings, "
            f"{len(self.failed)} failed"
        )
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)

    @property
    def success(self) -> bool:
        return len(self.failed) == 0


# ─── Checks ──────────────────────────────────────────────────────────

def check_top_level_structure(data: dict, r: ValidationResult):
    """Verify required top-level keys exist."""
    required = {
        "domain", "domain_ref", "scenario", "metadata",
        "nodes", "edges", "learning_path", "milestones", "coverage_map",
    }
    missing = required - set(data.keys())
    if missing:
        r.fail(f"Missing top-level keys: {missing}")
    else:
        r.ok("All top-level keys present")


def check_metadata(data: dict, r: ValidationResult):
    """Verify metadata fields."""
    meta = data.get("metadata", {})
    for field in ("generated", "node_count", "edge_count", "max_depth"):
        if field not in meta:
            r.fail(f"metadata.{field} missing")

    node_count = meta.get("node_count")
    if isinstance(node_count, int):
        actual = len(data.get("nodes", []))
        if node_count != actual:
            r.fail(
                f"metadata.node_count={node_count} but "
                f"actual nodes array has {actual} elements"
            )
        else:
            r.ok(f"metadata.node_count matches actual ({actual})")
    else:
        r.fail(f"metadata.node_count should be int, got {type(node_count).__name__}")

    edge_count = meta.get("edge_count")
    if isinstance(edge_count, int):
        actual = len(data.get("edges", []))
        if edge_count != actual:
            r.fail(
                f"metadata.edge_count={edge_count} but "
                f"actual edges array has {actual} elements"
            )
        else:
            r.ok(f"metadata.edge_count matches actual ({actual})")

    max_depth = meta.get("max_depth")
    if isinstance(max_depth, int) and max_depth > MAX_LAYER:
        r.fail(f"metadata.max_depth={max_depth} exceeds max {MAX_LAYER}")


def check_node_count(nodes: list, r: ValidationResult):
    """Node count within 15-25 range."""
    n = len(nodes)
    if MIN_NODES <= n <= MAX_NODES:
        r.ok(f"Node count {n} within [{MIN_NODES}, {MAX_NODES}]")
    else:
        r.fail(f"Node count {n} outside [{MIN_NODES}, {MAX_NODES}]")


def check_node_schema(nodes: list, r: ValidationResult):
    """Every node has exactly the 16 required fields."""
    for node in nodes:
        nid = node.get("id", "???")
        fields = set(node.keys())
        missing = REQUIRED_NODE_FIELDS - fields
        extra = fields - REQUIRED_NODE_FIELDS
        if missing:
            r.fail(f"Node {nid}: missing fields {missing}")
        if extra:
            r.fail(f"Node {nid}: extra fields {extra}")
        if not missing and not extra:
            r.ok(f"Node {nid}: schema correct (16 fields)")


def check_id_prefixes(nodes: list, r: ValidationResult):
    """Node IDs use correct category prefix."""
    for node in nodes:
        nid = node.get("id", "")
        cat = node.get("category", "")
        expected_prefix = CATEGORY_PREFIXES.get(cat)
        if expected_prefix and not nid.startswith(expected_prefix):
            r.fail(
                f"Node {nid}: category '{cat}' expects "
                f"prefix '{expected_prefix}', got '{nid}'"
            )


def check_enums(nodes: list, r: ValidationResult):
    """Category, difficulty, and exercise_type values are valid enums."""
    errors = 0
    for node in nodes:
        nid = node.get("id", "???")
        cat = node.get("category")
        if cat not in VALID_CATEGORIES:
            r.fail(f"Node {nid}: invalid category '{cat}'")
            errors += 1
        diff = node.get("difficulty")
        if diff not in VALID_DIFFICULTIES:
            r.fail(f"Node {nid}: invalid difficulty '{diff}'")
            errors += 1
        etype = node.get("exercise_type")
        if etype not in VALID_EXERCISE_TYPES:
            r.fail(f"Node {nid}: invalid exercise_type '{etype}'")
            errors += 1
    if errors == 0:
        r.ok("All category, difficulty, and exercise_type values valid")


def check_exercise_type_distribution(nodes: list, r: ValidationResult):
    """Verify debug/read and capstone exercise requirements."""
    debug_read = [n for n in nodes if n.get("exercise_type") in ("debug", "read")]
    capstone = [n for n in nodes if n.get("exercise_type") == "integrate"]
    errors = 0

    # 2-3 debug/read nodes at layers 3-4
    if len(debug_read) < 2:
        r.fail(f"Only {len(debug_read)} debug/read nodes — need at least 2")
        errors += 1
    elif len(debug_read) > 3:
        r.warn(f"{len(debug_read)} debug/read nodes — expected 2-3")
    else:
        r.ok(f"{len(debug_read)} debug/read nodes (within 2-3 range)")

    for node in debug_read:
        layer = node.get("layer", 0)
        if layer < 3:
            r.fail(
                f"Debug/read node {node['id']} at layer {layer} "
                f"— should be at layer 3 or 4"
            )
            errors += 1

    # Exactly 1 capstone at layer 4
    if len(capstone) != 1:
        r.fail(f"{len(capstone)} capstone (integrate) nodes — need exactly 1")
        errors += 1
    else:
        cap = capstone[0]
        if cap.get("layer") != 4:
            r.fail(f"Capstone {cap['id']} at layer {cap.get('layer')} — must be layer 4")
            errors += 1
        if cap.get("category") != "capstone":
            r.fail(f"Capstone {cap['id']} has category '{cap.get('category')}' — must be 'capstone'")
            errors += 1
        if errors == 0:
            r.ok(f"Capstone node {cap['id']} correctly placed at layer 4")


def check_reference_hints(nodes: list, r: ValidationResult):
    """Every node must have a non-trivial reference_hint."""
    errors = 0
    for node in nodes:
        nid = node["id"]
        hint = node.get("reference_hint", "")
        if not hint or len(hint.strip()) < 20:
            r.fail(f"Node {nid}: reference_hint is missing or too short ({len(hint.strip())} chars)")
            errors += 1
    if errors == 0:
        r.ok("All nodes have non-trivial reference_hint (≥20 chars)")


def check_layers(nodes: list, r: ValidationResult):
    """Layer values 0-4, and layer-0 nodes have no prerequisites."""
    node_map = {n["id"]: n for n in nodes}
    errors = 0
    for node in nodes:
        nid = node["id"]
        layer = node.get("layer")
        if not isinstance(layer, int) or layer < 0 or layer > MAX_LAYER:
            r.fail(f"Node {nid}: layer={layer} outside [0, {MAX_LAYER}]")
            errors += 1
            continue
        if layer == 0 and node.get("prerequisites"):
            r.fail(f"Node {nid}: layer=0 but has prerequisites {node['prerequisites']}")
            errors += 1
        # Check that prerequisites are from strictly lower layers
        for pid in node.get("prerequisites", []):
            if pid in node_map:
                player = node_map[pid].get("layer", -1)
                if player >= layer:
                    r.fail(
                        f"Node {nid} (layer {layer}) has prerequisite "
                        f"{pid} (layer {player}) — must be strictly lower"
                    )
                    errors += 1
    if errors == 0:
        r.ok("All layer values valid and prerequisites respect layer ordering")


def check_time_estimates(nodes: list, r: ValidationResult):
    """Estimated time within 30-90 minutes."""
    errors = 0
    for node in nodes:
        nid = node["id"]
        t = node.get("estimated_time_minutes")
        if not isinstance(t, int) or t < TIME_MIN or t > TIME_MAX:
            r.warn(f"Node {nid}: estimated_time={t} outside [{TIME_MIN}, {TIME_MAX}]")
            errors += 1
    if errors == 0:
        r.ok(f"All time estimates within [{TIME_MIN}, {TIME_MAX}] minutes")


def check_prerequisite_count(nodes: list, r: ValidationResult):
    """No node has more than 3 prerequisites."""
    errors = 0
    for node in nodes:
        nid = node["id"]
        prereqs = node.get("prerequisites", [])
        if len(prereqs) > MAX_PREREQS:
            r.fail(f"Node {nid}: {len(prereqs)} prerequisites exceeds max {MAX_PREREQS}")
            errors += 1
    if errors == 0:
        r.ok(f"All nodes have ≤{MAX_PREREQS} prerequisites")


def check_id_references(nodes: list, edges: list, r: ValidationResult):
    """All IDs referenced in prerequisites, dependents, and edges exist."""
    node_ids = {n["id"] for n in nodes}
    errors = 0

    for node in nodes:
        nid = node["id"]
        for pid in node.get("prerequisites", []):
            if pid not in node_ids:
                r.fail(f"Node {nid}: prerequisite '{pid}' does not exist")
                errors += 1
        for did in node.get("dependents", []):
            if did not in node_ids:
                r.fail(f"Node {nid}: dependent '{did}' does not exist")
                errors += 1

    for edge in edges:
        if edge.get("from") not in node_ids:
            r.fail(f"Edge from '{edge.get('from')}' — node does not exist")
            errors += 1
        if edge.get("to") not in node_ids:
            r.fail(f"Edge to '{edge.get('to')}' — node does not exist")
            errors += 1

    if errors == 0:
        r.ok("All ID references valid")


def check_dependents_inverse(nodes: list, r: ValidationResult):
    """dependents[] is the exact inverse of prerequisites[]."""
    # Build expected dependents from prerequisites
    expected_dependents: dict[str, set[str]] = defaultdict(set)
    for node in nodes:
        nid = node["id"]
        for pid in node.get("prerequisites", []):
            expected_dependents[pid].add(nid)

    errors = 0
    node_map = {n["id"]: n for n in nodes}

    for node in nodes:
        nid = node["id"]
        actual = set(node.get("dependents", []))
        expected = expected_dependents.get(nid, set())
        if actual != expected:
            r.fail(
                f"Node {nid}: dependents={sorted(actual)} "
                f"but expected {sorted(expected)} from prerequisites inverse"
            )
            errors += 1

    if errors == 0:
        r.ok("dependents[] is exact inverse of prerequisites[] for all nodes")


def check_edges_match_prerequisites(nodes: list, edges: list, r: ValidationResult):
    """Edges array matches the prerequisite relationships in nodes."""
    # Build edge set from nodes
    node_edges = set()
    for node in nodes:
        for pid in node.get("prerequisites", []):
            node_edges.add((pid, node["id"]))

    # Build edge set from edges array
    array_edges = set()
    for edge in edges:
        array_edges.add((edge["from"], edge["to"]))

    missing_in_array = node_edges - array_edges
    extra_in_array = array_edges - node_edges

    if missing_in_array:
        r.fail(f"Edges missing from edges array: {missing_in_array}")
    if extra_in_array:
        r.fail(f"Extra edges in array not in prerequisites: {extra_in_array}")
    if not missing_in_array and not extra_in_array:
        r.ok("Edges array matches prerequisite relationships exactly")


def check_no_cycles(nodes: list, r: ValidationResult):
    """DAG check — no circular dependencies."""
    adj: dict[str, list[str]] = {n["id"]: list(n.get("prerequisites", [])) for n in nodes}
    visited: set[str] = set()
    in_stack: set[str] = set()
    has_cycle = False

    def dfs(nid: str) -> bool:
        nonlocal has_cycle
        if nid in in_stack:
            has_cycle = True
            return True
        if nid in visited:
            return False
        visited.add(nid)
        in_stack.add(nid)
        for pid in adj.get(nid, []):
            if dfs(pid):
                return True
        in_stack.discard(nid)
        return False

    for nid in adj:
        dfs(nid)

    if has_cycle:
        r.fail("Circular dependency detected")
    else:
        r.ok("No circular dependencies (valid DAG)")


def check_reachability(nodes: list, r: ValidationResult):
    """Every node is reachable from at least one layer-0 node."""
    node_map = {n["id"]: n for n in nodes}
    layer0 = {n["id"] for n in nodes if n.get("layer") == 0}

    # BFS forward from layer-0 via dependents
    reachable: set[str] = set()
    queue = list(layer0)
    while queue:
        nid = queue.pop(0)
        if nid in reachable:
            continue
        reachable.add(nid)
        for did in node_map.get(nid, {}).get("dependents", []):
            if did not in reachable:
                queue.append(did)

    unreachable = set(node_map.keys()) - reachable
    if unreachable:
        r.fail(f"Nodes not reachable from any layer-0 node: {sorted(unreachable)}")
    else:
        r.ok("All nodes reachable from layer-0 roots")


def check_topological_order(data: dict, nodes: list, r: ValidationResult):
    """topological_order respects all prerequisite constraints."""
    topo = data.get("learning_path", {}).get("topological_order", [])
    node_ids = {n["id"] for n in nodes}

    # Check completeness
    topo_set = set(topo)
    missing = node_ids - topo_set
    extra = topo_set - node_ids
    if missing:
        r.fail(f"topological_order missing nodes: {sorted(missing)}")
        return
    if extra:
        r.fail(f"topological_order has unknown nodes: {sorted(extra)}")
        return

    # Check ordering
    position = {nid: i for i, nid in enumerate(topo)}
    node_map = {n["id"]: n for n in nodes}
    errors = 0
    for node in nodes:
        nid = node["id"]
        for pid in node.get("prerequisites", []):
            if position.get(pid, -1) >= position.get(nid, -1):
                r.fail(
                    f"topological_order: {pid} (pos {position.get(pid)}) "
                    f"should come before {nid} (pos {position.get(nid)})"
                )
                errors += 1
    if errors == 0:
        r.ok("topological_order respects all prerequisites")


def check_coverage_map(data: dict, nodes: list, r: ValidationResult):
    """All 6 domain bullets covered, all referenced IDs exist."""
    cmap = data.get("coverage_map", {})
    node_ids = {n["id"] for n in nodes}

    missing_keys = REQUIRED_COVERAGE_KEYS - set(cmap.keys())
    if missing_keys:
        r.fail(f"coverage_map missing keys: {missing_keys}")
    else:
        r.ok("coverage_map has all 6 required keys")

    errors = 0
    for key, ids in cmap.items():
        if not ids:
            r.fail(f"coverage_map['{key}'] is empty — no nodes cover this bullet")
            errors += 1
        for nid in ids:
            if nid not in node_ids:
                r.fail(f"coverage_map['{key}'] references unknown node '{nid}'")
                errors += 1
    if errors == 0:
        r.ok("coverage_map: all referenced node IDs exist and no empty entries")


def check_milestones(data: dict, nodes: list, r: ValidationResult):
    """Milestone IDs use MS prefix, reference valid nodes."""
    milestones = data.get("milestones", [])
    node_ids = {n["id"] for n in nodes}
    errors = 0

    for ms in milestones:
        msid = ms.get("id", "???")
        if not msid.startswith("MS"):
            r.fail(f"Milestone '{msid}' does not use 'MS' prefix")
            errors += 1
        for nid in ms.get("nodes", []):
            if nid not in node_ids:
                r.fail(f"Milestone {msid} references unknown node '{nid}'")
                errors += 1

    # Check all nodes are in some milestone
    milestone_nodes = set()
    for ms in milestones:
        milestone_nodes.update(ms.get("nodes", []))
    uncovered = node_ids - milestone_nodes
    if uncovered:
        r.warn(f"Nodes not in any milestone: {sorted(uncovered)}")

    if errors == 0:
        r.ok("Milestones use MS prefix and reference valid nodes")


def check_unique_ids(nodes: list, r: ValidationResult):
    """All node IDs are unique."""
    ids = [n["id"] for n in nodes]
    dupes = [nid for nid in ids if ids.count(nid) > 1]
    if dupes:
        r.fail(f"Duplicate node IDs: {set(dupes)}")
    else:
        r.ok("All node IDs unique")


def check_string_quality(nodes: list, r: ValidationResult):
    """Exercise, pass_condition, fail_condition are non-empty and well-formed."""
    errors = 0
    for node in nodes:
        nid = node["id"]
        for field in ("exercise", "pass_condition", "fail_condition", "failure_mode", "teaches", "reference_hint"):
            val = node.get(field, "")
            if not val or len(val.strip()) < 10:
                r.warn(f"Node {nid}: '{field}' is too short or empty: '{val}'")
                errors += 1
    if errors == 0:
        r.ok("All text fields are non-trivially populated")


# ─── Main ────────────────────────────────────────────────────────────

def validate(path: Path) -> ValidationResult:
    r = ValidationResult()

    # Load JSON
    try:
        data = json.loads(path.read_text())
        r.ok(f"JSON parsed successfully from {path}")
    except json.JSONDecodeError as e:
        r.fail(f"Invalid JSON: {e}")
        return r

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Run all checks
    check_top_level_structure(data, r)
    check_metadata(data, r)
    check_unique_ids(nodes, r)
    check_node_count(nodes, r)
    check_node_schema(nodes, r)
    check_id_prefixes(nodes, r)
    check_enums(nodes, r)
    check_exercise_type_distribution(nodes, r)
    check_reference_hints(nodes, r)
    check_layers(nodes, r)
    check_time_estimates(nodes, r)
    check_prerequisite_count(nodes, r)
    check_id_references(nodes, edges, r)
    check_dependents_inverse(nodes, r)
    check_edges_match_prerequisites(nodes, edges, r)
    check_no_cycles(nodes, r)
    check_reachability(nodes, r)
    check_topological_order(data, nodes, r)
    check_coverage_map(data, nodes, r)
    check_milestones(data, nodes, r)
    check_string_quality(nodes, r)

    return r


def main():
    default_path = Path(__file__).parent.parent / "data" / "curriculum.json"
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path

    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    result = validate(path)
    print(result.report())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()

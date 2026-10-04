"""Guard Bruno's requirement: tool extensions must preserve Matt's transport."""

import ast
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
CONTRACT = json.loads((Path(__file__).with_name("matt_contract.json")).read_text())


@pytest.mark.parametrize("contract", CONTRACT["contracts"], ids=lambda item: item["id"])
def test_transport_matches_pinned_matt(contract):
    source = (ROOT / "custom_components/elise_live_test" / contract["file"]).read_text()
    if method := contract.get("method"):
        node = next(
            node for node in ast.walk(ast.parse(source))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == method
        )
        # Source segments are stable across Python AST schema revisions.
        canonical = ast.get_source_segment(source, node)
    else:
        canonical = source.replace('"elise_live_test"', '"gemini_live"').rstrip() + "\n"
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    assert digest == contract["sha256"], (
        f"Transport diverged from Matt {CONTRACT['commit']}: {contract['id']}. "
        "Review this change separately from tool additions."
    )

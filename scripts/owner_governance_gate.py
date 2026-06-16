"""Run Owner-facing governance gates used by hooks, CI, and release prep."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SOURCE_ROOT = ROOT / "src" / "agent_runtime" / "templates" / "project"


def _has_runtime_source_tree() -> bool:
    return RUNTIME_SOURCE_ROOT.exists()


def _state_machine_args() -> list[str]:
    args = [
        "scripts/state_machine_gate.py",
        "--path",
        "agents/project/STATE-MACHINES.yml",
        "--path",
        "schemas/state-machines.schema.json",
    ]
    template_paths = [
        "src/agent_runtime/templates/project/agents/project/STATE-MACHINES.yml",
        "src/agent_runtime/templates/project/schemas/state-machines.schema.json",
    ]
    for rel in template_paths:
        if (ROOT / rel).exists():
            args.extend(["--path", rel])
    return args


def run(args: list[str]) -> int:
    label = " ".join(args)
    print(f"owner-governance: start: {label}", flush=True)
    rc = subprocess.call([sys.executable, *args], cwd=ROOT)
    print(f"owner-governance: result: {label} -> {rc}", flush=True)
    return rc


def skip(args: list[str], reason: str) -> int:
    label = " ".join(args)
    print(f"owner-governance: skip: {label} ({reason})", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Owner governance gate")
    parser.add_argument("--allow-empty-owner-docs", action="store_true")
    args = parser.parse_args()

    owner_doc_args = ["scripts/owner_doc_format_gate.py", "--manifest", "owner-docs.yml"]
    if args.allow_empty_owner_docs:
        owner_doc_args.append("--allow-empty")
    host_project = not _has_runtime_source_tree()
    source_only_reason = "host project without src/agent_runtime/templates/project"
    checks: list[tuple[list[str], bool, str]] = [
        owner_doc_args,
        _state_machine_args(),
        (["scripts/response_contract_gate.py", "--check"], True, ""),
        (["scripts/continuity_contract_gate.py", "--check"], True, ""),
        (["scripts/task_identity.py", "check", "--check"], True, ""),
        (["scripts/work_item_classifier.py", "--check"], not host_project, source_only_reason),
        (["scripts/work_schema_gate.py", "--items", "--check"], True, ""),
        (["scripts/footprint_conflict_gate.py", "--check"], True, ""),
        (["scripts/taskset_work_gate.py", "--check"], not host_project, source_only_reason),
        (["scripts/evidence_index_generator.py", "--check"], not host_project, source_only_reason),
        (["scripts/verification_freshness_gate.py", "--check"], True, ""),
        # intentionally omitted: scripts/context_knowledge_gate.py -- root-repo-specific
        # (validates TASKSET-AR-CONTEXT-KNOWLEDGE contracts against src/agent_runtime/templates/**,
        # agents/project/overlays/**, and agents/project/evals/* evidence that generated projects
        # do not ship). Mirrored in tests/test_owner_governance_chain_parity.py exceptions.
        (["scripts/parallel_worktree_gate.py", "--check"], True, ""),
        (["scripts/worktree_lifecycle_gate.py", "--check"], True, ""),
        (["scripts/collaboration_concurrency_gate.py", "--check"], True, ""),
        (["scripts/rbac_write_gate.py", "--check"], True, ""),
        (["scripts/agent_identity_gate.py", "--check"], True, ""),
        (["scripts/attribution_gate.py", "--check"], True, ""),
        (["scripts/collaboration_governance_gate.py", "--check"], not host_project, source_only_reason),
        (["scripts/runtime_asset_usage.py", "--check"], not host_project, source_only_reason),
        (["scripts/state_sync_gate.py", "--check"], not host_project, source_only_reason),
        (["scripts/release_cadence_trigger.py", "--check"], True, ""),
        (["scripts/conversation_work_audit.py", "--check"], True, ""),
        (
            ["scripts/planning_loop.py", "gate", "--trigger", "hook", "--action", "scan"],
            (ROOT / "scripts" / "planning_loop.py").exists(),
            "script missing",
        ),
    ]

    failed = 0
    for item in checks:
        if len(item) == 3 and isinstance(item[1], bool):
            check, enabled, reason = item
        else:
            check, enabled, reason = item, True, ""
        rc = run(check) if enabled else skip(check, reason)
        if rc:
            failed = rc
    return failed


if __name__ == "__main__":
    raise SystemExit(main())

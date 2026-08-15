"""Shared report and digest plumbing for objective PDF checks."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

PASS = "pass"
WARN = "warn"
FAIL = "fail"


@dataclass
class Check:
    check_id: str
    level: str
    detail: str


def file_sha256(path: str) -> str:
    """Return the sha256 of the bytes this report describes."""
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError as exc:
        die(f"cannot read {path} to digest it ({exc}) — a report that "
            "cannot name the bytes it read binds nothing")


@dataclass
class Report:
    layer: str
    file: str
    checks: list[Check] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    def add(self, check_id: str, level: str, detail: str) -> None:
        self.checks.append(Check(check_id, level, detail))

    @property
    def failed(self) -> bool:
        return any(c.level == FAIL for c in self.checks)

    def to_dict(self) -> dict:
        return {
            "layer": self.layer,
            "file": self.file,
            "file_sha256": file_sha256(self.file),
            "result": FAIL if self.failed else PASS,
            "checks": [vars(c) for c in self.checks],
            "metrics": self.metrics,
            **self.extra,
        }

    def emit(self, as_json: bool) -> int:
        """Print the report and return the intended exit code."""
        if as_json:
            print(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))
        else:
            icon = {PASS: "ok", WARN: "!!", FAIL: "XX"}
            print(f"[{self.layer}] {self.file}")
            for c in self.checks:
                print(f"  {icon[c.level]}  {c.check_id}: {c.detail}")
            for k, v in self.metrics.items():
                print(f"      {k} = {v}")
            print(f"  => {'FAIL' if self.failed else 'PASS'}")
        return 1 if self.failed else 0


def die(msg: str) -> "NoReturn":  # noqa: F821 - py3.11 compat without typing import
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)

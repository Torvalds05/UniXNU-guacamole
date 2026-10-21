#!/usr/bin/env python3
"""Build the Aloha NOSB firmware volume with the UniXNU/DarwinBoot INFs.

Calls unixnu's firmware driver with the local trees, without the kernel-tree
fetch/assembly step. The package paths are the ones PlatformBuildNoSb.py uses.
"""
import sys
import tomllib
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "unixnu" / "scripts"))

from unixnu import firmware  # noqa: E402

UEFI = ROOT / "uefi"
EDK2 = UEFI / "MU_BASECORE"
TREE = ROOT / "build-tree"
WORK = ROOT / "out" / "guacamole"
LOGS = WORK / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

board = tomllib.loads((ROOT / "board.toml").read_text())
ctx = types.SimpleNamespace(
    board=board,
    tree=TREE,
    work=WORK,
    logs=LOGS,
    jobs=8,
    args=types.SimpleNamespace(skip_preflight=False),
    uefi=UEFI,
)
firmware.build(ctx, None, UEFI, EDK2, "DEBUG")

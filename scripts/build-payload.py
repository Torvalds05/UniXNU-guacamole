#!/usr/bin/env python3
"""Build the FAT payload with the prebuilt guacamole kernel and ADT wrapper."""
import sys
import tomllib
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "unixnu" / "scripts"))

from unixnu import payload  # noqa: E402

WORK = ROOT / "out" / "guacamole"
LOGS = WORK / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

board = tomllib.loads((ROOT / "board.toml").read_text())
ctx = types.SimpleNamespace(
    board=board,
    tree=ROOT / "build-tree",
    work=WORK,
    logs=LOGS,
    uefi=ROOT / "uefi",
    args=types.SimpleNamespace(
        kernel=ROOT / "inputs" / "guacamole" / "kernel.macho",
        kernel_arg=None,
        trust_cache=None,
        owner_trust_cache=None,
        data_ramdisk=None,
        skip_setup=False,
        unique_chip_id="0x5357454554000001",
    ),
)
payload.build(ctx)

#!/usr/bin/env python3
"""UniXNU ADT step for guacamole.

The UniXNU payload driver passes the generic ADT flags (chip-id,
owned-memory-size, root-match UUID, CPU registers, PSCI method, trust cache,
...). The guacamole hardware profile in mkadt.py owns those values; accept the
flags and generate the D22AP/guacamole tree with the requested DRAM size.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dram-size", default="0xc0000000")
    known, _unknown = parser.parse_known_args()
    tool = Path(__file__).resolve().parent / "mkadt.py"
    subprocess.run(
        [sys.executable, str(tool), known.output, "--device", "guacamole", "--dram-size", known.dram_size],
        check=True,
    )


if __name__ == "__main__":
    main()

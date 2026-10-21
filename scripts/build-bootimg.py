#!/usr/bin/env python3
"""Pack the Aloha boot image with the full guacamole DTB table.

unixnu's bootimg insists on a single FDT; the Aloha guacamole DTB is a
2,779,551-byte table whose first FDT is 0x7bed2 bytes. The prebuilt image
appends the whole table, matching the ABL/UEFI expectation, so do the same.
"""
import argparse
import gzip
import json
import sys
import tempfile
import tomllib
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "unixnu" / "scripts"))

from unixnu import bootimg  # noqa: E402
from unixnu.util import run, sha256_file  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--fd", default=str(ROOT / "inputs" / "uefi-prebuilt" / "nosb_fv.fd"))
parser.add_argument("--dtb", default=str(ROOT / "inputs" / "uefi-prebuilt" / "guacamole.dtb"))
parser.add_argument("--ramdisk", default=str(ROOT / "out" / "guacamole" / "payload" / "payload.img"))
parser.add_argument("-o", "--output", default=str(ROOT / "out" / "guacamole" / "boot" / "boot.img"))
args = parser.parse_args()

WORK = ROOT / "out" / "guacamole"
UEFI = ROOT / "uefi"
board = tomllib.loads((ROOT / "board.toml").read_text())
ctx = types.SimpleNamespace(board=board, work=WORK)
image, base, size, requires_header, config = bootimg.settings(ctx, UEFI)
fv = Path(args.fd).read_bytes()
if len(fv) != size:
    raise SystemExit(f"firmware volume is {len(fv):#x} bytes, expected {size:#x}")
dtb = Path(args.dtb).read_bytes()
ramdisk = Path(args.ramdisk)
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory(prefix="unixnu-bootimg-") as scratch_name:
    scratch = Path(scratch_name)
    shim = bootimg.compile_shim(UEFI, base, size, requires_header, scratch)
    combined = shim + fv
    kernel = gzip.compress(combined, mtime=0) + dtb
    kernel_path = scratch / "Image.gz-dtb"
    kernel_path.write_bytes(kernel)
    command = ["python3", str(UEFI / "Resources/Scripts/mkbootimg.py"),
               "--kernel", str(kernel_path), "--ramdisk", str(ramdisk), "-o", str(out)]
    for key in bootimg.MKBOOTIMG_FLAGS:
        if key in image:
            command += [f"--{key}", str(image[key])]
    run(command)

report = {
    "kernel_sha256": sha256_file(kernel_path) if kernel_path.exists() else None,
    "image_sha256": sha256_file(out),
    "image_bytes": out.stat().st_size,
    "fd_sha256": sha256_file(args.fd),
    "dtb_sha256": sha256_file(args.dtb),
    "dtb_bytes": len(dtb),
    "ramdisk_bytes": ramdisk.stat().st_size,
    "shim_bytes": len(shim),
    "hardware_tested": False,
}
(out.parent / "boot.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"bootimg: {out} ({out.stat().st_size} bytes)")

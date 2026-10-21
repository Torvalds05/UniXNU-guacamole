# UniXNU-guacamole

Separate bring-up project for the OnePlus 7 Pro (guacamole, SM8150). It boots the
existing `ios-sweet` guacamole XNU / iPhone X iOS 16.7.16 userland through the
Project Aloha guacamole UEFI (NOSB) plus UniXNU/DarwinBoot.

`ios-sweet` remains the kernel/rootfs source. This repository owns the
UEFI/payload integration and the board file; it is not a second kernel tree.

## Verified starting point

- The prebuilt Aloha `oneplus-guacamole_NOSB.img` boots on the GM1910 and
  enumerates a Qualcomm vendor-specific USB device (`045e:066b`, class 255).
  It is not a storage or network gadget.
- The image is `gzip(BootShim + FV) + DTB`:
  - BootShim: 0x70 bytes
  - FV: exactly 0x00300000 bytes at `0x9FC00000`
  - DTB: 2,779,551 bytes, appended
  - Android header: kernel at `0x8000`, tags at `0x100`, page 4096, v0
- The Aloha guacamole FDF includes UFSDxe, FAT, PartitionDxe, RamPartitionDxe,
  SimpleFbDxe, BdsDxe and the USB device drivers. DisplayDxe is commented out;
  SimpleFb uses the ABL framebuffer.
- There is no upstream `UniXNU-guacamole` repository. The sheng tree in
  `reference/UniXNU-sheng` is the integration model: DarwinBoot is in the FV,
  the kernel/ADT/trustcache live in a FAT ramdisk payload.

## Layout

```
board.toml                 UniXNU board file (firmware/payload/bootimg)
configs/                   kernel defconfigs (unused for the prebuilt kernel)
scripts/                   ADT wrapper, copied mkadt/adt/devices, preflight
package/                   device package (currently empty)
uefi/                      Project Aloha Mu-Silicium tree (ignored)
unixnu/                    UniXNU build driver and EFI packages (ignored)
reference/UniXNU-sheng/    sheng device repo, integration reference (ignored)
inputs/                    guacamole kernel, ADTs, prebuilt NOSB FV (ignored)
```

## Build inputs

The kernel is built in `../ios-sweet/ios-sweet`:

- `xnu/out-guacamole/kernel.development.guacamole`
- `shim/out/guacamole.adt`
- `research/ipsw-x/d22ap.adt`

The copied local inputs are under `inputs/`; the base D22AP ADT is also copied
to `scripts/base-d22ap.adt` because the ADT wrapper runs from the assembled
build tree.

## Build sequence

```sh
python3 scripts/build-firmware.py
python3 scripts/build-payload.py
python3 scripts/build-bootimg.py \
  --fd uefi/Build/SurfaceDuo1Pkg/DEBUG_CLANGPDB/FV/SM8150_EFI.fd \
  --dtb inputs/uefi-prebuilt/guacamole.dtb
```

The payload step uses `scripts/make-guacamole-adt.py`, which drives the copied
`mkadt.py` guacamole profile. `scripts/build-bootimg.py` packs the full
`android-guacamole.dtb` (2,779,551 bytes; the first FDT is only 0x7bed2) the
same way the prebuilt image does. `unixnu bootimg` refuses that table because
it insists on a single FDT, so the local packer bypasses that check.

The firmware step calls unixnu's `firmware.build` with the exact Aloha
`PlatformBuildNoSb.py` package paths; it does not fetch the kernel tree.

`fastboot boot out/guacamole/boot/boot.img` tests it without writing a
partition.

## Open items

- Does the prebuilt Aloha NOSB FV expose the Android ramdisk as a FAT volume
  to BDS? If it does, a payload-only boot works. If not, rebuild the FV with
  the UniXNU/DarwinBoot INFs (the firmware step does that).
- The GPU/GMU blocker (ARC rail votes, CM3/RSCC) is kernel-side and is not
  fixed by the bootloader. See `../ios-sweet/ios-sweet/NOTES.md` and
  `docs/GPU-ADRENO640.md`.

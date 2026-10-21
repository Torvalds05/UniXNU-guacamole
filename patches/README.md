# External tree patches

The build depends on two upstream checkouts that are not vendored here.

| Patch | Baseline | Applies in |
|---|---|---|
| `unixnu-guacamole.patch` | `UniXNU/UniXNU` `b6ae99c` | `unixnu/` |
| `aloha-guacamole.patch` | `Project-Aloha/mu_aloha_platforms` `0b798128` | `uefi/` |

## Apply

```sh
git -C unixnu apply ../patches/unixnu-guacamole.patch
git -C uefi apply ../patches/aloha-guacamole.patch
```

`aloha-guacamole.patch` adds the `ShengBootMemoryDxe` driver and the
guacamole boot-image resources, so it creates files; apply it to a clean
checkout.

## What each patch changes

`unixnu-guacamole.patch`

- `Config.c` / `Internal.h` / `UniXNULib.inf` / `Main.c`: always connect
  controllers for the application host, count `SimpleFileSystem` volumes,
  report whether the `GUACESP` label is present, and expose the shim status.
  These are the diagnostics that found the invalid FAT32 and the missing
  volume.
- `Volume.c`: open config files relative to the volume root (strip leading
  backslashes). Some FAT/FV drivers reject `\EFI\...` from `Root->Open`.
- `scripts/unixnu/bootimg.py`: accept the Aloha BootShim header, whose size
  field describes the FV rather than shim+FV.
- `scripts/unixnu/firmware.py`: build `defines` after `fields` exists, and
  substitute `{uefi}`, `{edk2}` and `{tree}` in define values.

`aloha-guacamole.patch`

- `BootShim/BootShim.S`: alias `UEFI_BASE`/`UEFI_SIZE` to the driver's
  `FD_BASE`/`FD_SIZE`, and preserve the DTB pointer at `0x9FF92000` before
  firmware overwrites `0x9FFFF000`.
- `ShengBootMemoryDxe`: validate the DTB initrd as a `GUACESP` FAT32 volume,
  remove it from the GCD, publish it as a logical-partition block device,
  and fall back to scanning the UEFI memory map for the boot sector.
- Device DSC/FDF and `PlatformBuildNoSb.py`: add `ShengBootMemoryDxe`,
  `UniXNU`, `UniXNUDxe`, `DarwinBoot`, `FdtLib` and `UniXNULib` to the
  guacamole NOSB build.
- `Resources/`: guacamole boot-image configuration and `mkbootimg.py`.

## Refresh

After changing either external tree:

```sh
git -C unixnu diff > patches/unixnu-guacamole.patch
git -C uefi add -N Platforms/AndromedaPkg/Driver/ShengBootMemoryDxe Resources
git -C uefi diff --binary -- . ':(exclude)MU_BASECORE' > patches/aloha-guacamole.patch
git -C uefi reset -- Platforms/AndromedaPkg/Driver/ShengBootMemoryDxe Resources
```

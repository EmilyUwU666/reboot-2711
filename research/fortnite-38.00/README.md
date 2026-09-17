# 38.00 executable compatibility investigation

Status: **native port blocked; gameplay support not implemented**. No new launcher
or DLL binary is provided by this investigation. Existing version gates remain.

The uploaded `38.00.zip` contains `38.00.exe` plus an AppleDouble metadata file.
Only the game executable was inspected, as data; it was never executed.

| Evidence | Value |
| --- | --- |
| Executable bytes | 411,324,416 |
| SHA256 | `f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0` |
| Embedded release marker | `++Fortnite+Release-38.00-CL-47722112` |
| Engine text | `Unreal Engine 5.7.0` |
| Fixed file/product version | 5.7.0.0 |
| Architecture | AMD64 PE32+ |
| Entry RVA | `0x09cc5188` |
| Sections | 12; readable `.text`, import and exception directories present |

The image has readable machine code and a conventional entry sequence. This is
consistent with an unpacked/dumped image, but does not establish that Windows can
load it, that its imports/relocations are intact, or that it can reach the lobby.
The upload is not reproduced in the repository.

## Concrete native blocker

`inspect_executable.py` inventories all 50 literal-string `FindPattern` calls in
the current patched `SDK/Offsets.h`, joins adjacent C++ literals, and searches
the file-backed `.text` section. **None matches this 38.00 image.** In particular,
none of the three initial engine-version patterns matches. Expanding `IsTarget`
would not resolve SDK startup; the SDK needs that version function first.

As a comparison check, running the same scanner and exact SDK source against the
previously inspected 30.20 executable finds 14 matching patterns, including one
engine-version fallback. The 30.20 hash is
`a2c7fcb3087c90df73dd80f47022b184f8bdbfba6a4ff26e2c11a56513384b97`.
This comparison checks the scanner against real positive results; it does not
validate every signature's function identity or calling convention.

The inventory includes historical branches, not 50 required bindings for each
release. It excludes conditional-expression patterns, generated scans and
string-reference lookups. Candidate addresses, if found, must be independently
validated before calling them.

Current launcher validation accepts 19.xx–30.xx. Native build selection accepts
UE 5.0–5.5 and those same game releases. The reflection layouts, ProcessEvent
lookup, object/name access, allocator and server hooks have not been validated
for UE 5.7. The current final map fallback is Helios; it is not evidence for a
38.00 map. Do not expand these gates or reuse old addresses as a compatibility fix.

## LEGO / Festival

Juno, Pilgrim and Sparks substring references exist in this executable, including
UTF-16 references containing `JunoRootPlayspace`, `PilgrimQuickplayPlayspace` and
`SparksSongCatalog`. These are not proof that the old exact reflected classes,
playlists or assets are available. Neither mode is implemented by this audit.

## Work needed to enable a runtime profile

1. Establish replacement core bindings and UE 5.7 reflection layouts against
   this exact image, using disassembly and a matching runtime/reflection dump.
2. Validate loader startup and SDK initialization on Windows with the matching
   full 38.00 installation. An executable alone does not contain cooked maps or
   provide a usable object registry from a running game.
3. Resolve the actual map, playlist and server dependencies, then validate host
   startup, client join, spawning and replication before enabling a release.
4. Integrate LEGO world persistence and Festival content/state separately;
   neither follows automatically from Battle Royale startup.

## Reproduce

Apply `revision2.patch` and `seasons19-30.patch` to the pinned native source ZIP,
then run:

```sh
python research/fortnite-38.00/inspect_executable.py /path/to/38.00.exe \
  /path/to/patched-source/SDK/Offsets.h > evidence.json
```

The checked-in report records executable and SDK source hashes, PE sections,
marker locations and all signature results. Marker offsets are byte offsets;
signature candidates are RVAs. The checker is an offline investigation tool,
not an executable authenticity validator or a runtime compatibility test.

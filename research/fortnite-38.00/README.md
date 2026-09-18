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

## Version binding follow-up

`build-support/modern-version-binding.patch` adds a fallback version binding
without enabling gameplay. The exact `GetEngineVersion` name at RVA 0x158854c8
is paired with exec wrapper RVA 0x0c38d3ac in the registration table at RVA
0x11c5e3f0. Disassembly of the wrapper shows relative calls at offsets 40 and 62
to storage getter 0x090866a2 and version formatter 0x0029d7e2, passing format
argument 4. The getter initializes storage through 0x09cf8dc4, whose constructor
writes major/minor 5/7 and patch 0. The formatter reads version fields and builds
an FString. These observations establish the purpose of the candidate calls.

The implementation uses a unique wrapper signature and bounded relative-call
resolution rather than fixed addresses. Thirteen portable checks passed,
including actual-image resolution and negative tests. Calling the functions in
a running game remains untested. The existing gameplay compatibility gate still
rejects 38.00. Versions 31-37 have not been examined.

## Additional reflection port blockers

The `Conv_NameToString` registration name at RVA 0x1591cc97 is paired with exec
wrapper RVA 0x0457145e in the native table at RVA 0x11c43b10. Its call at RVA
0x0457154d reaches 0x00028d86, a candidate native name-to-string function. That
function transforms the stored name index before indexing a name-pool table.
This supports a distinct modern binding path; it is not permission to treat the
stored index as a plain name-pool index or copy older lookup offsets.

The same exec wrapper's compiled-in parameter path reads a next-field value at
`[property + 0x10]` and conditionally transforms a tagged pointer before updating
`FFrame + 0x88`. The current SDK's latest profile assumes a plain next-field
pointer at offset 0x18. That concrete mismatch needs a reviewed modern reflection
accessor rather than only a new signature or expanded season gate. These are
static observations from this exact image; broader UE5.7 layout claims and
runtime behavior are not established.

No name-conversion or field-access candidate from this subsection has been wired
into the gameplay DLL. A matching runtime object/reflection dump and a full game
installation are still needed to validate object traversal, function dispatch,
map startup, client join and replication.

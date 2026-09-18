## 38.00 backend validation and native diagnostic results

- Native diagnostic run: https://github.com/EmilyUwU666/reboot-2711/actions/runs/35281579517
  - Both Windows x64 DLLs compiled; 322 Windows checks passed (288 profile, 23 ProcessEvent, 11 resolver).
  - Offline checks against the supplied executable also passed, 13 total including fixture checks.
  - Diagnostic artifact: https://github.com/EmilyUwU666/reboot-2711/actions/runs/35281579517/artifacts/10522593756
- Backend validation run: https://github.com/EmilyUwU666/reboot-2711/actions/runs/35304253021
  - Existing smoke suite and 400 additional synthetic HTTP checks passed through release 38.
  - Includes profile/calendar consistency, discovery, local session destination and network-ID cookie roundtrip.
  - Artifact: https://github.com/EmilyUwU666/reboot-2711/actions/runs/35304253021/artifacts/10531351848
  - Backend runtime behavior is unchanged; this packages the pinned backend after broader validation.
- Review: https://github.com/EmilyUwU666/reboot-2711/pull/1

**These are diagnostic and HTTP-validation packages, not full Season 38 support.**
The main launcher still rejects 38.00. The executable investigation now identifies
an additional field-link offset/tagged-pointer mismatch and a candidate name
conversion function. Those modern reflection bindings remain unwired and need
runtime validation with a matching full game installation/object dump. No host
startup, client join, spawning, replication, LEGO or Festival gameplay was tested.

---

## 38.00 engine port — version binding diagnostic

The uploaded 38.00 image identifies CL47722112 and Unreal Engine 5.7.0. The
[executable investigation](research/fortnite-38.00/README.md) records its identity,
limitations and the old SDK signature mismatch. The game executable is not
included in this repository.

`build-support/modern-version-binding.patch` adds a unique, bounded fallback for
the engine-version getter/formatter observed in that image. Thirteen offline
checks passed, including resolution against the uploaded image. Existing version
selection remains 19.xx-30.xx / UE 5.0-5.5: **Season 38 gameplay is not enabled**.
Object lookup, reflection layouts, authentication and server hooks still require
porting and runtime validation. Releases 31-37 have not been verified.

The separate `build-modern-version-binding.yml` workflow creates diagnostic DLLs;
the standard Emilyfn launcher package is unchanged. No Fortnite game process was
run in this environment. LEGO and Festival remain unimplemented.

---

## 30.40 follow-up — LEGO and Festival SDK evidence

The public 30.40 reflection archive has now been downloaded, hash-verified and
inspected. Its internal release label is 30.40 and its build date is
2024-08-02T23:01:14.134Z. It contains 1,014 Juno, 101 Sparks and 169 Pilgrim
native class declarations, with concrete world-persistence, music-playback and
Festival gameplay references. Four mode playlist names are present as Athena
playlist objects. These facts refine the earlier assessment: Athena types are
shared by the modes; the missing work is mode startup, behavior, content and
service integration.

The [research notes](research/fortnite-30.40/README.md) and
[repeatable SDK checker](research/fortnite-30.40/inspect_sdk.py) preserve the
findings, source hashes and a generated evidence inventory. The SDK does not
establish a match to the uploaded executable, supply cooked mode assets or provide
a working loader. **30.40 launch, LEGO and Festival remain blocked/unimplemented.**
There is no new Windows package or DLL in this research update; Emilyfn 0.3.1 below
remains the latest compiled launcher.

---

## Emilyfn 0.3.1 — protected executable diagnosis

- **Windows download:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35183004733/artifacts/10480194219
- **Source and 30.40 analysis:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35183004733/artifacts/10480284128
- **Successful build:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35183004733
- Workflow commit: `10231fb8a958cfd15c9893e9bbf53543dbe4607f`
- Windows ZIP: 115,558,665 bytes; SHA256 `6a0a26c0521f06ddecf505eac73a27a80c80c3bd9783cdcd01be8b2703bb5a97`.
- Emilyfn.exe: 141,987,168 bytes; SHA256 `61aa1583f55e612221bc2467030d18e0c8d29564772ccb4606b68e33be573152`.

**223 Windows checks passed**, including 21 new startup checks. The compiled
preflight detector was also run locally against the actual uploaded executable.

The supplied executable has an Epic-launcher-only TLS startup stub. Its callback
displays the Epic Launcher message before terminating; its normal entry point and
import table are absent and the main payload is opaque. The three reported timeouts
occurred while loading authentication, before login or server SDK initialization.
The upload's exact release cannot be independently established from its readable
metadata. Its SHA256 is
`81302ab997ce7a4015ded4cd60cbbf94a4ecd5810c4b8a1c8a2147aec3053c98`.

The launcher now identifies this specific stub before starting the game and names
the DLL in other loader timeout messages. This is a diagnosis/preflight update:
it does not unpack the game or make 30.40 playable. Suppressing the message would
not restore the encrypted game code or its original entry point. No verified loader
for this exact file was established in the follow-up investigation.

**LEGO Fortnite and Fortnite Festival remain unimplemented.** The executable's
opaque payload provides no usable mode reflection/asset information. The current
server selects Helios/Battle Royale and uses Athena game-state/player classes.
A compatible readable/unpacked 30.40 executable or matching runtime/SDK dump,
followed by the relevant mode assets and backend implementation, is still needed.
The full findings are in `30.40-ANALYSIS.md` in the package. The permanent logo and
existing downloader remain included; native game DLLs are unchanged.

---

## Emilyfn 0.3.0.1 — permanent logo

- **Windows download:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35137386465/artifacts/10463422669
- **Source:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35137386465/artifacts/10463562306
- **UI previews:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35137386465/artifacts/10463362897
- **Successful build:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35137386465
- Workflow commit: `178f807e7502efcd8f4b532e1d819f8d677aa304`
- Windows ZIP: 115,553,708 bytes; SHA256 `4a87d4d58a21ccd2240eae576c4d021bbc7deaeaf49ab52c258b501ecd426a8e`.

Emily's new square artwork is the permanent default Windows executable/window icon
and in-app badge. The complete uploaded image is preserved in the source and fitted
into the icon without cropping. The FortForge window inherits the launcher icon.
Application version remains 0.3.0; Windows file version is 0.3.0.1.

**202 Windows checks passed.** The compiled icon and launcher preview were inspected.
This update changes branding; the native game DLLs are unchanged. Fortnite 30.40
runtime compatibility remains unverified, including the reported module timeout.

---

## Emilyfn 0.3.0 — public build downloader

- **Windows download:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35136606000/artifacts/10464100705
- **Source:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35136606000/artifacts/10463765998
- **UI previews:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35136606000/artifacts/10464100712
- **Successful build:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35136606000
- Workflow commit: `47891aa4b4d2f34a289d3064cc4671a27aae4dd0`
- Windows ZIP: 115,129,088 bytes; SHA256 `325e74bde7e830be56b4c7aa526655990f3a81cfdaf6054906f7209e30ff1c28`.
- Emilyfn.exe: 141,552,992 bytes; SHA256 `046f770fbaf06eac0ae3ac4be0bbf4dfd3c8dc8281c8af7ae8340dbb79eaa60d`.

Library now includes 69 FortForge PC entries covering 19.xx–30.xx, including
30.40 CL-35235494, plus 13 direct ZIP mirrors and a custom URL option. FortForge
opens in an embedded WebView2 window so its live queue can issue temporary download
links. Completed ZIPs are extracted safely, checked against the selected Fortnite
release and added to Library. Existing installations are never overwritten.

**202 Windows checks passed**, covering download cancellation, checksums, version
mismatch, truncated transfers, archive traversal/links/duplicates, cleanup and
preserving existing installations. The compiled Library UI was rendered and
inspected. A full 30.40 transfer is about 101 GB and was not downloaded in CI.
FortForge availability and format can change; RAR/7z builds are rejected. Microsoft
Edge WebView2 Runtime is required for FortForge downloads.

---

# Emilyfn launcher and Fortnite component build status

## Emilyfn 0.2.0 — automatic build detection and Discord Rich Presence

The custom Emilyfn launcher is built and packaged with the existing backend,
its Node runtime, the .NET desktop runtime, and all three Seasons 19–30 DLLs.

- **Windows download:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35070250967/artifacts/10435927666
- **Corresponding source:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35070250967/artifacts/10435668258
- **Compiled UI preview:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35070250967/artifacts/10436465016
- **Successful build:** https://github.com/EmilyUwU666/reboot-2711/actions/runs/35070250967
- Workflow commit: `5ae2ea684c749692d7850adb7817fad70c825478`
- Windows package: 114,604,083 bytes; ZIP SHA256 `e3088730227a329bb9830c5bb1d3f09cf86353a63b192c7d08f22e0aabcd3aa5`.
- Emilyfn.exe: self-contained Windows x64, 140,387,935 bytes; SHA256 `448610fd938493826f763c17971bcef79acd56c8d31cc930439dc943b15b2953`.
- Source package ZIP SHA256: `89ad839dc308b59388e48204b1333ba6b648775a8e0ee5ff209da601a0f1fc75`.

Logo update, 2026-09-16: Emily's supplied artwork is embedded as the Windows
executable/window icon at 16, 24, 32, 48, 64, 128 and 256 pixels. The in-app badge
uses a separate high-resolution image. File version: `0.2.0.0`. The uploaded JPEG
is preserved exactly in the source, with only its surrounding white margins
excluded when fitting the icon. The compiled icon and WPF preview were inspected.

Automatic detection runs on startup and is available under Library → Detect builds
or Scan a folder. It reads Epic installation records and actual executable release
tags, deduplicates builds and leaves ambiguous versions for manual selection.

Discord Rich Presence is optional. Create an application named Emilyfn at
https://discord.com/developers/applications, copy its public Application ID into
Settings, enable presence and save. Keep Discord desktop open with activity sharing
enabled. No bot token or client secret is required. Tests exercise a local mock
Discord pipe, reconnects and clearing activity; live Discord presence is unverified.

### Setup

1. Extract the **whole** Windows ZIP into a folder.
2. Open `Emilyfn.exe`.
3. Open **Library → Browse**, select the Fortnite installation folder, check the
   release number, and click **Add to library**.
4. Open **Play → Play Fortnite**. By default Emilyfn starts the backend and host,
   waits for the host to listen, and then starts the client.
5. Ready up in the lobby. **Copy join command** provides `open 127.0.0.1:7777`
   for the in-game console.

No separate DLL selection or runtime installation is needed. Keep Emilyfn open
while playing. Settings and diagnostic logs are under `%LOCALAPPDATA%\Emilyfn`.

### LEGO Fortnite and Fortnite Festival request — not implemented

The current package does not support these modes. Source review found the following
concrete blockers; no playlist toggle or guessed map path has been shipped as support:

- `Reboot2711/RuntimeProfile.h` routes 28.xx–30.xx hosts to `Helios_Terrain`.
- `Erbium/Erbium/Public/Configuration.h` selects the Battle Royale Solo playlist.
- `Erbium/FortniteGame/Private/FortGameMode.cpp` assumes Athena game state,
  playlist, player spawning, inventory and replication behavior.
- The inspected backend has no LEGO/Festival-specific implementation.

Implementation needs an exact Chapter 5 build and its mode assets/reflection data,
then mode-specific host startup, player spawning and backend contracts. LEGO world
creation/save/reload and Festival stage/song/session behavior need separate runtime
tests. First verify one release before extending to other Chapter 5 releases.
The 30.40 executable supplied on 2026-09-17 was inspected, but its protected
payload provides no readable mode reflection or asset data. See the 0.3.1
investigation above and the analysis included in its package. These modes remain
unavailable, and support for 31.xx is outside the existing 19.xx–30.xx package.

### Behavior and validation

- Custom WPF interface with Play, Library, Settings and Logs pages.
- Saved game installations, local display name, automatic host and headless host.
- Release parsing separates `Fortnite+Release-27.11` from engine `5.4.0`.
- Host and client must use the same selected installation and release.
- Authentication is loaded first; host/client modules wait for completed login.
- Startup timeouts, actual process exit codes and exported diagnostic ZIPs.
- Stop controls only close processes owned by Emilyfn; a pre-existing compatible
  backend and unrelated processes are left running.
- **123 checks passed on Windows**, including native x64 DLL loading with synthetic
  fixtures, launch ordering, host UDP ownership, failure cleanup, log redaction,
  and the actual bundled backend's first start, stop, restart and data retention.
  The new checks cover build scanning and Discord IPC.
- Build succeeded with one nullable-analysis warning in path normalization.
- The published executable ran its WPF preview successfully; the rendered UI was
  visually inspected. The Library and Settings previews were also inspected.

**Runtime limit:** the included Seasons 19–30 game components remain experimental.
The tests use a synthetic game process and do not establish Fortnite match
compatibility. The earlier host crash/client Connecting issue remains unverified
in live Fortnite gameplay.

Launcher source is stored in `build-support/emilyfn-{core,ui,tests}.patch` and
materialized by `.github/workflows/build-emilyfn.yml`. The source artifact contains
the complete readable C#/XAML source, build instructions, native tests, corresponding
DLL source archive, and backend JavaScript. Fortnite game files are not included.

---

## Seasons 19-30 - experimental candidate 1

The combined Windows package is compiled and available:

- DLL download: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34847063986/artifacts/10349075304
- Corresponding source: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34847063986/artifacts/10348805925
- Successful build: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34847063986
- Workflow commit: 4aab950a0d518b0b13e5c545f49a0568d27341f8
- Server/client: 0 errors, 2 existing wchar_t-to-char conversion warnings.
- Authentication: 0 errors, 0 warnings.
- Checks passed: 288 version/profile, 23 ProcessEvent lookup, 2,020 authentication scanner, 42 Windows authentication hook/URL.
- Backend checks passed: 27 original HTTP/WebSocket and 157 cross-season HTTP/profile checks, covering all twelve seasons and switching back to Season 19.
- DLL ZIP SHA256: 60f623829b8939eadb1d3a31f8f161ac5b7ade5a166d8b6d17a0aeade020b479

| Launcher Internal files setting | DLL | SHA256 |
| --- | --- | --- |
| Authentication patcher | Reboot-S19-S30-Auth.dll | 878c3d6141e2ca9bf0b140f02f38d59393dbf15b6b954ab387c31387eac70ce3 |
| Unreal engine patcher | Reboot-S19-S30-Client.dll | 246b36a8a49fa7681ae039d8bf9424edd63b82194f9a90e42ecd005a1d0c1dfa |
| Custom game server | Reboot-S19-S30-Server.dll | 032ea3458f0a84fceeb158d20d03e7b97511e05004fd0087051421c43d9bced1 |

Close both game instances, extract the package, then select these three DLLs.
Keep the portable backend below running with Backend type Local and port 3551.
Both game instances must use the same exact Fortnite version/content. This
does not provide cross-version multiplayer.

The server/client now accept canonical 19.xx-30.xx release labels with UE
5.0-5.5, retain the actual release instead of forcing 27.11, select each chapter's
Battle Royale map, and share the existing reflection/replication policy.
Additional diagnostics record the selected build/map/replication. The Season
29+ Iris inventory configuration and required FName constructor are checked
before use. The authentication overlay changes its name and diagnostic paths;
it retains the earlier candidate's hook/ABI assumptions.

This enables existing code paths; it does not validate every native offset or
gameplay feature. Upstream documents partial support from 20.00 through 30.00.
Later 30.xx updates are accepted experimentally with an additional diagnostic,
without new verified offsets. No Fortnite executable was run during this build.
Full gameplay and the earlier 27.11 client loading stall/host crash remain
unverified. SETUP.md and COMPATIBILITY.md inside the package explain the scope.

The older 27.11 artifacts below remain available for rollback.

## Portable backend - candidate 1

A ready-to-run Windows x64 backend is available. It includes Node.js, all installed
dependencies, complete JavaScript source, licenses, and START-BACKEND.cmd.

- Download: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34817850310/artifacts/10337212644
- Successful build: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34817850310
- Workflow commit: dc15344b6d9c0b0c9e8e0f946931a04227550813
- Upstream: Lawin0129/LawinServer 7f0f26d7a772c6122c42b1783fd75f497e86d3a9
- Runtime: official Node.js 24.21.0, Windows x64; download SHA256 verified.
- Validation: 27 HTTP/WebSocket checks passed on Windows with the packaged runtime.
- Artifact ZIP: 52,564,187 bytes; SHA256 c881dc4fc12b09f2cbbda4b02812a0ad73a7a339ace9d96de58490f754b925e4.
- Files include BUILD-INFO.txt and per-file SHA256SUMS.txt.

The older embedded backend lacks the discovery access-token route repeatedly
requested in the supplied 27.11 logs. This package uses upstream's implemented
route and updated v1/v2 discovery responses. It includes the correct nonempty
manifest/chunk files and fixes the observed XMPP configuration mismatch by
accepting local connections on both 80 and 8080. HTTP stays on 3551 for the
existing authentication DLL. Listeners bind to loopback.

To use: close both Fortnite instances and stop the launcher's embedded backend.
Extract the entire download into a writable folder, then double-click
START-BACKEND.cmd and leave that window open. In Reboot Launcher choose Backend
type Local and port 3551, then Check server. Keep the existing Auth, Client,
and Server DLL selections. Start the separate host and playing client; test
with open 127.0.0.1:7777 from the playing client's console. Full instructions
and rollback steps are in BACKEND-SETUP.md inside the package.

This addresses confirmed backend response failures. It is not proof that the
client's CONNECTING stall or the reported host crash is fixed. The latest
paired game logs showed a connection timeout after the host log stopped.
Gameplay must still be confirmed on the user's installation.

## Authentication DLL - candidate 1

Reboot-27.11-Auth.dll compiled successfully with MSVC v143 on Windows Server 2022.

- Build: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34794929472
- Workflow commit: ddc4f497c905d75ba6b7ad46dc1994b515742b8f
- Compiler result: 0 errors, 0 warnings.
- Tests: 2,020 scanner checks and 42 Windows hook/URL checks passed.
- Validated format: AMD64 PE32+ DLL; 189,952 bytes.
- DLL SHA256: f28398cf8650f244f835670911e1a8fb19b9ff31678ab1a11cc1330433f85b87
- DLL package: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34794929472/artifacts/10329891308
- Corresponding source: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34794929472/artifacts/10329157898

Select Reboot-27.11-Auth.dll under Settings > Internal files > Authentication patcher. It targets an existing backend at http://127.0.0.1:3551. Extract the ZIP first; no copy into the Fortnite installation is required. AUTH-SETUP.md and the upstream BSD 3-Clause LICENSE are included.

This candidate is based on plooshi/Tellurium commit 8750678312c011888b82878fb1d011b97b33fff5, with bounded scanners and retry budgets, Windows unwind lookup with the upstream prologue fallback, checked table writes, URL bounds fixes, and startup diagnostics. The workflow pins upstream and applies build-support/auth-candidate1.patch.

The earlier launcher log showed Cobalt failing at CurlSetOptAddr before the client/server DLLs were injected. The subsequent Sinum attempt displayed FindPointerRef return nullptr. These were authentication startup failures. Later supplied logs show the Tellurium candidate reaching READY, successful login, and injection of the client/server DLLs. The playing client now reaches the lobby. The candidate still retains upstream request-object ABI assumptions; lobby login does not establish match compatibility.

After one launch, open %TEMP%/Reboot-27.11-Auth-startup.log. It records stages and relative addresses without credentials or request URLs. READY means hook installation succeeded; it does not mean login completed.

## Client/server DLLs - revision 2

Revision 2 compiled successfully with MSVC on Windows Server 2022.

- Build: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34776838190
- Workflow commit: 5bc7ba30d9158975a0a35ef5318a057d484762ce
- Compiler result: 0 errors, 2 warnings.
- Tests: 23 Windows ProcessEvent lookup checks and 25 version-parser checks passed.
- DLL package: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34776838190/artifacts/10323337616
- Corresponding source: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34776838190/artifacts/10323238257

Outputs are Reboot-27.11-Server.dll and Reboot-27.11-Client.dll. The build script validated both x64 PE DLLs and generated SHA256SUMS.txt. Keep the paired DLLs together.

The earlier screenshots reported missing ProcessEvent or Object class lookup failures. Later supplied logs show ProcessEvent resolving at virtual-table index 77 and successful SDK initialization. Those startup failures are not the current stopping point. Keep the startup logs if either error reappears.

The build string 5.4.0-29739262+++Fortnite+Release-27.11 contains engine version 5.4.0 and game release 27.11. The two versions are separate fields.

The original ZIP remains the reproducible client/server baseline. The client/server workflow applies build-support/revision2.patch and packages matching source. Its older VALIDATION.md and SETUP.md predate the completed builds; this status record supersedes their build-status claims.

Observed runtime progress: backend login reaches the lobby, a host listens on port 7777, and one earlier attempt records a successful player join. A later client attempt times out before completing the handshake; the paired host log stops before that connection attempt. The user also reports a host crash, without a matching crash dump yet. The latest fully loaded CONNECTING screen is the playing client. Multiplayer gameplay and the host-crash cause remain unresolved. Compilation and backend checks do not establish full game compatibility.

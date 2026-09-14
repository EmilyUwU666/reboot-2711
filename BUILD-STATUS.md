# Fortnite 27.11 build status

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

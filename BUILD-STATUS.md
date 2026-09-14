# Fortnite 27.11 build status

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

The earlier launcher log showed Cobalt failing at CurlSetOptAddr before the client/server DLLs were injected. The subsequent Sinum attempt displayed FindPointerRef return nullptr. These are authentication startup failures. The Tellurium candidate is compiled but has not yet been run on the user's Fortnite executable. It retains upstream request-object ABI assumptions and does not establish working authentication or gameplay.

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

The first package stopped because ProcessEvent was not located in the UObject virtual table. Revision 2 changes that lookup and adds diagnostics, but the user's revision-2 screenshot reports: Object class was not found in GObjects. That earlier SDK initialization failure remains unresolved. The authentication candidate does not fix it. If it reappears after login, collect %TEMP%/Reboot-27.11-Client-startup.log or the corresponding Server log.

The build string 5.4.0-29739262+++Fortnite+Release-27.11 contains engine version 5.4.0 and game release 27.11. The two versions are separate fields.

The original ZIP remains the reproducible client/server baseline. The client/server workflow applies build-support/revision2.patch and packages matching source. Its older VALIDATION.md and SETUP.md predate the completed builds; this status record supersedes their build-status claims.

Backend login, multiplayer and Fortnite gameplay compatibility remain unverified. Compilation and synthetic tests do not establish runtime compatibility.

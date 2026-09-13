# Fortnite 27.11 build status

Revision 2 compiled successfully with MSVC on Windows Server 2022.

- Build: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34776838190
- Workflow commit: 5bc7ba30d9158975a0a35ef5318a057d484762ce
- Compiler result: 0 errors, 2 warnings.
- Tests: 23 Windows ProcessEvent lookup checks and 25 version-parser checks passed.
- The build script checked that both outputs are x64 PE DLLs and generated SHA256SUMS.txt.
- DLL package: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34776838190/artifacts/10323337616
- Corresponding source: https://github.com/EmilyUwU666/reboot-2711/actions/runs/34776838190/artifacts/10323238257

Outputs are Reboot-27.11-Server.dll and Reboot-27.11-Client.dll. Replace both together after closing Fortnite.

The first package stopped on the user's installation because ProcessEvent was not located in the UObject virtual table. Revision 2 avoids the inferred default-object field offset during this lookup, recognizes bounded jump stubs, and logs the build string and detailed lookup results. It retains the upstream Season 27 signature and rejects unresolved/ambiguous matches. This is a candidate fix; successful startup on the user's executable is not yet confirmed.

The original ZIP is retained as the reproducible baseline. The workflow applies build-support/revision2.patch and packages the resulting corresponding source. The original VALIDATION.md predates these builds; this record and REVISION-2.md describe the current status.

If startup still fails, collect %TEMP%/Reboot-27.11-Client-startup.log and, when present, %TEMP%/Reboot-27.11-Server-startup.log. Revision 2 logs build and lookup data without requiring a game executable upload.

Backend login, multiplayer and Fortnite gameplay compatibility remain unverified. Compilation and synthetic tests do not establish runtime compatibility.

# Guarded game-thread diagnostic: CL47722112

The user's 2026-09-23 live report passed the read-only profile: 153,497 names,
631 owners, 2,030 properties and 495 function records, with no rejected chains
or bindings. A skipped object-table slot remains in the coverage count.

The supplied later capture's ThreadNames stream identifies thread 31688 as
GameThread, distinct from render, RHI and worker threads. That historical ID is
not reused: the launcher queries live Windows thread descriptions and requires
exactly one GameThread in the selected process.

The new button installs a WH_GETMESSAGE hook for that single thread. A random,
per-request named mapping, PID/thread identity, creation timestamp and deadline
bind the callback to the test. No global hook, arbitrary function interface or
code patch is installed. The hook is removed after completion or timeout;
already-running callbacks are reported separately and block repeat tests in
that game instance. This is experimental native execution, not a gameplay release.

The callback confirms its process/thread IDs and GameThread description. This
is a Windows thread identity check, not proof of Unreal's dynamic task-tag state.
Only one fixed test can execute: ActorComponent.GetOwner on its initialized
Default__ActorComponent. Name/class/outer identity, CDO flags, storage and parameter
sizes, native-entry bytes and dispatch slot are checked again in the callback.
The native exec wrapper at RVA 0x432782A returns the pointer at object+0xA8;
the dispatched result must equal a direct read of that field. SEH failure,
unchanged sentinel, differing result, missing target and timeout are distinct.

The supplied capture has GetOwner metadata but no Default__ActorComponent.
It therefore cannot serve as a successful function-call test: the callback can
be observed while the actual call is skipped. The diagnostic never constructs
an object or calls GetOwner on a substitute UObject.

Output: dispatch-test.json, with GameThreadCallbackObserved,
FunctionCallsAttempted, ControlledGetOwnerPassed and GameplayReady (always false).
The normal launcher/backend/gameplay DLL compatibility gates remain unchanged.

Build: materialize through emilyfn-thread-dispatch.patch, compile Probe.cpp using
MSVC x64 (/std:c++17 /EHsc /MT /LD, user32.lib), then pass -DiagnosticDllDirectory
to launcher/build.ps1. The workflow packages the DLL and its SHA-256 sidecar.

Windows fixtures exercise cross-process callback delivery, matching IDs, missing
and invalid targets, unpumped-queue timeout, wrong-process thread refusal and
exact-game-image rejection. They do not execute Fortnite functions.

API references:
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowshookexa
- https://learn.microsoft.com/en-us/windows/win32/winmsg/getmsgproc
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unhookwindowshookex
- https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getthreaddescription

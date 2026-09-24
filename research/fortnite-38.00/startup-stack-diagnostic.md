# Callback startup-stack diagnostic, CL47722112

The 2026-09-23 20:04 UTC user report confirms the corrected registry live:
23,051 matching object indices, no invalid slots, 633 populated owners,
2,032 properties and 497 function records. The GameThread callback completed,
the hook was removed, and the game remained alive. No Unreal function ran:
Default__ActorComponent still does not exist in the selected process.

The existing later capture has only six non-metadata objects: the Object,
Field, Struct, GCObjectReferencer and SlateThemeManager default objects plus
one GCObjectReferencer instance. This is evidence of incomplete startup,
not a valid ActorComponent receiver.

Offline examination of the GameThread context and captured memory yielded a
coherent x64 unwind chain. Fourteen direct call sites match their preceding
frame's function entry; one virtual-call frame remains only structurally
consistent. The thread-list stack descriptor has RVA zero in this full-memory
capture and must not be read as file offset zero. The unwind used Memory64
stack bytes; the snapshot is not guaranteed to be atomic.

The observed chain includes initialization function ranges 0x21AD6D4–0x21B3AD7,
0x201A730–0x201ADD1 and 0x8B84524–0x8B85AC9. Nearby live stack text refers to
FortnitePreLoadScreen.UpdateFinishing, and the innermost path parses a GUID.
The 0x8B84524 function references PatchGUID/PatchGUIDVersion. These observations
point to early startup/preload work, but do not establish the reason for waiting
or justify changing startup flags, constructing an object or skipping a guard.

The next diagnostic adds CaptureStackBackTrace inside the already verified
single-thread callback. It records at most 48 frames, then exports only return
addresses inside the selected main image as relative offsets. It never exports
raw stack memory, arguments, absolute pointers or frames from other modules.

Protocol version 2 uses a distinct registered message and mapping name, 1,024
mapping bytes, and a 552-byte shared structure. The host validates counts and
image bounds before serializing. A callback that timed out or is still running
does not expose partially written frames. Empty, truncated and exceptional
stack captures remain distinct from GetOwner success or gameplay support.
The trace describes callback delivery, not the GetOwner execution stack; native
callback boundaries or missing unwind information can omit callers.

The small dispatch-test.json report has format 2 and adds Callback fields:
CapturedStackFrames, GameFrameRvas, StackCapacityReached and StackCaptureException.
This is intended to diagnose startup without another full-memory upload.

Windows tests require the no-target callback to return a real trace containing
the fixture's main image, reject out-of-image results, and return no frames for
a cancelled callback. The existing invalid-target, timeout, identity, exact-image
and process-survival checks remain in place. Synthetic tests do not execute
Fortnite functions.

Materialize emilyfn-startup-stack.patch after emilyfn-runtime-registry.patch.
API reference: https://learn.microsoft.com/en-us/windows/win32/debug/capturestackbacktrace

# Name-block read failure reporting

After the patcher startup test build, the user reported `Name crosses block
boundary`. No new failing memory bytes or report were provided. This message
alone cannot distinguish an incomplete live read from a decoder/layout issue.
It is not evidence that a particular name or block can safely be skipped.

The previous live and dispatch report handlers caught IOException, but not
InvalidDataException. The decoder throws InvalidDataException, which does not
derive from IOException; this escaped to the UI before report serialization.
Both handlers now explicitly catch it and save the failed report.

The bounded reader retries up to three complete read-only verification attempts,
clearing the page cache each time. It checks raw name-pool and runtime-registry
boundary counters around every attempt and accepts only a decoded result with
unchanged counters. A decode failure is retried even when counters are unchanged:
unchanged allocation counters do not establish an atomic snapshot or completed
entry publication. The existing overall 90-second deadline remains in force.
Persistent malformed data and continuously changing counters still fail closed.
All existing callback/function-target gates remain in place.

Each attempt records whether decoding completed, whether boundary counters
matched, and any validation error. Name-boundary errors now include block number,
entry offset, numeric header, required/available bytes and current-block status;
they do not export name contents. Read-only startup-patcher observations are
collected before name decoding and included at the report top level even when
binding evidence could not be completed. GameAliveAfterProbe is null when no
callback was attempted, rather than falsely implying that verification killed
the game.

Fixture checks cover fresh-cache recovery, rejection of a decoded-but-changing
snapshot, repeated corrupt data, three-attempt bounds, deadline propagation and
precise truncated-entry diagnostics. The earlier supplied capture still passes
name, registry, reflection and startup-patcher verification. Whether retries
resolve this user's new failure requires a fresh live report; no decoder format
has been guessed or relaxed.

Materialize emilyfn-name-read-recovery.patch after emilyfn-patcher-startup.patch.

# Fortnite 30.40: LEGO and Festival reference investigation

Inspected 2026-09-17. **This is implementation research, not playable mode support
or a fix for the supplied executable's Epic Launcher startup stub.** Emilyfn's
current Windows package remains 0.3.1; no native DLL was changed by this audit.

## Source and version confidence

The public [30.40 reflection archive](https://github.com/KiNmiCallbackHeadList/fortnite-sdk/blob/main/Fortnite-Release-30.40.rar)
contains 3,337 files (169,840,448 uncompressed bytes), including generated class
declarations, a name dump and an object dump. The download was checked against
GitHub's blob ID before extraction:

- Archive: `Fortnite-Release-30.40.rar`, 23,673,295 bytes.
- SHA256: `bc16ca5a81c7dd16a3ea7529af79308c0f25f0c9e924e9df63b59e7c555dcbb7`.
- Git blob: `4390fdae7d3c0f2557742a348a467a38af83579e`.
- Internal `version.txt`: `Fortnite-Release-30.40`.
- Internal `build_date`: `2024-08-02T23:01:14.134Z`.

The internal label corroborates the filename. It does not bind this dump to the
user's executable: no executable hash or exact changelist is supplied in the
version metadata. A targeted search of the version, include and name files found
no `35235494` marker. The public repository README still names 30.30 and should
not be used as the version authority for this archive.

The user's protected executable has SHA256
`81302ab997ce7a4015ded4cd60cbbf94a4ecd5810c4b8a1c8a2147aec3053c98`.
This audit neither establishes the SDK's function addresses for that executable
nor supplies its unpacked code, imports or entry point. The generated report
deliberately contains no native function addresses or memory-write offsets.

## What was actually found

There are **1,014 Juno**, **101 Sparks**, and **169 Pilgrim** native class
declarations under those module prefixes. The checker records 16 relevant class
definitions and confirms that all 16 also occur as `Class` entries in the object
dump. Counts concern this snapshot, not every asset in an installed game.

| Area | Observed reference | Implication for implementation |
| --- | --- | --- |
| LEGO world selection | `JunoWorldManagerSubsystem`, `JunoWorldManagementHandler_WorldArbitrationService` | World selection and its service contract require implementation. |
| LEGO persistence | `JunoWorldPersistenceSubsystem`, `JunoPlayerPersistenceComponent` | World and player saves have separate handlers. |
| LEGO startup | `JunoRootPlayspace`, `JunoPlayerSpawningComponent`, `JunoWorldReadinessQueryComponent` | World readiness, persistence data and player spawning must be coordinated. |
| Festival shared music | `SparksMusicPlayspace`, `SparksSongPlayerSubsystem`, `SparksMediaStreamer` | Music playback has clock, MIDI, media and player state dependencies. |
| Festival rhythm gameplay | `PilgrimQuickplayPlayspace`, `PilgrimQuickplayStateMachine`, `PilgrimQuickplayState_Loading` | Sparks playback alone does not implement the rhythm game. |
| Festival catalog | `SparksSongCatalog`, `PilgrimSongCatalog` | Catalog retrieval and playable song/chart content must be supplied. |
| Festival Battle Stage | `PilgrimBattleStageGameManagerComponent` | Match initialization, setlists and band elimination add another mode-specific path. |

These package strings are present in `names_dump.txt`:

| Research label | Playlist package reference | Map package reference |
| --- | --- | --- |
| LEGO Fortnite | `/JunoGame/Playlists/Playlist_Juno` | `/JunoGame/Maps/Juno_World_Inception` |
| Festival Quickplay | `/SparksLobby/Playlist/Playlist_PilgrimQuickplay` | `/PilgrimCore/Maps/PilgrimCoreMap` |
| Festival Battle Stage | `/SparksLobby/Playlist/Playlist_PilgrimBattleStage` | No launch map established by this audit |
| Festival Jam | `/SparksLobby/Playlist/Playlist_FMClubIsland` | `/SparksCommon/Maps/Sparks_Festival_Island` |

All four playlist short names also occur as `FortPlaylistAthena` objects in the
object dump. Associating each short object with the similarly named package is
an inference; the dump does not give complete package ownership for these objects.
The map strings are references, not verified launch destinations. This source
contains no cooked map, playlist, Blueprint, chart or audio asset bytes. It does
not establish that the user's installation contains or can mount those packages.

## Correction to the earlier server assessment

Using Athena types is not by itself proof that an implementation cannot support
these modes. This dump exposes an `AFortPlayerControllerAthena` owner on
`JunoRootPlayspace`, an `AFortPlayerStateAthena` parameter on
`PilgrimQuickplayPlayspace.SetPlayerStateTeamIndex`, and Athena playlist objects
for all four playlist names. Shared networking and player infrastructure may be
reusable; that is an implementation possibility, not a tested compatibility claim.

The concrete gap in Emilyfn's current native server is its Battle Royale behavior:

- `Reboot2711/RuntimeProfile.h` selects `Helios_Terrain` for Chapter 5.
- `Erbium/Erbium/Public/Configuration.h` selects Battle Royale Solo.
- `FortGameMode.cpp` installs its own match-readiness, playlist, spawning, loot,
  aircraft and match logic. `SetupPlaylist` can fall back to Solo, and
  `ReadyToStartMatch_` runs the BR setup path.
- There is no integration for the world/persistence or Festival state systems
  identified above in the inspected native source.

Changing only the map and playlist would leave these hooks and missing services
in place. Hard-coding addresses from an unbound dump or forcing readiness flags
would not establish a working implementation.

## Next implementation gates

1. Obtain a compatible, readable 30.40 game image or a matching runtime image
   with module/build identity. Establish native initialization on Windows. The
   supplied startup stub prevents reaching this stage; the SDK archive is not a
   loader and cannot replace the game image.
2. Inventory the installed cooked assets and confirm the playlist's actual
   game mode, default player classes, map dependencies and game-feature setup.
   Load the intended assets and resolve reflected classes/functions in that
   running build before adopting any binding.
3. Separate BR hook installation from mode startup. Preserve native mode state
   and replication where they work; implement only the missing local services
   against observed contracts. Reuse of Athena infrastructure must be checked.
4. For LEGO, verify world creation, join/spawn, save, stop and reload with retained
   inventory/buildings. For Festival, first verify one local test song and chart,
   transition from loading to gameplay, playback timing and results; test Jam and
   Battle Stage separately. Multiplayer requires additional replication checks.

## Reproduce the reference inventory

Download the linked archive, check its SHA256 above, and extract it with a RAR
reader. Do not execute archive contents. Run with Python 3.11 or newer:

```sh
python research/fortnite-30.40/inspect_sdk.py \
  /path/to/Fortnite-Release-30.40 \
  --output /path/to/mode-evidence.json
```

The checker reads data only. It rejects a different internal release label,
records absent targets instead of treating search strings as found assets, and
distinguishes name references from object evidence. It records SHA256 hashes of
all 59 inspected inputs, source lines, class bases, reflected member names and
playlist evidence. It never changes the launcher, invokes a game function or
marks a mode supported. Archive provenance is verified separately from the input
directory; hashes in the report let subsequent runs compare the extracted files.

The checked-in [mode-evidence.json](mode-evidence.json) was generated from the
verified archive. It records all 16 selected classes and all four playlist name
and object pairs. This is source inspection, not a Windows gameplay test.

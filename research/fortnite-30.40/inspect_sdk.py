#!/usr/bin/env python3
"""Inventory an extracted reflection dump; never execute it or enable a mode."""

import argparse
import hashlib
import json
from pathlib import Path
import re


CLASSES = {
    "JunoWorldManagement.JunoWorldManagerSubsystem",
    "JunoWorldManagement.JunoWorldManagementHandler_WorldArbitrationService",
    "JunoGameNative.JunoWorldPersistenceSubsystem",
    "JunoGameNative.JunoRootPlayspace",
    "JunoGameNative.JunoPlayerSpawningComponent",
    "JunoGameNative.JunoPlayerPersistenceComponent",
    "JunoGameNative.JunoWorldReadinessQueryComponent",
    "SparksCMS.SparksSongCatalog",
    "SparksMusicPlayspaceRuntime.SparksMusicPlayspace",
    "SparksSongPlayerRuntime.SparksSongPlayerSubsystem",
    "SparksSongPlayerRuntime.SparksMediaStreamer",
    "PilgrimCoreRuntime.PilgrimSongCatalog",
    "PilgrimQuickplayRuntime.PilgrimQuickplayPlayspace",
    "PilgrimQuickplayRuntime.PilgrimQuickplayStateMachine",
    "PilgrimQuickplayRuntime.PilgrimQuickplayState_Loading",
    "PilgrimBattleStageRuntime.PilgrimBattleStageGameManagerComponent",
}

# These are search targets, not launch settings. Each needs evidence in the input.
PLAYLISTS = {
    "/JunoGame/Playlists/Playlist_Juno": "LEGO Fortnite",
    "/SparksLobby/Playlist/Playlist_PilgrimQuickplay": "Festival Quickplay",
    "/SparksLobby/Playlist/Playlist_PilgrimBattleStage": "Festival Battle Stage",
    "/SparksLobby/Playlist/Playlist_FMClubIsland": "Festival Jam",
}
PACKAGES = {
    "/JunoGame/Maps/Juno_World_Inception",
    "/JunoGame/CoreClasses/Juno_GameMode",
    "/JunoGame/CoreClasses/Juno_GameState",
    "/JunoGame/CoreClasses/Juno_PlayerController",
    "/JunoGame/CoreClasses/Juno_PlayerState",
    "/JunoGame/CoreClasses/BP_Juno_PlayerPawn_RealPlayer",
    "/SparksCommon/Maps/Sparks_Festival_Island",
    "/SparksCommon/Maps/Sparks_Festival_Pilgrim_Props",
    "/PilgrimCore/Maps/PilgrimCoreMap",
}
CLASS = re.compile(
    r"^// Class (?P<name>\w+\.\w+)\n"
    r"// Size: [^\n]+\nstruct (?P<type>\w+) : (?P<base>\w+) \{",
    re.MULTILINE,
)
OBJECT = re.compile(r"^\[\d+\]\s+<[^>]+>\s+<[^>]+>\s+(\w+) (.+)$")
NAME = re.compile(r"^\[\d+\]\s+(.+)$")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inspect(root):
    root = root.resolve()
    files = {}

    def source(name):
        path = root / name
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f"Missing input or path outside SDK root: {name}")
        files[name] = digest(path)
        return path

    version = source("version.txt").read_text(encoding="utf-8-sig")
    metadata = dict(line.split(": ", 1) for line in version.splitlines() if ": " in line)
    if metadata.get("version") != "Fortnite-Release-30.40":
        raise ValueError("The dump does not identify itself as Fortnite-Release-30.40")

    counts = {key: 0 for key in ("Juno", "Sparks", "Pilgrim")}
    classes = {}
    for path in sorted((root / "dump").glob("*_classes.h")):
        if not path.name.startswith(tuple(counts)):
            continue
        relative = path.relative_to(root).as_posix()
        text = source(relative).read_text(encoding="utf-8-sig")
        matches = list(CLASS.finditer(text))
        for i, match in enumerate(matches):
            name = match["name"]
            for prefix in counts:
                if name.startswith(prefix):
                    counts[prefix] += 1
            if name not in CLASSES:
                continue
            if name in classes:
                raise ValueError(f"Ambiguous duplicate class: {name}")
            stop = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            block = text[match.start():stop]
            fields = re.findall(r"^\s+[^\n;]+?\s+(\w+)(?:\[.*?\])?; // 0x", block, re.M)
            functions = re.findall(r"// Function " + re.escape(name) + r"\.(\w+)", block)
            classes[name] = {
                "reflection_name": name,
                "cpp_type": match["type"],
                "cpp_base": match["base"],
                "source": relative,
                "line": text.count("\n", 0, match.start()) + 1,
                "fields": [field for field in fields if not field.startswith("pad_")],
                "functions": functions,
                "object_dump_lines": [],
            }

    name_hits = {name: [] for name in sorted(PACKAGES | PLAYLISTS.keys())}
    with source("names_dump.txt").open(encoding="utf-8-sig") as stream:
        for line, value in enumerate(stream, 1):
            match = NAME.fullmatch(value.strip())
            if match and match[1] in name_hits:
                name_hits[match[1]].append(line)

    playlist_objects = {Path(path).name: [] for path in PLAYLISTS}
    with source("objects_dump.txt").open(encoding="utf-8-sig") as stream:
        for line, value in enumerate(stream, 1):
            match = OBJECT.fullmatch(value.strip())
            if not match:
                continue
            kind, name = match.groups()
            if kind == "Class" and name in classes:
                classes[name]["object_dump_lines"].append(line)
            if kind == "FortPlaylistAthena":
                for leaf in playlist_objects:
                    if name == leaf + "." + leaf:
                        playlist_objects[leaf].append(line)

    return {
        "schema_version": 1,
        "purpose": "reference inventory; not a runtime support profile",
        "dump_metadata": metadata,
        "exact_executable_match": "not established",
        "gameplay_support": "not implemented or tested by this audit",
        "native_class_counts_by_module_prefix": counts,
        "classes": [classes[name] for name in sorted(classes)],
        "missing_requested_classes": sorted(CLASSES - classes.keys()),
        "playlists": [
            {
                "research_label": label,
                "package_name": path,
                "name_dump_lines": name_hits[path],
                "short_object_name": Path(path).name + "." + Path(path).name,
                "short_object_class": "FortPlaylistAthena" if playlist_objects[Path(path).name] else None,
                "object_dump_lines": playlist_objects[Path(path).name],
                "package_to_object_link": "candidate inferred from matching short names",
                "asset_bytes_validated": False,
            }
            for path, label in sorted(PLAYLISTS.items())
        ],
        "package_references": [
            {"name": name, "name_dump_lines": name_hits[name], "asset_bytes_validated": False}
            for name in sorted(PACKAGES)
        ],
        "input_sha256": dict(sorted(files.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sdk_root", type=Path, help="Extracted directory containing version.txt and dump/")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = inspect(args.sdk_root)
        if args.output.resolve().is_relative_to(args.sdk_root.resolve()):
            raise ValueError("Write the report outside the source SDK directory")
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f"SDK inspection failed: {error}\n")
    print(f"Recorded {len(report['classes'])} requested classes; "
          f"{len(report['missing_requested_classes'])} absent. No gameplay support enabled.")


if __name__ == "__main__":
    main()

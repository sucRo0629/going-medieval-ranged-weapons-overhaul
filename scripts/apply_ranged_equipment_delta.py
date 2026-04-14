#!/usr/bin/env python3
"""
Ranged Equipment + WQS regeneration entry point (canonical for this Mod).

Calls ``tools/regenerate_ranged_from_vanilla.run_regeneration`` (full vanilla
``Equipment`` entries for the seven bow/crossbow ids, Marksman policy, role
post-pass, TwoHandBow WQS policy (shared by all bows; ``weaponType`` must stay a
vanilla enum), TwoHandCrossbow damage/attackSpeed flattening and gentle
``rangeMultiplier`` ramp).

Then applies **sling** overrides: vanilla deep copy + ``SLING_COMBAT`` primary
field merge only (legacy mod design for slings).

The old behaviour that replaced entire Equipment rows with a flat
``{id, damage, range, ...}`` stub caused merge/runtime issues; that path is
removed.

Usage (from Mod folder):

  python scripts/apply_ranged_equipment_delta.py
  python scripts/apply_ranged_equipment_delta.py --items-dir "D:/.../StreamingAssets/Items"
  python scripts/apply_ranged_equipment_delta.py --dry-run

Environment: ``GOING_MEDIEVAL_ITEMS`` may point at the ``Items`` folder.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from copy import deepcopy
from pathlib import Path

SLING_IDS = ("sling", "sling_staff")

# primaryWeaponMode fields to merge onto vanilla sling entries (mod design).
SLING_COMBAT: dict[str, dict[str, float]] = {
    "sling": {
        "damage": 16,
        "range": 13,
        "attackSpeed": 5.25,
        "precision": 0.97,
        "precisionFalloff": 0.02,
        "ignoresArmor": 0.25,
    },
    "sling_staff": {
        "damage": 21,
        "range": 16,
        "attackSpeed": 7.0,
        "precision": 0.97,
        "precisionFalloff": 0.02,
        "ignoresArmor": 0.35,
    },
}

PRIMARY_KEYS = (
    "damage",
    "range",
    "attackSpeed",
    "precision",
    "precisionFalloff",
    "ignoresArmor",
)


def _default_items_dir() -> Path | None:
    p = os.environ.get("GOING_MEDIEVAL_ITEMS")
    if p:
        return Path(p)
    return None


def _load_regenerate_module(mod_root: Path):
    path = mod_root / "tools" / "regenerate_ranged_from_vanilla.py"
    spec = importlib.util.spec_from_file_location("ranged_regenerate", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def apply_sling_overlays(
    *,
    items_dir: Path,
    mod_root: Path,
    van_repo: dict[str, dict],
) -> None:
    mod_eq = mod_root / "Data" / "Models" / "Equipment.json"
    data = json.loads(mod_eq.read_text(encoding="utf-8"))
    out: list[dict] = []
    for entry in data.get("repository", []):
        eid = entry.get("id")
        if eid not in SLING_IDS:
            out.append(entry)
            continue
        if eid not in van_repo:
            raise SystemExit(f"Vanilla Equipment.json missing sling id {eid!r}")
        ne = deepcopy(van_repo[eid])
        pwm = ne.setdefault("primaryWeaponMode", {})
        for k in PRIMARY_KEYS:
            if k in SLING_COMBAT[eid]:
                pwm[k] = SLING_COMBAT[eid][k]
        out.append(ne)
    data["repository"] = out
    mod_eq.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("Wrote (sling overlays)", mod_eq)


def main() -> None:
    mod_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--items-dir",
        type=Path,
        default=_default_items_dir(),
        help="Folder containing vanilla Equipment.json and WeaponQualitySettings.json",
    )
    parser.add_argument(
        "--vanilla",
        type=Path,
        default=None,
        help="Legacy: path to vanilla Equipment.json (parent folder used as Items dir)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    items_dir = args.items_dir
    if args.vanilla is not None:
        items_dir = args.vanilla.parent
    if not items_dir or not items_dir.is_dir():
        print(
            "ERROR: Set GOING_MEDIEVAL_ITEMS to .../StreamingAssets/Items or pass --items-dir",
            file=sys.stderr,
        )
        sys.exit(1)
    van_eq = items_dir / "Equipment.json"
    if not van_eq.is_file():
        print(f"ERROR: Missing {van_eq}", file=sys.stderr)
        sys.exit(1)

    van_repo = {
        e["id"]: e
        for e in json.loads(van_eq.read_text(encoding="utf-8"))["repository"]
    }
    missing_slings = [i for i in SLING_IDS if i not in van_repo]
    if missing_slings:
        print(f"ERROR: Vanilla missing sling ids: {missing_slings}", file=sys.stderr)
        sys.exit(1)

    reg = _load_regenerate_module(mod_root)

    if args.dry_run:
        print("--dry-run: would run run_regeneration + sling overlays")
        print(f"  items_dir={items_dir}")
        return

    reg.run_regeneration(items_dir, mod_root)
    van_repo_full = {e["id"]: deepcopy(e) for e in van_repo.values()}
    apply_sling_overlays(items_dir=items_dir, mod_root=mod_root, van_repo=van_repo_full)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Compare vanilla Equipment vs Production vs ProductionComponentsRepository.

Outputs:
  - A: Equipment ids with no Production entry (same id).
  - B: Equipment ids where Production exists but no workstation lists that production id.

StreamingAssets layout:
  Items/Equipment.json
  Resources/Production.json
  Constructables/ProductionComponentsRepository.json

Usage:
  export GM_STREAMING_ASSETS="/path/to/Going Medieval_Data/StreamingAssets"
  python scripts/vanilla_production_station_audit.py

  python scripts/vanilla_production_station_audit.py --streaming-assets "D:/.../StreamingAssets"

  # If only GOING_MEDIEVAL_ITEMS is set (points at .../Items):
  export GOING_MEDIEVAL_ITEMS="/path/to/StreamingAssets/Items"
  python scripts/vanilla_production_station_audit.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_streaming_assets(args: argparse.Namespace) -> Path:
    if args.streaming_assets:
        return Path(args.streaming_assets).resolve()
    env = os.environ.get("GM_STREAMING_ASSETS")
    if env:
        return Path(env).resolve()
    items = os.environ.get("GOING_MEDIEVAL_ITEMS")
    if items:
        p = Path(items).resolve()
        if p.name == "Items":
            return p.parent
    print(
        "Set --streaming-assets, or GM_STREAMING_ASSETS, or GOING_MEDIEVAL_ITEMS (…/StreamingAssets/Items).",
        file=sys.stderr,
    )
    sys.exit(2)
    raise SystemExit  # unreachable


def _equip_ids_by_scope(repo: list[dict], scope: str) -> set[str]:
    out: set[str] = set()
    for e in repo:
        eid = str(e.get("id", ""))
        it = e.get("itemType")
        if scope == "all":
            out.add(eid)
        elif scope == "weapon":
            if it == 1:
                out.add(eid)
        elif scope == "weapon_shield":
            if it == 1:
                out.add(eid)
            elif it == 3 and "shield" in eid.lower():
                out.add(eid)
        else:
            raise ValueError(scope)
    return out


def _kind(repo: list[dict], eid: str) -> str:
    for e in repo:
        if e.get("id") != eid:
            continue
        it = e.get("itemType")
        if it == 1:
            return "weapon"
        if it == 2:
            return "garment"
        if it == 3:
            if "shield" in str(e.get("id", "")).lower():
                return "shield"
            return "armor"
        return f"type_{it}"
    return "?"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit unreachable / unreciped equipment in vanilla data.")
    parser.add_argument(
        "--streaming-assets",
        help="Path to Going Medieval_Data/StreamingAssets",
    )
    parser.add_argument(
        "--scope",
        choices=("all", "weapon", "weapon_shield"),
        default="weapon_shield",
        help="Which Equipment rows to include (default: weapon_shield)",
    )
    args = parser.parse_args()
    sa = _resolve_streaming_assets(args)

    eq_path = sa / "Items" / "Equipment.json"
    prod_path = sa / "Resources" / "Production.json"
    pc_path = sa / "Constructables" / "ProductionComponentsRepository.json"
    for p in (eq_path, prod_path, pc_path):
        if not p.is_file():
            print(f"Missing: {p}", file=sys.stderr)
            sys.exit(1)

    eq_data = _load_json(eq_path)
    prod_data = _load_json(prod_path)
    pc_data = _load_json(pc_path)

    repo_eq = eq_data.get("repository") or []
    prod_ids = {p["id"] for p in prod_data.get("repository") or [] if isinstance(p, dict) and p.get("id")}

    station_ids: set[str] = set()
    for comp in pc_data.get("repository") or []:
        for pid in comp.get("productions") or []:
            station_ids.add(pid)

    orphan_prod = prod_ids - station_ids
    equip_ids = _equip_ids_by_scope(repo_eq, args.scope)

    A = sorted(equip_ids - prod_ids)
    B = sorted(equip_ids & orphan_prod)

    print(f"StreamingAssets: {sa}")
    print(f"Scope: {args.scope}")
    print(f"Production entries: {len(prod_ids)}")
    print(f"Production ids on at least one workstation: {len(station_ids)}")
    print(f"Orphan productions (no workstation): {len(orphan_prod)}")
    print()
    print(f"A - no Production id (recipe missing): {len(A)}")
    for x in A:
        print(f"  {x}")
    print()
    print(f"B - Production exists but not on any workstation: {len(B)}")
    for x in B:
        print(f"  {x}")

    if args.scope == "all" and A:
        from collections import defaultdict

        by: dict[str, list[str]] = defaultdict(list)
        for x in A:
            by[_kind(repo_eq, x)].append(x)
        print()
        print("A breakdown by kind:")
        for k in sorted(by.keys()):
            print(f"  {k}: {len(by[k])}")


if __name__ == "__main__":
    main()

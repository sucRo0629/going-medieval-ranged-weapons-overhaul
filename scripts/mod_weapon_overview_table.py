#!/usr/bin/env python3
"""
Mod 用: 全武器（製作不可を含む）を weaponType 別・ティア順に並べる表。

- バニラ `StreamingAssets` の Production / 作業台 / Research で「実際に工房で作れるか」を判定。
- **製作不可**の行は、作業台以降（作業台・レシピ要求スキル・レシピ要約・研究）を `-` で埋める。
  （`Production.id` と備考はデータ確認用に残す）

Mod の `Equipment.json` で `weaponType` とティア表示を解決（既定: リポジトリの Data/Models/Equipment.json）。

  python scripts/mod_weapon_overview_table.py --streaming-assets PATH -o docs/MOD_WEAPON_OVERVIEW.generated.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import weapon_table_common as W


def _mod_data_file(*parts: str) -> Path:
    return Path(__file__).resolve().parent.parent.joinpath("Data", *parts)


def _merge_repo_by_id(base_repo: list[dict], mod_repo: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    passthrough: list[dict] = []
    for row in base_repo:
        if isinstance(row, dict) and row.get("id"):
            merged[str(row["id"])] = row
        elif isinstance(row, dict):
            passthrough.append(row)
    for row in mod_repo:
        if isinstance(row, dict) and row.get("id"):
            merged[str(row["id"])] = row
        elif isinstance(row, dict):
            passthrough.append(row)
    return [*merged.values(), *passthrough]


def _craft_status(wid: str, prod_by_id: dict, station_map: dict) -> str:
    if wid not in prod_by_id:
        return "A: レシピなし"
    if wid not in station_map:
        return "B: 作業台オーファン"
    return "製作可"


def _equip_skill_text(eq_row: dict) -> str:
    txt = W.skills(eq_row)
    if txt == "—":
        return "なし"
    return txt


def build_markdown(sa: Path, mod_equipment_path: Path | None) -> str:
    eq_path = sa / "Items" / "Equipment.json"
    prod_path = sa / "Resources" / "Production.json"
    pc_path = sa / "Constructables" / "ProductionComponentsRepository.json"
    res_path = sa / "Research" / "Research.json"
    for p in (eq_path, prod_path, pc_path, res_path):
        if not p.is_file():
            return f"# Error\n\nMissing: `{p}`\n"

    eq_data = W.load_json(eq_path)
    prod_data = W.load_json(prod_path)
    pc_data = W.load_json(pc_path)
    res_data = W.load_json(res_path)

    mod_path = mod_equipment_path or W.default_mod_equipment_path()
    mod_index: dict[str, dict] = {}
    if mod_path.is_file():
        mod_index = W.repository_index(W.load_json(mod_path))
    vanilla_index = W.repository_index(eq_data)

    eq_repo = eq_data.get("repository") or []
    prod_repo = prod_data.get("repository") or []
    pc_repo = pc_data.get("repository") or []
    research_repo = res_data.get("repository") or []

    mod_prod = _mod_data_file("Resources", "Production.json")
    if mod_prod.is_file():
        prod_repo = _merge_repo_by_id(prod_repo, (W.load_json(mod_prod).get("repository") or []))
    mod_pc = _mod_data_file("Constructables", "ProductionComponentsRepository.json")
    if mod_pc.is_file():
        pc_repo = _merge_repo_by_id(pc_repo, (W.load_json(mod_pc).get("repository") or []))
    mod_res = _mod_data_file("Research", "Research.json")
    if mod_res.is_file():
        research_repo = _merge_repo_by_id(research_repo, (W.load_json(mod_res).get("repository") or []))

    prod_by_id = {str(p["id"]): p for p in prod_repo if isinstance(p, dict) and p.get("id")}
    weapons = W.weapon_ids(eq_repo)
    st_map = W.station_map(pc_repo)
    depth = W.research_depth(research_repo)
    res_by_id = {str(n["id"]): n for n in research_repo if isinstance(n, dict) and n.get("id")}

    craftable_ids = {w for w in weapons if w in prod_by_id and w in st_map}
    unlock = W.research_unlock_map(research_repo, set(weapons) & set(prod_by_id.keys()))

    mod_label = f"`{mod_path}`" if mod_path.is_file() else "_(Mod Equipment なし)_"

    def equip_for(wid: str) -> dict:
        return mod_index.get(wid) or vanilla_index.get(wid) or {}

    by_wt: dict[str, list[str]] = {}
    for w in weapons:
        wt = W.weapon_type_from_equip(equip_for(w))
        by_wt.setdefault(wt, []).append(w)

    for wt in by_wt:
        by_wt[wt] = sorted(
            by_wt[wt],
            key=lambda wid: W.tier_sort_key(
                wid,
                wt,
                prod_by_id.get(wid) or {},
                equip_for(wid),
            ),
        )

    section_keys = [k for k in W.WEAPON_TYPE_SECTION_ORDER if k in by_wt]
    section_keys += sorted(k for k in by_wt if k not in W.WEAPON_TYPE_SECTION_ORDER)

    lines: list[str] = [
        "# Mod 用: 全武器一覧（ティア順・製作可否）（生成）",
        "",
        f"> **バニラデータ**: `{sa}`（Production / 作業台 / Research）",
        f"> **武器種・ティア**: Mod {mod_label}",
        "",
        "- **製作可** = 同名 `Production` があり、かついずれかの作業台 `productions` に載っている。",
        "- **製作不可**の行は **作業台・必要スキル（レシピ）・レシピ要約・研究** を `-`（データ上はレシピや研究があってもプレイヤー製作できないため）。",
        "- **装備必要スキル（Mod）** = Mod（無ければバニラ）`Equipment.requiredSkills`。",
        "- **備考**: `A` = レシピなし、`B` = レシピはあるが作業台未掲載（オーファン）。",
        "",
        f"- 武器総数: **{len(weapons)}** / 製作可: **{len(craftable_ids)}**",
        "",
    ]

    for wt in section_keys:
        wids = by_wt[wt]
        title = W.WEAPON_TYPE_LABEL_JA.get(wt, wt)
        lines.extend(
            [
                f"## {title}",
                "",
                "| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for w in wids:
            eqr = equip_for(w)
            prod = prod_by_id.get(w) or {}
            tier = W.tier_display(w, wt, prod, eqr)
            pid_cell = f"`{w}`" if w in prod_by_id else "-"
            craft_note = _craft_status(w, prod_by_id, st_map)
            equip_skill = _equip_skill_text(eqr).replace("|", "/")
            note = craft_note
            craft = w in craftable_ids
            if craft:
                stations = ", ".join(f"`{x}`" for x in st_map.get(w, []))
                sk = W.skills(prod).replace("|", "/")
                rec = W.recipe_summary(prod).replace("|", "/")
                rids = unlock.get(w, [])
                rparts: list[str] = []
                for rid in rids:
                    node = res_by_id.get(rid, {})
                    en = W.research_display_name(node)
                    dp = depth.get(rid)
                    dps = str(dp) if dp is not None else "-"
                    label = en.replace("|", "\\|") if en else "-"
                    rparts.append(f"`{rid}` / {label} / {dps}")
                if rparts:
                    rcol = "<br>".join(rparts)
                else:
                    rcol = (
                        "-（`Research.unlocks` 無し・初期解禁等）"
                    )
            else:
                stations = "-"
                sk = "-"
                rec = "-"
                rcol = "-"
            lines.append(
                f"| `{w}` | `{wt}` | {tier.replace('|', '/')} | {pid_cell} | {stations} | {sk} | {rec} | {rcol} | {equip_skill} | {note} |"
            )
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "_生成: `scripts/mod_weapon_overview_table.py`_",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--streaming-assets", type=Path, default=None)
    parser.add_argument(
        "--mod-equipment",
        type=Path,
        default=None,
        help="Mod Equipment.json (default: repo Data/Models/Equipment.json)",
    )
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args()
    sa = W.resolve_streaming_assets(args)
    md = build_markdown(sa, args.mod_equipment)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print("Wrote", args.output)
    else:
        print(md)


if __name__ == "__main__":
    main()

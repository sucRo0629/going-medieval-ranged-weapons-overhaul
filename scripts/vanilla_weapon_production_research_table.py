#!/usr/bin/env python3
"""
Build markdown: vanilla weapons that are craftable (Production exists AND listed on
at least one workstation), with recipe summary and research unlocks.

Tables are **split by weapon type** (`primaryWeaponMode.weaponType`) from **Mod**
`Data/Models/Equipment.json` when provided (fallback: vanilla `Items/Equipment.json`).
Rows within each table are sorted by **design tier** (bows/crossbows per
`BOW_DESIGN_TARGETS` T1–T4) or by recipe skill gates (melee / other).

Requires:
  StreamingAssets/Items/Equipment.json
  StreamingAssets/Resources/Production.json
  StreamingAssets/Constructables/ProductionComponentsRepository.json
  StreamingAssets/Research/Research.json

Optional:
  --mod-equipment PATH   default: <repo>/Data/Models/Equipment.json next to this script

Environment:
  GM_STREAMING_ASSETS  or  --streaming-assets PATH
  GOING_MEDIEVAL_ITEMS (parent must be StreamingAssets)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import deque
from pathlib import Path
from typing import Any

# 弓／クロス並び順: [BOW_DESIGN_TARGETS.md] のティア表に合わせる（数値が小さいほど序盤）。
_DESIGN_TIER_SORT: dict[str, tuple[int, str]] = {
    "short_bow": (1, "T1"),
    "war_bow": (2, "T2"),
    "light_crossbow": (2, "T2"),
    "curved_bow": (3, "T3"),
    "crossbow": (3, "T3"),
    "long_bow": (4, "T4"),
    "heavy_crossbow": (4, "T4"),
}

# セクション見出し順（weaponType）
_WEAPON_TYPE_SECTION_ORDER: list[str] = [
    "TwoHandBow",
    "TwoHandCrossbow",
    "OneHandSling",
    "TwoHandSling",
    "OneHandThrow",
    "OneHandAxe",
    "TwoHandAxe",
    "OneHandSword",
    "TwoHandSword",
    "OneHandMace",
    "TwoHandMace",
    "TwoHandSpear",
    "TwoHandStaff",
    "TwoHandRam",
    "Trap",
]

_WEAPON_TYPE_LABEL_JA: dict[str, str] = {
    "TwoHandBow": "弓（TwoHandBow）",
    "TwoHandCrossbow": "クロスボウ（TwoHandCrossbow）",
    "OneHandSling": "片手スリング（OneHandSling）",
    "TwoHandSling": "両手スリング（TwoHandSling）",
    "OneHandThrow": "投擲（OneHandThrow）",
    "OneHandAxe": "片手斧（OneHandAxe）",
    "TwoHandAxe": "両手斧（TwoHandAxe）",
    "OneHandSword": "片手剣（OneHandSword）",
    "TwoHandSword": "両手剣（TwoHandSword）",
    "OneHandMace": "片手鈍器（OneHandMace）",
    "TwoHandMace": "両手鈍器（TwoHandMace）",
    "TwoHandSpear": "槍／長柄（TwoHandSpear）",
    "TwoHandStaff": "杖（TwoHandStaff）",
    "TwoHandRam": "ラム（TwoHandRam）",
    "Trap": "トラップ（Trap）",
    "Unknown": "種別未解決（Unknown）",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_sa(args: argparse.Namespace) -> Path:
    if args.streaming_assets:
        return Path(args.streaming_assets).resolve()
    env = os.environ.get("GM_STREAMING_ASSETS")
    if env:
        return Path(env).resolve()
    gmi = os.environ.get("GOING_MEDIEVAL_ITEMS")
    if gmi:
        p = Path(gmi).resolve()
        if p.name == "Items":
            return p.parent
    print(
        "Set --streaming-assets or GM_STREAMING_ASSETS or GOING_MEDIEVAL_ITEMS (…/StreamingAssets/Items).",
        file=sys.stderr,
    )
    sys.exit(2)
    raise SystemExit


def _weapon_ids(eq_repo: list[dict]) -> list[str]:
    return sorted(str(e["id"]) for e in eq_repo if isinstance(e, dict) and e.get("itemType") == 1 and e.get("id"))


def _station_map(pc_repo: list[dict]) -> dict[str, list[str]]:
    """production_id -> list of ProductionComponentsRepository entry ids."""
    out: dict[str, list[str]] = {}
    for comp in pc_repo:
        if not isinstance(comp, dict):
            continue
        cid = str(comp.get("id", ""))
        for pid in comp.get("productions") or []:
            pid = str(pid)
            out.setdefault(pid, []).append(cid)
    for k in out:
        out[k] = sorted(set(out[k]))
    return out


# Production.json の recipe は `key` が文字列（資源 id）またはカテゴリ bitmask（int）。
# 数量は `value`（`amount` ではないことが多い）。
_CATEGORY_MASK_JA: dict[int, str] = {
    256: "皮革類（leather 系・カテゴリマスク）",
    2048: "金属インゴット類（iron/steel 等・カテゴリマスク）",
    131072: "木材・燃料・骨など（wood/coal 等・カテゴリマスク）",
}


def _recipe_summary(prod: dict) -> str:
    parts: list[str] = []
    for row in prod.get("recipe") or []:
        if not isinstance(row, dict):
            continue
        key = row.get("key")
        amt = row.get("value", row.get("amount", ""))
        if isinstance(key, str):
            parts.append(f"{key} x{amt}")
        elif isinstance(key, int):
            label = _CATEGORY_MASK_JA.get(key, f"category_mask_{key}")
            parts.append(f"{label} x{amt}")
        else:
            parts.append(f"{key!s} x{amt}")
    return ", ".join(parts) if parts else "—"


def _collect_string_values(obj: Any, out: set[str]) -> None:
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_string_values(v, out)
    elif isinstance(obj, list):
        for x in obj:
            _collect_string_values(x, out)


def _research_unlock_map(
    research_repo: list[dict],
    candidate_ids: set[str],
) -> dict[str, list[str]]:
    """production_id -> research node ids.

    Primary: `unlocks[].unlockId` (official link).
    Secondary: any string leaf equal to production id (fallback for unusual nodes).
    """
    prod_to_research: dict[str, set[str]] = {x: set() for x in candidate_ids}
    for node in research_repo:
        if not isinstance(node, dict):
            continue
        nid = str(node.get("id", ""))
        if not nid:
            continue
        for u in node.get("unlocks") or []:
            if isinstance(u, dict):
                uid = u.get("unlockId")
                if isinstance(uid, str) and uid in candidate_ids:
                    prod_to_research[uid].add(nid)
        strings: set[str] = set()
        _collect_string_values(node, strings)
        for pid in candidate_ids:
            if pid in strings:
                prod_to_research[pid].add(nid)
    return {k: sorted(v) for k, v in prod_to_research.items()}


def _research_depth(research_repo: list[dict]) -> dict[str, int | None]:
    ids = [str(n["id"]) for n in research_repo if isinstance(n, dict) and n.get("id")]
    children: dict[str, list[str]] = {i: [] for i in ids}
    incoming: set[str] = set()
    for n in research_repo:
        if not isinstance(n, dict) or not n.get("id"):
            continue
        src = str(n["id"])
        for tgt in n.get("nextNodesIDs") or []:
            tgt = str(tgt)
            if tgt in children:
                children[src].append(tgt)
                incoming.add(tgt)
    roots = [i for i in ids if i not in incoming]
    depth: dict[str, int | None] = {i: None for i in ids}
    if not roots:
        return depth
    q: deque[tuple[str, int]] = deque()
    for r in roots:
        depth[r] = 0
        q.append((r, 0))
    while q:
        u, d = q.popleft()
        for v in children.get(u) or []:
            if depth.get(v) is None or d + 1 < (depth[v] or 9999):
                depth[v] = d + 1
                q.append((v, d + 1))
    return depth


def _research_display_name(node: dict) -> str:
    loc = node.get("locKeys")
    if isinstance(loc, list):
        for row in loc:
            if isinstance(row, dict) and row.get("languageName") == "English":
                n = row.get("name")
                if n:
                    s = str(n)
                    if s.startswith("research_name_"):
                        return f"`{s}`（ローカライズキー）"
                    return s
        for row in loc:
            if isinstance(row, dict) and row.get("name"):
                s = str(row["name"])
                if s.startswith("research_name_"):
                    return f"`{s}`（ローカライズキー）"
                return s
    return ""


def _skills(prod: dict) -> str:
    rs = prod.get("requiredSkills") or []
    if not isinstance(rs, list):
        return "—"
    parts = []
    for row in rs:
        if isinstance(row, dict):
            parts.append(f"{row.get('key','')} {row.get('value','')}")
    return ", ".join(parts) if parts else "—"


def _skill_val(obj: dict, key: str) -> int | None:
    for row in obj.get("requiredSkills") or []:
        if isinstance(row, dict) and row.get("key") == key:
            try:
                return int(row.get("value", 0))
            except (TypeError, ValueError):
                return None
    return None


def _default_mod_equipment_path() -> Path:
    return Path(__file__).resolve().parent.parent / "Data" / "Models" / "Equipment.json"


def _repository_index(data: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in data.get("repository") or []:
        if isinstance(row, dict) and row.get("id"):
            out[str(row["id"])] = row
    return out


def _weapon_type_from_equip(eq_row: dict) -> str:
    pwm = eq_row.get("primaryWeaponMode")
    if isinstance(pwm, dict):
        wt = pwm.get("weaponType")
        if isinstance(wt, str) and wt:
            return wt
    return "Unknown"


def _tier_sort_key(
    wid: str,
    wtype: str,
    prod: dict,
    equip_row: dict,
) -> tuple:
    """Lower tuple sorts earlier. Used within one weaponType group."""
    if wtype in ("TwoHandBow", "TwoHandCrossbow"):
        if wid in _DESIGN_TIER_SORT:
            return (0, _DESIGN_TIER_SORT[wid][0], wid)
        m = _skill_val(equip_row, "Marksman")
        mv = m if m is not None else -1
        return (1, mv, wid)
    if wtype in ("OneHandSling", "TwoHandSling"):
        r = equip_row.get("primaryWeaponMode") or {}
        rng = r.get("range")
        try:
            rv = float(rng) if rng is not None else 0.0
        except (TypeError, ValueError):
            rv = 0.0
        return (0, rv, wid)
    sm = _skill_val(prod, "Smithing")
    cr = _skill_val(prod, "Carpentry")
    tl = _skill_val(prod, "Tailoring")
    # 木工作業台のみ（Carpentry のみ）を鍛冶より先に並べる
    if sm is None and cr is not None:
        bench = 0
    elif sm is not None:
        bench = 1
    else:
        bench = 2
    return (bench, sm or 0, cr or 0, tl or 0, wid)


def _tier_display(wid: str, wtype: str, prod: dict, equip_row: dict) -> str:
    if wtype in ("TwoHandBow", "TwoHandCrossbow") and wid in _DESIGN_TIER_SORT:
        _, label = _DESIGN_TIER_SORT[wid]
        return f"設計{label}"
    if wtype in ("TwoHandBow", "TwoHandCrossbow"):
        m = _skill_val(equip_row, "Marksman")
        if m is not None:
            return f"門限 Marksman {m}"
        return "門限なし（Mod）"
    if wtype in ("OneHandSling", "TwoHandSling"):
        return "射程・素体順（短いほど先）"
    sm = _skill_val(prod, "Smithing")
    cr = _skill_val(prod, "Carpentry")
    tl = _skill_val(prod, "Tailoring")
    bits = []
    if sm is not None:
        bits.append(f"Smithing {sm}")
    if cr is not None:
        bits.append(f"Carpentry {cr}")
    if tl is not None:
        bits.append(f"Tailoring {tl}")
    body = "レシピ " + ", ".join(bits) if bits else "—"
    return body


def build_markdown(sa: Path, mod_equipment_path: Path | None) -> str:
    eq_path = sa / "Items" / "Equipment.json"
    prod_path = sa / "Resources" / "Production.json"
    pc_path = sa / "Constructables" / "ProductionComponentsRepository.json"
    res_path = sa / "Research" / "Research.json"
    for p in (eq_path, prod_path, pc_path, res_path):
        if not p.is_file():
            return f"# Error\n\nMissing: `{p}`\n"

    eq_data = _load(eq_path)
    prod_data = _load(prod_path)
    pc_data = _load(pc_path)
    res_data = _load(res_path)

    mod_path = mod_equipment_path or _default_mod_equipment_path()
    mod_index: dict[str, dict] = {}
    if mod_path.is_file():
        mod_index = _repository_index(_load(mod_path))
    vanilla_index = _repository_index(eq_data)

    eq_repo = eq_data.get("repository") or []
    prod_repo = prod_data.get("repository") or []
    pc_repo = pc_data.get("repository") or []
    research_repo = res_data.get("repository") or []

    prod_by_id = {str(p["id"]): p for p in prod_repo if isinstance(p, dict) and p.get("id")}
    weapons = _weapon_ids(eq_repo)
    station_map = _station_map(pc_repo)
    depth = _research_depth(research_repo)
    res_by_id = {str(n["id"]): n for n in research_repo if isinstance(n, dict) and n.get("id")}

    craftable: list[str] = []
    for w in weapons:
        if w not in prod_by_id:
            continue
        if w not in station_map:
            continue
        craftable.append(w)

    candidate_ids = set(craftable)
    unlock = _research_unlock_map(research_repo, candidate_ids)

    mod_label = f"`{mod_path}`" if mod_path.is_file() else "_(Mod `Equipment.json` なし — バニラ装備のみで weaponType 解決)_"

    lines: list[str] = [
        "# バニラ武器: 製作可能なものの研究・レシピ一覧（生成）",
        "",
        f"> **データソース（バニラ製作・研究）**: `{sa}`",
        f"> **武器種・門限（並びの参考）**: Mod {mod_label}",
        "",
        "- **武器** = `Items/Equipment.json` の `itemType == 1`。",
        "- **製作可能** = 同名の `Production.repository[].id` があり、かつ `ProductionComponentsRepository` のいずれかの `productions` にその id が含まれる。",
        "- **武器種**: `primaryWeaponMode.weaponType`（**Mod の `Equipment.json` があれば優先**、無い id はバニラ装備で補完）。",
        "- **ティア順**: 弓／クロスは **[BOW_DESIGN_TARGETS.md](../implementation_policies/ranged/BOW_DESIGN_TARGETS.md) の T1–T4** に対応する `設計T*`。スリング系は **合成射程の短い順**（Mod の `range`）。その他は **レシピ要求スキル**で、同一武器種内では **木工のみ（Carpentry のみ）を鍛冶レシピより先**に並べる。",
        "- **研究**: 各ノードの **`unlocks[].unlockId`** が `Production.id` と一致するものを正とする。併せて JSON 全体の文字列一致で補足ヒットを拾う（稀な定義用）。",
        "- **深さ**: `nextNodesIDs` から作った木で、ルート（誰の `nextNodesIDs` の先でもない id）からの BFS 深さ。複数ルートがある場合は最短。",
        "",
        f"- 武器総数（itemType 1）: **{len(weapons)}**",
        f"- 製作可能（レシピあり・作業台掲載あり）: **{len(craftable)}**",
        "",
    ]

    def equip_for(wid: str) -> dict:
        return mod_index.get(wid) or vanilla_index.get(wid) or {}

    by_wt: dict[str, list[str]] = {}
    for w in craftable:
        wt = _weapon_type_from_equip(equip_for(w))
        by_wt.setdefault(wt, []).append(w)

    for wt in by_wt:
        by_wt[wt] = sorted(
            by_wt[wt],
            key=lambda wid: _tier_sort_key(
                wid,
                wt,
                prod_by_id[wid],
                equip_for(wid),
            ),
        )

    section_keys = [k for k in _WEAPON_TYPE_SECTION_ORDER if k in by_wt]
    section_keys += sorted(k for k in by_wt if k not in _WEAPON_TYPE_SECTION_ORDER)

    for wt in section_keys:
        wids = by_wt[wt]
        title = _WEAPON_TYPE_LABEL_JA.get(wt, wt)
        lines.extend(
            [
                f"## {title}",
                "",
                "| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for w in wids:
            prod = prod_by_id[w]
            eqr = equip_for(w)
            stations = ", ".join(f"`{x}`" for x in station_map.get(w, []))
            rec = _recipe_summary(prod)
            sk = _skills(prod)
            tier = _tier_display(w, wt, prod, eqr)
            rids = unlock.get(w, [])
            rparts: list[str] = []
            for rid in rids:
                node = res_by_id.get(rid, {})
                en = _research_display_name(node)
                dp = depth.get(rid)
                dps = str(dp) if dp is not None else "—"
                label = en.replace("|", "\\|") if en else "—"
                rparts.append(f"`{rid}` / {label} / {dps}")
            if rparts:
                rcol = "<br>".join(rparts)
            else:
                rcol = (
                    "—（`Research.unlocks` に該当なし。初期から製作可能、"
                    "または建物・シナリオ等で別解錠の可能性）"
                )
            lines.append(
                f"| `{w}` | `{wt}` | {tier.replace('|', '/')} | `{w}` | {stations} | "
                f"{sk.replace('|', '/')} | {rec.replace('|', '/')} | {rcol} |"
            )
        lines.append("")

    not_craft = sorted(set(weapons) - set(craftable))
    lines.extend(
        [
            "",
            "## 参考: 武器だが本作では製作不可（レシピ無し or 作業台未掲載）",
            "",
            "Mod で解禁する場合は `WEAPON_PRODUCTION_RESEARCH_AUDIT.md` の区分 A / B に沿って `Production` / `ProductionComponentsRepository` / `Research` を検討。",
            "",
        ]
    )
    for x in not_craft:
        reason = []
        if x not in prod_by_id:
            reason.append("レシピなし")
        elif x not in station_map:
            reason.append("作業台オーファン")
        lines.append(f"- `{x}`: {' / '.join(reason)}")
    lines.extend(
        [
            "",
            "---",
            "",
            "_生成: `scripts/vanilla_weapon_production_research_table.py`_",
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
        help="Mod Equipment.json for weaponType / tier ordering (default: repo Data/Models/Equipment.json)",
    )
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args()
    sa = _resolve_sa(args)
    mod_eq = args.mod_equipment
    md = build_markdown(sa, mod_eq)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print("Wrote", args.output)
    else:
        print(md)


if __name__ == "__main__":
    main()

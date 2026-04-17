"""Shared helpers for vanilla_weapon_production_research_table.py and mod_weapon_overview_table.py."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import deque
from pathlib import Path
from typing import Any

# 弓／クロス並び順: [BOW_DESIGN_TARGETS.md] のティア表に合わせる（数値が小さいほど序盤）。
DESIGN_TIER_SORT: dict[str, tuple[int, str]] = {
    "short_bow": (1, "T1"),
    "war_bow": (2, "T2"),
    "light_crossbow": (2, "T2"),
    "curved_bow": (3, "T3"),
    "crossbow": (3, "T3"),
    "long_bow": (4, "T4"),
    "heavy_crossbow": (4, "T4"),
}

WEAPON_TYPE_SECTION_ORDER: list[str] = [
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

WEAPON_TYPE_LABEL_JA: dict[str, str] = {
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

CATEGORY_MASK_JA: dict[int, str] = {
    256: "皮革類（leather 系・カテゴリマスク）",
    2048: "金属インゴット類（iron/steel 等・カテゴリマスク）",
    131072: "木材・燃料・骨など（wood/coal 等・カテゴリマスク）",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_streaming_assets(args: argparse.Namespace) -> Path:
    if getattr(args, "streaming_assets", None):
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


def weapon_ids(eq_repo: list[dict]) -> list[str]:
    return sorted(str(e["id"]) for e in eq_repo if isinstance(e, dict) and e.get("itemType") == 1 and e.get("id"))


def station_map(pc_repo: list[dict]) -> dict[str, list[str]]:
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


def recipe_summary(prod: dict) -> str:
    parts: list[str] = []
    for row in prod.get("recipe") or []:
        if not isinstance(row, dict):
            continue
        key = row.get("key")
        amt = row.get("value", row.get("amount", ""))
        if isinstance(key, str):
            parts.append(f"{key} x{amt}")
        elif isinstance(key, int):
            label = CATEGORY_MASK_JA.get(key, f"category_mask_{key}")
            parts.append(f"{label} x{amt}")
        else:
            parts.append(f"{key!s} x{amt}")
    return ", ".join(parts) if parts else "—"


def collect_string_values(obj: Any, out: set[str]) -> None:
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_string_values(v, out)
    elif isinstance(obj, list):
        for x in obj:
            collect_string_values(x, out)


def research_unlock_map(
    research_repo: list[dict],
    candidate_ids: set[str],
) -> dict[str, list[str]]:
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
        collect_string_values(node, strings)
        for pid in candidate_ids:
            if pid in strings:
                prod_to_research[pid].add(nid)
    return {k: sorted(v) for k, v in prod_to_research.items()}


def research_depth(research_repo: list[dict]) -> dict[str, int | None]:
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


def research_display_name(node: dict) -> str:
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


def skills(prod: dict) -> str:
    rs = prod.get("requiredSkills") or []
    if not isinstance(rs, list):
        return "—"
    parts = []
    for row in rs:
        if isinstance(row, dict):
            parts.append(f"{row.get('key','')} {row.get('value','')}")
    return ", ".join(parts) if parts else "—"


def skill_val(obj: dict, key: str) -> int | None:
    for row in obj.get("requiredSkills") or []:
        if isinstance(row, dict) and row.get("key") == key:
            try:
                return int(row.get("value", 0))
            except (TypeError, ValueError):
                return None
    return None


def default_mod_equipment_path() -> Path:
    return Path(__file__).resolve().parent.parent / "Data" / "Models" / "Equipment.json"


def repository_index(data: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in data.get("repository") or []:
        if isinstance(row, dict) and row.get("id"):
            out[str(row["id"])] = row
    return out


def weapon_type_from_equip(eq_row: dict) -> str:
    pwm = eq_row.get("primaryWeaponMode")
    if isinstance(pwm, dict):
        wt = pwm.get("weaponType")
        if isinstance(wt, str) and wt:
            return wt
    return "Unknown"


def tier_sort_key(
    wid: str,
    wtype: str,
    prod: dict,
    equip_row: dict,
) -> tuple:
    if wtype in ("TwoHandBow", "TwoHandCrossbow"):
        if wid in DESIGN_TIER_SORT:
            return (0, DESIGN_TIER_SORT[wid][0], wid)
        m = skill_val(equip_row, "Marksman")
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
    sm = skill_val(prod, "Smithing")
    cr = skill_val(prod, "Carpentry")
    tl = skill_val(prod, "Tailoring")
    if sm is None and cr is not None:
        bench = 0
    elif sm is not None:
        bench = 1
    else:
        bench = 2
    return (bench, sm or 0, cr or 0, tl or 0, wid)


def tier_display(wid: str, wtype: str, prod: dict, equip_row: dict) -> str:
    if wtype in ("TwoHandBow", "TwoHandCrossbow") and wid in DESIGN_TIER_SORT:
        _, label = DESIGN_TIER_SORT[wid]
        return f"設計{label}"
    if wtype in ("TwoHandBow", "TwoHandCrossbow"):
        m = skill_val(equip_row, "Marksman")
        if m is not None:
            return f"門限 Marksman {m}"
        return "門限なし（Mod）"
    if wtype in ("OneHandSling", "TwoHandSling"):
        return "射程・素体順（短いほど先）"
    sm = skill_val(prod, "Smithing")
    cr = skill_val(prod, "Carpentry")
    tl = skill_val(prod, "Tailoring")
    bits = []
    if sm is not None:
        bits.append(f"Smithing {sm}")
    if cr is not None:
        bits.append(f"Carpentry {cr}")
    if tl is not None:
        bits.append(f"Tailoring {tl}")
    body = "レシピ " + ", ".join(bits) if bits else "—"
    return body

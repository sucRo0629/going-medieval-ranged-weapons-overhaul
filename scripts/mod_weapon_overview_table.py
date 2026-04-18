#!/usr/bin/env python3
"""
Mod 用: 全武器（製作不可を含む）を weaponType 別・ティア順に並べる表（同一種内は damage 昇順でタイブレーク）。
先頭に **製作可能な武器＋（レシピ調整前でもティア帯を見たい id）** を全種混在・グローバルティア順に並べた「ティア調整用」表を置く（`DESIGN_TIER_ALL` の見直し用）。

- バニラ `StreamingAssets` の Production / 作業台 / Research で「実際に工房で作れるか」を判定。
- **製作不可**の行は、作業台以降（作業台・レシピ要求スキル・レシピ要約・研究）を `-` で埋める。
  （`Production.id` と備考はデータ確認用に残す）

Mod の `Equipment.json` はバニラ行の上に重ねる（再帰マージ）。装備ステータスは **Mod 適用後** を表示（既定: リポジトリの Data/Models/Equipment.json）。

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

# レシピ・作業台が未整備でも、一括ティア表に「製作予定」として含める武器 id（`weapon_table_common.DESIGN_TIER_ALL` と併せて調整する用）。
TIER_PLANNING_EXTRA_WEAPON_IDS: frozenset[str] = frozenset(
    {
        "warfork",
        "reinforced_spear",
        "billhook",
        "two_handed_flanged_mace",
        "two_handed_warhammer",
        "military_pick",
        "reinforced_flail",
        "warhammer",
    }
)


# ティア内順位用のコスト序列（小→大）。
_COST_RANK_BY_WEAPON_TYPE: dict[str, int] = {
    "TwoHandSpear": 1,
    "OneHandThrow": 2,
    "OneHandAxe": 3,
    "TwoHandAxe": 3,
    "OneHandMace": 4,
    "TwoHandMace": 4,
    "OneHandSword": 5,
    "TwoHandSword": 5,
}

_MELEE_THROW_TYPES: set[str] = {
    "OneHandSword",
    "TwoHandSword",
    "OneHandAxe",
    "TwoHandAxe",
    "OneHandMace",
    "TwoHandMace",
    "TwoHandSpear",
    "TwoHandStaff",
    "TwoHandRam",
    "OneHandThrow",
}


def _mod_data_file(*parts: str) -> Path:
    return Path(__file__).resolve().parent.parent.joinpath("Data", *parts)


def _deep_merge_dict(base: dict, overlay: dict) -> dict:
    """overlay のキーを優先して再帰マージ（リスト・スカラーは overlay があれば置換）。"""
    out = dict(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge_dict(out[k], v)
        else:
            out[k] = v
    return out


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


def _fmt_weapon_stat(val: object | None, *, decimals: int = 4) -> str:
    if val is None:
        return "—"
    try:
        x = float(val)
    except (TypeError, ValueError):
        return str(val).replace("|", "/")
    if decimals <= 0:
        return str(int(x)) if float(x).is_integer() else str(x)
    s = f"{x:.{decimals}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def _primary_mode_combat_cells(eq_row: dict) -> tuple[str, str, str, str]:
    pwm = eq_row.get("primaryWeaponMode")
    if not isinstance(pwm, dict):
        return ("—", "—", "—", "—")
    return (
        _fmt_weapon_stat(pwm.get("damage")),
        _fmt_weapon_stat(pwm.get("attackSpeed")),
        _fmt_weapon_stat(pwm.get("ignoresArmor")),
        _fmt_weapon_stat(pwm.get("armorDamage")),
    )


def _combat_score(eq_row: dict) -> float | None:
    """武器種横断の実戦補正スコア v2（比較用）。大きいほど強い想定。"""
    pwm = eq_row.get("primaryWeaponMode")
    if not isinstance(pwm, dict):
        return None
    try:
        damage = float(pwm.get("damage"))
        attack_speed = float(pwm.get("attackSpeed"))
        ignores_armor = float(pwm.get("ignoresArmor"))
        armor_damage = float(pwm.get("armorDamage"))
        precision = float(pwm.get("precision", 1.0))
        precision_falloff = float(pwm.get("precisionFalloff", 0.0))
        range_v = float(pwm.get("range", 0.0))
    except (TypeError, ValueError):
        return None
    if attack_speed <= 0:
        return None

    wt = str(pwm.get("weaponType", ""))
    base_dps = damage / attack_speed

    # 軽装/重装ケースを混ぜた実効ダメージ補正。
    # ignoresArmor は被甲率の減衰、armorDamage は継戦での装甲剥離寄与として扱う。
    light_armor = 0.22
    heavy_armor = 0.58

    def post_pen_armor(raw_armor: float) -> float:
        return max(0.0, raw_armor * (1.0 - ignores_armor))

    def dmg_mult_from_armor(raw_armor: float) -> float:
        # 装甲で減衰しても最低保証を残す（ゼロ化しすぎない）。
        return max(0.25, 1.0 - post_pen_armor(raw_armor))

    light_mult = dmg_mult_from_armor(light_armor)
    heavy_mult = dmg_mult_from_armor(heavy_armor)
    armor_case_mix = 0.55 * light_mult + 0.45 * heavy_mult

    light_break = 1.0 + min(0.20, armor_damage * 0.04)
    heavy_break = 1.0 + min(0.45, armor_damage * 0.10)
    armor_break_mix = 0.55 * light_break + 0.45 * heavy_break

    stability = 0.90 + max(0.0, min(0.12, (precision - 0.90) * 0.80))

    ranged_types = {
        "TwoHandBow",
        "TwoHandCrossbow",
        "OneHandSling",
        "TwoHandSling",
        "OneHandThrow",
    }
    if wt in ranged_types:
        reach = 1.02 + max(0.0, min(0.22, (range_v - 8.0) * 0.012))
        if wt == "OneHandThrow":
            reach -= 0.05

        # 遠距離は「主戦場 10m」を最重視して命中係数を合成する。
        # 10m を厚く（0.60）、18m/25m は補助評価（0.25/0.15）。
        # precisionFalloff は距離に比例して悪化させる（range が足りない距離は到達率で減衰）。
        def _distance_hit_factor(distance_m: float) -> float:
            # 射程不足は命中機会そのものが減るとして減衰（0.35〜1.00）
            in_range = max(0.35, min(1.0, range_v / max(1.0, distance_m)))
            # distance が伸びるほど precisionFalloff が効く。
            dist_scale = max(0.0, (distance_m - 10.0) / 15.0)
            drop = min(0.45, precision_falloff * (0.08 + 0.60 * dist_scale))
            return max(0.55, min(1.05, precision * (1.0 - drop) * in_range))

        hit_10m = _distance_hit_factor(10.0)
        hit_18m = _distance_hit_factor(18.0)
        hit_25m = _distance_hit_factor(25.0)
        band_hit = 0.60 * hit_10m + 0.25 * hit_18m + 0.15 * hit_25m
        stability = 0.88 + 0.12 * band_hit
    else:
        # 近接は接敵ロスを控えめ減点。長柄の射程差はわずかに加点。
        reach = 0.88 + max(0.0, min(0.12, range_v * 0.18))
        falloff_penalty = min(0.05, precision_falloff * 0.04)
        stability *= max(0.70, 1.0 - falloff_penalty)

    return base_dps * armor_case_mix * armor_break_mix * stability * reach


def _combat_score_cell(eq_row: dict) -> str:
    score = _combat_score(eq_row)
    if score is None:
        return "—"
    return _fmt_weapon_stat(score, decimals=2)


def _combat_score_with_material(
    eq_row: dict,
    *,
    damage_multiplier: float,
    attack_speed_multiplier: float,
) -> float | None:
    """素材補正を仮適用した CombatScore。"""
    pwm = eq_row.get("primaryWeaponMode")
    if not isinstance(pwm, dict):
        return None
    try:
        damage = float(pwm.get("damage"))
        attack_speed = float(pwm.get("attackSpeed"))
    except (TypeError, ValueError):
        return None

    pwm2 = dict(pwm)
    pwm2["damage"] = damage * damage_multiplier
    pwm2["attackSpeed"] = attack_speed * attack_speed_multiplier
    eq2 = dict(eq_row)
    eq2["primaryWeaponMode"] = pwm2
    return _combat_score(eq2)


def _steel_material_multipliers(sa: Path) -> tuple[float, float] | None:
    """MaterialSettings の steel 補正（damage, attackSpeed）を返す。"""
    path = sa / "Items" / "MaterialSettings.json"
    if not path.is_file():
        return None
    data = W.load_json(path)
    repo = data.get("repository") or []
    for row in repo:
        if isinstance(row, dict) and str(row.get("id")) == "steel":
            try:
                dmg = float(row.get("damageMultiplier", 1.0))
                atk = float(row.get("attackSpeedMultiplier", 1.0))
            except (TypeError, ValueError):
                return None
            return (dmg, atk)
    return None


def _is_metal_recipe(prod_row: dict) -> bool:
    """レシピが金属材（鉄/鋼）対応かどうか。"""
    if not isinstance(prod_row, dict):
        return False
    for ing in (prod_row.get("recipe") or []):
        if not isinstance(ing, dict):
            continue
        key = ing.get("key")
        if key == 2048 or key in {"iron_ingot", "steel_ingot"}:
            return True
    for cp in (prod_row.get("customProducts") or []):
        if isinstance(cp, dict) and cp.get("input") == "steel_ingot":
            return True
    return False


def _combat_score_steel_cell(
    eq_row: dict,
    *,
    steel_multipliers: tuple[float, float] | None,
    steel_applicable: bool,
) -> str:
    if not steel_applicable:
        return "-"
    if steel_multipliers is None:
        return "—"
    dmg_mul, atk_mul = steel_multipliers
    score = _combat_score_with_material(
        eq_row,
        damage_multiplier=dmg_mul,
        attack_speed_multiplier=atk_mul,
    )
    if score is None:
        return "—"
    return _fmt_weapon_stat(score, decimals=2)


def _combat_score_sort_value(eq_row: dict) -> float:
    score = _combat_score(eq_row)
    if score is None:
        return float("inf")
    return score


def _tier_internal_rank_score(
    *,
    base_score: float,
    weapon_type: str,
    tier: str,
    is_metal_recipe: bool,
) -> float:
    """
    ティア内順位用の補正スコア。
    - コスト序列（槍 < 投擲槍 < 斧 < メイス < 剣）を反映
    - 非金属の近接/投擲は順位を低めに抑える
    """
    low_tier = tier in {"T1", "T2", "T3"}
    cost_step = 0.08 if low_tier else 0.03
    non_metal_penalty = 0.12 if low_tier else 0.05

    cost_rank = _COST_RANK_BY_WEAPON_TYPE.get(weapon_type, 3)
    adjusted = base_score + cost_step * (cost_rank - 3)

    if (not is_metal_recipe) and weapon_type in _MELEE_THROW_TYPES:
        adjusted -= non_metal_penalty

    return adjusted


def _build_auto_tier_by_combat_score(
    weapon_ids: list[str],
    equip_for,
) -> tuple[dict[str, str], dict[str, float]]:
    """CombatScore の固定閾値で T1..T5 に自動割当（低→高）。"""
    scored: list[tuple[str, float]] = []
    for wid in weapon_ids:
        score = _combat_score(equip_for(wid))
        if score is not None:
            scored.append((wid, score))
    if not scored:
        return {}, {}

    thresholds = {
        "t2_min": 2.5,
        "t3_min": 3.0,
        "t4_min": 3.5,
        "t5_min": 4.0,
        "t5_max": 4.5,
    }

    out: dict[str, str] = {}
    for wid, s in scored:
        if s >= thresholds["t5_min"]:
            out[wid] = "T5"
        elif s >= thresholds["t4_min"]:
            out[wid] = "T4"
        elif s >= thresholds["t3_min"]:
            out[wid] = "T3"
        elif s >= thresholds["t2_min"]:
            out[wid] = "T2"
        else:
            out[wid] = "T1"
    return out, thresholds


def _primary_damage_sort_value(eq_row: dict) -> float:
    """昇順ソート用。欠損・不正値は最後に回す。"""
    pwm = eq_row.get("primaryWeaponMode")
    if not isinstance(pwm, dict):
        return float("inf")
    d = pwm.get("damage")
    try:
        if d is None:
            return float("inf")
        return float(d)
    except (TypeError, ValueError):
        return float("inf")


def _overview_row_sort_key(
    wid: str,
    wt: str,
    prod_by_id: dict[str, dict],
    equip_for,
    auto_tier_by_wid: dict[str, str],
) -> tuple:
    """同一 weaponType 内: ティア内補正後スコア昇順 → damage 昇順 → id。"""
    eq = equip_for(wid)
    prod = prod_by_id.get(wid) or {}
    tier = auto_tier_by_wid.get(wid, "未算出")
    cs = _combat_score_sort_value(eq)
    cs = _tier_internal_rank_score(
        base_score=cs,
        weapon_type=wt,
        tier=tier,
        is_metal_recipe=_is_metal_recipe(prod),
    )
    dmg = _primary_damage_sort_value(eq)
    return (cs, dmg, wid)


def _global_tier_sort_key(
    wid: str,
    prod_by_id: dict[str, dict],
    equip_for,
    auto_tier_by_wid: dict[str, str],
) -> tuple:
    """全 weaponType 混在: ティア → damage 昇順 → id（種別横断の並び）。"""
    wt = W.weapon_type_from_equip(equip_for(wid))
    return _overview_row_sort_key(wid, wt, prod_by_id, equip_for, auto_tier_by_wid)


def build_markdown(sa: Path, mod_equipment_path: Path | None) -> str:
    eq_path = sa / "Data" / "Models" / "Items" / "Equipment.json"
    prod_path = sa / "Data" / "Models" / "Resources" / "Production.json"
    pc_path = sa / "Data" / "Models" / "Constructables" / "ProductionComponentsRepository.json"
    res_path = sa / "Data" / "Models" / "Research" / "Research.json"
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
    weapon_id_set = set(W.weapon_ids(eq_repo))
    for wid, row in mod_index.items():
        if isinstance(row, dict) and row.get("itemType") == 1:
            weapon_id_set.add(wid)
    weapons = sorted(weapon_id_set)
    st_map = W.station_map(pc_repo)
    depth = W.research_depth(research_repo)
    res_by_id = {str(n["id"]): n for n in research_repo if isinstance(n, dict) and n.get("id")}

    craftable_ids = {w for w in weapons if w in prod_by_id and w in st_map}
    unlock = W.research_unlock_map(research_repo, set(weapons) & set(prod_by_id.keys()))

    mod_label = f"`{mod_path}`" if mod_path.is_file() else "_(Mod Equipment なし)_"
    steel_multipliers = _steel_material_multipliers(sa)

    def equip_for(wid: str) -> dict:
        """バニラ行に Mod 行を重ねた結果（Mod のキーが優先）。一覧の数値はここを正本にする。"""
        v = vanilla_index.get(wid)
        m = mod_index.get(wid)
        if v and m:
            return _deep_merge_dict(v, m)
        return m or v or {}

    auto_tier_by_wid, tier_thresholds = _build_auto_tier_by_combat_score(weapons, equip_for)

    by_wt: dict[str, list[str]] = {}
    for w in weapons:
        wt = W.weapon_type_from_equip(equip_for(w))
        by_wt.setdefault(wt, []).append(w)

    for wt in by_wt:
        by_wt[wt] = sorted(
            by_wt[wt],
            key=lambda wid, _wt=wt: _overview_row_sort_key(
                wid, _wt, prod_by_id, equip_for, auto_tier_by_wid
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
        "- **装備必要スキル** = 上記と同じマージ後 `requiredSkills`（Mod で上書きした分が優先）。",
        "- **並び（同一 weaponType 内）**: **CombatScore(Base)** に対してコスト補正（槍 < 投擲槍 < 斧 < メイス < 剣）を加えたティア内順位を優先し、同順位は **`primaryWeaponMode.damage` 昇順**、最後に weapon id。",
        "- **damage / attackSpeed / ignoresArmor / armorDamage** = **バニラ `Equipment` に Mod `Equipment` を再帰マージした** `primaryWeaponMode`（Mod キー優先・**Mod 適用後の実効値**）。品質倍率は含まない。",
        "- **CombatScore(Base)** = `damage / attackSpeed` を基礎に、`ignoresArmor`（貫通）・`armorDamage`（装甲剥離）・`precision`・`precisionFalloff`・到達性補正（近接は接敵ロス、遠隔は射程優位）を乗せた比較用スコア。遠距離は **10m/18m/25m の命中係数を 0.60/0.25/0.15 で合成**し、主戦場 10m を重めに評価。",
        "- **CombatScore(鋼想定)** = `MaterialSettings.steel` の `damageMultiplier` / `attackSpeedMultiplier` を `primaryWeaponMode` に仮適用した想定値（金属レシピ行のみ表示）。",
        "- **ティア列**は **CombatScore(Base)** に固定閾値（T2:2.5〜 / T3:3.0〜 / T4:3.5〜 / T5:4.0〜4.5）を適用。",
        "- **鋼版上限方針**: 鋼想定スコアは目安として **T5: 5.0 以下** を維持する。",
        "- **備考**: `A` = レシピなし、`B` = レシピはあるが作業台未掲載（オーファン）。",
        "- **ティア調整用表**（下）: **データ上製作可**に加え `TIER_PLANNING_EXTRA_WEAPON_IDS` の武器を **全 weaponType 混在** で並べ、CombatScore ベースの自動ティアを種別横断で比較する。",
        "",
        f"- 武器総数: **{len(weapons)}** / 製作可: **{len(craftable_ids)}**",
        (
            f"- CombatScore自動ティア閾値（絶対）: "
            f"T1:<**{_fmt_weapon_stat(tier_thresholds.get('t2_min'), decimals=2)}**, "
            f"T2:>=**{_fmt_weapon_stat(tier_thresholds.get('t2_min'), decimals=2)}**, "
            f"T3:>=**{_fmt_weapon_stat(tier_thresholds.get('t3_min'), decimals=2)}**, "
            f"T4:>=**{_fmt_weapon_stat(tier_thresholds.get('t4_min'), decimals=2)}**, "
            f"T5:**{_fmt_weapon_stat(tier_thresholds.get('t5_min'), decimals=2)}**〜**{_fmt_weapon_stat(tier_thresholds.get('t5_max'), decimals=2)}**"
        ),
        (
            f"- 鋼補正（`MaterialSettings.steel`）: "
            + (
                f"damage x**{_fmt_weapon_stat(steel_multipliers[0], decimals=2)}**, "
                f"attackSpeed x**{_fmt_weapon_stat(steel_multipliers[1], decimals=2)}**"
                if steel_multipliers
                else "未取得"
            )
        ),
        "",
    ]

    tier_balance_ids = craftable_ids | (TIER_PLANNING_EXTRA_WEAPON_IDS & weapon_id_set)
    craftable_sorted_global = sorted(
        tier_balance_ids,
        key=lambda w: (
            _combat_score_sort_value(equip_for(w)),
            W.weapon_type_from_equip(equip_for(w)),
            w,
        ),
    )
    lines.extend(
        [
            "## ティア調整用: 製作可＋計画武器（全武器種・ティア順）",
            "",
            "> **製作可**（マージ後 `Production` ＋作業台）に加え、レシピ調整前でもティアだけ揃えたい id は **`TIER_PLANNING_EXTRA_WEAPON_IDS`**（スクリプト先頭定数）。**ティアは CombatScore の固定閾値（T2:2.5〜 / T3:3.0〜 / T4:3.5〜 / T5:4.0〜4.5）で自動割当**。並びは **ティア内補正後スコア昇順** → **`weaponType` 昇順** → weapon id。",
            "",
            "| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | damage | attackSpeed | ignoresArmor | armorDamage | 製作 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for w in craftable_sorted_global:
        wt = W.weapon_type_from_equip(equip_for(w))
        eqr = equip_for(w)
        prod = prod_by_id.get(w) or {}
        tier = auto_tier_by_wid.get(w, "未算出")
        d_cell, as_cell, ia_cell, ad_cell = _primary_mode_combat_cells(eqr)
        cs_cell = _combat_score_cell(eqr)
        css_cell = _combat_score_steel_cell(
            eqr,
            steel_multipliers=steel_multipliers,
            steel_applicable=_is_metal_recipe(prod),
        )
        craft_cell = "可" if w in craftable_ids else "予定"
        lines.append(
            f"| `{w}` | `{wt}` | {cs_cell} | {css_cell} | {tier} | {d_cell} | {as_cell} | {ia_cell} | {ad_cell} | {craft_cell} |"
        )
    lines.extend(["", "---", ""])

    for wt in section_keys:
        wids = by_wt[wt]
        title = W.WEAPON_TYPE_LABEL_JA.get(wt, wt)
        lines.extend(
            [
                f"## {title}",
                "",
                "| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for w in wids:
            eqr = equip_for(w)
            prod = prod_by_id.get(w) or {}
            tier = auto_tier_by_wid.get(w, "未算出")
            craft_note = _craft_status(w, prod_by_id, st_map)
            equip_skill = _equip_skill_text(eqr).replace("|", "/")
            d_cell, as_cell, ia_cell, ad_cell = _primary_mode_combat_cells(eqr)
            cs_cell = _combat_score_cell(eqr)
            css_cell = _combat_score_steel_cell(
                eqr,
                steel_multipliers=steel_multipliers,
                steel_applicable=_is_metal_recipe(prod),
            )
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
                f"| `{w}` | `{wt}` | {cs_cell} | {css_cell} | {tier.replace('|', '/')} | {stations} | {sk} | {rec} | {rcol} | {equip_skill} | {d_cell} | {as_cell} | {ia_cell} | {ad_cell} | {note} |"
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

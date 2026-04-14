#!/usr/bin/env python3
"""
Reset mod ranged weapon data to vanilla Equipment + TwoHandBow / TwoHandCrossbow WQS,
then apply Marksman ``requiredSkills`` from ``BOW_DESIGN_TARGETS.md`` (装備門限).

After the vanilla copy, applies a **role post-pass** on Equipment (ROLE_RANGE, BOW_ATTACK_SPEED,
BOW_PRIMARY_IGNORES_ARMOR, CROSSBOW_RANGED_COVER): vanilla ``precision`` / ``precisionFalloff`` /
``damage`` stay from the copy; ``range`` follows the documented bow+crossbow order; bow ``attackSpeed``
follows the four-bow chain; bow ``ignoresArmor`` follows ``BOW_DESIGN_TARGETS.md`` 装甲無視の理論レンジ;
crossbow ``rangedCover`` is tiered below buckler.

**Movement**: 弓／クロスに ``onEquipEffectors`` による移動特徴付けは **付けない**（2026-04-16）。
設計上の移動倍率は [`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md) のみ参照。

After copying vanilla WQS:

- **TwoHandBow** — ``TWO_HAND_BOW_QUALITY_DELTAS`` overwrites ``damageMultiplier``,
  ``rangeMultiplier``, ``attackSpeedMultiplier`` per ``productQuality``. ``precisionMultiplier`` /
  ``precisionFalloffMultiplier`` and other columns stay **vanilla** (CREATION: 命中系は本体表、
  火力・攻速・射程は品質で控えめに増やすが、**クロスより品質の効きを大きく**する)。
  **射程の品質伸び**は本体 ``WeaponType`` にカスタム値を足せないため、四弓とも
  ``weaponType`` = ``TwoHandBow`` のまま共有し、``rangeMultiplier`` の勾配は全弓共通。
  短弓だけ別 WQS にできない分、**素体** ``ROLE_RANGE`` と ``BOW_ATTACK_SPEED`` で短弓と長弓三種を切る。

- **TwoHandCrossbow** — vanilla **except** ``damageMultiplier`` / ``attackSpeedMultiplier`` /
  ``rangeMultiplier``, replaced with ``TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`` (gentler
  damage/攻速 ramp than vanilla; **射程は品質で微増**). Precision / falloff columns stay **vanilla**.
  ``ROLE_RANGE`` の ``heavy_crossbow`` 素体は、Q6 合成で ``war_bow`` をわずかに超えつつ ``curved_bow``
  未満に収めるため **20.11**（ライト／標準は 16 / 17 のまま）。弓の ``rangeMultiplier`` Q6 は **1.05**
  に抑え、長弓三種の素体射程を上げて従来の合成に近づける。

Tune the two ``*_DELTAS`` / ``*_OVERRIDES`` dicts when policy numbers move.

Requires a local Going Medieval install (Steam). Paths default from env:
  GOING_MEDIEVAL_ITEMS  -> parent of Equipment.json (e.g. .../StreamingAssets/Items)
Or pass ``--items-dir`` explicitly.

Usage (from repo / Mod folder):

  python scripts/apply_ranged_equipment_delta.py --items-dir "D:/.../StreamingAssets/Items"

Same logic (no sling pass):

  python tools/regenerate_ranged_from_vanilla.py --items-dir "D:/.../StreamingAssets/Items"
"""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from pathlib import Path

RANGED_IDS = [
    "short_bow",
    "war_bow",
    "curved_bow",
    "long_bow",
    "light_crossbow",
    "crossbow",
    "heavy_crossbow",
]

# None = omit requiredSkills key. Align with BOW_DESIGN_TARGETS.md 装備門限表.
REQUIRED_SKILLS: dict[str, list[dict[str, str | int]] | None] = {
    "short_bow": None,
    "war_bow": [{"key": "Marksman", "value": 5}],
    "curved_bow": [{"key": "Marksman", "value": 10}],
    "long_bow": [{"key": "Marksman", "value": 15}],
    "light_crossbow": None,
    "crossbow": [{"key": "Marksman", "value": 5}],
    "heavy_crossbow": [{"key": "Marksman", "value": 10}],
}

WQS_VANILLA_SOURCE_IDS = ("TwoHandBow", "TwoHandCrossbow")

# Post-pass: keep vanilla primary precision / precisionFalloff / damage (from copy above).
# BOW_DESIGN_TARGETS — 弓＋クロス射程順（素体で段を付ける）、弓の attackSpeed 鎖、クロス rangedCover。
# 四弓とも `weaponType` = TwoHandBow（列挙型にカスタム値不可）。短弓は低い素体 range + 速い
# BOW_ATTACK_SPEED。長弓三種は Q6 合成が旧 TwoHandBow×1.1 に近づくよう素体を上げる（war/curved/long）。
ROLE_RANGE: dict[str, float] = {
    # 標準クロス素体 − 短弓素体 ≈ ヘビィクロス素体 − ウォー素体（WQS の rangeMultiplier 段が弓／クロスで同じため全 Q で合成差も一致）。
    # 20.11 − 19.9 = 0.21 → crossbow = 17.65 − 0.21 = 17.44。ライトは cross−light = 0.65 を維持（旧 17.15−16.5）。
    "light_crossbow": 16.79,
    "crossbow": 17.44,
    "short_bow": 17.65,
    "war_bow": 19.9,
    "heavy_crossbow": 20.11,
    "curved_bow": 22.0,
    "long_bow": 24.1,
}

# 弓: long_bow → curved_bow → war_bow → short_bow（遅い→速い = attackSpeed 大→小）。
# 意図語り: BOW_DESIGN_TARGETS.md「四弓のコンセプト」— short は長弓三種より攻速で飛び抜ける。
# 素体間隔はチャートで「短弓＝別クラス」「長弓はウォー／曲弓／長で段が見える」程度まで空ける。
# ノミナル DPS（damage÷attackSpeed）のウォー−ショートは設計目安 +1〜+2 付近に収める。
BOW_ATTACK_SPEED: dict[str, float] = {
    "short_bow": 3.72,
    "war_bow": 4.72,
    "curved_bow": 5.18,
    "long_bow": 5.72,
}

# バックラー rangedCover 0.45 未満。ライト < 標準 < ヘビィの段差。
CROSSBOW_RANGED_COVER: dict[str, float] = {
    "light_crossbow": 0.1,
    "crossbow": 0.15,
    "heavy_crossbow": 0.2,
}

# BOW_DESIGN_TARGETS.md「命中・装甲無視」— 理論レンジ（短弓 0.35〜0.50・上限 0.60、長弓三種 0.55〜0.80・常にクロス未満）。
# 素体で四弓の段を付ける（TwoHandBow の ignoresArmorMultiplier は 1 のままなので Q1–Q6 で一定）。
# 順序: short < war < long < curved < crossbows；Q3 鎖 long < curved は long < curved で満たす。
# **`ignoresArmor` を 0 にしない**: 実機で射撃が禁止される（`COMBAT_PLAYTEST_POLICY.md` 実機メモ）。比較は正の値同士。
BOW_PRIMARY_IGNORES_ARMOR: dict[str, float] = {
    "short_bow": 0.35,
    "war_bow": 0.58,
    "long_bow": 0.7,
    "curved_bow": 0.78,
}

# TwoHandBow: after vanilla WQS copy — 「大きく押し上げない」≠ 変化ゼロ。range + damage + attackSpeed
# を品質で動かし、**バニラ TwoHandCrossbow より Q1→Q6 の damage/攻速の振れを大きく**する。
# precision* はバニラ行のまま（命中・減衰の品質勾配は本体表に任せる）。
# rangeMultiplier Q6=1.05 — 旧 1.10 より品質による射程伸びを抑える（短弓・長弓で WQS を分けられないため）。
TWO_HAND_BOW_QUALITY_DELTAS: dict[int, dict[str, float]] = {
    1: {"damageMultiplier": 0.92, "rangeMultiplier": 1.0, "attackSpeedMultiplier": 1.03},
    2: {"damageMultiplier": 0.95, "rangeMultiplier": 1.01, "attackSpeedMultiplier": 1.02},
    3: {"damageMultiplier": 0.98, "rangeMultiplier": 1.02, "attackSpeedMultiplier": 1.0},
    4: {"damageMultiplier": 1.03, "rangeMultiplier": 1.03, "attackSpeedMultiplier": 0.98},
    5: {"damageMultiplier": 1.09, "rangeMultiplier": 1.04, "attackSpeedMultiplier": 0.95},
    6: {"damageMultiplier": 1.15, "rangeMultiplier": 1.05, "attackSpeedMultiplier": 0.91},
}

# TwoHandCrossbow: damage + attackSpeed + rangeMultiplier (vanilla rest). Damage/攻速 ramp stays
# gentler than vanilla so bow WQS remains the stronger signal; rangeMultiplier micro-ramp so
# synthetic range rises with Q; Q5→Q6 uses same +0.01 step as lower rows (1.04→1.05).
TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES: dict[int, dict[str, float]] = {
    1: {
        "damageMultiplier": 0.94,
        "attackSpeedMultiplier": 1.02,
        "rangeMultiplier": 1.0,
    },
    2: {
        "damageMultiplier": 0.97,
        "attackSpeedMultiplier": 1.01,
        "rangeMultiplier": 1.01,
    },
    3: {
        "damageMultiplier": 1.0,
        "attackSpeedMultiplier": 1.0,
        "rangeMultiplier": 1.02,
    },
    4: {
        "damageMultiplier": 1.02,
        "attackSpeedMultiplier": 0.99,
        "rangeMultiplier": 1.03,
    },
    5: {
        "damageMultiplier": 1.04,
        "attackSpeedMultiplier": 0.98,
        "rangeMultiplier": 1.04,
    },
    6: {
        "damageMultiplier": 1.06,
        "attackSpeedMultiplier": 0.96,
        "rangeMultiplier": 1.05,
    },
}


def apply_two_hand_bow_wqs_policy(two_hand_bow_block: dict) -> None:
    rows = two_hand_bow_block.get("qualitySettings")
    if not isinstance(rows, list):
        return
    for row in rows:
        pq = row.get("productQuality")
        if pq not in TWO_HAND_BOW_QUALITY_DELTAS:
            continue
        d = TWO_HAND_BOW_QUALITY_DELTAS[pq]
        for key, val in d.items():
            row[key] = val


def apply_two_hand_crossbow_wqs_policy(two_hand_crossbow_block: dict) -> None:
    rows = two_hand_crossbow_block.get("qualitySettings")
    if not isinstance(rows, list):
        return
    for row in rows:
        pq = row.get("productQuality")
        if pq not in TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES:
            continue
        d = TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES[pq]
        for key, val in d.items():
            row[key] = val


def apply_ranged_role_postprocess(eid: str, entry: dict) -> None:
    pwm = entry.get("primaryWeaponMode")
    if isinstance(pwm, dict):
        if eid in ROLE_RANGE:
            pwm["range"] = ROLE_RANGE[eid]
        if eid in BOW_ATTACK_SPEED:
            pwm["attackSpeed"] = BOW_ATTACK_SPEED[eid]
        if eid in BOW_PRIMARY_IGNORES_ARMOR:
            pwm["ignoresArmor"] = BOW_PRIMARY_IGNORES_ARMOR[eid]
    if eid in CROSSBOW_RANGED_COVER:
        entry["rangedCover"] = CROSSBOW_RANGED_COVER[eid]
    if eid in RANGED_IDS:
        entry.pop("onEquipEffectors", None)


def _default_items_dir() -> Path | None:
    p = os.environ.get("GOING_MEDIEVAL_ITEMS")
    if p:
        return Path(p)
    return None


def run_regeneration(items_dir: Path, mod_root: Path) -> None:
    """Vanilla Equipment/WQS merge + Equipment Overhaul ranged policy. Used by this CLI and ``scripts/apply_ranged_equipment_delta.py``."""
    mod_eq = mod_root / "Data" / "Models" / "Equipment.json"
    mod_wq = mod_root / "Data" / "Models" / "WeaponQualitySettings.json"

    van_eq_path = items_dir / "Equipment.json"
    van_wq_path = items_dir / "WeaponQualitySettings.json"
    if not van_eq_path.is_file() or not van_wq_path.is_file():
        raise SystemExit(f"Missing vanilla JSON under {items_dir}")

    van_list = json.loads(van_eq_path.read_text(encoding="utf-8"))["repository"]
    van_repo = {e["id"]: e for e in van_list}

    mod_data = json.loads(mod_eq.read_text(encoding="utf-8"))
    # General Mod merge replaces the whole Equipment catalog with this file. If we only
    # kept rows that used to live in the Mod JSON, quality-tier ids (e.g. fine_wood_war_bow)
    # vanish and NPCManager errors when spawning raiders with those equipment ids.
    out_repo: list[dict] = []
    for e in van_list:
        eid = e.get("id")
        if eid in RANGED_IDS:
            if eid not in van_repo:
                raise SystemExit(f"Vanilla Equipment.json missing id {eid!r}")
            ne = deepcopy(van_repo[eid])
            rs = REQUIRED_SKILLS[eid]
            if rs is None:
                ne.pop("requiredSkills", None)
            else:
                ne["requiredSkills"] = deepcopy(rs)
            apply_ranged_role_postprocess(eid, ne)
            out_repo.append(ne)
        else:
            out_repo.append(deepcopy(e))
    mod_data["repository"] = out_repo
    mod_eq.write_text(
        json.dumps(mod_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    van_wq = json.loads(van_wq_path.read_text(encoding="utf-8"))
    van_by_wq_id = {e.get("id"): deepcopy(e) for e in van_wq["repository"]}
    missing = [i for i in WQS_VANILLA_SOURCE_IDS if i not in van_by_wq_id]
    if missing:
        raise SystemExit(f"Vanilla WeaponQualitySettings.json missing: {missing!r}")

    bow_block = van_by_wq_id["TwoHandBow"]
    apply_two_hand_bow_wqs_policy(bow_block)

    cross_block = van_by_wq_id["TwoHandCrossbow"]
    apply_two_hand_crossbow_wqs_policy(cross_block)

    van_wq_repo = [bow_block, cross_block]
    mod_wq_data = json.loads(mod_wq.read_text(encoding="utf-8"))
    mod_wq_data["repository"] = van_wq_repo
    mod_wq.write_text(
        json.dumps(mod_wq_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Wrote", mod_eq)
    print("Wrote", mod_wq)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--items-dir",
        type=Path,
        default=_default_items_dir(),
        help="Folder containing vanilla Equipment.json and WeaponQualitySettings.json",
    )
    args = ap.parse_args()
    if not args.items_dir:
        raise SystemExit(
            "Set GOING_MEDIEVAL_ITEMS to .../StreamingAssets/Items or pass --items-dir"
        )
    run_regeneration(args.items_dir, root)


if __name__ == "__main__":
    main()

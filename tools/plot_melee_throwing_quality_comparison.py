"""
Generate melee/throwing vanilla-vs-mod quality charts and summaries.

Outputs:
- quality_charts/melee_throwing/same_tier/<tier>/      (tier-matched comparisons, overlay)
- quality_charts/melee_throwing/by_category/<category>/    (per category + stat: grid `*_Q1_Q6_vanilla_vs_mod.png` and
  overlay `*_all_weapons_overlay.png`, same idea as `tools/plot_weapon_quality_comparison.py` ranged outputs)
- quality_charts/melee_throwing/layer1_eval_bundle.md
- quality_charts/melee_throwing/script/         (tier/category stat summary CSVs)
- quality_charts/armor_proxy/                   (flat + Q3 sim CSVs; `armor_proxy_heatmap_*.png` mod-only;
  `armor_proxy_heatmap_compare_*.png` vanilla|mod Q3 per category + ranged;
  `armor_proxy_heatmap_type_vs_armor.png` weapon-type × armor matchup summary)
"""

from __future__ import annotations

import csv
import importlib.util
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
_RANGED_PLOT = _THIS.parent / "plot_weapon_quality_comparison.py"
_SCRIPTS = _ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import weapon_table_common as WCOMMON


def _load_shared():
    spec = importlib.util.spec_from_file_location("ranged_plot_shared", _RANGED_PLOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load shared plotting module: {_RANGED_PLOT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SHARED = _load_shared()

MOD_EQUIPMENT = _ROOT / "Data" / "Models" / "Equipment.json"
MOD_WQS = _ROOT / "Data" / "Models" / "WeaponQualitySettings.json"

OUT_BASE = _ROOT / "quality_charts" / "melee_throwing"
OUT_SAME_TIER = OUT_BASE / "same_tier"
OUT_BY_CATEGORY = OUT_BASE / "by_category"
OUT_SCRIPT = OUT_BASE / "script"
# Flat-armor / full-weapon simulation artifacts (ranged + melee).
OUT_ARMOR_PROXY = _ROOT / "quality_charts" / "armor_proxy"

BY_CATEGORY_GRID_NCOLS = 4

# Flat mitigation proxy (same formula as `tools/plot_weapon_quality_comparison.py` layer-1).
# `plate_iron` uses the same scalar as ranged profile `heavy` (0.68) — not a parsed iron item.
MELEE_ARMOR_PROXY_PROFILES: tuple[tuple[str, float], ...] = (
    ("none", 0.0),
    ("light", 0.28),
    ("plate_iron", 0.68),
)

# Ranged bow/crossbow ids (same set as `tools/plot_weapon_quality_comparison.py` WEAPON_IDS).
RANGED_WEAPON_IDS: tuple[str, ...] = (
    "short_bow",
    "war_bow",
    "curved_bow",
    "long_bow",
    "light_crossbow",
    "crossbow",
    "heavy_crossbow",
)

# Curated “mid tier” sim: **quality = Q3** (index 2). Melee picks: one mid 1H + 2H where both exist;
# spears are all 2H in data → one mid spear; throwing → primary+secondary; ranged → all seven.
SIM_QUALITY_Q_INDEX = 2
SIM_DECAY_NUM_HITS = 20
# Fictional armor durability pool (not from Equipment armor items). armorDamage reduces it each hit.
ARMOR_HP_MAX_BY_PROFILE: dict[str, float] = {
    "none": 0.0,
    "light": 100.0,
    "plate_iron": 280.0,
}

QUALITIES = [f"Q{i}" for i in range(1, 7)]

SWORDS = ["dagger", "short_sword", "falchion", "knightly_sword", "longsword", "greatsword"]
SPEARS = ["spear", "reinforced_spear", "warfork", "billhook", "berdiche"]
AXES = ["hatchet", "greataxe"]
BLUNTS = [
    "cudgel",
    "bludgeon",
    "mace",
    "warhammer",
    "flail",
    "reinforced_flail",
    "military_pick",
    "two_handed_mace",
    "two_handed_flanged_mace",
    "two_handed_warhammer",
    "two_handed_flail",
]


@dataclass(frozen=True)
class WeaponMode:
    weapon_id: str
    mode: str  # "primary" or "secondary"
    label: str
    family: str  # sword/spear/axe/blunt


MODE_SPECS: dict[str, WeaponMode] = {
    # melee primaries
    **{wid: WeaponMode(wid, "primary", wid, "sword") for wid in SWORDS},
    **{wid: WeaponMode(wid, "primary", wid, "spear") for wid in SPEARS},
    **{wid: WeaponMode(wid, "primary", wid, "axe") for wid in AXES},
    **{wid: WeaponMode(wid, "primary", wid, "blunt") for wid in BLUNTS},
    # throwing split modes
    "throwing_axes_throw": WeaponMode("throwing_axes", "primary", "throwing_axes_throw", "axe"),
    "throwing_axes_melee": WeaponMode("throwing_axes", "secondary", "throwing_axes_melee", "axe"),
    "light_javelins_throw": WeaponMode("light_javelins", "primary", "light_javelins_throw", "spear"),
    "light_javelins_melee": WeaponMode("light_javelins", "secondary", "light_javelins_melee", "spear"),
}

def _tier_sort_key(label: str) -> tuple[int, str]:
    if label.startswith("T"):
        try:
            return (0, int(label[1:]))
        except ValueError:
            pass
    return (1, label)


def build_same_tier_groups() -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for mode_key, spec in MODE_SPECS.items():
        tier_label = WCOMMON.DESIGN_TIER_ALL.get(spec.weapon_id, (99, "未割当"))[1]
        group_name = f"tier_{tier_label}"
        grouped.setdefault(group_name, []).append(mode_key)
    out: dict[str, list[str]] = {}
    for group_name in sorted(grouped, key=lambda g: _tier_sort_key(g.removeprefix("tier_"))):
        out[group_name] = sorted(grouped[group_name], key=lambda mk: MODE_SPECS[mk].label)
    return out


SAME_TIER_GROUPS: dict[str, list[str]] = build_same_tier_groups()

CATEGORY_GROUPS: dict[str, list[str]] = {
    "sword_family": SWORDS,
    "spear_family_with_throwing": SPEARS + ["light_javelins_throw", "light_javelins_melee"],
    "axe_family_with_throwing": AXES + ["throwing_axes_throw", "throwing_axes_melee"],
    "blunt_family": BLUNTS,
}

# Short slugs for `armor_proxy_heatmap_{slug}.png` under `quality_charts/armor_proxy/`.
ARMOR_PROXY_HEATMAP_SLUG: dict[str, str] = {
    "sword_family": "sword",
    "spear_family_with_throwing": "spear",
    "axe_family_with_throwing": "axe",
    "blunt_family": "blunt",
}

# Cross-type armor matchup chart: display label, CATEGORY_GROUPS key, or None for ranged aggregate.
ARMOR_PROXY_TYPE_VS_ARMOR_ROWS: list[tuple[str, str | None]] = [
    ("Sword family", "sword_family"),
    ("Spear + javelins", "spear_family_with_throwing"),
    ("Axe + throwing axes", "axe_family_with_throwing"),
    ("Blunt family", "blunt_family"),
    ("Bows & crossbows", None),
]


@dataclass(frozen=True)
class StatSpec:
    key: str
    label: str
    short_label: str  # overlay title / y-axis (aligned with ranged chart naming)


# Order matches ranged core stats, then melee-only armorDamage (see plot_weapon_quality_comparison.py main()).
STAT_SPECS: list[StatSpec] = [
    StatSpec("damage", "Damage (computed, base × quality)", "Damage"),
    StatSpec(
        "attackSpeed",
        "Attack speed / reload (computed, lower is faster)",
        "Attack speed / reload",
    ),
    StatSpec("range", "Range (computed, base × quality)", "Range"),
    StatSpec("precision", "Precision (computed, base × quality)", "Precision"),
    StatSpec(
        "precisionFalloff",
        "Precision falloff (computed, base × quality)",
        "Precision falloff",
    ),
    StatSpec("ignoresArmor", "Ignores armor (computed, base × quality)", "Ignores armor"),
    StatSpec("armorDamage", "Armor damage (computed, base × quality)", "Armor damage"),
]

IA_CAP_BY_FAMILY = {"sword": 0.32, "spear": 0.50, "axe": 0.32, "blunt": 0.18}
CORE_MELEE_IDS_BY_FAMILY = {
    "sword": SWORDS,
    "spear": SPEARS,
    "axe": AXES,
    "blunt": BLUNTS,
}

THROW_MODE_COLORS: dict[str, str] = {
    "throwing_axes_throw": "#C44E52",
    "throwing_axes_melee": "#E39CA0",
    "light_javelins_throw": "#7E57C2",
    "light_javelins_melee": "#B39DDB",
}

# Display tier for per-weapon chart titles (source: `scripts/weapon_table_common.py` DESIGN_TIER_ALL).
WEAPON_TIER_DISPLAY: dict[str, str] = {
    spec.weapon_id: WCOMMON.DESIGN_TIER_ALL.get(spec.weapon_id, (99, "未割当"))[1]
    for spec in MODE_SPECS.values()
}

_wids_in_modes = {MODE_SPECS[k].weapon_id for k in MODE_SPECS}
_missing_tier = sorted(_wids_in_modes - set(WEAPON_TIER_DISPLAY))
if _missing_tier:
    raise RuntimeError(f"WEAPON_TIER_DISPLAY missing weapon_id(s): {_missing_tier}")


def per_weapon_category_label(spec: WeaponMode) -> str:
    if spec.weapon_id == "throwing_axes":
        return "Throwing axe"
    if spec.weapon_id == "light_javelins":
        return "Throwing spear"
    return {"sword": "Sword", "spear": "Spear", "axe": "Axe", "blunt": "Blunt"}[spec.family]


def per_weapon_name_label(spec: WeaponMode) -> str:
    wid = spec.weapon_id
    if wid == "throwing_axes":
        return f"{wid} (throw)" if spec.mode == "primary" else f"{wid} (melee)"
    if wid == "light_javelins":
        return f"{wid} (throw)" if spec.mode == "primary" else f"{wid} (melee)"
    return wid


def mode_key_subplot_title(mode_key: str) -> str:
    spec = MODE_SPECS[mode_key]
    tier = WEAPON_TIER_DISPLAY[spec.weapon_id]
    cat = per_weapon_category_label(spec)
    name = per_weapon_name_label(spec)
    return f"{cat} | {tier}\n{name}"


def apply_quality_extended(base: dict, row: dict) -> dict:
    def m(key: str, default: float = 1.0) -> float:
        return float(row.get(key, default))

    return {
        "damage": float(base["damage"]) * m("damageMultiplier"),
        "armorDamage": float(base.get("armorDamage", 0.0)) * m("armorDamageMultiplier"),
        "ignoresArmor": float(base.get("ignoresArmor", 0.0)) * m("ignoresArmorMultiplier"),
        "attackSpeed": float(base["attackSpeed"]) * m("attackSpeedMultiplier"),
        "range": float(base["range"]) * m("rangeMultiplier"),
        "precision": float(base.get("precision", 1.0)) * m("precisionMultiplier"),
        "precisionFalloff": float(base.get("precisionFalloff", 0.0)) * m("precisionFalloffMultiplier"),
    }


def mode_block(merged: dict, mode: str) -> dict:
    if mode == "primary":
        return merged["primaryWeaponMode"]
    if mode == "secondary":
        sec = merged.get("secondaryWeaponMode")
        if not sec:
            raise KeyError("secondaryWeaponMode is missing")
        return sec
    raise ValueError(mode)


def series_for_mode(merged: dict, mode: str, wqs: dict) -> list[dict]:
    block = mode_block(merged, mode)
    rows = SHARED.quality_rows(wqs, block["weaponType"])
    return [apply_quality_extended(block, r) for r in rows]


def merged_item_maps() -> tuple[dict[str, dict], dict[str, dict], dict, dict]:
    vanilla_root = SHARED.resolve_vanilla_items_dir()
    vanilla_eq = SHARED.load_json(vanilla_root / "Equipment.json")
    wqs_vanilla = SHARED.load_json(vanilla_root / "WeaponQualitySettings.json")
    wqs_mod = SHARED.merge_wqs_overlay(wqs_vanilla, MOD_WQS)
    mod_eq = SHARED.load_json(MOD_EQUIPMENT)
    vmap = SHARED.repo_by_id(vanilla_eq)
    mmap = SHARED.repo_by_id(mod_eq)
    return vmap, mmap, wqs_vanilla, wqs_mod


def series_pair(
    mode_key: str, vmap: dict[str, dict], mmap: dict[str, dict], wqs_vanilla: dict, wqs_mod: dict
) -> tuple[list[dict], list[dict]]:
    spec = MODE_SPECS[mode_key]
    v_only = SHARED.merge_ranged(vmap[spec.weapon_id], None)
    v_item = SHARED.merge_ranged(vmap[spec.weapon_id], mmap.get(spec.weapon_id))
    return (
        series_for_mode(v_only, spec.mode, wqs_vanilla),
        series_for_mode(v_item, spec.mode, wqs_mod),
    )


def mode_color(mode_key: str, fallback_palette: list[tuple[float, float, float]], idx: int) -> tuple[float, float, float]:
    if mode_key in THROW_MODE_COLORS:
        return plt.matplotlib.colors.to_rgb(THROW_MODE_COLORS[mode_key])
    return fallback_palette[idx % len(fallback_palette)]


def plot_group_stat(
    *,
    group_name: str,
    mode_keys: list[str],
    stat: StatSpec,
    out_dir: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6))
    palette = list(plt.get_cmap("tab20").colors)
    for idx, mk in enumerate(mode_keys):
        y_v, y_m = series_pair(mk, vmap, mmap, wqs_vanilla, wqs_mod)
        col = mode_color(mk, palette, idx)
        label = MODE_SPECS[mk].label
        ax.plot(
            QUALITIES,
            [SHARED.round2(s[stat.key]) for s in y_v],
            linestyle="--",
            linewidth=1.8,
            color=col,
            label=f"{label} (V)",
        )
        ax.plot(
            QUALITIES,
            [SHARED.round2(s[stat.key]) for s in y_m],
            linestyle="-",
            linewidth=2.1,
            color=col,
            label=f"{label} (M)",
        )
    ax.set_title(f"{group_name.replace('_', ' ')} — {stat.label}")
    ax.set_xlabel("Quality")
    ax.set_ylabel(stat.short_label)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    out_path = out_dir / f"{group_name}_{stat.key}_Q1_Q6_vanilla_vs_mod.png"
    SHARED.savefig_png(fig, out_path, dpi=150, tight=True)
    plt.close(fig)
    return out_path


def plot_group_expected_armored_dps(
    *,
    group_name: str,
    mode_keys: list[str],
    mitigation_label: str,
    mitigation: float,
    out_dir: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6))
    palette = list(plt.get_cmap("tab20").colors)
    for idx, mk in enumerate(mode_keys):
        y_v, y_m = series_pair(mk, vmap, mmap, wqs_vanilla, wqs_mod)
        col = mode_color(mk, palette, idx)
        label = MODE_SPECS[mk].label
        ax.plot(
            QUALITIES,
            [SHARED.round2(melee_expected_dps_armor_proxy(s, mitigation)) for s in y_v],
            linestyle="--",
            linewidth=1.8,
            color=col,
            label=f"{label} (V)",
        )
        ax.plot(
            QUALITIES,
            [SHARED.round2(melee_expected_dps_armor_proxy(s, mitigation)) for s in y_m],
            linestyle="-",
            linewidth=2.1,
            color=col,
            label=f"{label} (M)",
        )
    ax.set_title(f"{group_name.replace('_', ' ')} — expected armored DPS ({mitigation_label})")
    ax.set_xlabel("Quality")
    ax.set_ylabel(f"Expected armored DPS ({mitigation_label})")
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    out_path = out_dir / f"{group_name}_expected_armored_dps_{mitigation_label}_Q1_Q6_vanilla_vs_mod.png"
    SHARED.savefig_png(fig, out_path, dpi=150, tight=True)
    plt.close(fig)
    return out_path


def plot_category_group_stat_overlay(
    *,
    group_name: str,
    mode_keys: list[str],
    stat: StatSpec,
    out_dir: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> Path:
    """All modes in one axes — mirrors ranged `save_all_weapons_overlay` → `*_all_weapons_overlay.png`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    palette = list(plt.get_cmap("tab20").colors)
    group_title = group_name.replace("_", " ")
    for idx, mk in enumerate(mode_keys):
        y_v, y_m = series_pair(mk, vmap, mmap, wqs_vanilla, wqs_mod)
        col = mode_color(mk, palette, idx)
        label = MODE_SPECS[mk].label
        ax.plot(
            QUALITIES,
            [SHARED.round2(s[stat.key]) for s in y_v],
            linestyle="--",
            linewidth=1.4,
            color=col,
            label=f"{label} (V)",
        )
        ax.plot(
            QUALITIES,
            [SHARED.round2(s[stat.key]) for s in y_m],
            linestyle="-",
            linewidth=2.2,
            color=col,
            label=f"{label} (M)",
        )
    ax.set_title(f"{stat.short_label} Q1–Q6: {group_title} (solid=mod, dashed=vanilla)")
    ax.set_xlabel("Quality")
    ax.set_ylabel(stat.short_label)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    out_path = out_dir / f"{group_name}_{stat.key}_all_weapons_overlay.png"
    SHARED.savefig_png(fig, out_path, dpi=150, tight=True)
    plt.close(fig)
    return out_path


def plot_category_group_stat_grid(
    *,
    group_name: str,
    mode_keys: list[str],
    stat: StatSpec,
    out_dir: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> Path:
    """One figure per category + stat: subplot per weapon/mode (same layout idea as ranged `*_Q1_Q6_vanilla_vs_mod.png`)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(mode_keys)
    if n == 0:
        raise ValueError("mode_keys is empty")
    ncols = BY_CATEGORY_GRID_NCOLS
    nrows = max(1, math.ceil(n / ncols))
    fig_w, fig_h = 14.0, max(6.5, 3.15 * nrows + 0.9)
    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h), sharex=True, sharey=False)
    if nrows == 1 and ncols == 1:
        axes_flat = [axes]
    else:
        axes_flat = list(axes.flatten())

    palette = list(plt.get_cmap("tab20").colors)
    vanilla_rgb = (0.55, 0.55, 0.55)

    fig.suptitle(
        f"{stat.label} — Vanilla vs mod (Equipment + mod quality multipliers where defined)\n"
        f"{group_name.replace('_', ' ')}",
        fontsize=11,
    )

    for i, ax in enumerate(axes_flat):
        if i >= n:
            ax.axis("off")
            continue
        mk = mode_keys[i]
        y_v, y_m = series_pair(mk, vmap, mmap, wqs_vanilla, wqs_mod)
        col_mod = mode_color(mk, palette, i)
        ax.plot(
            QUALITIES,
            [SHARED.round2(s[stat.key]) for s in y_v],
            marker="o",
            label="Vanilla",
            linewidth=1.5,
            color=vanilla_rgb,
        )
        ax.plot(
            QUALITIES,
            [SHARED.round2(s[stat.key]) for s in y_m],
            marker="s",
            label="Mod",
            linewidth=1.5,
            color=col_mod,
        )
        ax.set_title(mode_key_subplot_title(mk), fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis="x", labelsize=7)

    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.98, 0.02))
    plt.tight_layout(rect=(0, 0.03, 1, 0.92))
    out_path = out_dir / f"{group_name}_{stat.key}_Q1_Q6_vanilla_vs_mod.png"
    SHARED.savefig_png(fig, out_path, dpi=150, tight=False)
    plt.close(fig)
    return out_path


def write_summary_csv(
    *,
    group_type: str,
    groups: dict[str, list[str]],
    out_path: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "group_type",
                "group_name",
                "mode_key",
                "weapon_id",
                "mode",
                "quality",
                "dataset",
                "damage",
                "attackSpeed",
                "range",
                "precision",
                "precisionFalloff",
                "ignoresArmor",
                "armorDamage",
            ]
        )
        for group_name, mode_keys in groups.items():
            for mk in mode_keys:
                spec = MODE_SPECS[mk]
                v_series, m_series = series_pair(mk, vmap, mmap, wqs_vanilla, wqs_mod)
                for q_idx, q in enumerate(QUALITIES):
                    for dataset, row in (("vanilla", v_series[q_idx]), ("mod", m_series[q_idx])):
                        writer.writerow(
                            [
                                group_type,
                                group_name,
                                mk,
                                spec.weapon_id,
                                spec.mode,
                                q,
                                dataset,
                                f"{SHARED.round2(row['damage']):.2f}",
                                f"{SHARED.round2(row['attackSpeed']):.2f}",
                                f"{SHARED.round2(row['range']):.2f}",
                                f"{SHARED.round2(row['precision']):.3f}",
                                f"{SHARED.round2(row['precisionFalloff']):.4f}",
                                f"{SHARED.round2(row['ignoresArmor']):.4f}",
                                f"{SHARED.round2(row['armorDamage']):.2f}",
                            ]
                        )


def category_q3_average(
    family: str, vmap: dict[str, dict], mmap: dict[str, dict], wqs_mod: dict
) -> dict[str, float]:
    weapon_ids = CORE_MELEE_IDS_BY_FAMILY.get(family, [])
    if not weapon_ids:
        raise ValueError(f"No keys for family {family}")
    stat_sum = {s.key: 0.0 for s in STAT_SPECS}
    cover_sum = 0.0
    for wid in weapon_ids:
        merged = SHARED.merge_ranged(vmap[wid], mmap.get(wid))
        q3 = series_for_mode(merged, "primary", wqs_mod)[2]
        for s in STAT_SPECS:
            stat_sum[s.key] += float(q3[s.key])
        cover_sum += float(merged.get("meleeCover", 0.0))
    n = float(len(weapon_ids))
    out = {k: v / n for k, v in stat_sum.items()}
    out["meleeCover"] = cover_sum / n
    return out


def melee_dealt_hp_proxy(stats: dict, mitigation: float) -> float:
    return SHARED.damage_after_flat_armor_proxy(
        float(stats["damage"]),
        float(stats["ignoresArmor"]),
        mitigation,
    )


def melee_expected_dps_armor_proxy(stats: dict, mitigation: float) -> float:
    """`dealt / attackSpeed * precision` — distance / precisionFalloff omitted (layer-1)."""
    spd = float(stats["attackSpeed"])
    if spd <= 0.0:
        return 0.0
    return melee_dealt_hp_proxy(stats, mitigation) / spd * float(stats["precision"])


def mitigation_effective_from_armor_hp(
    mitigation_base: float, armor_hp: float, armor_hp_max: float
) -> float:
    """Scale flat mitigation by remaining fictional armor HP (1 at full, 0 when broken)."""
    if mitigation_base <= 0.0 or armor_hp_max <= 0.0:
        return 0.0
    frac = max(0.0, min(1.0, armor_hp / armor_hp_max))
    return mitigation_base * frac


def total_dealt_n_hits_static(stats: dict, mitigation_base: float, n_hits: int) -> float:
    """Same mitigation every hit (legacy flat proxy)."""
    if n_hits <= 0:
        return 0.0
    return float(n_hits) * melee_dealt_hp_proxy(stats, mitigation_base)


def total_dealt_n_hits_armor_decay(
    stats: dict, mitigation_base: float, armor_hp_max: float, n_hits: int
) -> float:
    """
    Pseudo decay: each hit uses mit = mitigation_base * (armor_hp / armor_hp_max),
    then armor_hp -= armorDamage (quality-scaled). `armor_hp_max <= 0` ⇒ unarmored path.
    """
    if n_hits <= 0:
        return 0.0
    if armor_hp_max <= 0.0:
        return float(n_hits) * float(stats["damage"])
    armor_hp = armor_hp_max
    total = 0.0
    dmg = float(stats["damage"])
    ia = float(stats["ignoresArmor"])
    ad = float(stats.get("armorDamage", 0.0))
    for _ in range(n_hits):
        m_eff = mitigation_effective_from_armor_hp(mitigation_base, armor_hp, armor_hp_max)
        total += SHARED.damage_after_flat_armor_proxy(dmg, ia, m_eff)
        armor_hp = max(0.0, armor_hp - ad)
    return total


def expected_dps_proxy_from_total_dealt(total_dealt: float, stats: dict, n_hits: int) -> float:
    spd = float(stats["attackSpeed"])
    if spd <= 0.0 or n_hits <= 0:
        return 0.0
    return total_dealt / (float(n_hits) * spd) * float(stats["precision"])


def ranged_stats_at_q_with_armor_damage(merged: dict, wqs: dict, q_idx: int) -> dict:
    """Primary ranged row + armorDamage (not in ranged `apply_quality` dict)."""
    pwm = merged["primaryWeaponMode"]
    rows = SHARED.quality_rows(wqs, pwm["weaponType"])
    row = rows[q_idx]

    def m(key: str, default: float = 1.0) -> float:
        return float(row.get(key, default))

    s = dict(SHARED.series_for_item(merged, wqs)[q_idx])
    s["armorDamage"] = float(pwm.get("armorDamage", 0.0)) * m("armorDamageMultiplier")
    return s


def stats_for_sim_row(
    weapon_id: str,
    mode: str,
    q_idx: int,
    *,
    dataset: str,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> dict:
    wqs = wqs_vanilla if dataset == "vanilla" else wqs_mod
    patch = None if dataset == "vanilla" else mmap.get(weapon_id)
    merged = SHARED.merge_ranged(vmap[weapon_id], patch)
    if weapon_id in RANGED_WEAPON_IDS:
        assert mode == "primary"
        return ranged_stats_at_q_with_armor_damage(merged, wqs, q_idx)
    return series_for_mode(merged, mode, wqs)[q_idx]


def sim_curated_weapon_entries() -> list[tuple[str, str, str, str, str]]:
    """(sim_id, category, hand_label, weapon_id, mode). Quality fixed separately to Q3.

    Representative picks (for `armor_proxy_sim_Q3_n20.csv`, not the full family heatmaps):
    - **Ranged**: all seven bows/crossbows (same as layer-1 ranged WEAPON_IDS) so tier progression is visible.
    - **Sword / axe / blunt**: where the game has both 1H and 2H, include **one mid 1H + one or two 2H** lines
      to show archetype spread without listing every blade.
    - **Spear**: data skews 2H; use **one mid spear** plus javelin throw/melee (different stat surfaces).
    - **Throwing axes / javelins**: **primary + secondary** modes (throw vs melee) because balance levers differ.
    """
    rows: list[tuple[str, str, str, str, str]] = []
    for wid in RANGED_WEAPON_IDS:
        rows.append((f"ranged_{wid}", "ranged", "ranged", wid, "primary"))
    rows.extend(
        [
            ("sword_1H_knightly", "sword", "1H", "knightly_sword", "primary"),
            ("sword_2H_longsword", "sword", "2H", "longsword", "primary"),
            ("sword_2H_greatsword", "sword", "2H", "greatsword", "primary"),
            ("spear_2H_reinforced", "spear", "2H", "reinforced_spear", "primary"),
            ("axe_1H_hatchet", "axe", "1H", "hatchet", "primary"),
            ("axe_2H_greataxe", "axe", "2H", "greataxe", "primary"),
            ("blunt_1H_mace", "blunt", "1H", "mace", "primary"),
            ("blunt_2H_warhammer", "blunt", "2H", "two_handed_warhammer", "primary"),
            ("throw_axes_throw", "throwing", "throw", "throwing_axes", "primary"),
            ("throw_axes_melee", "throwing", "melee", "throwing_axes", "secondary"),
            ("javelins_throw", "throwing", "throw", "light_javelins", "primary"),
            ("javelins_melee", "throwing", "melee", "light_javelins", "secondary"),
        ]
    )
    return rows


def write_full_weapon_armor_proxy_simulation_csv(
    *,
    out_path: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> Path:
    """Ranged + curated melee/thrown, Q3, vanilla+mod: static vs armor-decay totals over N hits."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    q_idx = SIM_QUALITY_Q_INDEX
    n_hits = SIM_DECAY_NUM_HITS
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "sim_id",
                "category",
                "hand_label",
                "weapon_id",
                "weapon_mode",
                "quality",
                "dataset",
                "armor_profile",
                "mitigation_base",
                "armor_hp_max_fictional",
                "n_hits",
                "damage",
                "ignoresArmor",
                "armorDamage",
                "attackSpeed",
                "precision",
                "total_dealt_hp_static",
                "total_dealt_hp_armor_decay",
                "expected_dps_proxy_static",
                "expected_dps_proxy_decay",
            ]
        )
        for sim_id, category, hand, wid, wmode in sim_curated_weapon_entries():
            for dataset in ("vanilla", "mod"):
                stats = stats_for_sim_row(
                    wid,
                    wmode,
                    q_idx,
                    dataset=dataset,
                    vmap=vmap,
                    mmap=mmap,
                    wqs_vanilla=wqs_vanilla,
                    wqs_mod=wqs_mod,
                )
                for profile, m0 in MELEE_ARMOR_PROXY_PROFILES:
                    hp_max = ARMOR_HP_MAX_BY_PROFILE[profile]
                    tot_st = total_dealt_n_hits_static(stats, m0, n_hits)
                    tot_dc = total_dealt_n_hits_armor_decay(stats, m0, hp_max, n_hits)
                    w.writerow(
                        [
                            sim_id,
                            category,
                            hand,
                            wid,
                            wmode,
                            QUALITIES[q_idx],
                            dataset,
                            profile,
                            f"{m0:.2f}",
                            f"{hp_max:.1f}",
                            str(n_hits),
                            f"{SHARED.round2(stats['damage']):.2f}",
                            f"{SHARED.round2(stats['ignoresArmor']):.4f}",
                            f"{SHARED.round2(stats['armorDamage']):.2f}",
                            f"{SHARED.round2(stats['attackSpeed']):.2f}",
                            f"{SHARED.round2(stats['precision']):.3f}",
                            f"{SHARED.round2(tot_st):.2f}",
                            f"{SHARED.round2(tot_dc):.2f}",
                            f"{SHARED.round2(expected_dps_proxy_from_total_dealt(tot_st, stats, n_hits)):.2f}",
                            f"{SHARED.round2(expected_dps_proxy_from_total_dealt(tot_dc, stats, n_hits)):.2f}",
                        ]
                    )
    return out_path


def write_armor_proxy_flat_csv(
    *,
    out_path: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
) -> Path:
    """Ranged bows/crossbows + all melee/throwing modes × quality × vanilla|mod × armor profiles."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "mode_key",
                "weapon_id",
                "weapon_mode",
                "quality",
                "dataset",
                "armor_profile",
                "flat_mitigation_proxy",
                "damage_raw",
                "ignoresArmor",
                "precision",
                "attackSpeed",
                "dealt_hp_damage_proxy",
                "expected_dps_armor_proxy",
                "armorDamage_raw_not_in_hp_proxy",
            ]
        )
        for wid in RANGED_WEAPON_IDS:
            for dataset, wqs, patch in (
                ("vanilla", wqs_vanilla, None),
                ("mod", wqs_mod, mmap.get(wid)),
            ):
                merged = SHARED.merge_ranged(vmap[wid], patch)
                for q_i, q in enumerate(QUALITIES):
                    stats = ranged_stats_at_q_with_armor_damage(merged, wqs, q_i)
                    for profile, mit in MELEE_ARMOR_PROXY_PROFILES:
                        dealt = melee_dealt_hp_proxy(stats, mit)
                        edps = melee_expected_dps_armor_proxy(stats, mit)
                        w.writerow(
                            [
                                wid,
                                wid,
                                "primary",
                                q,
                                dataset,
                                profile,
                                f"{mit:.2f}",
                                f"{SHARED.round2(stats['damage']):.2f}",
                                f"{SHARED.round2(stats['ignoresArmor']):.4f}",
                                f"{SHARED.round2(stats['precision']):.3f}",
                                f"{SHARED.round2(stats['attackSpeed']):.2f}",
                                f"{SHARED.round2(dealt):.2f}",
                                f"{SHARED.round2(edps):.2f}",
                                f"{SHARED.round2(stats['armorDamage']):.2f}",
                            ]
                        )
        for mk in sorted(MODE_SPECS.keys()):
            spec = MODE_SPECS[mk]
            for dataset, wqs, patch in (
                ("vanilla", wqs_vanilla, None),
                ("mod", wqs_mod, mmap.get(spec.weapon_id)),
            ):
                merged = SHARED.merge_ranged(vmap[spec.weapon_id], patch)
                series = series_for_mode(merged, spec.mode, wqs)
                for q_i, q in enumerate(QUALITIES):
                    stats = series[q_i]
                    for profile, mit in MELEE_ARMOR_PROXY_PROFILES:
                        dealt = melee_dealt_hp_proxy(stats, mit)
                        edps = melee_expected_dps_armor_proxy(stats, mit)
                        w.writerow(
                            [
                                mk,
                                spec.weapon_id,
                                spec.mode,
                                q,
                                dataset,
                                profile,
                                f"{mit:.2f}",
                                f"{SHARED.round2(stats['damage']):.2f}",
                                f"{SHARED.round2(stats['ignoresArmor']):.4f}",
                                f"{SHARED.round2(stats['precision']):.3f}",
                                f"{SHARED.round2(stats['attackSpeed']):.2f}",
                                f"{SHARED.round2(dealt):.2f}",
                                f"{SHARED.round2(edps):.2f}",
                                f"{SHARED.round2(stats['armorDamage']):.2f}",
                            ]
                        )
    return out_path


def _armor_proxy_vanilla_mod_heatmap_pair(
    data_v: list[list[float]],
    data_m: list[list[float]],
    row_labels: list[str],
    *,
    suptitle: str,
    out_path: Path,
    y_axis_label: str = "Weapon / mode",
) -> Path:
    """Two panels (vanilla | mod), same vmin/vmax for fair color comparison."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    flat = [x for row in data_v + data_m for x in row]
    vmin, vmax = min(flat), max(flat)
    if math.isclose(vmin, vmax):
        vmax = vmin + 1e-9
    n = len(data_v)
    ncol = len(MELEE_ARMOR_PROXY_PROFILES)
    fig_h = max(4.2, 0.38 * n + 1.2)
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(12.0, fig_h), sharey=True)
    xticklabels = [p[0] for p in MELEE_ARMOR_PROXY_PROFILES]
    im_last = None
    for ax, data, subtitle in (
        (ax0, data_v, "Vanilla (base + quality tables)"),
        (ax1, data_m, "Mod (Equipment.json + quality tables)"),
    ):
        im_last = ax.imshow(data, aspect="auto", cmap="viridis", vmin=vmin, vmax=vmax)
        ax.set_xticks(range(ncol))
        ax.set_xticklabels(xticklabels, rotation=20, ha="right")
        ax.set_yticks(range(n))
        ax.set_yticklabels(row_labels, fontsize=8)
        ax.set_xlabel("Armor profile (flat mitigation proxy)")
        ax.set_title(subtitle, fontsize=10)
    ax0.set_ylabel(y_axis_label)
    fig.suptitle(suptitle, fontsize=11)
    assert im_last is not None
    fig.colorbar(im_last, ax=[ax0, ax1], label="Q3 expected DPS proxy (shared scale)", shrink=0.82)
    plt.tight_layout()
    SHARED.savefig_png(fig, out_path, dpi=150, tight=True)
    plt.close(fig)
    return out_path


def plot_armor_proxy_ranged_heatmap(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    """Rows = bow/crossbow ids, cols = armor profiles; cell = Q3 mod `expected_dps_armor_proxy`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    q_idx = SIM_QUALITY_Q_INDEX
    n = len(RANGED_WEAPON_IDS)
    ncol = len(MELEE_ARMOR_PROXY_PROFILES)
    data: list[list[float]] = []
    for wid in RANGED_WEAPON_IDS:
        merged = SHARED.merge_ranged(vmap[wid], mmap.get(wid))
        stats = ranged_stats_at_q_with_armor_damage(merged, wqs_mod, q_idx)
        data.append([melee_expected_dps_armor_proxy(stats, mit) for _, mit in MELEE_ARMOR_PROXY_PROFILES])
    fig_h = max(4.2, 0.38 * n + 1.2)
    fig, ax = plt.subplots(figsize=(6.8, fig_h))
    im = ax.imshow(data, aspect="auto", cmap="viridis")
    ax.set_xticks(range(ncol))
    ax.set_xticklabels([p[0] for p in MELEE_ARMOR_PROXY_PROFILES], rotation=20, ha="right")
    ax.set_yticks(range(n))
    ax.set_yticklabels(list(RANGED_WEAPON_IDS), fontsize=8)
    ax.set_xlabel("Armor profile (flat mitigation proxy)")
    ax.set_ylabel("Weapon")
    fig.colorbar(im, ax=ax, label="Q3 mod expected DPS proxy (dealt/AT×precision)")
    fig.suptitle("Bows & crossbows — flat armor expected DPS proxy (Q3 mod)", fontsize=11)
    plt.tight_layout()
    outp = out_dir / "armor_proxy_heatmap_ranged.png"
    SHARED.savefig_png(fig, outp, dpi=150, tight=True)
    plt.close(fig)
    return outp


def plot_armor_proxy_melee_category_heatmaps(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
    out_dir: Path,
) -> list[Path]:
    """Per category: rows = mode_keys, cols = armor profiles; cell = Q3 mod `expected_dps_armor_proxy`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    q_idx = 2  # Q3
    for group_name, mode_keys in CATEGORY_GROUPS.items():
        n = len(mode_keys)
        ncol = len(MELEE_ARMOR_PROXY_PROFILES)
        data: list[list[float]] = []
        for mk in mode_keys:
            spec = MODE_SPECS[mk]
            merged = SHARED.merge_ranged(vmap[spec.weapon_id], mmap.get(spec.weapon_id))
            stats = series_for_mode(merged, spec.mode, wqs_mod)[q_idx]
            row = [melee_expected_dps_armor_proxy(stats, mit) for _, mit in MELEE_ARMOR_PROXY_PROFILES]
            data.append(row)
        fig_h = max(4.2, 0.38 * n + 1.2)
        fig, ax = plt.subplots(figsize=(6.8, fig_h))
        im = ax.imshow(data, aspect="auto", cmap="viridis")
        ax.set_xticks(range(ncol))
        ax.set_xticklabels([p[0] for p in MELEE_ARMOR_PROXY_PROFILES], rotation=20, ha="right")
        ax.set_yticks(range(n))
        ax.set_yticklabels([MODE_SPECS[mk].label for mk in mode_keys], fontsize=8)
        ax.set_xlabel("Armor profile (flat mitigation proxy)")
        ax.set_ylabel("Weapon / mode")
        fig.colorbar(im, ax=ax, label="Q3 mod expected DPS proxy (dealt/AT×precision)")
        fig.suptitle(
            f"{group_name.replace('_', ' ')} — flat armor expected DPS proxy (Q3 mod)",
            fontsize=11,
        )
        plt.tight_layout()
        slug = ARMOR_PROXY_HEATMAP_SLUG.get(group_name, group_name)
        outp = out_dir / f"armor_proxy_heatmap_{slug}.png"
        SHARED.savefig_png(fig, outp, dpi=150, tight=True)
        plt.close(fig)
        out_paths.append(outp)
    return out_paths


def plot_armor_proxy_melee_category_compare_heatmaps(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> list[Path]:
    """Per category: vanilla | mod panels, Q3, same rows as mod-only heatmaps; shared color scale."""
    out_paths: list[Path] = []
    q_idx = SIM_QUALITY_Q_INDEX
    for group_name, mode_keys in CATEGORY_GROUPS.items():
        data_v: list[list[float]] = []
        data_m: list[list[float]] = []
        labels: list[str] = []
        for mk in mode_keys:
            spec = MODE_SPECS[mk]
            mv = SHARED.merge_ranged(vmap[spec.weapon_id], None)
            mm = SHARED.merge_ranged(vmap[spec.weapon_id], mmap.get(spec.weapon_id))
            sv = series_for_mode(mv, spec.mode, wqs_vanilla)[q_idx]
            sm = series_for_mode(mm, spec.mode, wqs_mod)[q_idx]
            data_v.append([melee_expected_dps_armor_proxy(sv, mit) for _, mit in MELEE_ARMOR_PROXY_PROFILES])
            data_m.append([melee_expected_dps_armor_proxy(sm, mit) for _, mit in MELEE_ARMOR_PROXY_PROFILES])
            labels.append(MODE_SPECS[mk].label)
        slug = ARMOR_PROXY_HEATMAP_SLUG.get(group_name, group_name)
        outp = out_dir / f"armor_proxy_heatmap_compare_{slug}.png"
        _armor_proxy_vanilla_mod_heatmap_pair(
            data_v,
            data_m,
            labels,
            suptitle=f"{group_name.replace('_', ' ')} — Q3 expected DPS proxy (vanilla vs mod)",
            out_path=outp,
        )
        out_paths.append(outp)
    return out_paths


def plot_armor_proxy_ranged_compare_heatmap(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    """Bows/crossbows: vanilla | mod, Q3, shared color scale."""
    q_idx = SIM_QUALITY_Q_INDEX
    data_v: list[list[float]] = []
    data_m: list[list[float]] = []
    labels = list(RANGED_WEAPON_IDS)
    for wid in RANGED_WEAPON_IDS:
        v_stats = ranged_stats_at_q_with_armor_damage(
            SHARED.merge_ranged(vmap[wid], None), wqs_vanilla, q_idx
        )
        m_stats = ranged_stats_at_q_with_armor_damage(
            SHARED.merge_ranged(vmap[wid], mmap.get(wid)), wqs_mod, q_idx
        )
        data_v.append([melee_expected_dps_armor_proxy(v_stats, mit) for _, mit in MELEE_ARMOR_PROXY_PROFILES])
        data_m.append([melee_expected_dps_armor_proxy(m_stats, mit) for _, mit in MELEE_ARMOR_PROXY_PROFILES])
    outp = out_dir / "armor_proxy_heatmap_compare_ranged.png"
    _armor_proxy_vanilla_mod_heatmap_pair(
        data_v,
        data_m,
        labels,
        suptitle="Bows & crossbows — Q3 expected DPS proxy (vanilla vs mod)",
        out_path=outp,
        y_axis_label="Weapon",
    )
    return outp


def _median_expected_dps_proxy_across_modes(
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
    q_idx: int,
    mode_keys: list[str],
) -> list[float]:
    """One value per armor profile: median of Q3 mod expected DPS proxy over all modes in the group."""
    ncol = len(MELEE_ARMOR_PROXY_PROFILES)
    buckets: list[list[float]] = [[] for _ in range(ncol)]
    for mk in mode_keys:
        spec = MODE_SPECS[mk]
        merged = SHARED.merge_ranged(vmap[spec.weapon_id], mmap.get(spec.weapon_id))
        stats = series_for_mode(merged, spec.mode, wqs_mod)[q_idx]
        for j, (_, mit) in enumerate(MELEE_ARMOR_PROXY_PROFILES):
            buckets[j].append(melee_expected_dps_armor_proxy(stats, mit))
    return [statistics.median(b) for b in buckets]


def _median_expected_dps_proxy_ranged_weapons(
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
    q_idx: int,
) -> list[float]:
    ncol = len(MELEE_ARMOR_PROXY_PROFILES)
    buckets: list[list[float]] = [[] for _ in range(ncol)]
    for wid in RANGED_WEAPON_IDS:
        merged = SHARED.merge_ranged(vmap[wid], mmap.get(wid))
        stats = ranged_stats_at_q_with_armor_damage(merged, wqs_mod, q_idx)
        for j, (_, mit) in enumerate(MELEE_ARMOR_PROXY_PROFILES):
            buckets[j].append(melee_expected_dps_armor_proxy(stats, mit))
    return [statistics.median(b) for b in buckets]


def _row_normalize_max(row: list[float]) -> list[float]:
    m = max(row) if row else 1.0
    if m <= 0.0:
        m = 1e-9
    return [x / m for x in row]


def plot_armor_proxy_type_vs_armor_matchup(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    """Weapon-type rows × armor columns: (1) family median Q3 mod EDPS proxy, (2) row ÷ row max (affinity)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    q_idx = SIM_QUALITY_Q_INDEX
    row_labels: list[str] = []
    data_abs: list[list[float]] = []
    for label, gkey in ARMOR_PROXY_TYPE_VS_ARMOR_ROWS:
        row_labels.append(label)
        if gkey is None:
            data_abs.append(_median_expected_dps_proxy_ranged_weapons(vmap, mmap, wqs_mod, q_idx))
        else:
            mode_keys = CATEGORY_GROUPS[gkey]
            data_abs.append(_median_expected_dps_proxy_across_modes(vmap, mmap, wqs_mod, q_idx, mode_keys))
    data_rel = [_row_normalize_max(r) for r in data_abs]
    ncol = len(MELEE_ARMOR_PROXY_PROFILES)
    n = len(row_labels)
    xticklabels = [p[0] for p in MELEE_ARMOR_PROXY_PROFILES]
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(7.4, 7.8), sharex=True)
    im0 = ax0.imshow(data_abs, aspect="auto", cmap="viridis")
    ax0.set_yticks(range(n))
    ax0.set_yticklabels(row_labels, fontsize=9)
    ax0.set_ylabel("Weapon type (family median)")
    ax0.set_title("Median Q3 mod expected DPS proxy (modes within type; bows = median of 7)")
    fig.colorbar(im0, ax=ax0, label="Expected DPS proxy", shrink=0.85)
    im1 = ax1.imshow(data_rel, aspect="auto", cmap="magma", vmin=0.0, vmax=1.0)
    ax1.set_yticks(range(n))
    ax1.set_yticklabels(row_labels, fontsize=9)
    ax1.set_xticks(range(ncol))
    ax1.set_xticklabels(xticklabels, rotation=20, ha="right")
    ax1.set_xlabel("Armor profile (flat mitigation proxy)")
    ax1.set_ylabel("Weapon type (same as above)")
    ax1.set_title(
        "Each cell ÷ max(none, light, plate) in that row — retention vs that type's own peak (compare columns only)"
    )
    fig.colorbar(im1, ax=ax1, label="Fraction of that row’s max proxy (0–1)", shrink=0.85)
    fig.suptitle(
        "Weapon type vs armor — Q3 mod (family median + row-normalized matchup shape)",
        fontsize=11,
    )
    plt.tight_layout(rect=(0, 0, 1, 0.96))
    outp = out_dir / "armor_proxy_heatmap_type_vs_armor.png"
    SHARED.savefig_png(fig, outp, dpi=150, tight=True)
    plt.close(fig)
    return outp


def write_layer1_bundle(
    *,
    out_md: Path,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
) -> None:
    fams = ["spear", "sword", "axe", "blunt"]
    avg = {f: category_q3_average(f, vmap, mmap, wqs_mod) for f in fams}

    checks: list[tuple[str, bool, str]] = []
    checks.append(
        (
            "range: spear > sword > axe == blunt (Q3 avg)",
            avg["spear"]["range"] > avg["sword"]["range"] > avg["axe"]["range"]
            and abs(avg["axe"]["range"] - avg["blunt"]["range"]) < 1e-9,
            f"spear={avg['spear']['range']:.3f}, sword={avg['sword']['range']:.3f}, axe={avg['axe']['range']:.3f}, blunt={avg['blunt']['range']:.3f}",
        )
    )
    checks.append(
        (
            "ignoresArmor: spear > sword > axe > blunt (Q3 avg)",
            avg["spear"]["ignoresArmor"] > avg["sword"]["ignoresArmor"] > avg["axe"]["ignoresArmor"] > avg["blunt"]["ignoresArmor"],
            f"spear={avg['spear']['ignoresArmor']:.3f}, sword={avg['sword']['ignoresArmor']:.3f}, axe={avg['axe']['ignoresArmor']:.3f}, blunt={avg['blunt']['ignoresArmor']:.3f}",
        )
    )
    checks.append(
        (
            "armorDamage: blunt > axe > spear == sword (Q3 avg)",
            avg["blunt"]["armorDamage"] > avg["axe"]["armorDamage"] > avg["spear"]["armorDamage"]
            and abs(avg["spear"]["armorDamage"] - avg["sword"]["armorDamage"]) <= 0.05,
            f"blunt={avg['blunt']['armorDamage']:.3f}, axe={avg['axe']['armorDamage']:.3f}, spear={avg['spear']['armorDamage']:.3f}, sword={avg['sword']['armorDamage']:.3f}",
        )
    )
    checks.append(
        (
            "attackSpeed fast: sword < blunt < axe < spear (Q3 avg, lower is faster)",
            avg["sword"]["attackSpeed"] < avg["blunt"]["attackSpeed"] < avg["axe"]["attackSpeed"] < avg["spear"]["attackSpeed"],
            f"sword={avg['sword']['attackSpeed']:.3f}, blunt={avg['blunt']['attackSpeed']:.3f}, axe={avg['axe']['attackSpeed']:.3f}, spear={avg['spear']['attackSpeed']:.3f}",
        )
    )
    checks.append(
        (
            "precision: sword > blunt > axe > spear (Q3 avg)",
            avg["sword"]["precision"] > avg["blunt"]["precision"] > avg["axe"]["precision"] > avg["spear"]["precision"],
            f"sword={avg['sword']['precision']:.3f}, blunt={avg['blunt']['precision']:.3f}, axe={avg['axe']['precision']:.3f}, spear={avg['spear']['precision']:.3f}",
        )
    )
    checks.append(
        (
            "damage: axe > spear > sword > blunt (Q3 avg)",
            avg["axe"]["damage"] > avg["spear"]["damage"] > avg["sword"]["damage"] > avg["blunt"]["damage"],
            f"axe={avg['axe']['damage']:.3f}, spear={avg['spear']['damage']:.3f}, sword={avg['sword']['damage']:.3f}, blunt={avg['blunt']['damage']:.3f}",
        )
    )
    checks.append(
        (
            "meleeCover: spear > sword > axe > blunt (Q3 avg)",
            avg["spear"]["meleeCover"] > avg["sword"]["meleeCover"] > avg["axe"]["meleeCover"] > avg["blunt"]["meleeCover"],
            f"spear={avg['spear']['meleeCover']:.3f}, sword={avg['sword']['meleeCover']:.3f}, axe={avg['axe']['meleeCover']:.3f}, blunt={avg['blunt']['meleeCover']:.3f}",
        )
    )

    throw_modes = ["throwing_axes_throw", "throwing_axes_melee", "light_javelins_throw", "light_javelins_melee"]

    ia_cap_rows: list[tuple[str, str, str, float, float, bool]] = []
    # Core melee (primary only): per-weapon Q1–Q6 max vs family cap
    for family in ("sword", "spear", "axe", "blunt"):
        cap = IA_CAP_BY_FAMILY[family]
        for wid in CORE_MELEE_IDS_BY_FAMILY[family]:
            spec = MODE_SPECS[wid]
            merged = SHARED.merge_ranged(vmap[spec.weapon_id], mmap.get(spec.weapon_id))
            series = series_for_mode(merged, spec.mode, wqs_mod)
            mx = max(float(s["ignoresArmor"]) for s in series)
            ia_cap_rows.append((wid, spec.mode, family, mx, cap, mx <= cap + 1e-9))
    for mk in throw_modes:
        spec = MODE_SPECS[mk]
        merged = SHARED.merge_ranged(vmap[spec.weapon_id], mmap.get(spec.weapon_id))
        series = series_for_mode(merged, spec.mode, wqs_mod)
        mx = max(float(s["ignoresArmor"]) for s in series)
        cap = IA_CAP_BY_FAMILY[spec.family]
        ia_cap_rows.append((mk, spec.mode, spec.family, mx, cap, mx <= cap + 1e-9))

    lines: list[str] = [
        "# Melee/Throwing Layer 1 — evaluation bundle",
        "",
        "Auto-generated by `tools/plot_melee_throwing_quality_comparison.py`.",
        "",
        "## Outputs",
        "",
        "- same tier: `quality_charts/melee_throwing/same_tier/<tier>/`",
        "- by category: `quality_charts/melee_throwing/by_category/<category>/` — per stat: "
        "`{group}_{stat}_Q1_Q6_vanilla_vs_mod.png` (grid) and `{group}_{stat}_all_weapons_overlay.png` (overlay), "
        "same pattern as ranged `tools/plot_weapon_quality_comparison.py`",
        "- summaries: `quality_charts/melee_throwing/script/same_tier_q1_q6_summary.csv`, `quality_charts/melee_throwing/script/by_category_q1_q6_summary.csv`",
        "- flat-armor proxy CSV: `quality_charts/armor_proxy/armor_proxy_flat.csv`",
        "- armor proxy heatmap how-to (this folder): `quality_charts/armor_proxy/README.md`",
        "- flat-armor proxy heatmaps (Q3 mod): `quality_charts/armor_proxy/armor_proxy_heatmap_ranged.png`, "
        "`quality_charts/armor_proxy/armor_proxy_heatmap_{sword,spear,axe,blunt}.png`",
        "- flat-armor proxy **vanilla vs mod** heatmaps (Q3, shared color scale): "
        "`quality_charts/armor_proxy/armor_proxy_heatmap_compare_ranged.png`, "
        "`quality_charts/armor_proxy/armor_proxy_heatmap_compare_{sword,spear,axe,blunt}.png`",
        "- weapon **type vs armor** summary (Q3 mod): `quality_charts/armor_proxy/armor_proxy_heatmap_type_vs_armor.png`",
        "- full-weapon Q3 sim (ranged + curated melee, static vs armor decay): "
        "`quality_charts/armor_proxy/armor_proxy_sim_Q3_n20.csv`",
        "",
        "## Q3 category average checks (mod, computed values)",
        "",
        "| Check | OK | Detail |",
        "|---|---|---|",
    ]
    for t, ok, d in checks:
        lines.append(f"| {t} | {'yes' if ok else 'no'} | `{d}` |")
    lines += [
        "",
        "## `ignoresArmor` policy caps (core melee primary + throwing modes, Q1–Q6 max)",
        "",
        "Family caps: sword `0.32`, spear `0.50`, axe `0.32`, blunt `0.18` (see design policy).",
        "",
        "| entry | weapon_mode | family | max ignoresArmor | cap | within cap |",
        "|---|---|---|---|---|---|",
    ]
    for entry, wmode, family, mx, cap, ok in ia_cap_rows:
        lines.append(
            f"| {entry} | {wmode} | {family} | {mx:.4f} | {cap:.2f} | {'yes' if ok else 'no'} |"
        )
    all_ia_ok = all(x[5] for x in ia_cap_rows)
    lines += [
        "",
        "| Summary | OK |",
        "|---|---|",
        f"| All category-order checks | {'yes' if all(x[1] for x in checks) else 'no'} |",
        f"| All ignoresArmor cap checks (melee + throwing) | {'yes' if all_ia_ok else 'no'} |",
        "",
        "## Flat armor mitigation proxy (balance read, not game-accurate)",
        "",
        "Same scalar model as ranged `tools/plot_weapon_quality_comparison.py` layer-1:",
        "`dealt_hp = damage × (1 − mitigation × (1 − ignoresArmor))` when `mitigation > 0`; `mitigation = 0` is unarmored.",
        "",
        "**Profiles** (intended read):",
        "",
        "| profile | mitigation | note |",
        "|---|---|---|",
        "| none | 0.00 | 鎧なし |",
        "| light | 0.28 | 軽装相当（遠隔 `ARMOR_PROXY_PROFILES.light` と同じ） |",
        "| plate_iron | 0.68 | 重装・板金寄り（遠隔 `heavy` と同じスカラー; 鉄板専用ではない） |",
        "",
        "**Expected DPS proxy**: `dealt_hp / attackSpeed × precision` (距離・`precisionFalloff` は未使用)。",
        "従来の「固定軽減」行だけでは `armorDamage` が HP 被ダメに入らない（鈍器・斧の防具割りが見えにくい）。",
        "",
        "**Compare heatmaps** (`armor_proxy_heatmap_compare_*.png`): 同じ行（武器/モード）・列（鎧プロファイル）で **左=vanilla**、**右=mod**。"
        " **色スケールは左右共通**なので、同じ明るさは「同じ代理DPS」としてパネル間で比較できる。",
        "",
        "**Type vs armor** (`armor_proxy_heatmap_type_vs_armor.png`): 行は **武器系統5種**（剣・槍+投槍・斧+投斧・鈍器・弓弩7本）、列は鎧3種。"
        " **上段**は各鎧列について系統内モード（弓は7武器）の **中央値**期待DPS代理で **武器種同士**の強さ比較の目安に使う（両手など外れ値の平均押し上げを抑える）。"
        " **下段**は武器種同士の比較ではなく、**武器種ごとに**鎧を重くしたときピークからどれだけ残るか（鎧の影響の受け方）だけを見る；**同じ行の左→右**のみ比較し、行をまたいだ明暗は見ない。",
        "",
        "### 全武器キュレート + 防具耐久で軽減が落ちる擬似モデル（`armor_proxy_sim_Q3_n20.csv`）",
        "",
        "- **品質**: すべて **Q3**（中間ティア）。",
        "- **射撃**: 弓・クロスボウ **7 種すべて**（遠隔スクリプトの `WEAPON_IDS` と同一）。",
        "- **近接・投擲（キュレート列の代表選び）**: 目的は **全譜面の網羅ではなく、調整の効きを読むための最小セット**。"
        " 原則: (1) **1H と 2H が両方ある系**は中間寄りの **1H+2H** を含めてアーキタイプの幅を出す、"
        "(2) **槍はデータが両手寄り**なら中間の **1 本＋投槍の throw/melee** で別表面を出す、"
        "(3) **投擲は primary/secondary** の両方（投げと近接が別バランス）、"
        "(4) **遠隔の sim 行は 7 本すべて**（ティア横断の確認用）。"
        " 具体例は `sim_curated_weapon_entries()` の docstring を参照。",
        "- **連撃**: 同一ステータスで **20 ヒット**合算。",
        "- **decay 列**: 仮想防具 HP `armor_hp_max`（`none=0` / `light=100` / `plate_iron=280`）を開始値とし、各ヒット後に `armor_hp -= armorDamage`（品質合成後）。",
        "  その時点の軽減 `mitigation = mitigation_base × (armor_hp / armor_hp_max)`（`armor_hp_max=0` の profile は鎧なし扱い）。",
        "  各ヒットの HP ダメは従来どおり `damage × (1 − mitigation × (1 − ignoresArmor))`。",
        "- **static 列**: 各ヒット同一 `mitigation_base`（従来フラット代理）。",
        "",
        "**Outputs**: `quality_charts/armor_proxy/armor_proxy_flat.csv` と",
        "`quality_charts/armor_proxy/armor_proxy_heatmap_*.png`（mod のみ）と "
        "`armor_proxy_heatmap_compare_*.png`（vanilla|mod）、"
        "`armor_proxy_heatmap_type_vs_armor.png`（系統×鎧）、",
        "`quality_charts/armor_proxy/armor_proxy_sim_Q3_n20.csv`。",
        "ヒートマップの読み方の全文: `quality_charts/armor_proxy/README.md`。",
        "",
    ]
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    vmap, mmap, wqs_vanilla, wqs_mod = merged_item_maps()
    for out_dir in (OUT_SAME_TIER, OUT_BY_CATEGORY, OUT_SCRIPT, OUT_ARMOR_PROXY):
        out_dir.mkdir(parents=True, exist_ok=True)

    for group_name, mode_keys in SAME_TIER_GROUPS.items():
        tier_dir = OUT_SAME_TIER / group_name
        for stat in STAT_SPECS:
            print(
                plot_group_stat(
                    group_name=group_name,
                    mode_keys=mode_keys,
                    stat=stat,
                    out_dir=tier_dir,
                    vmap=vmap,
                    mmap=mmap,
                    wqs_vanilla=wqs_vanilla,
                    wqs_mod=wqs_mod,
                )
            )
        for mitigation_label, mitigation in (("light", 0.28), ("heavy", 0.68)):
            print(
                plot_group_expected_armored_dps(
                    group_name=group_name,
                    mode_keys=mode_keys,
                    mitigation_label=mitigation_label,
                    mitigation=mitigation,
                    out_dir=tier_dir,
                    vmap=vmap,
                    mmap=mmap,
                    wqs_vanilla=wqs_vanilla,
                    wqs_mod=wqs_mod,
                )
            )

    for group_name, mode_keys in CATEGORY_GROUPS.items():
        cat_dir = OUT_BY_CATEGORY / group_name
        for stat in STAT_SPECS:
            print(
                plot_category_group_stat_grid(
                    group_name=group_name,
                    mode_keys=mode_keys,
                    stat=stat,
                    out_dir=cat_dir,
                    vmap=vmap,
                    mmap=mmap,
                    wqs_vanilla=wqs_vanilla,
                    wqs_mod=wqs_mod,
                )
            )
            print(
                plot_category_group_stat_overlay(
                    group_name=group_name,
                    mode_keys=mode_keys,
                    stat=stat,
                    out_dir=cat_dir,
                    vmap=vmap,
                    mmap=mmap,
                    wqs_vanilla=wqs_vanilla,
                    wqs_mod=wqs_mod,
                )
            )

    tier_csv = OUT_SCRIPT / "same_tier_q1_q6_summary.csv"
    write_summary_csv(
        group_type="same_tier",
        groups=SAME_TIER_GROUPS,
        out_path=tier_csv,
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
    )
    print(tier_csv)

    category_csv = OUT_SCRIPT / "by_category_q1_q6_summary.csv"
    write_summary_csv(
        group_type="by_category",
        groups=CATEGORY_GROUPS,
        out_path=category_csv,
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
    )
    print(category_csv)

    ap_csv = write_armor_proxy_flat_csv(
        out_path=OUT_ARMOR_PROXY / "armor_proxy_flat.csv",
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
    )
    print(ap_csv)
    full_sim_csv = write_full_weapon_armor_proxy_simulation_csv(
        out_path=OUT_ARMOR_PROXY / "armor_proxy_sim_Q3_n20.csv",
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
    )
    print(full_sim_csv)
    for hp in plot_armor_proxy_melee_category_heatmaps(
        vmap=vmap, mmap=mmap, wqs_mod=wqs_mod, out_dir=OUT_ARMOR_PROXY
    ):
        print(hp)
    ranged_hm = plot_armor_proxy_ranged_heatmap(
        vmap=vmap, mmap=mmap, wqs_mod=wqs_mod, out_dir=OUT_ARMOR_PROXY
    )
    print(ranged_hm)
    for hp in plot_armor_proxy_melee_category_compare_heatmaps(
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
        out_dir=OUT_ARMOR_PROXY,
    ):
        print(hp)
    ranged_cmp = plot_armor_proxy_ranged_compare_heatmap(
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
        out_dir=OUT_ARMOR_PROXY,
    )
    print(ranged_cmp)
    print(
        plot_armor_proxy_type_vs_armor_matchup(
            vmap=vmap, mmap=mmap, wqs_mod=wqs_mod, out_dir=OUT_ARMOR_PROXY
        )
    )

    bundle_path = OUT_BASE / "layer1_eval_bundle.md"
    write_layer1_bundle(out_md=bundle_path, vmap=vmap, mmap=mmap, wqs_mod=wqs_mod)
    print(bundle_path)


if __name__ == "__main__":
    main()

"""
Compare vanilla vs this mod fork ranged weapon stats at Q1–Q6 using
vanilla Items/Equipment.json + Items/WeaponQualitySettings.json, merged with
this folder's Data/Models/Equipment.json patches and optional
Data/Models/WeaponQualitySettings.json (replaces the TwoHandBow / TwoHandCrossbow
rows in the vanilla quality table when present, including crossbow ``rangeMultiplier``).

This folder is laid out like a Going Medieval mod (ModInfo, Data/Models, …).
Vanilla Items are resolved from the installed game (Steam path / libraryfolders.vdf)
or GOING_MEDIEVAL_ITEMS. Mod patches always come from this repo's Data/Models only
(do not point the script at another mod's Equipment.json). This util folder is
typically under Documents/Foxy Voxel/Going Medieval/Mods/....

Expected-DPS proxy metrics (see BOW_DESIGN_TARGETS.md, same formulas here).
Nominal DPS (damage / attackSpeed) is used internally but **not** written as its own chart.

- Expected DPS = (damage / attackSpeed) * precision  (base hit, no distance falloff)
- Hit at distance d = max(0, min(1, precision - precisionFalloff * d)); if d > range, hit = 0
- Distance-specific expected DPS at d = (damage / attackSpeed) * hit(d)
- Charts use d in {10, 18, 22, 25} m as near / mid / far / ultra-far comparison distances (abstract units).

Also writes an optional **layer-1 bundle** (flat-armor proxy CSVs + `ignoresArmor` policy CSV
+ `layer1_eval_bundle.md`) with Q3 order checks, **`ignoresArmor` cap / bow-vs-cross ordering**
(see `BOW_DESIGN_TARGETS.md`), cover vs buckler, move-mult doc vs `onEquipEffectors`, and Marksman memo.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
from decimal import ROUND_HALF_UP, Decimal
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

_THIS = Path(__file__).resolve()
_UTIL_ROOT = _THIS.parent.parent

MOD_EQUIPMENT = _UTIL_ROOT / "Data" / "Models" / "Equipment.json"
MOD_WEAPON_QUALITY = _UTIL_ROOT / "Data" / "Models" / "WeaponQualitySettings.json"
OUT_DIR = _UTIL_ROOT / "quality_charts" / "ranged"
SCRIPT_OUT_DIR = OUT_DIR / "script"

WEAPON_IDS = [
    "short_bow",
    "war_bow",
    "curved_bow",
    "long_bow",
    "light_crossbow",
    "crossbow",
    "heavy_crossbow",
]

# Overlay / per-panel line colours: bows = blue → green; crossbows = dark yellow/amber → red (no bright yellow).
WEAPON_LINE_COLORS_MOD: dict[str, str] = {
    "short_bow": "#1565C0",
    "war_bow": "#00838F",
    "curved_bow": "#2E7D32",
    "long_bow": "#1B5E20",
    "light_crossbow": "#9E7C0C",
    "crossbow": "#D84315",
    "heavy_crossbow": "#B71C1C",
}


def _weapon_rgba_vanilla(wid: str, alpha: float = 0.52) -> tuple[float, float, float, float]:
    r, g, b = mcolors.to_rgb(WEAPON_LINE_COLORS_MOD[wid])
    return (r, g, b, alpha)


# Fixed distances for "near / mid / far" expected DPS charts (BOW policy naming).
DPS_DISTANCE_NEAR_M = 10.0
DPS_DISTANCE_MID_M = 18.0
DPS_DISTANCE_FAR_M = 22.0
DPS_DISTANCE_ULTRA_FAR_M = 25.0

# Layer-1 optional bundle: flat armor mitigation proxy (not game-accurate).
# dealt = damage * (1 - mitigation * (1 - ignoresArmor)); mitigation=0 => unarmored.
ARMOR_PROXY_PROFILES: tuple[tuple[str, float], ...] = (
    ("none", 0.0),
    ("light", 0.28),
    ("medium", 0.48),
    ("heavy", 0.68),
)

# Q3 four-way chains from BOW_DESIGN_TARGETS.md (synthetic stats after WQS apply).
Q3_CHAIN_RANGE_ASC = ["crossbow", "heavy_crossbow", "curved_bow", "long_bow"]
Q3_CHAIN_DAMAGE_ASC = ["long_bow", "curved_bow", "crossbow", "heavy_crossbow"]
Q3_CHAIN_IA_ASC = ["long_bow", "curved_bow", "crossbow", "heavy_crossbow"]
Q3_CHAIN_ATTACKSPEED_ASC = ["curved_bow", "long_bow", "crossbow", "heavy_crossbow"]

# Vanilla shield id for rangedCover ceiling check (lowest rangedCover among common shields).
BUCKLER_SHIELD_ID = "buckler_shield"

# EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md — documented move-mult targets (not read from JSON).
DESIGN_RANGED_MOVE_MULT: dict[str, float] = {
    "short_bow": 1.00,
    "curved_bow": 0.95,
    "war_bow": 0.85,
    "long_bow": 0.75,
    "light_crossbow": 0.85,
    "crossbow": 0.75,
    "heavy_crossbow": 0.70,
}

# BOW_DESIGN_TARGETS.md — post-WQS ignoresArmor caps (all qualities).
IA_CAP_BOW = 0.70
IA_CAP_CROSSBOW = 0.85
BOW_IDS_IA_POLICY = ("short_bow", "war_bow", "curved_bow", "long_bow")
CROSSBOW_IDS_IA_POLICY = ("light_crossbow", "crossbow", "heavy_crossbow")
IA_POLICY_EPS = 1e-6

_GOING_MEDIEVAL_ITEMS_REL = Path("Going Medieval_Data") / "StreamingAssets" / "Items"


def round2(value: float) -> float:
    """
    Round to 2 decimal places (half away from zero), i.e. 第三位を四捨五入して第二位まで.
    Used for chart series and tabular exports (damage, range, DPS, etc.).
    """
    if value != value or math.isinf(value):
        return value
    return float(
        Decimal(str(float(value))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )


def savefig_png(fig, out_path: Path, *, dpi: int = 150, tight: bool = True) -> None:
    """Write PNG; tolerate ``bbox_inches='tight'`` issues and flaky Windows file opens."""
    import io

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if tight:
        try:
            fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
            return
        except OSError:
            pass
    try:
        fig.savefig(out_path, dpi=dpi)
        return
    except OSError:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi)
        out_path.write_bytes(buf.getvalue())


def _steam_install_from_registry() -> Path | None:
    if os.name != "nt":
        return None
    try:
        import winreg

        for key_path in (
            r"SOFTWARE\WOW6432Node\Valve\Steam",
            r"SOFTWARE\Valve\Steam",
        ):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as k:
                    val, _ = winreg.QueryValueEx(k, "InstallPath")
                    return Path(val)
            except OSError:
                continue
    except Exception:
        return None
    return None


def _steam_library_roots(steam_install: Path) -> list[Path]:
    roots: list[Path] = [steam_install]
    vdf = steam_install / "config" / "libraryfolders.vdf"
    if not vdf.is_file():
        return roots
    try:
        text = vdf.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'"path"\s+"([^"]+)"', text):
            raw = m.group(1).replace("\\\\", "\\")
            p = Path(raw)
            if p.is_dir():
                roots.append(p)
    except OSError:
        pass
    seen: set[str] = set()
    uniq: list[Path] = []
    for r in roots:
        key = str(r.resolve())
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    return uniq


def _going_medieval_items_dirs() -> list[Path]:
    suffix = Path("steamapps") / "common" / "Going Medieval" / _GOING_MEDIEVAL_ITEMS_REL
    dirs: list[Path] = []
    steam = _steam_install_from_registry()
    if steam is not None:
        for lib in _steam_library_roots(steam):
            candidate = lib / suffix
            if candidate.is_dir():
                dirs.append(candidate)
    return dirs


def resolve_vanilla_items_dir() -> Path:
    env = os.environ.get("GOING_MEDIEVAL_ITEMS", "").strip()
    if env:
        p = Path(env).expanduser()
        if (p / "Equipment.json").is_file():
            return p.resolve()
        raise FileNotFoundError(
            f"GOING_MEDIEVAL_ITEMS is set but Equipment.json not found: {p}"
        )
    for candidate in _going_medieval_items_dirs():
        if (candidate / "Equipment.json").is_file():
            return candidate.resolve()
    steam = _steam_install_from_registry()
    tried = str(steam) if steam else "(Steam registry path not found)"
    raise FileNotFoundError(
        "Could not find Going Medieval vanilla Items folder "
        "(…/Going Medieval_Data/StreamingAssets/Items). "
        f"Tried Steam install: {tried}. "
        "Set GOING_MEDIEVAL_ITEMS to that Items directory, or install the game via Steam."
    )


PWM_STAT_KEYS = {
    "damage",
    "ignoresArmor",
    "armorDamage",
    "buildingDamage",
    "precision",
    "precisionFalloff",
    "range",
    "attackSpeed",
    "projectileSpeed",
    "projectileArcHeight",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def repo_by_id(data: dict) -> dict[str, dict]:
    return {e["id"]: e for e in data["repository"]}


def merge_wqs_overlay(base_wqs: dict, overlay_path: Path) -> dict:
    """Replace weapon-type blocks that appear in the mod WeaponQualitySettings overlay.

    Appends overlay-only ids not present in vanilla ``repository`` (if any).
    """
    out = deepcopy(base_wqs)
    if not overlay_path.is_file():
        return out
    overlay = load_json(overlay_path)
    by_id = {b["id"]: b for b in overlay["repository"]}
    base_ids = {b.get("id") for b in out["repository"]}
    new_repo: list[dict] = []
    for b in out["repository"]:
        bid = b.get("id")
        if bid in by_id:
            new_repo.append(deepcopy(by_id[bid]))
        else:
            new_repo.append(deepcopy(b))
    for bid, block in by_id.items():
        if bid not in base_ids:
            new_repo.append(deepcopy(block))
    out["repository"] = new_repo
    return out


def merge_ranged(vanilla_item: dict, mod_patch: dict | None) -> dict:
    out = deepcopy(vanilla_item)
    if not mod_patch:
        return out
    pwm = out.setdefault("primaryWeaponMode", {})
    for k, v in mod_patch.items():
        if k == "id":
            continue
        if k in PWM_STAT_KEYS:
            pwm[k] = v
        else:
            out[k] = deepcopy(v)
    return out


def quality_rows(wqs: dict, weapon_type_key: str) -> list[dict]:
    for block in wqs["repository"]:
        if block["id"] == weapon_type_key:
            rows = block["qualitySettings"]
            rows = sorted(rows, key=lambda r: r["productQuality"])
            assert len(rows) == 6
            return rows
    raise KeyError(weapon_type_key)


def apply_quality(base: dict, row: dict) -> dict:
    def m(key: str, default: float = 1.0) -> float:
        return float(row.get(key, default))

    return {
        "damage": float(base["damage"]) * m("damageMultiplier"),
        "attackSpeed": float(base["attackSpeed"]) * m("attackSpeedMultiplier"),
        "range": float(base["range"]) * m("rangeMultiplier"),
        "precision": float(base.get("precision", 1)) * m("precisionMultiplier"),
        "precisionFalloff": float(base.get("precisionFalloff", 0))
        * m("precisionFalloffMultiplier"),
        "ignoresArmor": float(base.get("ignoresArmor", 0)) * m("ignoresArmorMultiplier"),
        "armorDamage": float(base.get("armorDamage", 0.0)) * m("armorDamageMultiplier"),
    }


def series_for_item(merged: dict, wqs: dict) -> list[dict]:
    pwm = merged["primaryWeaponMode"]
    wtype = pwm["weaponType"]
    rows = quality_rows(wqs, wtype)
    return [apply_quality(pwm, r) for r in rows]


def nominal_dps(stats: dict) -> float:
    spd = float(stats["attackSpeed"])
    if spd <= 0:
        return 0.0
    return float(stats["damage"]) / spd


def hit_chance_at_distance(stats: dict, distance: float) -> float:
    """Linear falloff; no hits beyond weapon range."""
    rng = float(stats["range"])
    if distance > rng:
        return 0.0
    raw = float(stats["precision"]) - float(stats["precisionFalloff"]) * float(distance)
    return max(0.0, min(1.0, raw))


def expected_dps(stats: dict) -> float:
    return nominal_dps(stats) * float(stats["precision"])


def distance_expected_dps(stats: dict, distance: float) -> float:
    return nominal_dps(stats) * hit_chance_at_distance(stats, distance)


def damage_after_flat_armor_proxy(
    damage: float, ignores_armor: float, mitigation: float
) -> float:
    """Scalar proxy: higher ignoresArmor bypasses more of flat mitigation."""
    if mitigation <= 0.0:
        return float(damage)
    ia = max(0.0, min(1.0, float(ignores_armor)))
    return float(damage) * (1.0 - mitigation * (1.0 - ia))


def nominal_armored_dps(stats: dict, mitigation: float) -> float:
    spd = float(stats["attackSpeed"])
    if spd <= 0:
        return 0.0
    d_eff = damage_after_flat_armor_proxy(
        float(stats["damage"]), float(stats["ignoresArmor"]), mitigation
    )
    return d_eff / spd


def distance_expected_armored_dps(
    stats: dict, distance: float, mitigation: float
) -> float:
    return nominal_armored_dps(stats, mitigation) * hit_chance_at_distance(
        stats, distance
    )


def per_shot_expected_damage(stats: dict, distance: float, mitigation: float) -> float:
    d_eff = damage_after_flat_armor_proxy(
        float(stats["damage"]), float(stats["ignoresArmor"]), mitigation
    )
    return d_eff * hit_chance_at_distance(stats, distance)


def _band_values(stats: dict, center: float) -> list[float]:
    distances = [center - 1.0, center, center + 1.0]
    return [distance_expected_dps(stats, d) for d in distances]


def _band_values_armored(
    stats: dict, center: float, mitigation: float
) -> list[float]:
    distances = [center - 1.0, center, center + 1.0]
    return [
        distance_expected_armored_dps(stats, d, mitigation) for d in distances
    ]


def _band_values_per_shot(
    stats: dict, center: float, mitigation: float
) -> list[float]:
    distances = [center - 1.0, center, center + 1.0]
    return [per_shot_expected_damage(stats, d, mitigation) for d in distances]


def write_layer1_armored_distance_dps_band_summary_csv(
    *,
    qualities: list[str],
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    bands: list[tuple[str, float]] = [
        ("near", DPS_DISTANCE_NEAR_M),
        ("mid", DPS_DISTANCE_MID_M),
        ("far", DPS_DISTANCE_FAR_M),
        ("ultra_far", DPS_DISTANCE_ULTRA_FAR_M),
    ]
    out_path = out_dir / "layer1_armored_distance_dps_band_summary.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "weapon_id",
                "quality",
                "dataset",
                "band",
                "armor_profile",
                "flat_mitigation_proxy",
                "center_m",
                "sample_distances_m",
                "mean_distance_expected_armored_dps",
                "min_distance_expected_armored_dps",
            ]
        )
        for wid in WEAPON_IDS:
            v_only = merge_ranged(vmap[wid], None)
            v_item = merge_ranged(vmap[wid], mmap.get(wid))
            v_series = series_for_item(v_only, wqs_vanilla)
            m_series = series_for_item(v_item, wqs_mod)
            for q_idx, q in enumerate(qualities):
                for dataset, stats in (("vanilla", v_series[q_idx]), ("mod", m_series[q_idx])):
                    for band_name, center in bands:
                        for profile, mitigation in ARMOR_PROXY_PROFILES:
                            vals = _band_values_armored(stats, center, mitigation)
                            mean_v = round2(sum(vals) / len(vals))
                            min_v = round2(min(vals))
                            writer.writerow(
                                [
                                    wid,
                                    q,
                                    dataset,
                                    band_name,
                                    profile,
                                    f"{mitigation:.2f}",
                                    f"{center:.0f}",
                                    f"{center - 1:.0f}/{center:.0f}/{center + 1:.0f}",
                                    f"{mean_v:.2f}",
                                    f"{min_v:.2f}",
                                ]
                            )
    return out_path


def write_layer1_per_shot_expected_damage_band_summary_csv(
    *,
    qualities: list[str],
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    bands: list[tuple[str, float]] = [
        ("near", DPS_DISTANCE_NEAR_M),
        ("mid", DPS_DISTANCE_MID_M),
        ("far", DPS_DISTANCE_FAR_M),
        ("ultra_far", DPS_DISTANCE_ULTRA_FAR_M),
    ]
    out_path = out_dir / "layer1_per_shot_expected_damage_band_summary.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "weapon_id",
                "quality",
                "dataset",
                "band",
                "armor_profile",
                "flat_mitigation_proxy",
                "center_m",
                "sample_distances_m",
                "mean_expected_damage_per_shot",
                "min_expected_damage_per_shot",
            ]
        )
        for wid in WEAPON_IDS:
            v_only = merge_ranged(vmap[wid], None)
            v_item = merge_ranged(vmap[wid], mmap.get(wid))
            v_series = series_for_item(v_only, wqs_vanilla)
            m_series = series_for_item(v_item, wqs_mod)
            for q_idx, q in enumerate(qualities):
                for dataset, stats in (("vanilla", v_series[q_idx]), ("mod", m_series[q_idx])):
                    for band_name, center in bands:
                        for profile, mitigation in ARMOR_PROXY_PROFILES:
                            vals = _band_values_per_shot(stats, center, mitigation)
                            mean_v = round2(sum(vals) / len(vals))
                            min_v = round2(min(vals))
                            writer.writerow(
                                [
                                    wid,
                                    q,
                                    dataset,
                                    band_name,
                                    profile,
                                    f"{mitigation:.2f}",
                                    f"{center:.0f}",
                                    f"{center - 1:.0f}/{center:.0f}/{center + 1:.0f}",
                                    f"{mean_v:.2f}",
                                    f"{min_v:.2f}",
                                ]
                            )
    return out_path


def _q3_stats_by_id(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs: dict,
    dataset: str,
) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for wid in WEAPON_IDS:
        v_only = merge_ranged(vmap[wid], None)
        v_item = merge_ranged(vmap[wid], mmap.get(wid))
        merged = v_only if dataset == "vanilla" else v_item
        series = series_for_item(merged, wqs)
        out[wid] = series[2]
    return out


def _format_required_skills(item: dict) -> str:
    rs = item.get("requiredSkills")
    if not rs:
        return "(key omitted)"
    parts: list[str] = []
    for entry in rs:
        if isinstance(entry, dict):
            parts.append(f"{entry.get('key','?')}={entry.get('value','?')}")
        else:
            parts.append(str(entry))
    return ", ".join(parts) if parts else "[]"


def _format_on_equip_effectors(item: dict) -> str:
    oe = item.get("onEquipEffectors")
    if not oe:
        return "—"
    try:
        return json.dumps(oe, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return str(oe)


def _weak_asc_chain_ok(
    ids: list[str], values: dict[str, float], eps: float = 1e-6
) -> tuple[bool, str]:
    """Each value <= next (+eps); allows ties (Q3 ignoresArmor long vs curved, etc.)."""
    vals = [values[i] for i in ids]
    detail = ", ".join(f"{ids[j]}={vals[j]:.4f}" for j in range(len(ids)))
    for a, b in zip(vals, vals[1:]):
        if a > b + eps:
            return False, detail
    return True, detail


def _ia_cap_for_weapon_id(wid: str) -> float | None:
    if wid in BOW_IDS_IA_POLICY:
        return IA_CAP_BOW
    if wid in CROSSBOW_IDS_IA_POLICY:
        return IA_CAP_CROSSBOW
    return None


def _mod_ia_matrix(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
) -> dict[str, list[float]]:
    """ignoresArmor per weapon id, Q1..Q6 (mod merge + mod WQS)."""
    out: dict[str, list[float]] = {}
    for wid in WEAPON_IDS:
        merged = merge_ranged(vmap[wid], mmap.get(wid))
        series = series_for_item(merged, wqs_mod)
        out[wid] = [float(s["ignoresArmor"]) for s in series]
    return out


def write_layer1_ignores_armor_policy_csv(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
    qualities: list[str],
    out_dir: Path,
) -> Path:
    """Per weapon × quality: mod ignoresArmor, design cap (if any), within_cap flag."""
    out_path = out_dir / "layer1_ignores_armor_policy_summary.csv"
    mat = _mod_ia_matrix(vmap=vmap, mmap=mmap, wqs_mod=wqs_mod)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "weapon_id",
                "quality",
                "ignores_armor_mod",
                "cap",
                "within_cap",
            ]
        )
        for wid in WEAPON_IDS:
            cap = _ia_cap_for_weapon_id(wid)
            cap_s = f"{cap:.2f}" if cap is not None else ""
            for q_idx, q in enumerate(qualities):
                val = mat[wid][q_idx]
                if cap is None:
                    ok_s = "n/a"
                else:
                    ok_s = "yes" if val <= cap + IA_POLICY_EPS else "no"
                writer.writerow(
                    [
                        wid,
                        q,
                        f"{val:.4f}",
                        cap_s,
                        ok_s,
                    ]
                )
    return out_path


def save_ignores_armor_mod_policy_overlay(
    *,
    qualities: list[str],
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    """
    Mod-only ignoresArmor vs quality, with horizontal caps for bows/crossbows
    (BOW_DESIGN_TARGETS.md).
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    for wid in WEAPON_IDS:
        merged = merge_ranged(vmap[wid], mmap.get(wid))
        y_m = [round2(float(s["ignoresArmor"])) for s in series_for_item(merged, wqs_mod)]
        c_mod = WEAPON_LINE_COLORS_MOD[wid]
        ax.plot(
            qualities,
            y_m,
            linestyle="-",
            linewidth=2.2,
            color=c_mod,
            marker="s",
            label=f"{wid} (mod)",
        )
    ax.axhline(
        IA_CAP_BOW,
        color="#6D4C41",
        linestyle="--",
        linewidth=1.2,
        label=f"Cap 弓 (all bows) ≤ {IA_CAP_BOW:.2f}",
    )
    ax.axhline(
        IA_CAP_CROSSBOW,
        color="#5D4037",
        linestyle=":",
        linewidth=1.4,
        label=f"Cap クロスボウ (all crossbows) ≤ {IA_CAP_CROSSBOW:.2f}",
    )
    ax.set_title(
        "Ignores armor (mod only) — policy caps (BOW_DESIGN_TARGETS.md)"
    )
    ax.set_xlabel("Quality")
    ax.set_ylabel("ignoresArmor (post-WQS)")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    out_path = out_dir / "ignoresArmor_mod_policy_overlay.png"
    savefig_png(fig, out_path, dpi=150, tight=True)
    plt.close(fig)
    return out_path


def write_layer1_eval_bundle_md(
    *,
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
    armored_csv_name: str,
    per_shot_csv_name: str,
    ia_policy_csv_name: str,
    qualities: list[str],
    ia_policy_chart_name: str,
) -> Path:
    """Draft layer-1 bundle: formulas, Q3 chains, ignoresArmor policy, cover, move, Marksman."""
    out_path = out_dir / "layer1_eval_bundle.md"
    lines: list[str] = [
        "# Layer 1 — evaluation bundle (draft A)",
        "",
        "Auto-generated by `tools/plot_weapon_quality_comparison.py`. "
        "**Policy**: layer-1 complementary checks (armor proxy, per-shot expectation, "
        "Q3 four-chain order, **`ignoresArmor` caps / bow ordering vs crossbows**, "
        "Marksman memo) are **delegated to this bundle** — see "
        "[`POLICY_SESSION_QUICK.md`](../../implementation_policies/core/POLICY_SESSION_QUICK.md) (再生成) and "
        "[`BOW_DESIGN_TARGETS.md`](../../implementation_policies/ranged/BOW_DESIGN_TARGETS.md) (帯域・階層・命中・装甲無視). "
        "**Not** a substitute for in-game armor math, skills, cover, or UI timing.",
        "",
        "## Proxy formulas",
        "",
        "- **Flat armor proxy**: `dealt = damage * (1 - mitigation * (1 - ignoresArmor))` "
        "with `mitigation` in `{0, 0.28, 0.48, 0.68}` for profiles "
        "`none` / `light` / `medium` / `heavy`.",
        "- **Armored distance expected DPS**: `(dealt / attackSpeed) * hit(d)` with the same "
        "`hit(d)` as distance-expected DPS charts (linear precision falloff, hard `range` cut).",
        "- **Per-shot expected damage (band mean)**: `dealt * hit(d)` averaged over center±1m.",
        "",
        "## Machine-readable outputs",
        "",
        f"- [`{armored_csv_name}`]({armored_csv_name})",
        f"- [`{per_shot_csv_name}`]({per_shot_csv_name})",
        f"- [`{ia_policy_csv_name}`]({ia_policy_csv_name})",
        "",
        "## Chart outputs (this bundle)",
        "",
        f"- **[`{ia_policy_chart_name}`]({ia_policy_chart_name})** — Mod のみの "
        "`ignoresArmor`（品質合成）と、弓/クロスの **キャップ参照線**（弓 ≤ "
        f"{IA_CAP_BOW:.2f}、クロス ≤ {IA_CAP_CROSSBOW:.2f}）。",
        "- `armorDamage_Q1_Q6_vanilla_vs_mod.png` / `armorDamage_all_weapons_overlay.png` — "
        "武器別 Q1–Q6 と全武器オーバーレイの **armor damage**（品質合成）。",
        "",
        "## Q3 synthetic stats — order checks ([`BOW_DESIGN_TARGETS.md`](../../implementation_policies/ranged/BOW_DESIGN_TARGETS.md) four-way chains)",
        "",
        "**Mod の合成 Q3のみ**（マージ後素体 × WQS）。バニラ Q3 表は出さない。",
        "",
        "Weak order: each stat must be `<=` the next (ties allowed; eps 1e-6). "
        "Values are **post-WQS** `primaryWeaponMode` stats.",
        "",
    ]
    chain_defs: list[tuple[str, list[str], str]] = [
        ("range (short → long)", Q3_CHAIN_RANGE_ASC, "range"),
        ("damage (low → high)", Q3_CHAIN_DAMAGE_ASC, "damage"),
        ("ignoresArmor (low → high)", Q3_CHAIN_IA_ASC, "ignoresArmor"),
        (
            "attackSpeed (fast → slow, numeric increase)",
            Q3_CHAIN_ATTACKSPEED_ASC,
            "attackSpeed",
        ),
    ]
    st_mod = _q3_stats_by_id(vmap=vmap, mmap=mmap, wqs=wqs_mod, dataset="mod")
    lines.append("| Chain | OK | Detail |")
    lines.append("|---|---|---|")
    for title, ids, key in chain_defs:
        vals = {i: float(st_mod[i][key]) for i in ids}
        ok, detail = _weak_asc_chain_ok(ids, vals)
        lines.append(f"| {title} | {'yes' if ok else 'no'} | `{detail}` |")
    lines.append("")

    # --- ignoresArmor design policy (mod, all qualities) ---
    mat = _mod_ia_matrix(vmap=vmap, mmap=mmap, wqs_mod=wqs_mod)
    lines.append(
        "## `ignoresArmor` — 方針チェック（Mod 合成・全品質）"
    )
    lines.append("")
    lines.append(
        "参照: [`BOW_DESIGN_TARGETS.md`](../../implementation_policies/ranged/BOW_DESIGN_TARGETS.md)「命中・装甲無視」確定目標。"
    )
    lines.append("")
    lines.append(
        "値は **マージ後素体 × Mod `WeaponQualitySettings`** の `primaryWeaponMode` 合成。"
    )
    lines.append("")
    lines.append(
        "**機械チェックの注意**: `war_bow` < `curved_bow` は **厳密不等号**（同値は `no`）。"
        "キャップは **全品質の最大値** で判定する。"
    )
    lines.append("")

    cap_rows: list[tuple[str, float, float | None, bool | None]] = []
    for wid in WEAPON_IDS:
        cap = _ia_cap_for_weapon_id(wid)
        mx = max(mat[wid])
        if cap is None:
            cap_rows.append((wid, mx, cap, None))
        else:
            ok_cap = mx <= cap + IA_POLICY_EPS
            cap_rows.append((wid, mx, cap, ok_cap))

    lines.append("| weapon_id | max ignoresArmor (Q1–Q6) | cap | OK |")
    lines.append("|---|---|---|---|")
    for wid, mx, cap, ok_cap in cap_rows:
        cap_s = f"{cap:.2f}" if cap is not None else "—"
        if ok_cap is None:
            ok_s = "n/a"
        else:
            ok_s = "yes" if ok_cap else "no"
        lines.append(f"| {wid} | {mx:.4f} | {cap_s} | {ok_s} |")
    lines.append("")

    per_q_checks: list[tuple[str, bool, str]] = []
    bow_ids = list(BOW_IDS_IA_POLICY)
    cross_ids = list(CROSSBOW_IDS_IA_POLICY)
    for q_idx, q in enumerate(qualities):
        max_b = max(mat[w][q_idx] for w in bow_ids)
        min_c = min(mat[w][q_idx] for w in cross_ids)
        ok_mx = max_b < min_c - IA_POLICY_EPS
        per_q_checks.append(
            (
                f"Each Q: max(4 bows) < min(3 crossbows) [{q}]",
                ok_mx,
                f"max_bows={max_b:.4f}, min_cross={min_c:.4f}",
            )
        )
        s_, w_, c_, l_ = (
            mat["short_bow"][q_idx],
            mat["war_bow"][q_idx],
            mat["curved_bow"][q_idx],
            mat["long_bow"][q_idx],
        )
        ok_short_low = (
            s_ <= w_ + IA_POLICY_EPS
            and s_ <= c_ + IA_POLICY_EPS
            and s_ <= l_ + IA_POLICY_EPS
        )
        per_q_checks.append(
            (
                f"short_bow lowest among four bows [{q}]",
                ok_short_low,
                f"short={s_:.4f}, war={w_:.4f}, curved={c_:.4f}, long={l_:.4f}",
            )
        )
        ok_w_lt_c = w_ < c_ - IA_POLICY_EPS
        per_q_checks.append(
            (
                f"war_bow < curved_bow [{q}]",
                ok_w_lt_c,
                f"war={w_:.4f}, curved={c_:.4f}",
            )
        )
        ok_l_le_c = l_ <= c_ + IA_POLICY_EPS
        per_q_checks.append(
            (
                f"long_bow ≤ curved_bow (Q3 sub-chain) [{q}]",
                ok_l_le_c,
                f"long={l_:.4f}, curved={c_:.4f}",
            )
        )

    lines.append("| Policy check | OK | Detail |")
    lines.append("|---|---|---|")
    for title, ok, detail in per_q_checks:
        lines.append(f"| {title} | {'yes' if ok else 'no'} | `{detail}` |")

    all_caps_ok = all(r[3] for r in cap_rows if r[3] is not None)
    all_per_q_ok = all(ok for _, ok, _ in per_q_checks)
    lines.append(
        f"| **All cap rows (bows + crossbows)** | {'yes' if all_caps_ok else 'no'} | "
        f"弓 ≤ {IA_CAP_BOW:.2f}; クロス ≤ {IA_CAP_CROSSBOW:.2f} |"
    )
    lines.append(
        f"| **All per-quality ordering checks** | "
        f"{'yes' if all_per_q_ok else 'no'} | See rows above |"
    )
    lines.append("")

    buck = vmap.get(BUCKLER_SHIELD_ID)
    if buck is None:
        buck_rc: float | None = None
        buck_note = (
            f"`{BUCKLER_SHIELD_ID}` がバニラ `Equipment.json` に無いため参照不可。"
        )
    else:
        buck_rc = float(buck.get("rangedCover") or 0.0)
        buck_note = (
            f"バニラ `{BUCKLER_SHIELD_ID}.rangedCover` = **{buck_rc:.2f}**（盾のうち遠距離カバーが低い帯の基準）。"
        )

    lines.append(
        "## 掩体: `rangedCover` とバックラー基準（マージ後 Mod 装備ブロック）"
    )
    lines.append("")
    lines.append(
        "方針: クロスボウの `rangedCover` は **バックラー盾の遠距離カバーより低い**こと "
        "([`BOW_DESIGN_TARGETS.md`](../BOW_DESIGN_TARGETS.md) / "
        "[`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](../EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md))。"
        f" {buck_note}"
    )
    lines.append("")
    lines.append(
        "| weapon_id | rangedCover | meleeCover | coverAngle | rangedCover < buckler ref |"
    )
    lines.append("|---|---|---|---|---|")
    for wid in WEAPON_IDS:
        m = merge_ranged(vmap[wid], mmap.get(wid))
        rc = float(m.get("rangedCover") or 0.0)
        mc = float(m.get("meleeCover") or 0.0)
        ca = float(m.get("coverAngle") or 0.0)
        if buck_rc is None:
            vs = "—"
        else:
            vs = "yes" if rc < buck_rc - 1e-9 else "no"
        lines.append(
            f"| {wid} | {rc:.2f} | {mc:.2f} | {ca:.0f} | {vs} |"
        )
    lines.append("")

    lines.append("## 移動: 設計目標倍率とマージ JSON の `onEquipEffectors`")
    lines.append("")
    lines.append(
        "装備中の移動倍率の**設計目標**は "
        "[`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](../EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md) "
        "「弓・クロスの反映状況」。**低下の量**を JSON で追う場合は `onEquipEffectors` 等の装備時効果を確認する。"
        " 本表はマージ後ブロックをそのまま列挙する（無ければ `—`）。"
    )
    lines.append("")
    lines.append("| weapon_id | doc target move mult | `onEquipEffectors` (merged) |")
    lines.append("|---|---|---|")
    for wid in WEAPON_IDS:
        m = merge_ranged(vmap[wid], mmap.get(wid))
        mult = DESIGN_RANGED_MOVE_MULT.get(wid)
        mult_s = f"{mult:.2f}" if mult is not None else "—"
        lines.append(f"| {wid} | {mult_s} | {_format_on_equip_effectors(m)} |")
    lines.append("")

    lines.append("## Marksman / `requiredSkills` (merged item, reference only)")
    lines.append("")
    lines.append("| weapon_id | vanilla | mod |")
    lines.append("|---|---|---|")
    for wid in WEAPON_IDS:
        v_merged = merge_ranged(vmap[wid], None)
        m_merged = merge_ranged(vmap[wid], mmap.get(wid))
        lines.append(
            f"| {wid} | {_format_required_skills(v_merged)} | "
            f"{_format_required_skills(m_merged)} |"
        )
    lines.append("")
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return out_path


def write_distance_band_summary_csv(
    *,
    qualities: list[str],
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    """
    Write mean/min over +/-1m band around each anchor distance.
    Keeps chart count unchanged while adding machine-readable comparison output.
    """
    bands: list[tuple[str, float]] = [
        ("near", DPS_DISTANCE_NEAR_M),
        ("mid", DPS_DISTANCE_MID_M),
        ("far", DPS_DISTANCE_FAR_M),
        ("ultra_far", DPS_DISTANCE_ULTRA_FAR_M),
    ]
    out_path = out_dir / "distance_expected_dps_band_summary.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "weapon_id",
                "quality",
                "dataset",
                "band",
                "center_m",
                "sample_distances_m",
                "mean_distance_expected_dps",
                "min_distance_expected_dps",
            ]
        )
        for wid in WEAPON_IDS:
            v_only = merge_ranged(vmap[wid], None)
            v_item = merge_ranged(vmap[wid], mmap.get(wid))
            v_series = series_for_item(v_only, wqs_vanilla)
            m_series = series_for_item(v_item, wqs_mod)
            for q_idx, q in enumerate(qualities):
                for dataset, stats in (("vanilla", v_series[q_idx]), ("mod", m_series[q_idx])):
                    for band_name, center in bands:
                        vals = _band_values(stats, center)
                        mean_dps = round2(sum(vals) / len(vals))
                        min_dps = round2(min(vals))
                        writer.writerow(
                            [
                                wid,
                                q,
                                dataset,
                                band_name,
                                f"{center:.0f}",
                                f"{center - 1:.0f}/{center:.0f}/{center + 1:.0f}",
                                f"{mean_dps:.2f}",
                                f"{min_dps:.2f}",
                            ]
                        )
    return out_path


def save_all_weapons_overlay(
    *,
    stat_key: str,
    y_label: str,
    title: str,
    qualities: list[str],
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    for wid in WEAPON_IDS:
        v_only = merge_ranged(vmap[wid], None)
        v_item = merge_ranged(vmap[wid], mmap.get(wid))
        y_v = [round2(s[stat_key]) for s in series_for_item(v_only, wqs_vanilla)]
        y_m = [round2(s[stat_key]) for s in series_for_item(v_item, wqs_mod)]
        c_mod = WEAPON_LINE_COLORS_MOD[wid]
        ax.plot(
            qualities,
            y_v,
            linestyle="--",
            linewidth=1.4,
            color=_weapon_rgba_vanilla(wid),
            label=f"{wid} (V)",
        )
        ax.plot(
            qualities,
            y_m,
            linestyle="-",
            linewidth=2.2,
            color=c_mod,
            label=f"{wid} (M)",
        )
    ax.set_title(title)
    ax.set_xlabel("Quality")
    ax.set_ylabel(y_label)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    out_path = out_dir / f"{stat_key}_all_weapons_overlay.png"
    savefig_png(fig, out_path, dpi=150, tight=True)
    plt.close(fig)
    return out_path


def save_all_weapons_overlay_metric(
    *,
    value_getter: Callable[[dict], float],
    y_label: str,
    title: str,
    filename_base: str,
    qualities: list[str],
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    for wid in WEAPON_IDS:
        v_only = merge_ranged(vmap[wid], None)
        v_item = merge_ranged(vmap[wid], mmap.get(wid))
        y_v = [round2(value_getter(s)) for s in series_for_item(v_only, wqs_vanilla)]
        y_m = [round2(value_getter(s)) for s in series_for_item(v_item, wqs_mod)]
        c_mod = WEAPON_LINE_COLORS_MOD[wid]
        ax.plot(
            qualities,
            y_v,
            linestyle="--",
            linewidth=1.4,
            color=_weapon_rgba_vanilla(wid),
            label=f"{wid} (V)",
        )
        ax.plot(
            qualities,
            y_m,
            linestyle="-",
            linewidth=2.2,
            color=c_mod,
            label=f"{wid} (M)",
        )
    ax.set_title(title)
    ax.set_xlabel("Quality")
    ax.set_ylabel(y_label)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    out_path = out_dir / f"{filename_base}_all_weapons_overlay.png"
    savefig_png(fig, out_path, dpi=150, tight=True)
    plt.close(fig)
    return out_path


def plot_dps_grids(
    *,
    qualities: list[str],
    vmap: dict[str, dict],
    mmap: dict[str, dict],
    wqs_vanilla: dict,
    wqs_mod: dict,
    out_dir: Path,
) -> list[Path]:
    """Per-weapon Q1–Q6 vanilla vs mod for expected / distance-expected DPS (no raw DPS chart)."""
    mid_tag = f"{int(DPS_DISTANCE_MID_M)}m"
    far_tag = f"{int(DPS_DISTANCE_FAR_M)}m"
    ultra_far_tag = f"{int(DPS_DISTANCE_ULTRA_FAR_M)}m"
    specs: list[tuple[str, str, str, Callable[[dict], float]]] = [
        ("expected_dps", "Expected DPS (DPS × precision)", "Expected DPS Q1–Q6", expected_dps),
        (
            f"distance_expected_dps_{int(DPS_DISTANCE_NEAR_M)}m",
            f"Distance expected DPS @ {DPS_DISTANCE_NEAR_M:.0f} m",
            f"Distance expected DPS (near, d={DPS_DISTANCE_NEAR_M:.0f} m) Q1–Q6",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_NEAR_M),
        ),
        (
            f"distance_expected_dps_{mid_tag}",
            f"Distance expected DPS @ {DPS_DISTANCE_MID_M:.0f} m",
            f"Distance expected DPS (mid, d={DPS_DISTANCE_MID_M:.0f} m) Q1–Q6",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_MID_M),
        ),
        (
            f"distance_expected_dps_{far_tag}",
            f"Distance expected DPS @ {DPS_DISTANCE_FAR_M:.0f} m",
            f"Distance expected DPS (far, d={DPS_DISTANCE_FAR_M:.0f} m) Q1–Q6",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_FAR_M),
        ),
        (
            f"distance_expected_dps_{ultra_far_tag}",
            f"Distance expected DPS @ {DPS_DISTANCE_ULTRA_FAR_M:.0f} m",
            f"Distance expected DPS (ultra-far, d={DPS_DISTANCE_ULTRA_FAR_M:.0f} m) Q1–Q6",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_ULTRA_FAR_M),
        ),
    ]
    out_paths: list[Path] = []
    for file_key, y_label, title_prefix, getter in specs:
        fig, axes = plt.subplots(2, 4, figsize=(14, 7), sharex=True)
        fig.suptitle(
            f"{title_prefix} — Vanilla vs mod (proxy; see BOW_MOD_INTEGRATION_POLICY.md)",
            fontsize=12,
        )
        axes_flat = axes.flatten()
        for ax, wid in zip(axes_flat, WEAPON_IDS):
            v_only = merge_ranged(vmap[wid], None)
            v_item = merge_ranged(vmap[wid], mmap.get(wid))
            v_series = series_for_item(v_only, wqs_vanilla)
            m_series = series_for_item(v_item, wqs_mod)
            y_v = [round2(getter(s)) for s in v_series]
            y_m = [round2(getter(s)) for s in m_series]
            c_mod = WEAPON_LINE_COLORS_MOD[wid]
            ax.plot(
                qualities,
                y_v,
                marker="o",
                label="Vanilla",
                linewidth=1.5,
                color=_weapon_rgba_vanilla(wid),
            )
            ax.plot(
                qualities,
                y_m,
                marker="s",
                label="Mod",
                linewidth=1.5,
                color=c_mod,
            )
            ax.set_title(wid.replace("_", " "), fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis="x", rotation=0, labelsize=7)
        axes_flat[-1].axis("off")
        handles, labels = axes_flat[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.98, 0.02))
        plt.tight_layout(rect=(0, 0.04, 1, 0.95))
        out_path = out_dir / f"{file_key}_Q1_Q6_vanilla_vs_mod.png"
        savefig_png(fig, out_path, dpi=150, tight=False)
        plt.close(fig)
        out_paths.append(out_path)
    return out_paths


def main() -> None:
    vanilla_root = resolve_vanilla_items_dir()
    print(f"Vanilla Items: {vanilla_root}")
    vanilla_eq = load_json(vanilla_root / "Equipment.json")
    wqs_vanilla = load_json(vanilla_root / "WeaponQualitySettings.json")
    wqs_mod = merge_wqs_overlay(wqs_vanilla, MOD_WEAPON_QUALITY)
    mod_eq = load_json(MOD_EQUIPMENT)
    vmap = repo_by_id(vanilla_eq)
    mmap = repo_by_id(mod_eq)

    qualities = [f"Q{i}" for i in range(1, 7)]
    stats = [
        ("damage", "Damage (base × quality)"),
        ("attackSpeed", "Attack speed / reload (base × quality)"),
        ("range", "Range (tiles, base × quality)"),
        ("precision", "Precision (base × quality)"),
        ("precisionFalloff", "Precision falloff (base × quality)"),
        ("ignoresArmor", "Ignores armor (base × quality)"),
        ("armorDamage", "Armor damage (base × quality)"),
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPT_OUT_DIR.mkdir(parents=True, exist_ok=True)

    for stat_key, stat_label in stats:
        fig, axes = plt.subplots(2, 4, figsize=(14, 7), sharex=True)
        fig.suptitle(
            f"{stat_label} — Vanilla vs mod (Equipment + mod quality multipliers where defined)",
            fontsize=12,
        )
        axes_flat = axes.flatten()
        for ax, wid in zip(axes_flat, WEAPON_IDS):
            v_only = merge_ranged(vmap[wid], None)
            v_item = merge_ranged(vmap[wid], mmap.get(wid))
            v_series = series_for_item(v_only, wqs_vanilla)
            m_series = series_for_item(v_item, wqs_mod)
            y_v = [round2(s[stat_key]) for s in v_series]
            y_m = [round2(s[stat_key]) for s in m_series]
            c_mod = WEAPON_LINE_COLORS_MOD[wid]
            ax.plot(
                qualities,
                y_v,
                marker="o",
                label="Vanilla",
                linewidth=1.5,
                color=_weapon_rgba_vanilla(wid),
            )
            ax.plot(
                qualities,
                y_m,
                marker="s",
                label="Mod",
                linewidth=1.5,
                color=c_mod,
            )
            ax.set_title(wid.replace("_", " "), fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis="x", rotation=0, labelsize=7)
        axes_flat[-1].axis("off")
        handles, labels = axes_flat[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.98, 0.02))
        plt.tight_layout(rect=(0, 0.04, 1, 0.95))
        out_path = OUT_DIR / f"{stat_key}_Q1_Q6_vanilla_vs_mod.png"
        savefig_png(fig, out_path, dpi=150, tight=False)
        plt.close(fig)
        print(out_path)

    overlay_specs: list[tuple[str, str, str]] = [
        ("damage", "Damage", "Damage Q1–Q6: all ranged (solid=mod, dashed=vanilla)"),
        (
            "attackSpeed",
            "Attack speed / reload",
            "Attack speed Q1–Q6: all ranged (solid=mod, dashed=vanilla)",
        ),
        ("range", "Range (tiles)", "Range Q1–Q6: all ranged (solid=mod, dashed=vanilla)"),
        ("precision", "Precision", "Precision Q1–Q6: all ranged (solid=mod, dashed=vanilla)"),
        (
            "precisionFalloff",
            "Precision falloff",
            "Precision falloff Q1–Q6: all ranged (solid=mod, dashed=vanilla)",
        ),
        (
            "ignoresArmor",
            "Ignores armor",
            "Ignores armor Q1–Q6: all ranged (solid=mod, dashed=vanilla)",
        ),
        (
            "armorDamage",
            "Armor damage",
            "Armor damage Q1–Q6: all ranged (solid=mod, dashed=vanilla)",
        ),
    ]
    for stat_key, y_label, title in overlay_specs:
        p = save_all_weapons_overlay(
            stat_key=stat_key,
            y_label=y_label,
            title=title,
            qualities=qualities,
            vmap=vmap,
            mmap=mmap,
            wqs_vanilla=wqs_vanilla,
            wqs_mod=wqs_mod,
            out_dir=OUT_DIR,
        )
        print(p)

    mid_tag = f"{int(DPS_DISTANCE_MID_M)}m"
    far_tag = f"{int(DPS_DISTANCE_FAR_M)}m"
    ultra_far_tag = f"{int(DPS_DISTANCE_ULTRA_FAR_M)}m"
    dps_overlay_specs: list[tuple[str, str, str, Callable[[dict], float]]] = [
        (
            "expected_dps",
            "Expected DPS (DPS × precision)",
            "Expected DPS Q1–Q6: all ranged (solid=mod, dashed=vanilla)",
            expected_dps,
        ),
        (
            f"distance_expected_dps_{int(DPS_DISTANCE_NEAR_M)}m",
            f"Distance expected DPS @ {DPS_DISTANCE_NEAR_M:.0f} m",
            f"Distance expected DPS near (d={DPS_DISTANCE_NEAR_M:.0f} m) Q1–Q6: all ranged",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_NEAR_M),
        ),
        (
            f"distance_expected_dps_{mid_tag}",
            f"Distance expected DPS @ {DPS_DISTANCE_MID_M:.0f} m",
            f"Distance expected DPS mid (d={DPS_DISTANCE_MID_M:.0f} m) Q1–Q6: all ranged",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_MID_M),
        ),
        (
            f"distance_expected_dps_{far_tag}",
            f"Distance expected DPS @ {DPS_DISTANCE_FAR_M:.0f} m",
            f"Distance expected DPS far (d={DPS_DISTANCE_FAR_M:.0f} m) Q1–Q6: all ranged",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_FAR_M),
        ),
        (
            f"distance_expected_dps_{ultra_far_tag}",
            f"Distance expected DPS @ {DPS_DISTANCE_ULTRA_FAR_M:.0f} m",
            f"Distance expected DPS ultra-far (d={DPS_DISTANCE_ULTRA_FAR_M:.0f} m) Q1–Q6: all ranged",
            lambda s: distance_expected_dps(s, DPS_DISTANCE_ULTRA_FAR_M),
        ),
    ]
    for file_key, y_label, title, getter in dps_overlay_specs:
        p = save_all_weapons_overlay_metric(
            value_getter=getter,
            y_label=y_label,
            title=title,
            filename_base=file_key,
            qualities=qualities,
            vmap=vmap,
            mmap=mmap,
            wqs_vanilla=wqs_vanilla,
            wqs_mod=wqs_mod,
            out_dir=OUT_DIR,
        )
        print(p)

    for p in plot_dps_grids(
        qualities=qualities,
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
        out_dir=OUT_DIR,
    ):
        print(p)

    band_csv_path = write_distance_band_summary_csv(
        qualities=qualities,
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
        out_dir=SCRIPT_OUT_DIR,
    )
    print(band_csv_path)
    p_arm = write_layer1_armored_distance_dps_band_summary_csv(
        qualities=qualities,
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
        out_dir=SCRIPT_OUT_DIR,
    )
    print(p_arm)
    p_ps = write_layer1_per_shot_expected_damage_band_summary_csv(
        qualities=qualities,
        vmap=vmap,
        mmap=mmap,
        wqs_vanilla=wqs_vanilla,
        wqs_mod=wqs_mod,
        out_dir=SCRIPT_OUT_DIR,
    )
    print(p_ps)
    p_ia_csv = write_layer1_ignores_armor_policy_csv(
        qualities=qualities,
        vmap=vmap,
        mmap=mmap,
        wqs_mod=wqs_mod,
        out_dir=SCRIPT_OUT_DIR,
    )
    print(p_ia_csv)
    p_ia_chart = save_ignores_armor_mod_policy_overlay(
        qualities=qualities,
        vmap=vmap,
        mmap=mmap,
        wqs_mod=wqs_mod,
        out_dir=OUT_DIR,
    )
    print(p_ia_chart)
    print(
        write_layer1_eval_bundle_md(
            vmap=vmap,
            mmap=mmap,
            wqs_vanilla=wqs_vanilla,
            wqs_mod=wqs_mod,
            out_dir=OUT_DIR,
            armored_csv_name=f"script/{p_arm.name}",
            per_shot_csv_name=f"script/{p_ps.name}",
            ia_policy_csv_name=f"script/{p_ia_csv.name}",
            qualities=qualities,
            ia_policy_chart_name=p_ia_chart.name,
        )
    )


if __name__ == "__main__":
    main()

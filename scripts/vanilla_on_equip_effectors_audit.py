#!/usr/bin/env python3
"""
List vanilla on-equip effector ids (from Items/Equipment.json) and summarize
each definition from StatsSystem/Effectors.json.

Optional: StatsSystem/Attributes.json resolves numeric Attribute ids in effect
parameters to names (when present).

Environment:
  GM_STREAMING_ASSETS  Path to Going Medieval_Data/StreamingAssets
Or:
  --streaming-assets PATH
  --items-dir PATH     (StreamingAssets/Items; parent used as StreamingAssets)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _streaming_assets_from_args(args: argparse.Namespace) -> Path | None:
    env = os.environ.get("GM_STREAMING_ASSETS")
    if args.streaming_assets:
        return Path(args.streaming_assets)
    if env:
        return Path(env)
    if args.items_dir:
        return Path(args.items_dir).parent
    return None


def _attribute_name_index(sa: Path) -> dict[str, str]:
    """Map parameter 'value' for Attribute keys to a short label (id or devName)."""
    p = sa / "StatsSystem" / "Attributes.json"
    if not p.is_file():
        return {}
    data = _load(p)
    repo = data.get("repository")
    if not isinstance(repo, list):
        return {}
    out: dict[str, str] = {}
    for row in repo:
        if not isinstance(row, dict):
            continue
        aid = row.get("id")
        if aid is None:
            continue
        key = str(aid)
        name = row.get("devName") or row.get("name") or row.get("id")
        out[key] = str(name)
    return out


def _collect_on_equip_ids(equipment_path: Path) -> tuple[dict[str, int], int]:
    """Return effector_id -> use count, and number of equipment rows scanned."""
    data = _load(equipment_path)
    repo = data.get("repository")
    if not isinstance(repo, list):
        return {}, 0
    ctr: dict[str, int] = defaultdict(int)
    for row in repo:
        if not isinstance(row, dict):
            continue
        raw = row.get("onEquipEffectors")
        if not raw:
            continue
        if isinstance(raw, str):
            ctr[raw] += 1
            continue
        if isinstance(raw, list):
            for x in raw:
                if isinstance(x, str):
                    ctr[x] += 1
    return dict(ctr), len(repo)


def _effectors_by_id(sa: Path) -> dict[str, dict]:
    p = sa / "StatsSystem" / "Effectors.json"
    if not p.is_file():
        return {}
    data = _load(p)
    repo = data.get("repository")
    if not isinstance(repo, list):
        return {}
    out: dict[str, dict] = {}
    for row in repo:
        if isinstance(row, dict) and row.get("id"):
            out[str(row["id"])] = row
    return out


# 装備ブロック全体の日本語要約（Equipment が参照する effector id のみでよい）
_JA_EFFECTOR_SUMMARY: dict[str, str] = {
    "ImpairedMovementLow": "移動速度がやや低下（小）。射撃の攻撃間隔がやや長くなり、回避率もわずかに下がる。",
    "ImpairedMovementMed": "移動・回避のペナは Low と同程度だが、射撃の攻撃間隔への影響がより大きい（重装甲など）。",
    "WearingMorbidItem": "モルビッド系装備。気分がわずかに悪化する。",
    "ShieldCombatSpeedLow": "盾装備時、近接の攻撃間隔がやや長くなる（小）。",
    "ShieldCombatSpeedMed": "盾装備時、近接の攻撃間隔が長くなる（中）。",
    "ShieldCombatSpeedHigh": "盾装備時、近接の攻撃間隔が大きく長くなる（大）。",
    "SunMaxProtectItem": "日なたに晒されても不快になりにくい上限が高まる（帽子など）。",
    "ChainedUp": "拘束具。移動・回避・作業が大きく制限され、気分も大きく悪化する。",
}


def _params_to_dict(parameters: Any) -> dict[str, str]:
    if not isinstance(parameters, list):
        return {}
    d: dict[str, str] = {}
    for item in parameters:
        if not isinstance(item, dict):
            continue
        k = item.get("key")
        v = item.get("value")
        if k is not None:
            d[str(k)] = "" if v is None else str(v)
    return d


def _japanese_effect_note(eff: dict, attr_index: dict[str, str]) -> str:
    """Plain-language Japanese for one effect block (best-effort from parameters)."""
    et = eff.get("type")
    pd = _params_to_dict(eff.get("parameters"))
    if et == "MoodModify":
        bv = pd.get("BaseValue")
        if bv is not None:
            try:
                v = float(bv)
                if v < 0:
                    return f"気分が {v:.0f}（悪化）"
                if v > 0:
                    return f"気分が +{v:.0f}（改善）"
                return "気分に変化なし（0）"
            except ValueError:
                pass
        return "気分を変更"
    if et == "AttributeModify":
        attr_id = pd.get("Attribute")
        mult_s = pd.get("Multiplier") or pd.get("Value")
        name = (attr_index.get(attr_id) if attr_id else None) or ""
        if mult_s is None:
            return f"属性「{name or attr_id}」を変更"
        try:
            m = float(mult_s)
        except ValueError:
            return f"属性「{name or attr_id}」に乗算 {mult_s}"
        if name == "MovementSpeed":
            if m < 0.85:
                slow = "かなり遅い"
            elif m < 1:
                slow = "やや遅い"
            else:
                slow = "やや速い"
            return f"移動速度が基準の {m * 100:.0f}%（{slow}）"
        if name == "RangedSpeed":
            return (
                f"遠隔の攻撃間隔が {m * 100:.0f}%（"
                f"{'一射あたりの時間が長くなる' if m > 1 else '短くなる'}）"
            )
        if name == "EvadeChance":
            return f"回避の倍率が {m}（基準 1.0 より低いほど回避しづらい）"
        if name == "MeleeAttackSpeed":
            return (
                f"近接の攻撃間隔が {m * 100:.0f}%（"
                f"{'一撃あたりの時間が長くなる' if m > 1 else '短くなる'}）"
            )
        if name == "SunlightMax":
            disp = int(m) if m == int(m) else m
            return f"日なた耐性の上限が {disp} 倍"
        if name == "GlobalWorkSpeed":
            return f"あらゆる作業速度が {m * 100:.0f}%"
        return f"属性「{name or attr_id}」に乗算 {mult_s}"
    dev = eff.get("devName")
    return f"（`{dev}` の効果。タイプ {et}）" if dev or et else ""


def _format_effect(
    eff: dict,
    attr_index: dict[str, str],
) -> str:
    dev = eff.get("devName")
    et = eff.get("type")
    head = ""
    if dev is not None or et is not None:
        head = f"`{dev}` type={et}"
    pd = _params_to_dict(eff.get("parameters"))
    if not pd:
        return head if head else "(no parameters)"
    attr_id = pd.get("Attribute")
    name_hint = ""
    if attr_id is not None:
        name_hint = f" -> `{attr_index[attr_id]}`" if attr_id in attr_index else f" (unresolved Attribute id `{attr_id}`)"
    pairs = ", ".join(f"{k}={v}" for k, v in sorted(pd.items()))
    body = f"{pairs}{name_hint}"
    return f"{head} | {body}" if head else body


def _summarize_effector_row(entry: dict, attr_index: dict[str, str]) -> list[str]:
    eid = entry.get("id", "?")
    lines = [f"### `{eid}`"]
    ja_sum = _JA_EFFECTOR_SUMMARY.get(str(eid))
    if ja_sum:
        lines.append(f"- **装備時の意味（要約・日本語）**: {ja_sum}")
    loc = entry.get("locKeys")
    if isinstance(loc, list) and loc:
        first = loc[0]
        if isinstance(first, dict) and first.get("name"):
            lines.append(f"- **loc**: `{first['name']}`")
    uig = entry.get("uiGroup")
    if uig is not None:
        lines.append(f"- **uiGroup**: `{uig}`")
    effects = entry.get("effects")
    if not isinstance(effects, list) or not effects:
        lines.append("- **effects**: _(none or non-list)_")
        return lines
    lines.append("- **effects**:")
    for i, eff in enumerate(effects):
        if not isinstance(eff, dict):
            continue
        tech = _format_effect(eff, attr_index)
        ja = _japanese_effect_note(eff, attr_index)
        if ja:
            lines.append(f"  - {i + 1}. {tech}")
            lines.append(f"    - **日本語**: {ja}")
        else:
            lines.append(f"  - {i + 1}. {tech}")
    return lines


def build_markdown(sa: Path, equipment_path: Path) -> str:
    attr_index = _attribute_name_index(sa)
    by_id = _effectors_by_id(sa)
    usage, n_rows = _collect_on_equip_ids(equipment_path)
    used_sorted = sorted(usage.keys(), key=lambda x: (-usage[x], x))

    lines: list[str] = [
        "# バニラ onEquipEffectors 効果詳細（生成）",
        "",
        "> **正本**: インストール先 `Going Medieval_Data/StreamingAssets` の",
        "> `Items/Equipment.json`（参照する id の列挙）と `StatsSystem/Effectors.json`（各 id の `effects` 定義）。",
        "> 数値の Attribute ID は同階層 `StatsSystem/Attributes.json` で名前に解決できる（スクリプトが解決を試みる）。",
        "",
        f"- **Equipment 行数**: {n_rows}",
        f"- **onEquip 参照のユニーク id 数**: {len(used_sorted)}",
        "",
        "## 装備から参照される id（使用件数）",
        "",
        "| effector id | 参照件数（装備ブロック） | 日本語（概要） |",
        "| --- | ---: | --- |",
    ]
    for eid in used_sorted:
        ja = _JA_EFFECTOR_SUMMARY.get(eid, "—")
        lines.append(f"| `{eid}` | {usage[eid]} | {ja} |")

    lines.extend(
        [
            "",
            "## 各 id の定義（Effectors.json）",
            "",
        ]
    )

    missing = [eid for eid in used_sorted if eid not in by_id]
    if not by_id:
        lines.append(
            "_`StatsSystem/Effectors.json` が見つからないか空です。`GM_STREAMING_ASSETS` を本体の StreamingAssets に設定して再実行してください。_"
        )
    else:
        for eid in used_sorted:
            entry = by_id.get(eid)
            if entry is None:
                lines.append(f"### `{eid}`")
                lines.append("_**Effectors.json に同一 id のエントリなし**（参照切れの可能性）_")
                lines.append("")
                continue
            lines.extend(_summarize_effector_row(entry, attr_index))
            lines.append("")

    if missing and by_id:
        lines.extend(
            [
                "## 参照切れ（Equipment にあるが Effectors に無い id）",
                "",
                ", ".join(f"`{x}`" for x in missing),
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            "_このファイルは `scripts/vanilla_on_equip_effectors_audit.py` が生成しました。手で編集しないでください（上書きされます）。_",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--streaming-assets", type=Path, default=None)
    parser.add_argument("--items-dir", type=Path, default=None)
    parser.add_argument(
        "--equipment-json",
        type=Path,
        default=None,
        help="Defaults to Items/Equipment.json under StreamingAssets",
    )
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args()

    sa = _streaming_assets_from_args(args)
    if sa is None or not sa.is_dir():
        print("ERROR: set GM_STREAMING_ASSETS or pass --streaming-assets / --items-dir", file=sys.stderr)
        sys.exit(1)

    eq_path = args.equipment_json
    if eq_path is None:
        eq_path = sa / "Items" / "Equipment.json"
    if not eq_path.is_file():
        print(f"ERROR: missing {eq_path}", file=sys.stderr)
        sys.exit(1)

    md = build_markdown(sa, eq_path)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print("Wrote", args.output)
    else:
        print(md)


if __name__ == "__main__":
    main()

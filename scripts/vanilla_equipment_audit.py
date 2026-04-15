#!/usr/bin/env python3
"""
Extract armor / shield / weapon combat fields from Going Medieval Equipment.json.

Full audit (plan): point --items-dir at vanilla ``StreamingAssets/Items`` (or set
``GOING_MEDIEVAL_ITEMS``). Parent folder is treated as StreamingAssets for optional
``Combat/`` and ``StatsSystem/`` scans.

Partial mode: ``--equipment-json`` for a merged Mod file (subset of ids). Output
banner warns that armor values may match vanilla but weapon rows may be Modded.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from collections import Counter


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _summarize_numeric_rows(rows: list[dict], keys: list[str]) -> str:
    if not keys:
        return "_（列なし）_"
    lines = ["| " + " | ".join(keys) + " |", "| " + " | ".join(["---"] * len(keys)) + " |"]
    for row in sorted(rows, key=lambda r: r.get("productQuality", 0)):
        cells = [str(row.get(k, "")) for k in keys]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) if len(lines) > 2 else "_（行なし）_"


def _scan_combat_settings(sa: Path) -> str:
    p = sa / "Combat" / "DamageTakingAgentSettings.json"
    if not p.is_file():
        return f"_ファイルなし: `{p.as_posix()}`（`StreamingAssets` パスを確認）_\n"
    data = _load_json(p)
    out: list[str] = []
    if isinstance(data, dict):
        for k, v in sorted(data.items()):
            if k in ("name", "repository"):
                continue
            if isinstance(v, (str, int, float, bool)):
                out.append(f"- **`{k}`**: `{v}`")
            elif isinstance(v, list) and len(v) < 12:
                out.append(f"- **`{k}`**: `{v}`")
    # highlight accident / hit related keys
    hits = [line for line in out if re.search(r"accident|hit|miss|friendly|ally|damage", line, re.I)]
    body = "\n".join(out[:40]) if out else "_（トップレベルキーなし）_"
    extra = ""
    if hits:
        extra = "\n**命中・誤射っぽいキー（名称マッチ）:**\n" + "\n".join(hits[:20])
    return body + extra + "\n"


def _scan_hit_effector_groups(sa: Path, group_ids: set[str]) -> str:
    p = sa / "StatsSystem" / "HitEffectorGroups.json"
    if not p.is_file():
        return f"_ファイルなし: `{p.as_posix()}`_\n"
    data = _load_json(p)
    repo = data.get("repository") if isinstance(data, dict) else None
    if not isinstance(repo, list):
        return "_`repository` 形式が想定外_\n"
    lines: list[str] = []
    for entry in repo:
        gid = entry.get("id")
        if gid not in group_ids:
            continue
        lines.append(f"### `{gid}`")
        for row in entry.get("qualitySettings") or []:
            if not isinstance(row, dict):
                continue
            pq = row.get("productQuality")
            eff = row.get("effectors") or row.get("hitEffectors")
            lines.append(f"- Q{pq}: `{eff}`")
    return "\n".join(lines) + "\n" if lines else "_対象グループなし_\n"


def _grep_effector_movement(sa: Path) -> str:
    p = sa / "StatsSystem" / "Effectors.json"
    if not p.is_file():
        return f"_ファイルなし: `{p.as_posix()}`_\n"
    data = _load_json(p)
    repo = data.get("repository") if isinstance(data, dict) else None
    if not isinstance(repo, list):
        return "_`repository` 形式が想定外_\n"
    names = ("ImpairedMovementLow", "ImpairedMovementMed", "ShieldCombatSpeedLow", "ShieldCombatSpeedMed", "ShieldCombatSpeedHigh")
    lines: list[str] = []
    for entry in repo:
        eid = entry.get("id")
        if eid not in names:
            continue
        blob = json.dumps(entry, ensure_ascii=False)
        lines.append(f"- **`{eid}`**（抜粋）: `{blob[:400]}{'…' if len(blob) > 400 else ''}`")
    return "\n".join(lines) + "\n" if lines else "_該当 effector id なし_\n"


def build_markdown(
    *,
    equipment_path: Path,
    items_dir: Path | None,
    partial: bool,
) -> str:
    eq = _load_json(equipment_path)
    repo = eq["repository"]
    armors: list[dict] = []
    shields: list[dict] = []
    weapons: list[dict] = []
    for e in repo:
        it = e.get("itemType")
        eid = str(e.get("id", ""))
        if it == 3:
            if "shield" in eid.lower():
                shields.append(e)
            else:
                armors.append(e)
        elif it == 1:
            weapons.append(e)

    def armor_row(e: dict) -> str:
        return (
            f"| `{e.get('id')}` | {e.get('armorRating', '')} | {e.get('armorType', '')} | "
            f"{e.get('onEquipEffectors', '—')} |"
        )

    arm_tbl = "\n".join(
        ["| id | armorRating | armorType | onEquipEffectors |", "| --- | --- | --- | --- |"]
        + [armor_row(e) for e in sorted(armors, key=lambda x: str(x.get("id")))]
    )
    sh_tbl = "\n".join(
        ["| id | onEquipEffectors | meleeCover | rangedCover | coverAngle |", "| --- | --- | --- | --- | --- |"]
        + [
            f"| `{e.get('id')}` | {e.get('onEquipEffectors', '—')} | {e.get('meleeCover', '')} | "
            f"{e.get('rangedCover', '')} | {e.get('coverAngle', '')} |"
            for e in sorted(shields, key=lambda x: str(x.get("id")))
        ]
    )
    w_rows = []
    for e in sorted(weapons, key=lambda x: str(x.get("id"))):
        pwm = e.get("primaryWeaponMode") or {}
        if not isinstance(pwm, dict):
            continue
        w_rows.append(
            f"| `{e.get('id')}` | `{pwm.get('weaponType', '')}` | {pwm.get('damage', '')} | "
            f"{pwm.get('ignoresArmor', '')} | {pwm.get('armorDamage', '')} | {pwm.get('range', '')} |"
        )
    w_tbl = "\n".join(
        ["| id | weaponType | damage | ignoresArmor | armorDamage | range |", "| --- | --- | --- | --- | --- | --- |"]
        + w_rows
    )

    hit_ctr: Counter[str] = Counter()
    for e in weapons:
        pwm = e.get("primaryWeaponMode") or {}
        if isinstance(pwm, dict):
            for g in pwm.get("hitEffectorGroupIDs") or []:
                hit_ctr[str(g)] += 1
    hit_note = ""
    if hit_ctr:
        parts = [f"`{k}`: **{v}** 武器" for k, v in sorted(hit_ctr.items(), key=lambda x: (-x[1], x[0]))]
        hit_note = (
            "### 補足（本 `Equipment.json` 内の `hitEffectorGroupIDs` 件数）\n\n"
            + "、".join(parts)
            + "。確率・付帯エフェクタは `StatsSystem/HitEffectorGroups.json` を参照。\n\n"
        )

    sa: Path | None = items_dir.parent if items_dir else None
    aqs_md = ""
    wqs_md = ""
    combat_md = ""
    heg_md = ""
    eff_md = ""
    wqs_side = equipment_path.parent / "WeaponQualitySettings.json"
    if not items_dir and wqs_side.is_file():
        d = _load_json(wqs_side)
        rows = d.get("repository", []) if isinstance(d, dict) else []
        wqs_md = "### WeaponQualitySettings（Mod 同梱・抜粋）\n\n_バニラ `Items` ではない。弓・クロス行は Mod 方針反映済み。_\n\n"
        for wtype in ("TwoHandBow", "TwoHandCrossbow", "OneHandMace", "OneHandSword"):
            block = next((r for r in rows if isinstance(r, dict) and r.get("id") == wtype), None)
            if not block:
                continue
            qrows = block.get("qualitySettings") or []
            keys = [k for k in ("productQuality", "damageMultiplier", "rangeMultiplier", "ignoresArmorMultiplier", "attackSpeedMultiplier") if any(k in r for r in qrows)]
            wqs_md += f"**{wtype}**\n\n" + _summarize_numeric_rows(qrows, keys) + "\n\n"
    if items_dir and items_dir.is_dir():
        aqs = items_dir / "ArmorQualitySettings.json"
        if aqs.is_file():
            d = _load_json(aqs)
            rows = d.get("repository", []) if isinstance(d, dict) else []
            if rows and isinstance(rows[0], dict):
                keys = [k for k in rows[0].keys() if k not in ("name",) and not str(k).startswith("dev")]
                keys = [k for k in ("productQuality", "armorRatingMultiplier", "durabilityMultiplier") if k in rows[0]] + [
                    k for k in keys if k not in ("productQuality", "armorRatingMultiplier", "durabilityMultiplier")
                ][:6]
                aqs_md = "### ArmorQualitySettings\n\n" + _summarize_numeric_rows(rows, keys) + "\n\n"
        wqs = items_dir / "WeaponQualitySettings.json"
        if wqs.is_file():
            d = _load_json(wqs)
            rows = d.get("repository", []) if isinstance(d, dict) else []
            bow = next((r for r in rows if isinstance(r, dict) and r.get("weaponType") == "TwoHandBow"), None)
            cross = next((r for r in rows if isinstance(r, dict) and r.get("weaponType") == "TwoHandCrossbow"), None)
            wqs_md = "### WeaponQualitySettings（抜粋）\n\n"
            if bow:
                qrows = bow.get("qualitySettings") or []
                keys = [k for k in ("productQuality", "damageMultiplier", "rangeMultiplier", "ignoresArmorMultiplier") if any(k in r for r in qrows)]
                wqs_md += "**TwoHandBow** 品質行:\n\n" + _summarize_numeric_rows(qrows, keys or ["productQuality"]) + "\n\n"
            if cross:
                qrows = cross.get("qualitySettings") or []
                keys = [k for k in ("productQuality", "damageMultiplier", "rangeMultiplier", "ignoresArmorMultiplier") if any(k in r for r in qrows)]
                wqs_md += "**TwoHandCrossbow** 品質行:\n\n" + _summarize_numeric_rows(qrows, keys or ["productQuality"]) + "\n\n"
        if sa and sa.is_dir():
            combat_md = "### Combat / DamageTakingAgentSettings.json\n\n" + _scan_combat_settings(sa)
            group_ids = {"WoundsBlunt", "WoundsBluntHead", "WoundsPiercing", "WoundsPiercingHead", "WoundsCutting"}
            heg_md = "### StatsSystem / HitEffectorGroups（代表グループ）\n\n" + _scan_hit_effector_groups(sa, group_ids)
            eff_md = "### StatsSystem / Effectors（移動・盾戦闘系 id）\n\n" + _grep_effector_movement(sa)

    banner = ""
    if partial:
        banner = (
            "> **部分スナップショット**: 入力は Mod 同梱の `Equipment.json`（全 id ではない場合あり）。\n"
            ">\n"
            "> **防具・盾**の `onEquip` / `armorRating` はバニラ踏襲の可能性が高いが、**武器**は Mod 改変が混ざる。\n"
            ">\n"
            "> 武器表は「現リポジトリの値」として読み、**バニラ照合は `GOING_MEDIEVAL_ITEMS` で再抽出**すること。\n\n"
        )
    else:
        banner = (
            "> **データソース**: バニラ `Items/Equipment.json`（`--items-dir` または `GOING_MEDIEVAL_ITEMS`）。\n\n"
        )

    return f"""# バニラ装備データ監査（抽出・改善レバー整理）

{banner}
## 1. 前提と再実行方法

```bash
export GOING_MEDIEVAL_ITEMS="/path/to/Going Medieval_Data/StreamingAssets/Items"
python scripts/vanilla_equipment_audit.py --items-dir "$GOING_MEDIEVAL_ITEMS" --output docs/VANILLA_ARMOR_AUDIT.md
```

- `StreamingAssets` は `Items` の親ディレクトリ。スクリプトは `Combat/` と `StatsSystem/` を兄弟として読む。
- 本ファイルの **問題点の断定**は、上記バニラ `Equipment.json` を正に再生成した表で置き換えること。
- ビルドや配布形態によって、**`Equipment.json` の正本がかつて `Items/` 直下にあった／パスが異なっていた**という経緯メモもある。**実インストールのツリーを正**に `GOING_MEDIEVAL_ITEMS` を取る。

## 2. 防具（`itemType` 3、盾以外）

{arm_tbl}

## 3. 盾（`itemType` 3 かつ id に shield を含む等）

{sh_tbl}

## 4. 武器（`itemType` 1、`primaryWeaponMode`）

{w_tbl}

## 5. 品質曲線（バニラ `Items` にファイルがある場合のみ）

{aqs_md}{wqs_md}

## 6. 戦闘エージェント（バニラ `StreamingAssets/Combat`）

{combat_md}

## 7. 命中グループ・エフェクタ（バニラ `StreamingAssets/StatsSystem`）

{hit_note}{heg_md}{eff_md}

## 8. バニラ上の問題点（仮説・監査用チェックリスト）

| # | 観察・構造 | 根拠（データ） | 方針ファイルでの位置づけ |
| --- | --- | --- | --- |
| 1 | データ上、`gambeson_armor` 等に `ImpairedMovementLow`。**体感で足が重いかは実機要検証**。方針「ギャンベゾンは移動をほぼ殺さない」との**真のギャップは体感・バニラ正本照合のあと**に判定。栽培**麻のコスト対 mid 性能**はバニラ意図の一説として検証メモに含める | 上表 + [EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md) | 防具方針・経済文脈 |
| 2 | 鎖・板金は `ImpairedMovementLow/Med`。**負傷由来の減速と二重**になり退却が厳しい | 上表 + 近接不遇メモ | 退却可能性・負傷の肩代わし |
| 3 | 盾に `ShieldCombatSpeed*`。**盾＋近接の攻速・機動トレード**が重い | 上表 | カイトシールド方針・循環 |
| 4 | 武器 `ignoresArmor` が種別によって高帯。**鎧軽減が読みにくい** | 武器表（バニラ再抽出で検証） | 重装キラー主軸にしない／循環 |
| 5 | 鎧残量〜軽減の連続／階段調整は **Equipment 単体ではキー未確認**。**「軽減が確率で発動する」専用フィールドは未検出**（誤要約の可能性） | [COMBAT_PLAYTEST_POLICY.md](../COMBAT_PLAYTEST_POLICY.md) | 運ゲー・安定軽減の設計 |
| 6 | **味方誤射・流れ弾**は接敵近接のリスク要因になり得る | `DamageTakingAgentSettings` の accident/hit 系キー（存在時に要約） | 退却可能性・運ゲー |
| 7 | **プレイヤー側の損耗コスト非対称**: 住民は平時タスクを担うため、近接の負傷・療養・死亡は開拓地運用へ直撃しやすい。敵側は消耗前提で損益が対称にならない | プレイ観察 + [COMBAT_PLAYTEST_POLICY.md](../COMBAT_PLAYTEST_POLICY.md) 損耗コスト評価節 | 近接採用判断・勝ち筋の複線化 |

## 8a. プレイ観察メモ（JSON 外・要同定）

- **盾と退却**: 敵に盾面と `coverAngle` を向けたままでは下がりづらく、**退却時は背を見せてカバー角から外れる**ことが多い。防衛で有利でも、**退く局面では遠隔に背中を晒しやすい**。
- **攻城兵器周辺 AI**: 敵が**攻城兵器建設中**などの局面で、一定以上兵器から離れると**兵器へ退却**する挙動がある場合、**距離を釣って繰り返し背中を弓で削る**戦術が成立しやすく、**高 `rangedCover` 盾だけでは遠隔対策に乏しい**メタのカウンターになり得る（条件はバージョンで要再確認）。
- **損耗の非対称（運用）**: プレイヤー側は戦闘後に**療養で作業人員が欠ける**うえ、死亡時は住民全体の機嫌低下も重なりやすい。敵側は撤退・捕縛を含め消耗前提で、同被害でも実質コストが低い。

## 9. 改善レバー（方針マッピング）

| 方針（EQUIPMENT_OVERHAUL） | あり得るレバー（バニラ JSON） | 注意 |
| --- | --- | --- |
| 負傷の肩代わし | `armorRating` / `armorType`、`ArmorQualitySettings` の倍率、命中デバフは `HitEffectorGroups` | Mod 独自 Effector はマージ不確実 |
| 退却可能性 | 防具の `onEquipEffectors` の段階見直し、軽装から `ImpairedMovement*` を外す検討 | 盾 `ShieldCombatSpeed*`、**退却時の背中・カバー角**（観察）との兼ね合い |
| 運ゲー低減 | `Combat/*.json` に確率系があれば調整、なければ実戦検証のみ | キー未同定を明記 |
| 勝ち筋の複線化 | 遠隔の `ignoresArmor` 帯、近接の `armorDamage`（斧ルート） | 単独カテゴリ強化を避ける |
| プレイヤー運用の持続性 | 近接の被弾頻度・重症率を抑える方向（装備時移動ペナ、負傷付与、誤射リスク） | 戦闘勝率だけでなく**療養人日・死亡時の士気損失**を評価軸に含める |

## 10. 次アクション

1. ローカルで `GOING_MEDIEVAL_ITEMS` を設定し、本スクリプトを **フルバニラ**で再実行して表を差し替える。
2. `HitEffectorGroups` / `Wounds` で **脚部・移動系**の付き方を代表武器から追記する。
3. 変更は `Data/Models/Equipment.json` の **部分上書き**から着手し、[COMBAT_PLAYTEST_POLICY.md](../COMBAT_PLAYTEST_POLICY.md) の条件で実戦確認する。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items-dir", type=Path, default=None, help="Vanilla StreamingAssets/Items folder")
    parser.add_argument(
        "--equipment-json",
        type=Path,
        default=None,
        help="Single Equipment.json (e.g. Mod snapshot); implies --partial unless --items-dir set",
    )
    parser.add_argument("--output", "-o", type=Path, default=None)
    parser.add_argument("--partial", action="store_true", help="Force partial snapshot banner")
    args = parser.parse_args()

    items_dir = args.items_dir
    if items_dir is None:
        env = os.environ.get("GOING_MEDIEVAL_ITEMS")
        if env:
            items_dir = Path(env)
    eq_path: Path | None = args.equipment_json
    partial = args.partial
    if eq_path is None:
        if items_dir and (items_dir / "Equipment.json").is_file():
            eq_path = items_dir / "Equipment.json"
            partial = False
        else:
            print("ERROR: pass --items-dir, set GOING_MEDIEVAL_ITEMS, or --equipment-json", file=sys.stderr)
            sys.exit(1)
    if not eq_path.is_file():
        print(f"ERROR: missing {eq_path}", file=sys.stderr)
        sys.exit(1)
    if args.equipment_json is not None and items_dir is None:
        partial = True

    md = build_markdown(equipment_path=eq_path, items_dir=items_dir, partial=partial)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print("Wrote", args.output)
    else:
        print(md)


if __name__ == "__main__":
    main()

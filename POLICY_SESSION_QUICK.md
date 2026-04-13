# Ranged Weapons Overhaul — セッション早見（`POLICY_SESSION_QUICK.md`）

> **役割** — Cursor／人間が **最初に `@` する 1 枚**。タスク別の参照ファイルと **正本** を固定する。詳細は各リンク先のみ読む。

---

## 正本（数値・マージ）

| 正本 | パス |
|------|------|
| 装備の実装 | `Data/Models/Equipment.json`（`requiredSkills` はトップレベル。門限なしは **キー省略**。`Marksman` の `value: 0` は使わない） |
| 品質乗算 | `Data/Models/WeaponQualitySettings.json`（`tools/regenerate_ranged_from_vanilla.py` の `TWO_HAND_BOW_QUALITY_DELTAS` / `TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`） |
| バニラ比較・再同期 | 本体 `Items/Equipment.json` / `Items/WeaponQualitySettings.json`（[`CREATION_POLICY.md`](CREATION_POLICY.md) のパス） |

**Precedence（矛盾時）**: [`BOW_MOD_INTEGRATION_POLICY.md`](BOW_MOD_INTEGRATION_POLICY.md) の順序に従う（JSON ＞ 設計 MD のドラフト表）。

---

## タスク → `@` するファイル

| タスク | `@`（この順で足す） |
|--------|----------------------|
| 何から読むか迷う | 本ファイル → [`BOW_MOD_INTEGRATION_POLICY.md`](BOW_MOD_INTEGRATION_POLICY.md) |
| 弓・クロスの役割／**四弓コンセプト**／射程順／DPS 式／Q3 鎖／門限ドラフト | [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md)（同一ファイル内の「四弓のコンセプト」節） |
| 再生成・変更チェック・実装フェーズ・実効命中の下限 | [`BOW_IMPLEMENTATION_STATUS.md`](BOW_IMPLEMENTATION_STATUS.md) |
| Mod 全体スコープ・部分上書き・丸め・素体×品質 | [`CREATION_POLICY.md`](CREATION_POLICY.md) |
| プレイテスト手順 | [`COMBAT_PLAYTEST_POLICY.md`](COMBAT_PLAYTEST_POLICY.md) |
| 防具・盾・近接・スリング | [`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md) |

---

## よくある禁則（短く）

- 旧スキーマのトップレベル `range` / `damage` / `attackSpeed` は使わない（`primaryWeaponMode` / `secondaryWeaponMode` 配下）。[`CREATION_POLICY.md`](CREATION_POLICY.md)
- `Research.json` / `Production.json` は原則置かない。
- 浮動小数の装備パラメータは **小数第2位・四捨五入**（[`CREATION_POLICY.md`](CREATION_POLICY.md)）。

---

## 再生成ワンショット

弓／クロス 7 種＋門限・WQS: [`scripts/apply_ranged_equipment_delta.py`](scripts/apply_ranged_equipment_delta.py)。チャート: `tools/plot_weapon_quality_comparison.py`。環境変数 `GOING_MEDIEVAL_ITEMS`。

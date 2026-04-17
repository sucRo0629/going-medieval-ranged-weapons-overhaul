# バニラ `onEquipEffectors` の効果詳細

> **目的**: `Items/Equipment.json` の `onEquipEffectors` は **文字列 id の列挙**にすぎない。実際のステータス変化は **`StatsSystem/Effectors.json`**（必要に応じて **`StatsSystem/Attributes.json`** で属性 ID の名前解決）に定義される。本ドキュメントではその関係と、装備時エフェクタごとの**意味**を整理する。

**数値の完全転記（バニラ JSON からの生成）**: [`VANILLA_ON_EQUIP_EFFECTORS.generated.md`](VANILLA_ON_EQUIP_EFFECTORS.generated.md)（手元の `StreamingAssets` で `vanilla_on_equip_effectors_audit.py` を再実行すると更新できる）。

## データの流れ

1. **参照**: 各装備ブロックの `onEquipEffectors` に、`Effectors.json` の `repository[].id` と一致する文字列が並ぶ。
2. **定義**: `Effectors.json` の各エントリは `effects[]` を持ち、各要素は `parameters`（`key` / `value` のペア）で **属性 ID** と **乗算など**を指定する。
3. **属性名**: `parameters` の `Attribute` の `value` は数値 ID であることが多く、**人が読む名前**は `Attributes.json` の `repository` で対応付けられる（バージョンで ID が変わり得るため、**手元インストールの JSON を正**とする）。

コミュニティ解説（構造例・盾攻速ペナの例）: [Effectors.json — Going Medieval wiki](https://goingmedieval.wiki/json/?Effectors.json)

## `Effectors.json` の形（要点）

- **`effects`**: 装備中に適用される効果の配列。
- 各効果は `devName`・`type`・`parameters` を持つ。
- **`parameters`**: 例として `key: "Attribute"`, `value: "26"`（特性の数値 ID）と `key: "Multiplier"`, `value: "1.25"`（乗算）の組み合わせで、近接攻撃間隔などを変える。

同一ファイルには **移動速度以外**（経験値キャップ、行動優先度など）の定義も混在する。装備に載る id だけを対象に読むとよい。

## 装備でよく出る id の意味（要約）

バニラの**数値はバージョンで変わり得る**。確実な抽出は下記「再生成スクリプト」を実行するか、自前の `Effectors.json` を開いて `effects` を確認すること。

| effector id | ざっくりした役割（ゲーム内の意図） | 本リポジトリでの補足 |
|-------------|--------------------------------------|----------------------|
| `ImpairedMovementLow` | `MovementSpeed` ×0.95、`RangedSpeed` ×1.1、`EvadeChance` ×0.95（生成ファイルのとおり）。 | UI 上は移動「小」だが **射撃間隔・回避にも乗る**。弓／クロスへの恒久付与は採用しない方針（[`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](../implementation_policies/melee_armor/EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)）。 |
| `ImpairedMovementMed` | `RangedSpeed` ×1.18（`Low` より重い）、`MovementSpeed` ×0.95、`EvadeChance` ×0.95。 | **二刀ラム**等。移動倍率はデータ上 `Low` と同じだが **遠隔側のペナがより大きい**。 |
| `ShieldCombatSpeedLow` / `Med` / `High` | `MeleeAttackSpeed` に乗算（例: **1.10 / 1.18 / 1.25**）。 | wiki の「Attribute 26」は実データでは **`MeleeAttackSpeed`** 名で解決される。 |
| `WearingMorbidItem` | 気分 **BaseValue −1**（`MoodModify`）。 | `macabre_*` 等。 |
| `SunMaxProtectItem` | `SunlightMax` ×2。 | 例: `kettle_helmet`。 |
| `ChainedUp` | `MovementSpeed` ×0.75、`EvadeChance` ×0.4、`GlobalWorkSpeed` ×0.6、気分 **−20** など。 | 例: `shackles`。 |

## 自動抽出（インストールの `StreamingAssets` が必要）

`Equipment.json` から参照されている **すべての** on-equip id を列挙し、`Effectors.json` から各 `effects` を転記した **マシン可読の一覧**を生成できる。

```bash
export GM_STREAMING_ASSETS="/path/to/Going Medieval_Data/StreamingAssets"
python scripts/vanilla_on_equip_effectors_audit.py --streaming-assets "$GM_STREAMING_ASSETS" -o docs/VANILLA_ON_EQUIP_EFFECTORS.generated.md
```

Windows（例・Steam 既定に近いパス）:

```bat
set GM_STREAMING_ASSETS=D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets
python scripts\vanilla_on_equip_effectors_audit.py --streaming-assets "%GM_STREAMING_ASSETS%" -o docs\VANILLA_ON_EQUIP_EFFECTORS.generated.md
```

`--items-dir` に `.../StreamingAssets/Items` を渡すと、その親を `StreamingAssets` として扱う。

生成物は **`docs/VANILLA_ON_EQUIP_EFFECTORS.generated.md`** を想定（リポジトリにコミットするかは任意。バニラ更新のたびに再実行すると差分追跡に便利）。生成ファイルには **参照 id ごとの日本語要約**と、各 `effects` 行の **日本語説明**がスクリプトから付与される（文言は `scripts/vanilla_on_equip_effectors_audit.py` 内の辞書・ルールで調整）。

## 関連ドキュメント

- 防具・盾の一覧と `onEquipEffectors` の列: [`VANILLA_ARMOR_AUDIT.md`](VANILLA_ARMOR_AUDIT.md)
- 命中時エフェクタ（`hitEffectorGroupIDs`）は別系統: 同ファイルの「命中グループ」節と `StatsSystem/HitEffectorGroups.json`

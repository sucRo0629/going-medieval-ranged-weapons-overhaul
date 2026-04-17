# Mod 用: 全武器一覧（ティア順・製作可否）（生成）

> **バニラデータ**: `D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`（Production / 作業台 / Research）
> **武器種・ティア**: Mod `E:\Users\sucRo\Documents\Foxy Voxel\Going Medieval\Mods\Ranged Weapons Overhaul\Data\Models\Equipment.json`

- **製作可** = 同名 `Production` があり、かついずれかの作業台 `productions` に載っている。
- **製作不可**の行は **作業台・必要スキル（レシピ）・レシピ要約・研究** を `-`（データ上はレシピや研究があってもプレイヤー製作できないため）。
- **装備必要スキル** = 上記と同じマージ後 `requiredSkills`（Mod で上書きした分が優先）。
- **並び（同一 weaponType 内）**: **CombatScore(Base)** に対してコスト補正（槍 < 投擲槍 < 斧 < メイス < 剣）を加えたティア内順位を優先し、同順位は **`primaryWeaponMode.damage` 昇順**、最後に weapon id。
- **damage / attackSpeed / ignoresArmor / armorDamage** = **バニラ `Equipment` に Mod `Equipment` を再帰マージした** `primaryWeaponMode`（Mod キー優先・**Mod 適用後の実効値**）。品質倍率は含まない。
- **CombatScore(Base)** = `damage / attackSpeed` を基礎に、`ignoresArmor`（貫通）・`armorDamage`（装甲剥離）・`precision`・`precisionFalloff`・到達性補正（近接は接敵ロス、遠隔は射程優位）を乗せた比較用スコア。遠距離は **10m/18m/25m の命中係数を 0.60/0.25/0.15 で合成**し、主戦場 10m を重めに評価。
- **CombatScore(鋼想定)** = `MaterialSettings.steel` の `damageMultiplier` / `attackSpeedMultiplier` を `primaryWeaponMode` に仮適用した想定値（金属レシピ行のみ表示）。
- **ティア列**は **CombatScore(Base)** に固定閾値（T2:2.5〜 / T3:3.0〜 / T4:3.5〜 / T5:4.0〜4.5）を適用。
- **鋼版上限方針**: 鋼想定スコアは目安として **T5: 5.0 以下** を維持する。
- **備考**: `A` = レシピなし、`B` = レシピはあるが作業台未掲載（オーファン）。
- **ティア調整用表**（下）: **データ上製作可**に加え `TIER_PLANNING_EXTRA_WEAPON_IDS` の武器を **全 weaponType 混在** で並べ、CombatScore ベースの自動ティアを種別横断で比較する。

- 武器総数: **39** / 製作可: **35**
- CombatScore自動ティア閾値（絶対）: T1:<**2.5**, T2:>=**2.5**, T3:>=**3**, T4:>=**3.5**, T5:**4**〜**4.5**
- 鋼補正（`MaterialSettings.steel`）: damage x**1.2**, attackSpeed x**1**

## ティア調整用: 製作可＋計画武器（全武器種・ティア順）

> **製作可**（マージ後 `Production` ＋作業台）に加え、レシピ調整前でもティアだけ揃えたい id は **`TIER_PLANNING_EXTRA_WEAPON_IDS`**（スクリプト先頭定数）。**ティアは CombatScore の固定閾値（T2:2.5〜 / T3:3.0〜 / T4:3.5〜 / T5:4.0〜4.5）で自動割当**。並びは **ティア内補正後スコア昇順** → **`weaponType` 昇順** → weapon id。

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | damage | attackSpeed | ignoresArmor | armorDamage | 製作 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cudgel` | `OneHandMace` | 1.3 | - | T1 | 10 | 4.65 | 0.05 | 1.5 | 可 |
| `bludgeon` | `OneHandMace` | 1.64 | - | T1 | 14 | 5.25 | 0.05 | 1.95 | 可 |
| `flail` | `OneHandMace` | 1.79 | - | T1 | 10 | 3.6 | 0.08 | 2.3 | 可 |
| `sling` | `OneHandSling` | 2.11 | - | T1 | 14 | 5.25 | 0.25 | 0.7 | 可 |
| `spear` | `TwoHandSpear` | 2.3 | - | T1 | 20 | 6.2 | 0.36 | 0.55 | 可 |
| `light_javelins` | `OneHandThrow` | 2.32 | - | T1 | 18 | 6.1 | 0.3 | 0.9 | 可 |
| `dagger` | `OneHandSword` | 2.54 | 3.05 | T2 | 12 | 2.9 | 0.18 | 0.55 | 可 |
| `military_pick` | `OneHandMace` | 2.68 | 3.21 | T2 | 18 | 4.63 | 0.2 | 2.23 | 可 |
| `sling_staff` | `TwoHandSling` | 2.69 | - | T2 | 21 | 6.8 | 0.35 | 0.8 | 可 |
| `short_bow` | `TwoHandBow` | 2.7 | - | T2 | 11.12 | 3.52 | 0.35 | 0.1 | 可 |
| `reinforced_flail` | `OneHandMace` | 2.71 | 3.26 | T2 | 15 | 3.6 | 0.08 | 2.45 | 可 |
| `reinforced_spear` | `TwoHandSpear` | 2.8 | 3.36 | T2 | 23 | 6.15 | 0.38 | 0.65 | 可 |
| `warfork` | `TwoHandSpear` | 2.92 | - | T2 | 25 | 6.3 | 0.44 | 0.5 | 可 |
| `throwing_axes` | `OneHandThrow` | 2.93 | 3.52 | T2 | 21 | 5.21 | 0.22 | 1 | 可 |
| `light_crossbow` | `TwoHandCrossbow` | 2.98 | - | T2 | 26 | 8.6 | 0.65 | 0.2 | 可 |
| `hatchet` | `OneHandAxe` | 3 | 3.6 | T2 | 18 | 3.85 | 0.2 | 1.45 | 可 |
| `two_handed_flail` | `TwoHandMace` | 3.14 | 3.77 | T3 | 26 | 5.2 | 0.1 | 2.35 | 可 |
| `falchion` | `OneHandSword` | 3.17 | 3.81 | T3 | 15 | 3 | 0.22 | 0.72 | 可 |
| `war_bow` | `TwoHandBow` | 3.33 | - | T3 | 15.9 | 4.72 | 0.58 | 0.1 | 可 |
| `warhammer` | `OneHandMace` | 3.35 | 4.02 | T3 | 21 | 4.05 | 0.1 | 2.1 | 可 |
| `mace` | `OneHandMace` | 3.44 | 4.13 | T3 | 18 | 3.4 | 0.09 | 2.3 | 可 |
| `crossbow` | `TwoHandCrossbow` | 3.44 | - | T3 | 32 | 9.6 | 0.72 | 0.2 | 可 |
| `billhook` | `TwoHandSpear` | 3.47 | 4.16 | T3 | 27 | 5.9 | 0.34 | 0.9 | 可 |
| `two_handed_warhammer` | `TwoHandMace` | 3.66 | 4.39 | T4 | 30 | 5.2 | 0.13 | 2.2 | 可 |
| `short_sword` | `OneHandSword` | 3.7 | 4.44 | T4 | 17 | 3 | 0.29 | 0.58 | 可 |
| `curved_bow` | `TwoHandBow` | 3.7 | - | T4 | 18 | 5.2 | 0.68 | 0.1 | 可 |
| `two_handed_mace` | `TwoHandMace` | 3.8 | 4.56 | T4 | 30 | 4.95 | 0.11 | 2.2 | 可 |
| `berdiche` | `TwoHandSpear` | 3.97 | 4.76 | T4 | 31 | 6 | 0.42 | 0.75 | 可 |
| `heavy_crossbow` | `TwoHandCrossbow` | 4.02 | 4.82 | T5 | 37.8 | 10.6 | 0.85 | 0.2 | 可 |
| `two_handed_flanged_mace` | `TwoHandMace` | 4.05 | 4.86 | T5 | 29.6 | 4.65 | 0.12 | 2.35 | 可 |
| `knightly_sword` | `OneHandSword` | 4.12 | 4.95 | T5 | 20.4 | 3.28 | 0.31 | 0.66 | 可 |
| `long_bow` | `TwoHandBow` | 4.15 | 4.98 | T5 | 23.3 | 6.2 | 0.7 | 0.1 | 可 |
| `longsword` | `TwoHandSword` | 4.16 | 4.99 | T5 | 27.1 | 4.43 | 0.32 | 0.68 | 可 |
| `greatsword` | `TwoHandSword` | 4.16 | 4.99 | T5 | 31.5 | 5.17 | 0.32 | 0.75 | 可 |
| `greataxe` | `TwoHandAxe` | 4.16 | 4.99 | T5 | 33.1 | 5.1 | 0.22 | 1.55 | 可 |

---

## 弓（TwoHandBow）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `short_bow` | `TwoHandBow` | 2.7 | - | T2 | `fletchers_table` | Carpentry 5 | wood x20 | -（`Research.unlocks` 無し・初期解禁等） | なし | 11.12 | 3.52 | 0.35 | 0.1 | 製作可 |
| `war_bow` | `TwoHandBow` | 3.33 | - | T3 | `fletchers_table` | Carpentry 10 | wood x30, leather x5 | -（`Research.unlocks` 無し・初期解禁等） | Marksman 5 | 15.9 | 4.72 | 0.58 | 0.1 | 製作可 |
| `curved_bow` | `TwoHandBow` | 3.7 | - | T4 | `fletchers_table` | Carpentry 10 | wood x35, leather x10 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | Marksman 10 | 18 | 5.2 | 0.68 | 0.1 | 製作可 |
| `long_bow` | `TwoHandBow` | 4.15 | 4.98 | T5 | `fletchers_table` | Carpentry 20 | wood x50, leather x10, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | Marksman 20 | 23.3 | 6.2 | 0.7 | 0.1 | 製作可 |

## クロスボウ（TwoHandCrossbow）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `light_crossbow` | `TwoHandCrossbow` | 2.98 | - | T2 | `fletchers_table` | Carpentry 10 | wood x25, wood_mechanical_parts x1 | `crossbows_lvl2` / `research_name_crossbows_lvl2`（ローカライズキー） / 3 | なし | 26 | 8.6 | 0.65 | 0.2 | 製作可 |
| `crossbow` | `TwoHandCrossbow` | 3.44 | - | T3 | `fletchers_table` | Carpentry 15 | wood x40, wood_mechanical_parts x5 | `crossbows_lvl2` / `research_name_crossbows_lvl2`（ローカライズキー） / 3 | なし | 32 | 9.6 | 0.72 | 0.2 | 製作可 |
| `heavy_crossbow` | `TwoHandCrossbow` | 4.02 | 4.82 | T5 | `fletchers_table` | Carpentry 15 | wood x45, mechanical_parts x5, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | `crossbows_lvl3` / `research_name_crossbows_lvl3`（ローカライズキー） / 4 | Marksman 15 | 37.8 | 10.6 | 0.85 | 0.2 | 製作可 |

## 片手スリング（OneHandSling）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sling` | `OneHandSling` | 2.11 | - | T1 | `fletchers_table` | Tailoring 0 | 皮革類（leather 系・カテゴリマスク） x1 | -（`Research.unlocks` 無し・初期解禁等） | なし | 14 | 5.25 | 0.25 | 0.7 | 製作可 |

## 両手スリング（TwoHandSling）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sling_staff` | `TwoHandSling` | 2.69 | - | T2 | `fletchers_table` | Carpentry 0 | 皮革類（leather 系・カテゴリマスク） x3, wood x5 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | なし | 21 | 6.8 | 0.35 | 0.8 | 製作可 |

## 投擲（OneHandThrow）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `light_javelins` | `OneHandThrow` | 2.32 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x18 | -（`Research.unlocks` 無し・初期解禁等） | Marksman 5 | 18 | 6.1 | 0.3 | 0.9 | 製作可 |
| `throwing_axes` | `OneHandThrow` | 2.93 | 3.52 | T2 | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x5, wood x20 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 | Marksman 5 | 21 | 5.21 | 0.22 | 1 | 製作可 |

## 片手斧（OneHandAxe）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hatchet` | `OneHandAxe` | 3 | 3.6 | T2 | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x10, wood x10 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 | なし | 18 | 3.85 | 0.2 | 1.45 | 製作可 |

## 両手斧（TwoHandAxe）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `greataxe` | `TwoHandAxe` | 4.16 | 4.99 | T5 | `blacksmith_station` | Smithing 20 | 金属インゴット類（iron/steel 等・カテゴリマスク） x40, wood x15 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 | Melee 20 | 33.1 | 5.1 | 0.22 | 1.55 | 製作可 |

## 片手剣（OneHandSword）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `example_weapon` | `OneHandSword` | 0.35 | - | T1 | - | - | - | - | Botanical 20, Speechcraft 5 | 2 | 3.6 | 0.2 | 0.6 | A: レシピなし |
| `dagger` | `OneHandSword` | 2.54 | 3.05 | T2 | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x10, wood x20 | -（`Research.unlocks` 無し・初期解禁等） | なし | 12 | 2.9 | 0.18 | 0.55 | 製作可 |
| `falchion` | `OneHandSword` | 3.17 | 3.81 | T3 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x20, wood x15 | -（`Research.unlocks` 無し・初期解禁等） | Melee 5 | 15 | 3 | 0.22 | 0.72 | 製作可 |
| `short_sword` | `OneHandSword` | 3.7 | 4.44 | T4 | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x30, wood x20 | -（`Research.unlocks` 無し・初期解禁等） | Melee 10 | 17 | 3 | 0.29 | 0.58 | 製作可 |
| `knightly_sword` | `OneHandSword` | 4.12 | 4.95 | T5 | `blacksmith_station` | Smithing 15 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, wood x40 | -（`Research.unlocks` 無し・初期解禁等） | Melee 15 | 20.4 | 3.28 | 0.31 | 0.66 | 製作可 |

## 両手剣（TwoHandSword）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `longsword` | `TwoHandSword` | 4.16 | 4.99 | T5 | `blacksmith_station` | Smithing 20 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, wood x35 | `swords_lvl2` / `research_name_swords_lvl2`（ローカライズキー） / 3 | Melee 15 | 27.1 | 4.43 | 0.32 | 0.68 | 製作可 |
| `greatsword` | `TwoHandSword` | 4.16 | 4.99 | T5 | `blacksmith_station` | Smithing 25 | 金属インゴット類（iron/steel 等・カテゴリマスク） x45, wood x30 | `swords_lvl2` / `research_name_swords_lvl2`（ローカライズキー） / 3 | Melee 20 | 31.5 | 5.17 | 0.32 | 0.75 | 製作可 |

## 片手鈍器（OneHandMace）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cudgel` | `OneHandMace` | 1.3 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x25 | -（`Research.unlocks` 無し・初期解禁等） | なし | 10 | 4.65 | 0.05 | 1.5 | 製作可 |
| `bludgeon` | `OneHandMace` | 1.64 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x25 | -（`Research.unlocks` 無し・初期解禁等） | Melee 5 | 14 | 5.25 | 0.05 | 1.95 | 製作可 |
| `flail` | `OneHandMace` | 1.79 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x30 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | なし | 10 | 3.6 | 0.08 | 2.3 | 製作可 |
| `military_pick` | `OneHandMace` | 2.68 | 3.21 | T2 | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x11, wood x11 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 0 | 18 | 4.63 | 0.2 | 2.23 | 製作可 |
| `reinforced_flail` | `OneHandMace` | 2.71 | 3.26 | T2 | `blacksmith_station`, `woodwork_bench` | Smithing 5, Carpentry 5 | wood x30, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 0 | 15 | 3.6 | 0.08 | 2.45 | 製作可 |
| `warhammer` | `OneHandMace` | 3.35 | 4.02 | T3 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, wood x10 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | なし | 21 | 4.05 | 0.1 | 2.1 | 製作可 |
| `mace` | `OneHandMace` | 3.44 | 4.13 | T3 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x20, wood x10 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | なし | 18 | 3.4 | 0.09 | 2.3 | 製作可 |

## 両手鈍器（TwoHandMace）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `two_handed_flail` | `TwoHandMace` | 3.14 | 3.77 | T3 | `blacksmith_station`, `woodwork_bench` | Smithing 5, Carpentry 10 | wood x45, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3<br>`woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | Melee 5 | 26 | 5.2 | 0.1 | 2.35 | 製作可 |
| `two_handed_warhammer` | `TwoHandMace` | 3.66 | 4.39 | T4 | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x30, wood x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 10 | 30 | 5.2 | 0.13 | 2.2 | 製作可 |
| `two_handed_mace` | `TwoHandMace` | 3.8 | 4.56 | T4 | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, wood x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 10 | 30 | 4.95 | 0.11 | 2.2 | 製作可 |
| `two_handed_flanged_mace` | `TwoHandMace` | 4.05 | 4.86 | T5 | `blacksmith_station` | Smithing 15 | 金属インゴット類（iron/steel 等・カテゴリマスク） x40, wood x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 10 | 29.6 | 4.65 | 0.12 | 2.35 | 製作可 |

## 槍／長柄（TwoHandSpear）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `spear` | `TwoHandSpear` | 2.3 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x15 | -（`Research.unlocks` 無し・初期解禁等） | なし | 20 | 6.2 | 0.36 | 0.55 | 製作可 |
| `warfork` | `TwoHandSpear` | 2.92 | - | T2 | `woodwork_bench` | Carpentry 5 | wood x15 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | なし | 25 | 6.3 | 0.44 | 0.5 | 製作可 |
| `reinforced_spear` | `TwoHandSpear` | 2.8 | 3.36 | T2 | `blacksmith_station`, `woodwork_bench` | Carpentry 5 | wood x15, 金属インゴット類（iron/steel 等・カテゴリマスク） x3 | -（`Research.unlocks` 無し・初期解禁等） | なし | 23 | 6.15 | 0.38 | 0.65 | 製作可 |
| `billhook` | `TwoHandSpear` | 3.47 | 4.16 | T3 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x10, wood x10 | -（`Research.unlocks` 無し・初期解禁等） | なし | 27 | 5.9 | 0.34 | 0.9 | 製作可 |
| `berdiche` | `TwoHandSpear` | 3.97 | 4.76 | T4 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, wood x10 | -（`Research.unlocks` 無し・初期解禁等） | なし | 31 | 6 | 0.42 | 0.75 | 製作可 |

## 杖（TwoHandStaff）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `staff` | `TwoHandStaff` | 3.43 | - | T3 | - | - | - | - | なし | 28 | 4.95 | 0.1 | 1.1 | B: 作業台オーファン |

## ラム（TwoHandRam）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hand_ram` | `TwoHandRam` | 3.28 | - | T3 | - | - | - | - | なし | 40 | 8.1 | 0.4 | 1 | A: レシピなし |
| `metal_hand_ram` | `TwoHandRam` | 3.77 | - | T4 | - | - | - | - | なし | 46 | 8.1 | 0.4 | 1 | A: レシピなし |

---

_生成: `scripts/mod_weapon_overview_table.py`_

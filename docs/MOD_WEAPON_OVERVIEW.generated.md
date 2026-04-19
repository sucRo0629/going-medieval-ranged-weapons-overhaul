# Mod 用: 全武器一覧（ティア順・製作可否）（生成）

> **バニラデータ**: `D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`（Production / 作業台 / Research）
> **武器種・ティア**: Mod `Data\Models\Items\Equipment.json`

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

- 武器総数: **40** / 製作可: **36**
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
| `light_javelins` | `OneHandThrow` | 2.23 | - | T1 | 17.6 | 6.1 | 0.3 | 0.6 | 可 |
| `spear` | `TwoHandSpear` | 2.3 | - | T1 | 20 | 6.2 | 0.36 | 0.55 | 可 |
| `short_bow` | `TwoHandBow` | 2.47 | - | T1 | 11 | 3.5 | 0.2 | 0.05 | 可 |
| `reinforced_flail` | `OneHandMace` | 2.57 | 3.08 | T2 | 15 | 3.8 | 0.08 | 2.45 | 可 |
| `dagger` | `OneHandSword` | 2.67 | 3.2 | T2 | 10 | 2.2 | 0.15 | 0.12 | 可 |
| `military_pick` | `OneHandMace` | 2.68 | 3.21 | T2 | 18 | 4.63 | 0.2 | 2.23 | 可 |
| `sling_staff` | `TwoHandSling` | 2.69 | - | T2 | 21 | 6.8 | 0.35 | 0.8 | 可 |
| `throwing_axes` | `OneHandThrow` | 2.8 | 3.36 | T2 | 17.5 | 4.5 | 0.2 | 1 | 可 |
| `hatchet` | `OneHandAxe` | 2.8 | 3.36 | T2 | 19 | 4.35 | 0.2 | 1.45 | 可 |
| `warfork` | `TwoHandSpear` | 2.88 | - | T2 | 21.6 | 5.3 | 0.36 | 0.5 | 可 |
| `reinforced_spear` | `TwoHandSpear` | 2.97 | 3.56 | T2 | 23 | 5.8 | 0.4 | 0.5 | 可 |
| `light_crossbow` | `TwoHandCrossbow` | 2.98 | - | T2 | 26 | 8.6 | 0.65 | 0.2 | 可 |
| `falchion` | `OneHandSword` | 3.02 | 3.63 | T3 | 15 | 3.15 | 0.22 | 0.72 | 可 |
| `mace` | `OneHandMace` | 3.23 | 3.87 | T3 | 17.5 | 3.5 | 0.09 | 2.2 | 可 |
| `warhammer` | `OneHandMace` | 3.23 | 3.88 | T3 | 20.4 | 4.05 | 0.1 | 2 | 可 |
| `war_bow` | `TwoHandBow` | 3.33 | - | T3 | 15.9 | 4.72 | 0.58 | 0.1 | 可 |
| `two_handed_flail` | `TwoHandMace` | 3.33 | 4 | T3 | 26 | 5 | 0.1 | 2.7 | 可 |
| `crossbow` | `TwoHandCrossbow` | 3.44 | - | T3 | 32 | 9.6 | 0.72 | 0.2 | 可 |
| `billhook` | `TwoHandSpear` | 3.47 | 4.16 | T3 | 27 | 5.9 | 0.34 | 0.9 | 可 |
| `short_sword` | `OneHandSword` | 3.53 | 4.23 | T4 | 17 | 3 | 0.2 | 0.58 | 可 |
| `javelins` | `OneHandThrow` | 3.57 | 4.28 | T4 | 25 | 5.8 | 0.3 | 1.5 | 可 |
| `curved_bow` | `TwoHandBow` | 3.7 | - | T4 | 18 | 5.2 | 0.68 | 0.1 | 可 |
| `two_handed_warhammer` | `TwoHandMace` | 3.74 | 4.49 | T4 | 30.1 | 5.1 | 0.13 | 2.2 | 可 |
| `two_handed_mace` | `TwoHandMace` | 3.74 | 4.49 | T4 | 28.4 | 4.8 | 0.11 | 2.36 | 可 |
| `berdiche` | `TwoHandSpear` | 3.97 | 4.76 | T4 | 31 | 6 | 0.42 | 0.75 | 可 |
| `knightly_sword` | `OneHandSword` | 4 | 4.8 | T5 | 19.5 | 3.23 | 0.31 | 0.66 | 可 |
| `longsword` | `TwoHandSword` | 4.06 | 4.88 | T5 | 26.5 | 4.43 | 0.32 | 0.68 | 可 |
| `heavy_crossbow` | `TwoHandCrossbow` | 4.12 | 4.94 | T5 | 38 | 10.4 | 0.85 | 0.2 | 可 |
| `greatsword` | `TwoHandSword` | 4.15 | 4.98 | T5 | 31 | 5.1 | 0.32 | 0.75 | 可 |
| `greataxe` | `TwoHandAxe` | 4.15 | 4.98 | T5 | 34 | 5.3 | 0.22 | 1.7 | 可 |
| `two_handed_flanged_mace` | `TwoHandMace` | 4.15 | 4.98 | T5 | 29.6 | 4.65 | 0.15 | 2.5 | 可 |
| `long_bow` | `TwoHandBow` | 4.15 | 4.98 | T5 | 23.3 | 6.2 | 0.7 | 0.1 | 可 |

---

## 弓（TwoHandBow）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `short_bow` | `TwoHandBow` | 2.47 | - | T1 | `fletchers_table` | Carpentry 5 | — | -（`Research.unlocks` 無し・初期解禁等） | なし | 11 | 3.5 | 0.2 | 0.05 | 製作可 |
| `war_bow` | `TwoHandBow` | 3.33 | - | T3 | `fletchers_table` | Carpentry 10 | wood x30, 皮革類（leather 系・カテゴリマスク） x5 | -（`Research.unlocks` 無し・初期解禁等） | Marksman 5 | 15.9 | 4.72 | 0.58 | 0.1 | 製作可 |
| `curved_bow` | `TwoHandBow` | 3.7 | - | T4 | `fletchers_table` | Carpentry 10 | wood x45, 皮革類（leather 系・カテゴリマスク） x10 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | Marksman 10 | 18 | 5.2 | 0.68 | 0.1 | 製作可 |
| `long_bow` | `TwoHandBow` | 4.15 | 4.98 | T5 | `fletchers_table` | Carpentry 20 | wood x50, 皮革類（leather 系・カテゴリマスク） x10, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | Marksman 20 | 23.3 | 6.2 | 0.7 | 0.1 | 製作可 |

## クロスボウ（TwoHandCrossbow）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `light_crossbow` | `TwoHandCrossbow` | 2.98 | - | T2 | `fletchers_table` | Carpentry 15 | wood x25, wood_mechanical_parts x2 | `crossbows_lvl2` / `research_name_crossbows_lvl2`（ローカライズキー） / 3 | なし | 26 | 8.6 | 0.65 | 0.2 | 製作可 |
| `crossbow` | `TwoHandCrossbow` | 3.44 | - | T3 | `fletchers_table` | — | wood x40, wood_mechanical_parts x3 | `crossbows_lvl2` / `research_name_crossbows_lvl2`（ローカライズキー） / 3 | なし | 32 | 9.6 | 0.72 | 0.2 | 製作可 |
| `heavy_crossbow` | `TwoHandCrossbow` | 4.12 | 4.94 | T5 | `fletchers_table` | Carpentry 25 | wood x45, mechanical_parts x6, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | `crossbows_lvl3` / `research_name_crossbows_lvl3`（ローカライズキー） / 4 | Marksman 15 | 38 | 10.4 | 0.85 | 0.2 | 製作可 |

## 片手スリング（OneHandSling）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sling` | `OneHandSling` | 2.11 | - | T1 | `fletchers_table` | — | 皮革類（leather 系・カテゴリマスク） x2 | -（`Research.unlocks` 無し・初期解禁等） | なし | 14 | 5.25 | 0.25 | 0.7 | 製作可 |

## 両手スリング（TwoHandSling）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sling_staff` | `TwoHandSling` | 2.69 | - | T2 | `fletchers_table` | — | 皮革類（leather 系・カテゴリマスク） x3, wood x5 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | なし | 21 | 6.8 | 0.35 | 0.8 | 製作可 |

## 投擲（OneHandThrow）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `light_javelins` | `OneHandThrow` | 2.23 | - | T1 | `woodwork_bench` | — | — | -（`Research.unlocks` 無し・初期解禁等） | Marksman 5 | 17.6 | 6.1 | 0.3 | 0.6 | 製作可 |
| `throwing_axes` | `OneHandThrow` | 2.8 | 3.36 | T2 | `blacksmith_station` | — | iron_ingot x0, wood x20, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | -（`Research.unlocks` 無し・初期解禁等） | Marksman 5 | 17.5 | 4.5 | 0.2 | 1 | 製作可 |
| `javelins` | `OneHandThrow` | 3.57 | 4.28 | T4 | `blacksmith_station`, `woodwork_bench` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x10, wood x20 | -（`Research.unlocks` 無し・初期解禁等） | Marksman 10 | 25 | 5.8 | 0.3 | 1.5 | 製作可 |

## 片手斧（OneHandAxe）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hatchet` | `OneHandAxe` | 2.8 | 3.36 | T2 | `blacksmith_station` | — | 金属インゴット類（iron/steel 等・カテゴリマスク） x10, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | -（`Research.unlocks` 無し・初期解禁等） | なし | 19 | 4.35 | 0.2 | 1.45 | 製作可 |

## 両手斧（TwoHandAxe）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `greataxe` | `TwoHandAxe` | 4.15 | 4.98 | T5 | `blacksmith_station` | — | 金属インゴット類（iron/steel 等・カテゴリマスク） x45, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x30 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 | Melee 20 | 34 | 5.3 | 0.22 | 1.7 | 製作可 |

## 片手剣（OneHandSword）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `example_weapon` | `OneHandSword` | 0.44 | - | T1 | - | - | - | - | Botanical 20, Speechcraft 5 | 2 | 3.6 | 0.7 | 0.6 | A: レシピなし |
| `dagger` | `OneHandSword` | 2.67 | 3.2 | T2 | `blacksmith_station` | — | 金属インゴット類（iron/steel 等・カテゴリマスク） x10, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | -（`Research.unlocks` 無し・初期解禁等） | なし | 10 | 2.2 | 0.15 | 0.12 | 製作可 |
| `falchion` | `OneHandSword` | 3.02 | 3.63 | T3 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x20, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | -（`Research.unlocks` 無し・初期解禁等） | Melee 5 | 15 | 3.15 | 0.22 | 0.72 | 製作可 |
| `short_sword` | `OneHandSword` | 3.53 | 4.23 | T4 | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x30, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x20 | -（`Research.unlocks` 無し・初期解禁等） | Melee 10 | 17 | 3 | 0.2 | 0.58 | 製作可 |
| `knightly_sword` | `OneHandSword` | 4 | 4.8 | T5 | `blacksmith_station` | Smithing 15 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x40 | -（`Research.unlocks` 無し・初期解禁等） | Melee 15 | 19.5 | 3.23 | 0.31 | 0.66 | 製作可 |

## 両手剣（TwoHandSword）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `longsword` | `TwoHandSword` | 4.06 | 4.88 | T5 | `blacksmith_station` | Smithing 20 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x35 | `swords_lvl2` / `research_name_swords_lvl2`（ローカライズキー） / 3 | Melee 15 | 26.5 | 4.43 | 0.32 | 0.68 | 製作可 |
| `greatsword` | `TwoHandSword` | 4.15 | 4.98 | T5 | `blacksmith_station` | Smithing 25 | 金属インゴット類（iron/steel 等・カテゴリマスク） x45, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x30 | `swords_lvl2` / `research_name_swords_lvl2`（ローカライズキー） / 3 | Melee 20 | 31 | 5.1 | 0.32 | 0.75 | 製作可 |

## 片手鈍器（OneHandMace）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cudgel` | `OneHandMace` | 1.3 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x25 | -（`Research.unlocks` 無し・初期解禁等） | なし | 10 | 4.65 | 0.05 | 1.5 | 製作可 |
| `bludgeon` | `OneHandMace` | 1.64 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x25 | -（`Research.unlocks` 無し・初期解禁等） | Melee 5 | 14 | 5.25 | 0.05 | 1.95 | 製作可 |
| `flail` | `OneHandMace` | 1.79 | - | T1 | `woodwork_bench` | Carpentry 0 | wood x30 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | なし | 10 | 3.6 | 0.08 | 2.3 | 製作可 |
| `reinforced_flail` | `OneHandMace` | 2.57 | 3.08 | T2 | `blacksmith_station`, `woodwork_bench` | Carpentry 5 | wood x30, iron_ingot x0, 金属インゴット類（iron/steel 等・カテゴリマスク） x2 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 0 | 15 | 3.8 | 0.08 | 2.45 | 製作可 |
| `military_pick` | `OneHandMace` | 2.68 | 3.21 | T2 | `blacksmith_station` | — | iron_ingot x0, 金属インゴット類（iron/steel 等・カテゴリマスク） x10, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 0 | 18 | 4.63 | 0.2 | 2.23 | 製作可 |
| `mace` | `OneHandMace` | 3.23 | 3.87 | T3 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x20, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | なし | 17.5 | 3.5 | 0.09 | 2.2 | 製作可 |
| `warhammer` | `OneHandMace` | 3.23 | 3.88 | T3 | `blacksmith_station` | Smithing 5 | wood x10, iron_ingot x0, 金属インゴット類（iron/steel 等・カテゴリマスク） x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | なし | 20.4 | 4.05 | 0.1 | 2 | 製作可 |

## 両手鈍器（TwoHandMace）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `two_handed_flail` | `TwoHandMace` | 3.33 | 4 | T3 | `blacksmith_station`, `woodwork_bench` | Smithing 5 | wood x45, 金属インゴット類（iron/steel 等・カテゴリマスク） x5 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3<br>`woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | Melee 5 | 26 | 5 | 0.1 | 2.7 | 製作可 |
| `two_handed_warhammer` | `TwoHandMace` | 3.74 | 4.49 | T4 | `blacksmith_station` | Smithing 10 | iron_ingot x0, wood x15, 金属インゴット類（iron/steel 等・カテゴリマスク） x30 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 10 | 30.1 | 5.1 | 0.13 | 2.2 | 製作可 |
| `two_handed_mace` | `TwoHandMace` | 3.74 | 4.49 | T4 | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 10 | 28.4 | 4.8 | 0.11 | 2.36 | 製作可 |
| `two_handed_flanged_mace` | `TwoHandMace` | 4.15 | 4.98 | T5 | `blacksmith_station` | Smithing 15 | iron_ingot x0, 金属インゴット類（iron/steel 等・カテゴリマスク） x40, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 10 | 29.6 | 4.65 | 0.15 | 2.5 | 製作可 |

## 槍／長柄（TwoHandSpear）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `spear` | `TwoHandSpear` | 2.3 | - | T1 | `woodwork_bench` | — | wood x15 | -（`Research.unlocks` 無し・初期解禁等） | なし | 20 | 6.2 | 0.36 | 0.55 | 製作可 |
| `warfork` | `TwoHandSpear` | 2.88 | - | T2 | `woodwork_bench` | — | wood x15 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | なし | 21.6 | 5.3 | 0.36 | 0.5 | 製作可 |
| `reinforced_spear` | `TwoHandSpear` | 2.97 | 3.56 | T2 | `blacksmith_station`, `woodwork_bench` | Carpentry 5 | wood x15, iron_ingot x0, 金属インゴット類（iron/steel 等・カテゴリマスク） x2 | -（`Research.unlocks` 無し・初期解禁等） | なし | 23 | 5.8 | 0.4 | 0.5 | 製作可 |
| `billhook` | `TwoHandSpear` | 3.47 | 4.16 | T3 | `blacksmith_station` | Smithing 5 | iron_ingot x0, wood x0, 金属インゴット類（iron/steel 等・カテゴリマスク） x10, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | -（`Research.unlocks` 無し・初期解禁等） | なし | 27 | 5.9 | 0.34 | 0.9 | 製作可 |
| `berdiche` | `TwoHandSpear` | 3.97 | 4.76 | T4 | `blacksmith_station` | Smithing 5 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | -（`Research.unlocks` 無し・初期解禁等） | なし | 31 | 6 | 0.42 | 0.75 | 製作可 |

## 杖（TwoHandStaff）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `staff` | `TwoHandStaff` | 3.43 | - | T3 | - | Carpentry 0 | wood x20 | - | なし | 28 | 4.95 | 0.1 | 1.1 | B: 作業台オーファン |

## ラム（TwoHandRam）

| weapon | `weaponType` | CombatScore(Base) | CombatScore(鋼想定) | ティア（CombatScore自動） | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | damage | attackSpeed | ignoresArmor | armorDamage | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hand_ram` | `TwoHandRam` | 3.28 | - | T3 | - | - | - | - | なし | 40 | 8.1 | 0.4 | 1 | A: レシピなし |
| `metal_hand_ram` | `TwoHandRam` | 3.77 | - | T4 | - | - | - | - | なし | 46 | 8.1 | 0.4 | 1 | A: レシピなし |

---

_生成: `scripts/mod_weapon_overview_table.py`_

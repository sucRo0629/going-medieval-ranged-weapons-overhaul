# Mod 用: 全武器一覧（ティア順・製作可否）（生成）

> **バニラデータ**: `D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`（Production / 作業台 / Research）
> **武器種・ティア**: Mod `Data\Models\Equipment.json`

- **製作可** = 同名 `Production` があり、かついずれかの作業台 `productions` に載っている。
- **製作不可**の行は **作業台・必要スキル（レシピ）・レシピ要約・研究** を `-`（データ上はレシピや研究があってもプレイヤー製作できないため）。
- **装備必要スキル（Mod）** = Mod（無ければバニラ）`Equipment.requiredSkills`。
- **備考**: `A` = レシピなし、`B` = レシピはあるが作業台未掲載（オーファン）。

- 武器総数: **39** / 製作可: **21**

## 弓（TwoHandBow）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `short_bow` | `TwoHandBow` | 設計T1 | `short_bow` | `fletchers_table` | Carpentry 0 | wood x20 | -（`Research.unlocks` 無し・初期解禁等） | なし | 製作可 |
| `war_bow` | `TwoHandBow` | 設計T2 | `war_bow` | `fletchers_table` | Carpentry 5 | wood x25, 皮革類（leather 系・カテゴリマスク） x5 | -（`Research.unlocks` 無し・初期解禁等） | Marksman 5 | 製作可 |
| `curved_bow` | `TwoHandBow` | 設計T3 | `curved_bow` | `fletchers_table` | Carpentry 10 | wood x30, 皮革類（leather 系・カテゴリマスク） x5 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | Marksman 10 | 製作可 |
| `long_bow` | `TwoHandBow` | 設計T4 | `long_bow` | `fletchers_table` | Carpentry 15 | wood x40, 皮革類（leather 系・カテゴリマスク） x5 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | Marksman 20 | 製作可 |

## クロスボウ（TwoHandCrossbow）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `light_crossbow` | `TwoHandCrossbow` | 設計T2 | `light_crossbow` | - | - | - | - | なし | B: 作業台オーファン |
| `crossbow` | `TwoHandCrossbow` | 設計T3 | `crossbow` | `fletchers_table` | Carpentry 20 | wood x35, wood_mechanical_parts x3 | `crossbows_lvl2` / `research_name_crossbows_lvl2`（ローカライズキー） / 3 | なし | 製作可 |
| `heavy_crossbow` | `TwoHandCrossbow` | 設計T4 | `heavy_crossbow` | `fletchers_table` | Carpentry 20 | wood x45, mechanical_parts x3 | `crossbows_lvl3` / `research_name_crossbows_lvl3`（ローカライズキー） / 4 | Marksman 15 | 製作可 |

## 片手スリング（OneHandSling）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sling` | `OneHandSling` | 射程・素体順（短いほど先） | `sling` | `fletchers_table` | Tailoring 0 | 皮革類（leather 系・カテゴリマスク） x5 | -（`Research.unlocks` 無し・初期解禁等） | なし | 製作可 |

## 両手スリング（TwoHandSling）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sling_staff` | `TwoHandSling` | 射程・素体順（短いほど先） | `sling_staff` | `fletchers_table` | Carpentry 0 | 皮革類（leather 系・カテゴリマスク） x5, wood x10 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 | なし | 製作可 |

## 投擲（OneHandThrow）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `light_javelins` | `OneHandThrow` | レシピ Carpentry 0 | `light_javelins` | `woodwork_bench` | Carpentry 0 | wood x20 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | なし | 製作可 |
| `throwing_axes` | `OneHandThrow` | レシピ Smithing 10 | `throwing_axes` | `blacksmith_station` | Smithing 10 | iron_ingot x5, wood x20 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 | Marksman 5 | 製作可 |

## 片手斧（OneHandAxe）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hatchet` | `OneHandAxe` | レシピ Smithing 0 | `hatchet` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 | なし | 製作可 |

## 両手斧（TwoHandAxe）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `greataxe` | `TwoHandAxe` | レシピ Smithing 20 | `greataxe` | `blacksmith_station` | Smithing 20 | 金属インゴット類（iron/steel 等・カテゴリマスク） x40, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 | Melee 15 | 製作可 |

## 片手剣（OneHandSword）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `falchion` | `OneHandSword` | レシピ Carpentry 0 | `falchion` | - | - | - | - | なし | B: 作業台オーファン |
| `dagger` | `OneHandSword` | レシピ Smithing 0 | `dagger` | - | - | - | - | なし | B: 作業台オーファン |
| `short_sword` | `OneHandSword` | レシピ Smithing 0 | `short_sword` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | -（`Research.unlocks` 無し・初期解禁等） | なし | 製作可 |
| `knightly_sword` | `OneHandSword` | レシピ Smithing 10 | `knightly_sword` | - | - | - | - | Melee 10 | B: 作業台オーファン |
| `example_weapon` | `OneHandSword` | — | - | - | - | - | - | Botanical 20, Speechcraft 5 | A: レシピなし |

## 両手剣（TwoHandSword）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `greatsword` | `TwoHandSword` | レシピ Smithing 20 | `greatsword` | - | - | - | - | Melee 20 | B: 作業台オーファン |
| `longsword` | `TwoHandSword` | レシピ Smithing 20 | `longsword` | `blacksmith_station` | Smithing 20 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x25 | `swords_lvl2` / `research_name_swords_lvl2`（ローカライズキー） / 3 | Melee 15 | 製作可 |

## 片手鈍器（OneHandMace）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bludgeon` | `OneHandMace` | レシピ Carpentry 0 | `bludgeon` | - | - | - | - | なし | B: 作業台オーファン |
| `cudgel` | `OneHandMace` | レシピ Carpentry 0 | `cudgel` | `woodwork_bench` | Carpentry 0 | wood x25 | -（`Research.unlocks` 無し・初期解禁等） | なし | 製作可 |
| `flail` | `OneHandMace` | レシピ Carpentry 0 | `flail` | `woodwork_bench` | Carpentry 0 | wood x30 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | なし | 製作可 |
| `reinforced_flail` | `OneHandMace` | レシピ Carpentry 0 | `reinforced_flail` | - | - | - | - | なし | B: 作業台オーファン |
| `mace` | `OneHandMace` | レシピ Smithing 0 | `mace` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | なし | 製作可 |
| `military_pick` | `OneHandMace` | レシピ Smithing 0 | `military_pick` | - | - | - | - | Melee 10 | B: 作業台オーファン |
| `warhammer` | `OneHandMace` | レシピ Smithing 10 | `warhammer` | - | - | - | - | なし | B: 作業台オーファン |

## 両手鈍器（TwoHandMace）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `two_handed_flail` | `TwoHandMace` | レシピ Carpentry 0 | `two_handed_flail` | `woodwork_bench` | Carpentry 0 | wood x45 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 | なし | 製作可 |
| `two_handed_flanged_mace` | `TwoHandMace` | レシピ Smithing 0 | `two_handed_flanged_mace` | - | - | - | - | Melee 10 | B: 作業台オーファン |
| `two_handed_mace` | `TwoHandMace` | レシピ Smithing 10 | `two_handed_mace` | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x30, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 | Melee 10 | 製作可 |
| `two_handed_warhammer` | `TwoHandMace` | レシピ Smithing 20 | `two_handed_warhammer` | - | - | - | - | Melee 10 | B: 作業台オーファン |

## 槍／長柄（TwoHandSpear）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `reinforced_spear` | `TwoHandSpear` | レシピ Carpentry 0 | `reinforced_spear` | - | - | - | - | なし | B: 作業台オーファン |
| `spear` | `TwoHandSpear` | レシピ Carpentry 0 | `spear` | `woodwork_bench` | Carpentry 0 | wood x30 | -（`Research.unlocks` 無し・初期解禁等） | なし | 製作可 |
| `warfork` | `TwoHandSpear` | レシピ Carpentry 0 | `warfork` | - | - | - | - | なし | B: 作業台オーファン |
| `berdiche` | `TwoHandSpear` | レシピ Smithing 0 | `berdiche` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | -（`Research.unlocks` 無し・初期解禁等） | なし | 製作可 |
| `billhook` | `TwoHandSpear` | レシピ Smithing 10 | `billhook` | - | - | - | - | なし | B: 作業台オーファン |

## 杖（TwoHandStaff）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `staff` | `TwoHandStaff` | レシピ Carpentry 0 | `staff` | - | - | - | - | なし | B: 作業台オーファン |

## ラム（TwoHandRam）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究（id / 表示名 / 深さ） | 装備必要スキル（Mod） | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hand_ram` | `TwoHandRam` | — | - | - | - | - | - | なし | A: レシピなし |
| `metal_hand_ram` | `TwoHandRam` | — | - | - | - | - | - | なし | A: レシピなし |

---

_生成: `scripts/mod_weapon_overview_table.py`_

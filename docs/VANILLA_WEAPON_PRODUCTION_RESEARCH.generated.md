# バニラ武器: 製作可能なものの研究・レシピ一覧（生成）

> **データソース（バニラ製作・研究）**: `D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`
> **武器種・門限（並びの参考）**: Mod `e:\Users\sucRo\Documents\Foxy Voxel\Going Medieval\Mods\Ranged Weapons Overhaul\Data\Models\Equipment.json`

- **武器** = `Items/Equipment.json` の `itemType == 1`。
- **製作可能** = 同名の `Production.repository[].id` があり、かつ `ProductionComponentsRepository` のいずれかの `productions` にその id が含まれる。
- **武器種**: `primaryWeaponMode.weaponType`（**Mod の `Equipment.json` があれば優先**、無い id はバニラ装備で補完）。
- **ティア順**: 弓／クロスは **[BOW_DESIGN_TARGETS.md](../implementation_policies/ranged/BOW_DESIGN_TARGETS.md) の T1–T4** に対応する `設計T*`。スリング系は **合成射程の短い順**（Mod の `range`）。その他は **レシピ要求スキル**で、同一武器種内では **木工のみ（Carpentry のみ）を鍛冶レシピより先**に並べる。
- **研究**: 各ノードの **`unlocks[].unlockId`** が `Production.id` と一致するものを正とする。併せて JSON 全体の文字列一致で補足ヒットを拾う（稀な定義用）。
- **深さ**: `nextNodesIDs` から作った木で、ルート（誰の `nextNodesIDs` の先でもない id）からの BFS 深さ。複数ルートがある場合は最短。

- 武器総数（itemType 1）: **39**
- 製作可能（レシピあり・作業台掲載あり）: **19**

## 弓（TwoHandBow）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `short_bow` | `TwoHandBow` | 設計T1 | `short_bow` | `fletchers_table` | Carpentry 0 | wood x20 | —（`Research.unlocks` に該当なし。初期から製作可能、または建物・シナリオ等で別解錠の可能性） |
| `long_bow` | `TwoHandBow` | 設計T4 | `long_bow` | `fletchers_table` | Carpentry 0 | wood x40 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 |

## クロスボウ（TwoHandCrossbow）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `crossbow` | `TwoHandCrossbow` | 設計T3 | `crossbow` | `fletchers_table` | Carpentry 20 | wood x35, wood_mechanical_parts x3 | `crossbows_lvl2` / `research_name_crossbows_lvl2`（ローカライズキー） / 3 |
| `heavy_crossbow` | `TwoHandCrossbow` | 設計T4 | `heavy_crossbow` | `fletchers_table` | Carpentry 20 | wood x45, mechanical_parts x3 | `crossbows_lvl3` / `research_name_crossbows_lvl3`（ローカライズキー） / 4 |

## 片手スリング（OneHandSling）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sling` | `OneHandSling` | 射程・素体順（短いほど先） | `sling` | `fletchers_table` | Tailoring 0 | 皮革類（leather 系・カテゴリマスク） x5 | —（`Research.unlocks` に該当なし。初期から製作可能、または建物・シナリオ等で別解錠の可能性） |

## 両手スリング（TwoHandSling）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sling_staff` | `TwoHandSling` | 射程・素体順（短いほど先） | `sling_staff` | `fletchers_table` | Carpentry 0 | 皮革類（leather 系・カテゴリマスク） x5, wood x10 | `fletchering_lvl2` / `research_name_fletchering_lvl2`（ローカライズキー） / 2 |

## 投擲（OneHandThrow）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `light_javelins` | `OneHandThrow` | レシピ Carpentry 0 | `light_javelins` | `woodwork_bench` | Carpentry 0 | wood x20 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 |
| `throwing_axes` | `OneHandThrow` | レシピ Smithing 10 | `throwing_axes` | `blacksmith_station` | Smithing 10 | iron_ingot x5, wood x20 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 |

## 片手斧（OneHandAxe）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hatchet` | `OneHandAxe` | レシピ Smithing 0 | `hatchet` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 |

## 両手斧（TwoHandAxe）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `greataxe` | `TwoHandAxe` | レシピ Smithing 20 | `greataxe` | `blacksmith_station` | Smithing 20 | 金属インゴット類（iron/steel 等・カテゴリマスク） x40, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | `axes_lvl2` / `research_name_axes_lvl2`（ローカライズキー） / 3 |

## 片手剣（OneHandSword）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `short_sword` | `OneHandSword` | レシピ Smithing 0 | `short_sword` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | —（`Research.unlocks` に該当なし。初期から製作可能、または建物・シナリオ等で別解錠の可能性） |

## 両手剣（TwoHandSword）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `longsword` | `TwoHandSword` | レシピ Smithing 20 | `longsword` | `blacksmith_station` | Smithing 20 | 金属インゴット類（iron/steel 等・カテゴリマスク） x35, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x25 | `swords_lvl2` / `research_name_swords_lvl2`（ローカライズキー） / 3 |

## 片手鈍器（OneHandMace）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cudgel` | `OneHandMace` | レシピ Carpentry 0 | `cudgel` | `woodwork_bench` | Carpentry 0 | wood x25 | —（`Research.unlocks` に該当なし。初期から製作可能、または建物・シナリオ等で別解錠の可能性） |
| `flail` | `OneHandMace` | レシピ Carpentry 0 | `flail` | `woodwork_bench` | Carpentry 0 | wood x30 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 |
| `mace` | `OneHandMace` | レシピ Smithing 0 | `mace` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 |

## 両手鈍器（TwoHandMace）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `two_handed_flail` | `TwoHandMace` | レシピ Carpentry 0 | `two_handed_flail` | `woodwork_bench` | Carpentry 0 | wood x45 | `woodwork_lvl2` / `research_name_woodwork_lvl2`（ローカライズキー） / 2 |
| `two_handed_mace` | `TwoHandMace` | レシピ Smithing 10 | `two_handed_mace` | `blacksmith_station` | Smithing 10 | 金属インゴット類（iron/steel 等・カテゴリマスク） x30, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x15 | `maces_lvl2` / `research_name_maces_lvl2`（ローカライズキー） / 3 |

## 槍／長柄（TwoHandSpear）

| weapon | `weaponType` | ティア（並び） | `Production.id` | 作業台 | 必要スキル（レシピ） | レシピ（要約） | 研究ノード（id / 表示名 / 深さ） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `spear` | `TwoHandSpear` | レシピ Carpentry 0 | `spear` | `woodwork_bench` | Carpentry 0 | wood x30 | —（`Research.unlocks` に該当なし。初期から製作可能、または建物・シナリオ等で別解錠の可能性） |
| `berdiche` | `TwoHandSpear` | レシピ Smithing 0 | `berdiche` | `blacksmith_station` | Smithing 0 | 金属インゴット類（iron/steel 等・カテゴリマスク） x15, 木材・燃料・骨など（wood/coal 等・カテゴリマスク） x10 | —（`Research.unlocks` に該当なし。初期から製作可能、または建物・シナリオ等で別解錠の可能性） |


## 参考: 武器だが本作では製作不可（レシピ無し or 作業台未掲載）

Mod で解禁する場合は `WEAPON_PRODUCTION_RESEARCH_AUDIT.md` の区分 A / B に沿って `Production` / `ProductionComponentsRepository` / `Research` を検討。

- `billhook`: 作業台オーファン
- `bludgeon`: 作業台オーファン
- `curved_bow`: 作業台オーファン
- `dagger`: 作業台オーファン
- `example_weapon`: レシピなし
- `falchion`: 作業台オーファン
- `greatsword`: 作業台オーファン
- `hand_ram`: レシピなし
- `knightly_sword`: 作業台オーファン
- `light_crossbow`: 作業台オーファン
- `metal_hand_ram`: レシピなし
- `military_pick`: 作業台オーファン
- `reinforced_flail`: 作業台オーファン
- `reinforced_spear`: 作業台オーファン
- `staff`: 作業台オーファン
- `two_handed_flanged_mace`: 作業台オーファン
- `two_handed_warhammer`: 作業台オーファン
- `war_bow`: 作業台オーファン
- `warfork`: 作業台オーファン
- `warhammer`: 作業台オーファン

---

_生成: `scripts/vanilla_weapon_production_research_table.py`_

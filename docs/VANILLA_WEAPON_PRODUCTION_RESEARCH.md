# バニラ武器の製作・研究・レシピ（手引き）

> **目的**: Mod で「バニラでは作れない武器」を解禁する際の足場として、**現行バニラで製作できる武器**について、`Production`（レシピ）・作業台掲載・`Research.unlocks`（研究アンロック）の対応を一覧化する。

## 正本と生成物

- **一覧（マシン生成）**: `[VANILLA_WEAPON_PRODUCTION_RESEARCH.generated.md](VANILLA_WEAPON_PRODUCTION_RESEARCH.generated.md)`
  - 手元の `Going Medieval_Data/StreamingAssets` を読み、バージョンに追従した表を出す。
- **Mod 用・全武器（製作不可含む・ティア順・非製作は作業台以降 `-`）**: `[MOD_WEAPON_OVERVIEW.generated.md](MOD_WEAPON_OVERVIEW.generated.md)` — 再生成は `scripts/mod_weapon_overview_table.py`（同じ `--streaming-assets` / `--mod-equipment`）。
- **製作不可の区分（A/B）**: `[WEAPON_PRODUCTION_RESEARCH_AUDIT.md](WEAPON_PRODUCTION_RESEARCH_AUDIT.md)`

## 再生成

```bash
export GM_STREAMING_ASSETS="/path/to/Going Medieval_Data/StreamingAssets"
python scripts/vanilla_weapon_production_research_table.py \
  --streaming-assets "$GM_STREAMING_ASSETS" \
  --mod-equipment "Data/Models/Equipment.json" \
  -o docs/VANILLA_WEAPON_PRODUCTION_RESEARCH.generated.md
```

`--mod-equipment` を省略すると、リポジトリ既定の `Data/Models/Equipment.json` が使われる（無い場合はバニラ装備だけで `weaponType` を解決）。

**Mod 用・全武器一覧**（`MOD_WEAPON_OVERVIEW.generated.md`）は同じパスで:

```bash
export GM_STREAMING_ASSETS="D:/SteamLibrary/steamapps/common/Going Medieval/Going Medieval_Data/StreamingAssets"
python scripts/mod_weapon_overview_table.py \
  --streaming-assets "$GM_STREAMING_ASSETS" \
  --mod-equipment "Data/Models/Items/Equipment.json" \
  -o docs/MOD_WEAPON_OVERVIEW.generated.md
```

Windows の例:

```bash
set GM_STREAMING_ASSETS=D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets
python scripts\vanilla_weapon_production_research_table.py --streaming-assets "%GM_STREAMING_ASSETS%" --mod-equipment "Data\Models\Items\Equipment.json" -o docs\VANILLA_WEAPON_PRODUCTION_RESEARCH.generated.md
python scripts\mod_weapon_overview_table.py --streaming-assets "%GM_STREAMING_ASSETS%" --mod-equipment "Data\Models\Items\Equipment.json" -o docs\MOD_WEAPON_OVERVIEW.generated.md
```

## 列の意味（生成表）

生成結果は `**weaponType` ごとに別表**になり、表内は **ティア順\*\*（弓／クロスは設計 T1–T4、その他は主にレシピ要求スキル＋木工優先）で並ぶ。

| 列              | 内容                                                                                                                                                                                      |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `weaponType`    | Mod（またはバニラ）の `Equipment.json` の `primaryWeaponMode.weaponType`。                                                                                                                |
| ティア（並び）  | 弓／クロスは `設計T1`～`T4`（[BOW_DESIGN_TARGETS.md](../implementation_policies/ranged/BOW_DESIGN_TARGETS.md)）。その他はレシピの要求スキル要約。                                         |
| `Production.id` | バニラでは通常 `Equipment.id` と同名。                                                                                                                                                    |
| 作業台          | `Constructables/ProductionComponentsRepository.json` のエントリ `id`（どの建物コンポーネントがそのレシピを出すか）。                                                                      |
| レシピ          | `Resources/Production.json` の `recipe`。`key` が **文字列**のときは資源 id、**整数**のときは資源カテゴリの bitmask（スクリプト側で日本語ラベル化）。数量は `**value`\*\*。               |
| 研究            | `Research/Research.json` の `**unlocks[].unlockId**` が武器の `Production.id` と一致するノード。該当なしの行は **研究テーブルで明示アンロックされない**（初期から製作可能など）の可能性。 |

## Mod で「制作不可」を可能にする場合（要約）

- **A（レシピなし）**: `Production` 定義の追加 ＋ 作業台 `productions` への id 追加 ＋ 必要なら `Research.unlocks`。
- **B（オーファン）**: `Production` は既にあるので、**作業台 `productions` への id 追加**が主。研究はバニラで未リンクなら `unlocks` 追加を検討。

本作の方針で除外する id（手ラム、`macabre_`\_、`forest\__`等）は`[implementation_policies/core/CREATION_POLICY.md](../implementation_policies/core/CREATION_POLICY.md)` を参照。

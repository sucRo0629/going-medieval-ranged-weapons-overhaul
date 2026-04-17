# 作業台に載らない／レシピが無い装備の監査

> **目的**: 「研究を進めても作れない」に見える装備を、データ上 **なぜ作れないか**に分類して洗い出す。  
> **正本（バニラ）**: `Going Medieval_Data/StreamingAssets` 直下の  
> - `Items/Equipment.json`  
> - `Resources/Production.json`（レシピ定義）  
> - `Constructables/ProductionComponentsRepository.json`（**どの作業台がどの `Production.id` を出すか**）  
> `Research.json` だけでは足りない（後述）。

## なにが起きているか（要点）

- プレイヤーが工房 UI で選べるのは、各作業台コンポーネントの **`productions` に列挙された `Production` の `id`** だけである。
- そのため **`Production.json` にレシピがあっても**、いずれの作業台にも載っていなければ **常に作れない**（オーファン）。例: `war_bow`, `curved_bow`, `light_crossbow`。
- **`Production` 自体が無い**装備は、先に「レシピが無い」。例: `kite_shield`, `pavise_shield`。`macabre_shield` も A だが、本作では **敵専用**として意図的に触れない（下記）。`forest_` 系防具も同様（下記）。

## 区分の定義

| 区分 | 意味 | 判定（装備 `id` と `Production.id` が同名である前提） |
|------|------|--------------------------------------------------------|
| **A: レシピなし** | 同名の `Production.repository[].id` が存在しない | `equip_id ∉ prod_ids` |
| **B: レシピはあるが作業台なし（オーファン）** | `Production` はあるが、全作業台の `productions` の和集合に含まれない | `equip_id ∈ prod_ids` かつ `equip_id ∉ station_prod_ids` |

- `prod_ids` = `Production.repository[].id` の集合  
- `station_prod_ids` = 全 `ProductionComponentsRepository.repository[].productions[]` の和集合  
- `orphan_productions` = `prod_ids - station_prod_ids`  
- **B（装備に限定）** = `equip_ids ∩ orphan_productions`

装備 `id` と `Production.id` が一致しないケース（将来のデータ）では、`produced[].blueprintID` からの逆引きが必要になる。

## 再実行

```bash
export GM_STREAMING_ASSETS="/path/to/Going Medieval_Data/StreamingAssets"
python scripts/vanilla_production_station_audit.py
```

または `--streaming-assets` を渡す。`GOING_MEDIEVAL_ITEMS` のみ指定している場合は、その **親ディレクトリ**が `StreamingAssets` であること（`Items` と同じ階層に `Constructables` / `Resources` があること）。

## バニラ抽出結果の例（ゲームデータ 1 インストール・参考値）

**スコープ「武器 + 盾」**（`itemType == 1` または `itemType == 3` かつ id に `shield` を含む）:

### A: レシピなし（同名 `Production` が無い）

| id | 備考 |
|----|------|
| `example_weapon` | 開発用想定。レシピ対象外でよい。 |
| `hand_ram` | **本作では制作不可のまま**（Mod でレシピ・研究は追加しない）。 |
| `metal_hand_ram` | 同上。 |
| `kite_shield` | バニラ `Production` に `kite_shield` が無い。 |
| `macabre_shield` | **敵専用のまま**（Mod でレシピ・作業台・研究解禁はしない）。 |
| `pavise_shield` | バニラ `Production` に `pavise_shield` が無い。 |

### B: レシピはあるが作業台に載らない（オーファン）

| id |
|----|
| `billhook` |
| `bludgeon` |
| `curved_bow` |
| `dagger` |
| `falchion` |
| `greatsword` |
| `knightly_sword` |
| `light_crossbow` |
| `military_pick` |
| `reinforced_flail` |
| `reinforced_spear` |
| `staff` |
| `two_handed_flanged_mace` |
| `two_handed_warhammer` |
| `war_bow` |
| `warfork` |
| `warhammer` |

**スコープ「武器のみ」**の A は `example_weapon`, `hand_ram`, `metal_hand_ram` の 3 件（上表の盾 3 件は含まない）。B は上表と同一 17 件。

**スコープ「全装備」**では、防具・衣服の多くが **A（レシピなし）** に入る（バニラでは購入・ドロップ・シナリオ前提など）。件数はバージョンで変わるため、**スクリプトの出力を正**とする。

## バニラで製作できる武器の研究・レシピ一覧

現行バニラの **製作可能武器**の `Production`・作業台・`Research.unlocks` 対応は、再生成式の表にまとめてある。

- [`VANILLA_WEAPON_PRODUCTION_RESEARCH.md`](VANILLA_WEAPON_PRODUCTION_RESEARCH.md)（手引き）
- [`VANILLA_WEAPON_PRODUCTION_RESEARCH.generated.md`](VANILLA_WEAPON_PRODUCTION_RESEARCH.generated.md)（`scripts/vanilla_weapon_production_research_table.py` の出力）

## Mod でプレイ可能にする場合の含意

- **A**: 最低限 `Data/Models/Production.json`（レシピ）＋必要なら `Research.json`。  
- **B**: `Production` は既にあるため、**`ProductionComponentsRepository` の差分**（対象作業台の `productions` に `id` を追加）が必要なことが多い。`Research` / `Production` だけでは足りない。

**除外（本作）**: `macabre_*` / `forest_*` は敵専用のままとし、上記の「解禁」対象に含めない。

## バッティングラム（`hand_ram` / `metal_hand_ram`）

バニラどおり **A（レシピなし）のまま**とし、本 Mod では **手ラム用の `Production` / `Research` 差分を置かない**。

## macabre_系（敵専用）

`macabre_armor` / `macabre_helmet` / `macabre_shield` / `macabre_crown` は **敵専用のまま**とし、本 Mod で **プレイヤー制作・研究解禁の差分は置かない**。

## forest_系（敵専用）

`forest_light_armor` / `forest_mask` / `forest_horned_mask` / `forest_horned_helmet` は **敵専用のまま**とし、本 Mod で **プレイヤー制作・研究解禁の差分は置かない**。

## バニラバージョン

- 上記一覧は **特定インストールの `StreamingAssets`** に対する参考値。  
- `ModInfo.json` の `gameVersion` と併せ、バニラ更新後は **`scripts/vanilla_production_station_audit.py` の再実行**を推奨。

# バニラ onEquipEffectors 効果詳細（生成）

> **正本**: インストール先 `Going Medieval_Data/StreamingAssets` の
> `Items/Equipment.json`（参照する id の列挙）と `StatsSystem/Effectors.json`（各 id の `effects` 定義）。
> 数値の Attribute ID は同階層 `StatsSystem/Attributes.json` で名前に解決できる（スクリプトが解決を試みる）。

- **Equipment 行数**: 80
- **onEquip 参照のユニーク id 数**: 8

## 装備から参照される id（使用件数）

| effector id | 参照件数（装備ブロック） | 日本語（概要） |
| --- | ---: | --- |
| `ImpairedMovementLow` | 7 | 移動速度がやや低下（小）。射撃の攻撃間隔がやや長くなり、回避率もわずかに下がる。 |
| `ImpairedMovementMed` | 4 | 移動・回避のペナは Low と同程度だが、射撃の攻撃間隔への影響がより大きい（重装甲など）。 |
| `WearingMorbidItem` | 4 | モルビッド系装備。気分がわずかに悪化する。 |
| `ShieldCombatSpeedLow` | 3 | 盾装備時、近接の攻撃間隔がやや長くなる（小）。 |
| `ShieldCombatSpeedHigh` | 2 | 盾装備時、近接の攻撃間隔が大きく長くなる（大）。 |
| `ShieldCombatSpeedMed` | 2 | 盾装備時、近接の攻撃間隔が長くなる（中）。 |
| `SunMaxProtectItem` | 2 | 日なたに晒されても不快になりにくい上限が高まる（帽子など）。 |
| `ChainedUp` | 1 | 拘束具。移動・回避・作業が大きく制限され、気分も大きく悪化する。 |

## 各 id の定義（Effectors.json）

### `ImpairedMovementLow`
- **装備時の意味（要約・日本語）**: 移動速度がやや低下（小）。射撃の攻撃間隔がやや長くなり、回避率もわずかに下がる。
- **loc**: `effector_name_ImpairedMovementLow`
- **uiGroup**: `4`
- **effects**:
  - 1. `RangedCombatSpeedImpactLow` type=AttributeModify | Attribute=RangedSpeed, Multiplier=1.1 -> `RangedSpeed`
    - **日本語**: 遠隔の攻撃間隔が 110%（一射あたりの時間が長くなる）
  - 2. `MovementSpeedSlower1` type=AttributeModify | Attribute=MovementSpeed, Multiplier=0.95 -> `MovementSpeed`
    - **日本語**: 移動速度が基準の 95%（やや遅い）
  - 3. `EvedeSpeedSlower` type=AttributeModify | Attribute=EvadeChance, Multiplier=0.95 -> `EvadeChance`
    - **日本語**: 回避の倍率が 0.95（基準 1.0 より低いほど回避しづらい）

### `ImpairedMovementMed`
- **装備時の意味（要約・日本語）**: 移動・回避のペナは Low と同程度だが、射撃の攻撃間隔への影響がより大きい（重装甲など）。
- **loc**: `effector_name_ImpairedMovementMed`
- **uiGroup**: `4`
- **effects**:
  - 1. `RangedCombatSpeedImpactMed` type=AttributeModify | Attribute=RangedSpeed, Multiplier=1.18 -> `RangedSpeed`
    - **日本語**: 遠隔の攻撃間隔が 118%（一射あたりの時間が長くなる）
  - 2. `MovementSpeedSlower1` type=AttributeModify | Attribute=MovementSpeed, Multiplier=0.95 -> `MovementSpeed`
    - **日本語**: 移動速度が基準の 95%（やや遅い）
  - 3. `EvedeSpeedSlower` type=AttributeModify | Attribute=EvadeChance, Multiplier=0.95 -> `EvadeChance`
    - **日本語**: 回避の倍率が 0.95（基準 1.0 より低いほど回避しづらい）

### `WearingMorbidItem`
- **装備時の意味（要約・日本語）**: モルビッド系装備。気分がわずかに悪化する。
- **loc**: `effector_name_WearingMorbidItem`
- **uiGroup**: `1`
- **effects**:
  - 1. `MoodNegativeVerySmall` type=MoodModify | BaseValue=-1
    - **日本語**: 気分が -1（悪化）

### `ShieldCombatSpeedLow`
- **装備時の意味（要約・日本語）**: 盾装備時、近接の攻撃間隔がやや長くなる（小）。
- **loc**: `effector_name_ShieldCombatSpeedLow`
- **uiGroup**: `4`
- **effects**:
  - 1. `CombatSpeedImpactLow` type=AttributeModify | Attribute=MeleeAttackSpeed, Multiplier=1.1 -> `MeleeAttackSpeed`
    - **日本語**: 近接の攻撃間隔が 110%（一撃あたりの時間が長くなる）

### `ShieldCombatSpeedHigh`
- **装備時の意味（要約・日本語）**: 盾装備時、近接の攻撃間隔が大きく長くなる（大）。
- **loc**: `effector_name_ShieldCombatSpeedHigh`
- **uiGroup**: `4`
- **effects**:
  - 1. `CombatSpeedImpactHigh` type=AttributeModify | Attribute=MeleeAttackSpeed, Multiplier=1.25 -> `MeleeAttackSpeed`
    - **日本語**: 近接の攻撃間隔が 125%（一撃あたりの時間が長くなる）

### `ShieldCombatSpeedMed`
- **装備時の意味（要約・日本語）**: 盾装備時、近接の攻撃間隔が長くなる（中）。
- **loc**: `effector_name_ShieldCombatSpeedMed`
- **uiGroup**: `4`
- **effects**:
  - 1. `CombatSpeedImpactMed` type=AttributeModify | Attribute=MeleeAttackSpeed, Multiplier=1.18 -> `MeleeAttackSpeed`
    - **日本語**: 近接の攻撃間隔が 118%（一撃あたりの時間が長くなる）

### `SunMaxProtectItem`
- **装備時の意味（要約・日本語）**: 日なたに晒されても不快になりにくい上限が高まる（帽子など）。
- **uiGroup**: `0`
- **effects**:
  - 1. `MaxSunlightItem` type=AttributeModify | Attribute=SunlightMax, Multiplier=2 -> `SunlightMax`
    - **日本語**: 日なた耐性の上限が 2 倍

### `ChainedUp`
- **装備時の意味（要約・日本語）**: 拘束具。移動・回避・作業が大きく制限され、気分も大きく悪化する。
- **loc**: `effector_name_ChainedUp`
- **uiGroup**: `5`
- **effects**:
  - 1. `MovementSpeedSlowerChain` type=AttributeModify | Attribute=MovementSpeed, Multiplier=0.75 -> `MovementSpeed`
    - **日本語**: 移動速度が基準の 75%（かなり遅い）
  - 2. `EvadeSpeedSlowerChains` type=AttributeModify | Attribute=EvadeChance, Multiplier=0.4 -> `EvadeChance`
    - **日本語**: 回避の倍率が 0.4（基準 1.0 より低いほど回避しづらい）
  - 3. `MoodNegativeExtLarge` type=MoodModify | BaseValue=-20
    - **日本語**: 気分が -20（悪化）
  - 4. `GlobalWorkChains` type=AttributeModify | Attribute=GlobalWorkSpeed, Multiplier=0.6 -> `GlobalWorkSpeed`
    - **日本語**: あらゆる作業速度が 60%

---

_このファイルは `scripts/vanilla_on_equip_effectors_audit.py` が生成しました。手で編集しないでください（上書きされます）。_

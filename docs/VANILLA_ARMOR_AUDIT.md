# バニラ装備データ監査（抽出・改善レバー整理）

> **部分スナップショット**: 入力は Mod 同梱の `Equipment.json`（全 id ではない場合あり）。
>
> **防具・盾**の `onEquip` / `armorRating` はバニラ踏襲の可能性が高いが、**武器**は Mod 改変が混ざる。
>
> 武器表は「現リポジトリの値」として読み、**バニラ照合は `GOING_MEDIEVAL_ITEMS` で再抽出**すること。


## 1. 前提と再実行方法

```bash
export GOING_MEDIEVAL_ITEMS="/path/to/Going Medieval_Data/StreamingAssets/Items"
python scripts/vanilla_equipment_audit.py --items-dir "$GOING_MEDIEVAL_ITEMS" --output docs/VANILLA_ARMOR_AUDIT.md
```

- `StreamingAssets` は `Items` の親ディレクトリ。スクリプトは `Combat/` と `StatsSystem/` を兄弟として読む。
- 本ファイルの **問題点の断定**は、上記バニラ `Equipment.json` を正に再生成した表で置き換えること。

## 2. 防具（`itemType` 3、盾以外）

| id | armorRating | armorType | onEquipEffectors |
| --- | --- | --- | --- |
| `forest_horned_helmet` | 0.1 | 1 | — |
| `forest_horned_mask` | 0.09 | 1 | — |
| `forest_light_armor` | 0.05 | 2 | ['ImpairedMovementLow'] |
| `forest_mask` | 0.07 | 1 | — |
| `gambeson_armor` | 0.2 | 2 | ['ImpairedMovementLow'] |
| `heretic_helmet` | 0.06 | 1 | — |
| `kettle_helmet` | 0.11 | 1 | ['SunMaxProtectItem'] |
| `light_armor` | 0.2 | 2 | — |
| `light_helmet` | 0.2 | 1 | — |
| `macabre_armor` | 0.07 | 2 | ['ImpairedMovementLow', 'WearingMorbidItem'] |
| `macabre_helmet` | 0.06 | 1 | ['WearingMorbidItem'] |
| `mail_armor` | 0.3 | 2 | ['ImpairedMovementLow'] |
| `mail_helmet` | 0.3 | 1 | — |
| `pigface_helmet` | 0.3 | 1 | — |
| `plate_armor` | 0.4 | 2 | ['ImpairedMovementMed'] |
| `plate_helmet` | 0.4 | 1 | — |
| `savage_heavy_armor` | 0.15 | 2 | ['ImpairedMovementMed'] |
| `shackles` |  | 3 | ['ChainedUp'] |

## 3. 盾（`itemType` 3 かつ id に shield を含む等）

| id | onEquipEffectors | meleeCover | rangedCover | coverAngle |
| --- | --- | --- | --- | --- |
| `buckler_shield` | ['ShieldCombatSpeedLow'] | 0.4 | 0.45 | 90 |
| `heater_shield` | ['ShieldCombatSpeedMed'] | 0.25 | 0.7 | 120 |
| `kite_shield` | ['ShieldCombatSpeedMed'] | 0.3 | 0.75 | 120 |
| `macabre_shield` | ['ShieldCombatSpeedLow', 'WearingMorbidItem'] | 0.23 | 0.6 | 110 |
| `pavise_shield` | ['ImpairedMovementLow', 'ShieldCombatSpeedLow'] | 0.32 | 0.9 | 170 |
| `tower_shield` | ['ImpairedMovementLow', 'ShieldCombatSpeedHigh'] | 0.35 | 0.95 | 200 |

## 4. 武器（`itemType` 1、`primaryWeaponMode`）

| id | weaponType | damage | ignoresArmor | armorDamage | range |
| --- | --- | --- | --- | --- | --- |
| `berdiche` | `TwoHandSpear` | 27 | 0.9 | 0.6 | 0.7 |
| `billhook` | `TwoHandSpear` | 26 | 0.9 | 0.6 | 0.7 |
| `bludgeon` | `OneHandMace` | 12 | 0.5 | 1 | 0 |
| `crossbow` | `TwoHandCrossbow` | 26 | 0.9 | 0.5 | 17.44 |
| `cudgel` | `OneHandMace` | 12 | 0.5 | 1 | 0 |
| `curved_bow` | `TwoHandBow` | 24 | 0.78 | 0.4 | 22.0 |
| `dagger` | `OneHandSword` | 12 | 0.7 | 0.6 | 0 |
| `example_weapon` | `OneHandSword` | 2 | 0.7 | 0.6 | 0 |
| `falchion` | `OneHandSword` | 16 | 0.7 | 0.6 | 0 |
| `flail` | `OneHandMace` | 10 | 0.5 | 2 | 0 |
| `greataxe` | `TwoHandAxe` | 36 | 0.6 | 1.1 | 0 |
| `greatsword` | `TwoHandSword` | 40 | 0.7 | 0.6 | 0.3 |
| `hand_ram` | `TwoHandRam` | 40 | 0.4 | 1 | 0.1 |
| `hatchet` | `OneHandAxe` | 18 | 0.6 | 1.1 | 0 |
| `heavy_crossbow` | `TwoHandCrossbow` | 36 | 0.92 | 0.5 | 20.11 |
| `knightly_sword` | `OneHandSword` | 16 | 0.75 | 0.6 | 0 |
| `light_crossbow` | `TwoHandCrossbow` | 26 | 0.9 | 0.5 | 16.79 |
| `light_javelins` | `OneHandThrow` | 16 | 0.35 | 1.2 | 10 |
| `long_bow` | `TwoHandBow` | 22 | 0.7 | 0.4 | 24.1 |
| `longsword` | `TwoHandSword` | 32 | 0.7 | 0.6 | 0.3 |
| `mace` | `OneHandMace` | 16 | 0.6 | 2 | 0 |
| `metal_hand_ram` | `TwoHandRam` | 46 | 0.4 | 1 | 0.1 |
| `military_pick` | `OneHandMace` | 16 | 0.6 | 1.9 | 0 |
| `reinforced_flail` | `OneHandMace` | 11 | 0.5 | 2.1 | 0 |
| `reinforced_spear` | `TwoHandSpear` | 27 | 0.9 | 0.65 | 0.8 |
| `short_bow` | `TwoHandBow` | 12 | 0.35 | 0.4 | 17.65 |
| `short_sword` | `OneHandSword` | 16 | 0.7 | 0.6 | 0 |
| `sling` | `OneHandSling` | 16 | 0.25 | 0.7 | 13 |
| `sling_staff` | `TwoHandSling` | 21 | 0.35 | 0.8 | 16 |
| `spear` | `TwoHandSpear` | 26 | 0.9 | 0.55 | 0.7 |
| `staff` | `TwoHandStaff` | 28 | 0.5 | 1 | 0.2 |
| `throwing_axes` | `OneHandThrow` | 17 | 0.4 | 1.4 | 10 |
| `two_handed_flail` | `TwoHandMace` | 26 | 0.5 | 2 | 0 |
| `two_handed_flanged_mace` | `TwoHandMace` | 30 | 0.6 | 1.9 | 0 |
| `two_handed_mace` | `TwoHandMace` | 30 | 0.6 | 1.9 | 0 |
| `two_handed_warhammer` | `TwoHandMace` | 30 | 0.5 | 1.7 | 0 |
| `war_bow` | `TwoHandBow` | 20 | 0.58 | 0.4 | 19.9 |
| `warfork` | `TwoHandSpear` | 26 | 0.9 | 0.6 | 0.7 |
| `warhammer` | `OneHandMace` | 16 | 0.5 | 1.7 | 0 |

## 5. 品質曲線（バニラ `Items` にファイルがある場合のみ）

### WeaponQualitySettings（Mod 同梱・抜粋）

_バニラ `Items` ではない。弓・クロス行は Mod 方針反映済み。_

**TwoHandBow**

| productQuality | damageMultiplier | rangeMultiplier | ignoresArmorMultiplier | attackSpeedMultiplier |
| --- | --- | --- | --- | --- |
| 1 | 0.92 | 1.0 | 1 | 1.03 |
| 2 | 0.95 | 1.01 | 1 | 1.02 |
| 3 | 0.98 | 1.02 | 1 | 1.0 |
| 4 | 1.03 | 1.03 | 1 | 0.98 |
| 5 | 1.09 | 1.04 | 1 | 0.95 |
| 6 | 1.15 | 1.05 | 1 | 0.91 |

**TwoHandCrossbow**

| productQuality | damageMultiplier | rangeMultiplier | ignoresArmorMultiplier | attackSpeedMultiplier |
| --- | --- | --- | --- | --- |
| 1 | 0.94 | 1.0 | 1 | 1.02 |
| 2 | 0.97 | 1.01 | 1 | 1.01 |
| 3 | 1.0 | 1.02 | 1 | 1.0 |
| 4 | 1.02 | 1.03 | 1 | 0.99 |
| 5 | 1.04 | 1.04 | 1 | 0.98 |
| 6 | 1.06 | 1.05 | 1 | 0.96 |



## 6. 戦闘エージェント（バニラ `StreamingAssets/Combat`）



## 7. 命中グループ・エフェクタ（バニラ `StreamingAssets/StatsSystem`）

### 補足（本 `Equipment.json` 内の `hitEffectorGroupIDs` 件数）

`WoundsBlunt`: **16** 武器、`WoundsPiercing`: **13** 武器、`WoundsCutting`: **10** 武器。確率・付帯エフェクタは `StatsSystem/HitEffectorGroups.json` を参照。



## 8. バニラ上の問題点（仮説・監査用チェックリスト）

| # | 観察・構造 | 根拠（データ） | 方針ファイルでの位置づけ |
| --- | --- | --- | --- |
| 1 | ギャンベゾン等でも装備時 `ImpairedMovementLow` があり、**軽装でも移動ペナ**が乗る | 上表 `gambeson_armor` / `forest_light_armor` 等 | [EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md) 「ギャンベゾンは移動をほぼ殺さない」とのギャップ |
| 2 | 鎖・板金は `ImpairedMovementLow/Med`。**負傷由来の減速と二重**になり退却が厳しい | 上表 + 近接不遇メモ | 退却可能性・負傷の肩代わし |
| 3 | 盾に `ShieldCombatSpeed*`。**盾＋近接の攻速・機動トレード**が重い | 上表 | カイトシールド方針・循環 |
| 4 | 武器 `ignoresArmor` が種別によって高帯。**鎧軽減が読みにくい** | 武器表（バニラ再抽出で検証） | 重装キラー主軸にしない／循環 |
| 5 | 鎧残量と軽減の関係は **Equipment 単体ではキー未確認** | [COMBAT_PLAYTEST_POLICY.md](../COMBAT_PLAYTEST_POLICY.md) | 運ゲー・安定軽減の設計 |
| 6 | **味方誤射・流れ弾**は接敵近接のリスク要因になり得る | `DamageTakingAgentSettings` の accident/hit 系キー（存在時に要約） | 退却可能性・運ゲー |

## 9. 改善レバー（方針マッピング）

| 方針（EQUIPMENT_OVERHAUL） | あり得るレバー（バニラ JSON） | 注意 |
| --- | --- | --- |
| 負傷の肩代わし | `armorRating` / `armorType`、`ArmorQualitySettings` の倍率、命中デバフは `HitEffectorGroups` | Mod 独自 Effector はマージ不確実 |
| 退却可能性 | 防具の `onEquipEffectors` の段階見直し、軽装から `ImpairedMovement*` を外す検討 | 盾 `ShieldCombatSpeed*` との兼ね合い |
| 運ゲー低減 | `Combat/*.json` に確率系があれば調整、なければ実戦検証のみ | キー未同定を明記 |
| 勝ち筋の複線化 | 遠隔の `ignoresArmor` 帯、近接の `armorDamage`（斧ルート） | 単独カテゴリ強化を避ける |

## 10. 次アクション

1. ローカルで `GOING_MEDIEVAL_ITEMS` を設定し、本スクリプトを **フルバニラ**で再実行して表を差し替える。
2. `HitEffectorGroups` / `Wounds` で **脚部・移動系**の付き方を代表武器から追記する。
3. 変更は `Data/Models/Equipment.json` の **部分上書き**から着手し、[COMBAT_PLAYTEST_POLICY.md](../COMBAT_PLAYTEST_POLICY.md) の条件で実戦確認する。

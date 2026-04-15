# 近接・投擲・防具・盾 データ変更方針（入口）

> **このファイルの役割** — 近接・投擲・防具・盾方針の入口と正本優先順位（Precedence）を示す。  
> 設計目標は `MELEE_ARMOR_DESIGN_TARGETS.md`、実装状況と作業手順は `MELEE_ARMOR_IMPLEMENTATION_STATUS.md` を正本とする。

---

## 正本の優先順位（Precedence）

矛盾がある場合は次の順で上位を正とする。

1. `Data/Models/Equipment.json`
  - 武器・防具・盾の素体値（`requiredSkills`、`primaryWeaponMode`/`secondaryWeaponMode` 含む）
2. `Data/Models/WeaponQualitySettings.json`
  - 品質乗算（投擲 `OneHandThrow` を含む）
3. バニラ `Items/Equipment.json` / `Items/WeaponQualitySettings.json`
  - 比較基準と再同期の参照元
4. 方針ドキュメント
  - 本ファイル、`MELEE_ARMOR_DESIGN_TARGETS.md`、`MELEE_ARMOR_IMPLEMENTATION_STATUS.md`

---

## どのファイルを読むか


| やりたいこと                 | まず開くファイル                                   |
| ---------------------- | ------------------------------------------ |
| 方針の入口・正本参照順を確認         | `MELEE_ARMOR_MOD_INTEGRATION_POLICY.md`    |
| 役割分離・数値ターゲット・ガードレールを確認 | `MELEE_ARMOR_DESIGN_TARGETS.md`            |
| 現状フェーズ・変更チェック・ゲート運用を確認 | `MELEE_ARMOR_IMPLEMENTATION_STATUS.md`     |
| 既存の統合メモ/履歴を確認          | `EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md` |


---

## 運用ルール

- 実装を先に更新した場合、同ターンで設計/状況ドキュメントを追随する。
- 近接・投擲・防具・盾の同時変更時は、**死亡率・離脱再編可否・治癒時間**をセットで評価する。
- `StatsSystem` の直編集は前提にせず、`Equipment.json` 側の間接制御で調整する。
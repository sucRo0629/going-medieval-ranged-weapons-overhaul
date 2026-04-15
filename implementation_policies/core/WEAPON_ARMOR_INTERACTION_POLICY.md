# 武器×防具 相互作用ポリシー（横断）

> **このファイルの役割** — 全武器種を横断して、`ignoresArmor` / `armorDamage` の共通ルールを定義する。
> 近接・投擲の個別計画は `../melee_armor/melee_throwing/MELEE_THROWING_PLAN.md`、鎧・盾は `../melee_armor/armor_shield/ARMOR_SHIELD_PLAN.md` を参照。

---

## 正本と優先順位

矛盾がある場合は次の順序を正とする。

1. `Data/Models/Equipment.json`
2. `Data/Models/WeaponQualitySettings.json`
3. バニラ `Items/Equipment.json` / `Items/WeaponQualitySettings.json`
4. 本ドキュメントと各計画書

---

## 共通ルール

- `ignoresArmor` の上限は `0.5`（カテゴリ横断）。
- 武器カテゴリの相対順位はバニラ準拠を維持する。
- 重装対応は「`ignoresArmor` だけ」で表現せず、`armorDamage` との役割分担で設計する。
- 1回の調整で複数軸を同時に大きく動かさない（再現可能性確保）。

---

## バニラ準拠順位（近接基準）

- 防具無視（高い順）: 槍 > 剣 > 斧 > 鈍器
- 防具/盾ダメージ（高い順）: 鈍器 > 斧 > 剣 = 槍

---

## ガードレール

- `precision` は弱体影響が大きいため、順位調整の主手段に使わない。
- 重装メタの調整は、まず `armorDamage` 側で行い、`ignoresArmor` の大幅増減は最後に検討する。
- 変更後は `general_basic_med` 系の同条件比較で、死亡率・気絶率・治癒時間を確認する。


# 弓・クロス データ変更方針（入口）

> **このファイルの役割** — 弓／クロス方針の **入口** と **正本の優先順位（Precedence）** を示す。詳細本文は子ファイルに分割している。  
> Mod の目的・スコープ・バニラの開き方・スリング・素体 × 品質の一般論は **[`CREATION_POLICY.md`](CREATION_POLICY.md)**。

---

## 正本の優先順位（Precedence）

次の **上から順**に従う。下位の Markdown の記述が上位と矛盾する場合は **上位を正**にし、ドキュメントかデータを追随する。

1. **本 Mod の** [`Data/Models/Equipment.json`](Data/Models/Equipment.json) — 装備ブロックの数値・`requiredSkills`・`primaryWeaponMode` / `secondaryWeaponMode` の**実装の正**。
2. **本 Mod の** [`Data/Models/WeaponQualitySettings.json`](Data/Models/WeaponQualitySettings.json) — 品質乗算。定数は **`tools/regenerate_ranged_from_vanilla.py`** の **`TWO_HAND_BOW_QUALITY_DELTAS`**（弓）と **`TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`**（クロス・damage／攻速の平坦化＋**`rangeMultiplier` の微増**）。
3. **バニラ** `Items/Equipment.json` / `Items/WeaponQualitySettings.json` — 再同期・比較・「バニラ下限」の基準。
4. **設計意図・検証手順** — [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md)、[`BOW_IMPLEMENTATION_STATUS.md`](BOW_IMPLEMENTATION_STATUS.md)、[`COMBAT_PLAYTEST_POLICY.md`](COMBAT_PLAYTEST_POLICY.md)。  
   - 表の **ドラフト門限** と JSON が食い違うときは **JSON を正**にし、その後ドキュメントを更新する。

**参照範囲**: 本文・表と実装の突き合わせは **バニラ `Items/Equipment.json`** と **本 Mod の `Data/Models/Equipment.json`** のみとし、**他 Mod の `Equipment.json` は参照しない**。

---

## どのファイルを読むか

| やりたいこと | まず `@` するファイル |
|--------------|------------------------|
| セッション開始・タスク別の最小セット全体 | [`POLICY_SESSION_QUICK.md`](POLICY_SESSION_QUICK.md) |
| 役割・四弓（短弓＋長弓三種）コンセプト・射程順・DPS 定義・Q3 鎖・門限ドラフト・ガード | [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md) |
| 現状フェーズ・変更チェックリスト・実効命中の拘束・再生成手順 | [`BOW_IMPLEMENTATION_STATUS.md`](BOW_IMPLEMENTATION_STATUS.md) |
| Mod 全体のスコープ・部分上書き・丸め・共通禁則 | [`CREATION_POLICY.md`](CREATION_POLICY.md) |
| プレイテスト手順・敵 NPC・距離 | [`COMBAT_PLAYTEST_POLICY.md`](COMBAT_PLAYTEST_POLICY.md) |
| 防具・盾・近接メタ・スリング | [`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md) |

---

## 旧来の参照について

外部ドキュメントやチャットで **`BOW_MOD_INTEGRATION_POLICY.md` のみ**を指している場合は、**本入口＋上表に従い**、設計なら [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md)、作業・現状なら [`BOW_IMPLEMENTATION_STATUS.md`](BOW_IMPLEMENTATION_STATUS.md) を開く。

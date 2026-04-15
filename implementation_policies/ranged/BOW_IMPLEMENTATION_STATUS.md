# 弓・クロス — 実装・現状・作業手順

> **このファイルの役割** — リポジトリの**実装フェーズ**、再生成スクリプト、**変更時チェックリスト**、実戦・実効命中の**拘束**。  
> **バランス目標・数式・Q3 鎖・門限ドラフト**は `[BOW_DESIGN_TARGETS.md](BOW_DESIGN_TARGETS.md)`。入口と **正本の優先順位** は `[BOW_MOD_INTEGRATION_POLICY.md](BOW_MOD_INTEGRATION_POLICY.md)`。防具・盾・近接メタ・スリングは `[EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../melee_armor/EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)`。

---

## `weaponType` と列挙型（本体制約）

`Equipment.json` の `primaryWeaponMode.weaponType` は **本体の `WeaponType` 列挙に含まれる文字列のみ**有効。`Player.log` に `Incorrect enum value '…' for enum WeaponType` が出る場合、その値は**拒否**される（例: カスタム名 `TwoHandBowShort` は **不可**）。

短弓と長弓三種の差は `**TwoHandBow` を共有した WQS** と、**素体**の `range` / `attackSpeed`（`ROLE_RANGE` / `BOW_ATTACK_SPEED`）で付ける。短弓だけ別 WQS 行を足しても、`weaponType` が列挙外ならロード時に落ちる。

検証は **起動・ロード**、短弓の**装備・射撃**、品質差、`Player.log` にエラーがないか、の順で行う。

---

## Repository phase（実装の現状）

**現状（2026-04 以降の再生成パイプライン）**: 7 種はバニラ装備の完全コピーを土台に、**門限**・`ROLE_RANGE` / `BOW_ATTACK_SPEED` / `CROSSBOW_RANGED_COVER`・`TWO_HAND_BOW_QUALITY_DELTAS`・`TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`（damage／攻速＋**射程の品質微増**）を適用する。弓は四種とも `**weaponType` = `TwoHandBow`**（列挙型制約）。弓／クロスには `**onEquipEffectors` を付けない**（再生成時にキー削除。理由は `[EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../melee_armor/EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)` 弓・クロス節）。エントリ: `[scripts/apply_ranged_equipment_delta.py](../../scripts/apply_ranged_equipment_delta.py)` / `[tools/regenerate_ranged_from_vanilla.py](../../tools/regenerate_ranged_from_vanilla.py)`。**設計上の数値目標**（Q3 鎖・距離別 DPS 順・「弓を長射程にする場合」等）がすべて満たされているとは限らない。再チューン時は `[BOW_DESIGN_TARGETS.md](BOW_DESIGN_TARGETS.md)` の **評価基準の階層**の層 1 から合わせ、層 3・4 で採否する。

**一区切り（弓・クロス・2026-04）**: 装備 UI の **装甲貫通大中小は JSON と一致しないことがある**が、**戦闘は JSON を正**とし、**表記に合わせて数値を曲げない**（詳細は `[COMBAT_PLAYTEST_POLICY.md](../core/COMBAT_PLAYTEST_POLICY.md)`）。弓／クロスラインは **当面ここで区切り**；大きな追加は **装備オーバーホール全体**（`[EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../melee_armor/EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)`）側を優先する。

---

## 実戦検証（別ファイル）

実戦検証の固定シナリオと観察項目は  
`[COMBAT_PLAYTEST_POLICY.md](../core/COMBAT_PLAYTEST_POLICY.md)` に分離して管理する。  
（12ケース、共通ルール、評価項目の更新は同ファイルを正とする）

---

## 実効命中のバニラ下限（実戦拘束）

**原則（2026-04-14）**: 弓／クロスは、**バニラ `Items/Equipment.json` と同等に近い条件**（同程度の Marksman・同品質帯・**平地・高台ボーナスなし**・ターゲットが一方的に撃たれる、等）で比較したとき、**実効命中がバニラより悪い状態にしない**。`Equipment.json` の `precision` / `precisionFalloff` / `range`（および品質乗算後の合成）を変える場合は、**短弓・序盤帯・「可」品質・中距離〜近距離**でも討伐が非現実的な時間にならないよう、バニラ実測または並行セーブ比較で確認する。

根拠ログ・距離の取り方・推奨敵 NPC は `[COMBAT_PLAYTEST_POLICY.md](../core/COMBAT_PLAYTEST_POLICY.md)`（距離加算、10m オプション、プレイテスト記録、敵 NPC 表）を参照する。

---

## 変更するとき

1. **Q3 四種鎖**（`crossbow` / `heavy_crossbow` / `curved_bow` / `long_bow`）と **Equipment** の両方を意識し、矛盾が出ないよう往復する（鎖の定義は `[BOW_DESIGN_TARGETS.md](BOW_DESIGN_TARGETS.md)`）。`**ignoresArmor`** は同ファイル「命中・装甲無視」の **確定目標**（弓四種上限 **0.70**、クロス三種上限 **0.85**、四弓内段・クロス未満）を満たすか確認する。
2. 数値を変えたら、`tools/plot_weapon_quality_comparison.py` でグラフを生成し、品質込みの性能を確認する（**期待DPS**・**距離別期待DPS** の `expected_dps*.png` / `distance_expected_dps_*.png`。単体の `dps_*.png` は出さない）。**合成 `range`** は `[BOW_DESIGN_TARGETS.md](BOW_DESIGN_TARGETS.md)` の **Q3／Q4 厳守順**を `range_`* で確認（Q1・Q2・Q5・Q6 はティア緩和あり）。**チャートだけで採否しない** — 同ファイルの **評価基準の階層**の **層 3・4**（プレイテスト／バニラ差分）を通す。
  - あわせて `quality_charts/ranged/script/distance_expected_dps_band_summary.csv` を確認し、帯域の平均/最小値を記録する。**層 1 の補完（対鎧プロキシ距離 DPS・帯域単発期待ダメ・Q3 四鎖・`ignoresArmor` 方針 CSV／チャート・掩体/バックラー比較・移動目標（ドキュメント）・門限メモ）**は `[quality_charts/ranged/layer1_eval_bundle.md](../../quality_charts/ranged/layer1_eval_bundle.md)` と同時生成の `quality_charts/ranged/script/layer1_*_band_summary.csv` 2 本＋`quality_charts/ranged/script/layer1_ignores_armor_policy_summary.csv` に任せ、再生成のたびに当該 MD を確認する。
3. 移動ペナルティ・掩体（`[BOW_DESIGN_TARGETS.md](BOW_DESIGN_TARGETS.md)`「弓とクロスボウの差別化」の共通箇所）は鎖とは独立に触ってよいが、**素体の火力をヘビィだけ突出**させて鎖や役割説明と矛盾させないこと。**装備時移動（`onEquipEffectors`）は現状データに含めない**（設計目標の倍率は `[EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../melee_armor/EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)` のみ）。
4. **同ティア近接との比較・被弾メタ**を検証に含め、**高品質弓一択**にならないよう帯域・曲線・WQS を確認する。実戦手順は `COMBAT_PLAYTEST_POLICY.md` に従う。
5. `**requiredSkills`（Marksman）**を変えたら、`[BOW_DESIGN_TARGETS.md](BOW_DESIGN_TARGETS.md)` の「装備門限」節と **Q3 総合強さの検証水準**と整合するか確認する。
6. `**precision` / `precisionFalloff` / `range` を変えたら**、上記「**実効命中のバニラ下限**」と `COMBAT_PLAYTEST_POLICY.md` のオプション距離（10m 等）を満たすか確認する。

---

## 再生成・ツール（正本への近道）

- 弓／クロス 7 種＋ WQS の再同期・門限適用の正本: `**[scripts/apply_ranged_equipment_delta.py](../../scripts/apply_ranged_equipment_delta.py)`**（内部で `tools/regenerate_ranged_from_vanilla.run_regeneration` を呼び、続けてスリング上書きを適用）。
- 7 種＋ WQS のみ: `**[tools/regenerate_ranged_from_vanilla.py](../../tools/regenerate_ranged_from_vanilla.py)`**（`TWO_HAND_BOW_QUALITY_DELTAS` / `TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`）。
- 環境変数: `**GOING_MEDIEVAL_ITEMS`**（`Items` フォルダ）、チャート生成は `tools/plot_weapon_quality_comparison.py`（`[CREATION_POLICY.md](../core/CREATION_POLICY.md)` 参照）。
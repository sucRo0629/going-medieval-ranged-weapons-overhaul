# 弓・クロス — 実装・現状・作業手順

> **このファイルの役割** — リポジトリの**実装フェーズ**、再生成スクリプト、**変更時チェックリスト**、実戦・実効命中の**拘束**。  
> **バランス目標・数式・Q3 鎖・門限ドラフト**は [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md)。入口と **正本の優先順位** は [`BOW_MOD_INTEGRATION_POLICY.md`](BOW_MOD_INTEGRATION_POLICY.md)。

---

## Repository phase（実装の現状）

**現状（2026-04 以降の再生成パイプライン）**: 7 種はバニラ装備の完全コピーを土台に、**門限**・**`ROLE_RANGE` / `BOW_ATTACK_SPEED` / `CROSSBOW_RANGED_COVER`**・**`TWO_HAND_BOW_QUALITY_DELTAS`**・**`TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`** を適用する（[`scripts/apply_ranged_equipment_delta.py`](scripts/apply_ranged_equipment_delta.py) / [`tools/regenerate_ranged_from_vanilla.py`](tools/regenerate_ranged_from_vanilla.py)）。**設計上の数値目標**（Q3 鎖・距離別 DPS 順・「弓を長射程にする場合」等）がすべて満たされているとは限らない。再チューン時は [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md) の **評価基準の階層**の層 1 から合わせ、層 3・4 で採否する。

---

## 実戦検証（別ファイル）

実戦検証の固定シナリオと観察項目は  
**[`COMBAT_PLAYTEST_POLICY.md`](COMBAT_PLAYTEST_POLICY.md)** に分離して管理する。  
（12ケース、共通ルール、評価項目の更新は同ファイルを正とする）

---

## 実効命中のバニラ下限（実戦拘束）

**原則（2026-04-14）**: 弓／クロスは、**バニラ `Items/Equipment.json` と同等に近い条件**（同程度の Marksman・同品質帯・**平地・高台ボーナスなし**・ターゲットが一方的に撃たれる、等）で比較したとき、**実効命中がバニラより悪い状態にしない**。`Equipment.json` の `precision` / `precisionFalloff` / `range`（および品質乗算後の合成）を変える場合は、**短弓・序盤帯・「可」品質・中距離〜近距離**でも討伐が非現実的な時間にならないよう、バニラ実測または並行セーブ比較で確認する。

根拠ログ・距離の取り方・推奨敵 NPC は **[`COMBAT_PLAYTEST_POLICY.md`](COMBAT_PLAYTEST_POLICY.md)**（距離加算、10m オプション、プレイテスト記録、敵 NPC 表）を参照する。

---

## 変更するとき

1. **Q3 四種鎖**（`crossbow` / `heavy_crossbow` / `curved_bow` / `long_bow`）と **Equipment** の両方を意識し、矛盾が出ないよう往復する（鎖の定義は [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md)）。
2. 数値を変えたら、`tools/plot_weapon_quality_comparison.py` でグラフを生成し、品質込みの性能を確認する（**期待DPS**・**距離別期待DPS** の `ranged_expected_dps*.png` / `ranged_distance_expected_dps_*.png`。単体の `ranged_dps_*.png` は出さない）。**チャートだけで採否しない** — [`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md) の **評価基準の階層**の **層 3・4**（プレイテスト／バニラ差分）を通す。
   - あわせて `ranged_distance_expected_dps_band_summary.csv` と `ranged_distance_expected_dps_decision_summary.md` を確認し、帯域の平均/最小値と主要ペアの勝敗推移を記録する。
3. 移動ペナルティ・掩体（[`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md)「弓とクロスボウの差別化」の共通箇所）は鎖とは独立に触ってよいが、**素体の火力をヘビィだけ突出**させて鎖や役割説明と矛盾させないこと。
4. **同ティア近接との比較・被弾メタ**を検証に含め、**高品質弓一択**にならないよう帯域・曲線・WQS を確認する。実戦手順は `COMBAT_PLAYTEST_POLICY.md` に従う。
5. **`requiredSkills`（Marksman）**を変えたら、[`BOW_DESIGN_TARGETS.md`](BOW_DESIGN_TARGETS.md) の「装備門限」節と **Q3 総合強さの検証水準**と整合するか確認する。
6. **`precision` / `precisionFalloff` / `range` を変えたら**、上記「**実効命中のバニラ下限**」と `COMBAT_PLAYTEST_POLICY.md` のオプション距離（10m 等）を満たすか確認する。

---

## 再生成・ツール（正本への近道）

- 弓／クロス 7 種＋ WQS の再同期・門限適用の正本: **[`scripts/apply_ranged_equipment_delta.py`](scripts/apply_ranged_equipment_delta.py)**（内部で `tools/regenerate_ranged_from_vanilla.run_regeneration` を呼び、続けてスリング上書きを適用）。
- 7 種＋ WQS のみ: **[`tools/regenerate_ranged_from_vanilla.py`](tools/regenerate_ranged_from_vanilla.py)**（`TWO_HAND_BOW_QUALITY_DELTAS` / `TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`）。
- 環境変数: **`GOING_MEDIEVAL_ITEMS`**（`Items` フォルダ）、チャート生成は `tools/plot_weapon_quality_comparison.py`（[`CREATION_POLICY.md`](CREATION_POLICY.md) 参照）。

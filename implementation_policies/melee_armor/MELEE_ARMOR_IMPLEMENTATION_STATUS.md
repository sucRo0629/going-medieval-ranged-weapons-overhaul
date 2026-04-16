# 近接・投擲・防具・盾 — 実装・現状・作業手順

> **このファイルの役割** — 実装フェーズ、変更時チェックリスト、ゲート評価手順を管理する。  
> バランス目標は `MELEE_ARMOR_DESIGN_TARGETS.md` を参照。  
> 分離計画は `melee_throwing/MELEE_THROWING_PLAN.md`（近接・投擲）と `armor_shield/ARMOR_SHIELD_PLAN.md`（鎧・盾）を参照。

---

## Repository phase（現状）

- フェーズ1: 防具 `armorRating` の底上げは実装済み（重装中心）。
- フェーズ2: 近接・投擲のロール分離を実装中。
  - `ignoresArmor` はバニラ準拠順位（槍 > 剣 > 斧 > 鈍器）で再配分
  - 鈍器は `ignoresArmor=0.0` 固定ではなく、最低帯（低値）で運用
  - 上限はカテゴリ共通で `0.5` を維持
  - 重装対応は鈍器の `armorDamage` 主軸で表現
  - 投擲 `OneHandThrow` の品質曲線を追加し、品質で射程/ダメージを微増

- **区切り（2026-04-16）**: 鎧（フェーズ1）と近接武器の調整は一旦完了として凍結し、次は遠隔/投擲/盾など他レバーの検証・調整に移る（詳細ログは `playtest_results/2026-04-14_armor_phase1_gate.md`）。

---

## 判定ゲート（実運用）

- 主シナリオ: `general_basic_med` ×3
- 必須記録:
  - 死亡率 / 気絶率
  - 初被弾後の離脱再編可否
  - 治癒時間（重傷含む）
- 補助記録:
  - 投擲 vs 弓/クロスの平地比較
  - 盾角度変更後の背後射撃有効性

---

## 変更するとき

1. 変更対象のカテゴリ（剣/槍/斧/鈍器/投擲/防具/盾）を明記する。
2. `Equipment.json` 変更後にカテゴリ上限（`ignoresArmor <= 0.5`）を検証する。
3. `WeaponQualitySettings.json` を変更した場合、Q1/Q3/Q6の実数値を記録する。
4. `playtest_results/2026-04-14_armor_phase1_gate.md` に結果を追記する。
5. 設計目標と実装値が乖離した場合は `MELEE_ARMOR_DESIGN_TARGETS.md` を更新する。

---

## 既存統合ドキュメントとの関係

- 既存の詳細メモ・観察履歴は `EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md` に残している。
- 本ファイルは「現在有効な実装運用」を短く保つ。
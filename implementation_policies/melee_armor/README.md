# 近接・鎧方針（集約入口）

近接・投擲と鎧・盾は更新サイクルが異なるため、計画書を分離して管理する。

## 計画書の分離構成

1. 近接・投擲計画
  - `melee_throwing/MELEE_THROWING_PLAN.md`
2. 鎧・盾計画
  - `armor_shield/ARMOR_SHIELD_PLAN.md`
3. 横断ルール（全武器種の防具相互作用）
  - `../core/WEAPON_ARMOR_INTERACTION_POLICY.md`

## 既存ファイルの役割（継続運用）

1. 入口（Precedence / 参照順）
  - `MELEE_ARMOR_MOD_INTEGRATION_POLICY.md`
2. 設計目標（全体方針）
  - `MELEE_ARMOR_DESIGN_TARGETS.md`
3. 実装状況（フェーズ / チェックリスト / ゲート）
  - `MELEE_ARMOR_IMPLEMENTATION_STATUS.md`
4. 詳細履歴
  - `EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`

## 重複ルール

- 正本は原則1か所に固定する（SSOT）。
- 入口ドキュメントには、AI検索性のため「要約 + 正本リンク」の重複を許可する。
- 数値表や厳密ルールは重複させず、正本を参照する。
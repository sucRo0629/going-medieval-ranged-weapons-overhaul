# 鎧・盾 計画書

> **このファイルの役割** — 鎧（`armorRating`）と盾（`meleeCover` / `rangedCover` / `coverAngle`）の実装計画を管理する。
> 武器側の横断ルールは `../../core/WEAPON_ARMOR_INTERACTION_POLICY.md` を参照。

---

## 計画対象

- 胴/頭防具の `armorRating` 調整
- 盾の `coverAngle` / `rangedCover` / `meleeCover` 調整
- 退却時の事故死軽減と、背後射撃の勝ち筋維持の両立

---

## 設計原則

- 重装中心の強化を優先し、軽装・鎖の過強化を避ける。
- 盾の `coverAngle` 拡張は許容するが、大盾の `rangedCover` は必要に応じて抑制する。
- 盾と武器 `meleeCover` の合算で過防御化しないよう、段階調整で確認する。

---

## 実装手順（小ステップ）

1. 防具または盾のどちらを触るかを先に固定する。
2. 1回の変更幅を制限して `Equipment.json` を更新する。
3. 退却/包囲シナリオで、離脱不能ループが悪化しないかを確認する。
4. `playtest_results/2026-04-14_armor_phase1_gate.md` に記録する。

---

## 判定ゲート

- 主要ケースでレイド処理時間 `+15%` 超ならロールバック検討。
- 大盾調整後も背後射撃の有効性が完全には消えないことを確認。


# Equipment Overhaul — セッション早見（`POLICY_SESSION_QUICK.md`）

> **役割** — Cursor／人間が **最初に `@` する 1 枚**。タスク別の参照ファイルと **正本** を固定する。詳細は各リンク先のみ読む。

**Mod 名・スコープ**: ゲーム内表示名は **`ModInfo.json` の `name`（Equipment Overhaul）**。ローカルの **リポジトリ／Mod フォルダ名**は環境ごとに異なってよい（ドキュメントでは **リポジトリ相対パス**を正とする）。装備全体（遠距離に限らず防具・盾・近接メタ・スリング）の概論と禁則は **[`CREATION_POLICY.md`](CREATION_POLICY.md)**。遠距離を変える作業でもそれらに触れる想定なら **[`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)** を必ず併読する。

**弓・クロス（2026-04 一区切り）**: 装甲貫通の **アイテム表記は JSON とずれることがある**が、**戦闘は `Equipment.json` / WQS を正**とし、表記に合わせて数値を曲げない。詳細は **`[COMBAT_PLAYTEST_POLICY.md](COMBAT_PLAYTEST_POLICY.md)`** / **`[BOW_IMPLEMENTATION_STATUS.md](BOW_IMPLEMENTATION_STATUS.md)`**。

---

## 正本（数値・マージ）


| 正本        | パス                                                                                                                                                                |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 装備の実装     | `Data/Models/Equipment.json`（`requiredSkills` はトップレベル。門限なしは **キー省略**。`Marksman` の `value: 0` は使わない）                                                               |
| 品質乗算      | `Data/Models/WeaponQualitySettings.json`（`TWO_HAND_BOW_QUALITY_DELTAS` / `TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES`＝`tools/regenerate_ranged_from_vanilla.py`） |
| バニラ比較・再同期 | 本体 `Items/Equipment.json` / `Items/WeaponQualitySettings.json`（`[CREATION_POLICY.md](CREATION_POLICY.md)` のパス）                                                    |

### ゲームログ（本体・Unity）

Windows の既定保存先（**Foxy Voxel / Going Medieval**）:

- **現在セッション**: `%USERPROFILE%\AppData\LocalLow\Foxy Voxel\Going Medieval\Player.log`
- **直前に終了したセッション**（容量が大きいことが多い）: 同フォルダの `Player-prev.log`

テキストエディタで開き、`[ERR]` / `[WARN]` / `Exception` / 装備・NPC 関連の `id` などで検索する。プレイテスト手順との対応は [`COMBAT_PLAYTEST_POLICY.md`](COMBAT_PLAYTEST_POLICY.md) を参照。

**Precedence（矛盾時）**: `[BOW_MOD_INTEGRATION_POLICY.md](BOW_MOD_INTEGRATION_POLICY.md)` の順序に従う（JSON ＞ 設計 MD のドラフト表）。

---

## タスク → `@` するファイル


| タスク                                        | `@`（この順で足す）                                                                            |
| ------------------------------------------ | -------------------------------------------------------------------------------------- |
| 何から読むか迷う                                   | 本ファイル → `[BOW_MOD_INTEGRATION_POLICY.md](BOW_MOD_INTEGRATION_POLICY.md)`               |
| 弓・クロスの役割／**四弓（短弓＋長弓三種）コンセプト**／射程順／DPS 式／Q3 鎖／門限ドラフト | `[BOW_DESIGN_TARGETS.md](BOW_DESIGN_TARGETS.md)`（同一ファイル内の「四弓のコンセプト」節）                  |
| 再生成・変更チェック・実装フェーズ・実効命中の下限                  | `[BOW_IMPLEMENTATION_STATUS.md](BOW_IMPLEMENTATION_STATUS.md)`                         |
| 層 1 補完（対鎧プロキシ・単発期待・Q3 鎖・`ignoresArmor` 方針・門限メモ）       | [`quality_charts/ranged_layer1_eval_bundle.md`](quality_charts/ranged_layer1_eval_bundle.md)（`plot_weapon_quality_comparison.py` 再生成で更新）        |
| Mod 全体スコープ・部分上書き・丸め・素体×品質                  | `[CREATION_POLICY.md](CREATION_POLICY.md)`                                             |
| プレイテスト手順                                   | `[COMBAT_PLAYTEST_POLICY.md](COMBAT_PLAYTEST_POLICY.md)`（ログ場所は本ファイル「ゲームログ」）                               |
| 防具・盾・近接・スリング                               | `[EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)` |


---

## よくある禁則（短く）

- 旧スキーマのトップレベル `range` / `damage` / `attackSpeed` は使わない（`primaryWeaponMode` / `secondaryWeaponMode` 配下）。`[CREATION_POLICY.md](CREATION_POLICY.md)`
- `Research.json` / `Production.json` は原則置かない。
- 浮動小数の装備パラメータは **小数第2位・四捨五入**（`[CREATION_POLICY.md](CREATION_POLICY.md)`）。

---

## 再生成ワンショット

弓／クロス 7 種＋門限・WQS: `[scripts/apply_ranged_equipment_delta.py](scripts/apply_ranged_equipment_delta.py)`。チャート: `tools/plot_weapon_quality_comparison.py`。環境変数 `GOING_MEDIEVAL_ITEMS`。

**層 1 の補完評価（対鎧プロキシ・帯域単発期待ダメ・Q3 四鎖・`ignoresArmor` 方針・`rangedCover`/バックラー比較・移動目標（ドキュメント）・門限メモ）**は、同スクリプトが `quality_charts/` に出す **[`ranged_layer1_eval_bundle.md`](quality_charts/ranged_layer1_eval_bundle.md)** と同時生成の CSV（`ranged_layer1_*_band_summary.csv` 2 本＋`ranged_layer1_ignores_armor_policy_summary.csv`）および **`ranged_ignoresArmor_mod_policy_overlay.png`** に**任せる**（式と限界はその MD 先頭）。再生成のたびに当該 MD を開き、必要なら CSV を突き合わせる。
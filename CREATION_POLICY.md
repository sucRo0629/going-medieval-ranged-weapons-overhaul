# Equipment Overhaul — 作成方針（概論）

> **このファイルの役割** — Mod 全体の設計哲学・データ編集スコープ・参照元・品質計算・実装時の共通チェックを定義する。  
> 弓／クロスの詳細は **[`BOW_MOD_INTEGRATION_POLICY.md`](BOW_MOD_INTEGRATION_POLICY.md)**、防具／盾／近接メタ／スリングの詳細は **[`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)** を参照する。

本 Mod は「射撃だけの再調整」から「装備全体のトレードオフ設計」へ拡張する。  
**武器素体の基準は常にバニラ `Items/Equipment.json`** であり、Mod 側には **バニラと異なる `id`・フィールドのみ**を置く。

## 核心設計（Core Philosophy）

- **万能装備を作らない**: すべての武器・防具に「強み」と「明確な弱み」を持たせる。
- **運依存から装備選択へ**: 防御は偶然任せではなく、装備と編成で再現可能な結果に寄せる。
- **擬似ロールを成立させる**: 遊撃・前衛・据え撃ちなど、配置と連携に意味が出る設計を優先する。

## ドキュメント構成（概論／各論）

- **概論（本書）**: 全カテゴリ共通のルール、データの参照順、変更時チェック。
- **各論 1（弓・クロス）**: **[`BOW_MOD_INTEGRATION_POLICY.md`](BOW_MOD_INTEGRATION_POLICY.md)**  
  射程帯・Q3 鎖・Marksman 門限・被弾メタ前提・検証手順。
- **各論 2（防具・盾・近接メタ）**: **[`EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md`](EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)**  
  鎧／盾の役割、スリング・斧の対メタ設計、全装備の整合チェック。

## スコープと編集原則

**`Items/Equipment.json`（バニラ）をスコープ全体**とみなし、変更が必要な装備だけを本 Mod の `Data/Models/Equipment.json` に記述する。

- 各 `id` は **部分上書き**（変更したいキーのみ）。
- バニラと同値にしたいキーは **Mod 側に書かない**。
- `Research.json` / `Production.json` は原則置かない（解禁・レシピはバニラ準拠）。
- 品質曲線を触るときだけ `WeaponQualitySettings.json` を任意同梱。
- 参照対象は **バニラ + 本 Mod 差分のみ**（他 Mod の `Equipment.json` は参照しない）。

## 実装ガイド（全カテゴリ共通）

1. **火力を上げたら機動コストを検討**: 遠隔・重装・盾強化のいずれでも、立ち回り制約をセットで確認する。
2. **軽減率より先に安定性を確認**: 防具は単純な防御値だけでなく、coverage 系の働きと負傷発生率の変化を重視する。
3. **メタの相互存在を担保**: あるカテゴリを強化したら、別カテゴリに対抗手段が残るか必ず確認する。
4. **射撃だけで完結させない**: 射撃調整時は同ティア近接・盾運用との比較をセットで行う。

## バニラ参照元と環境変数

本体の `Going Medieval_Data/StreamingAssets/` を参照の起点にする（インストール済みゲームのバニラのみ）。

- `Items/Equipment.json` — `primaryWeaponMode` / `secondaryWeaponMode` など装備素体の基準。
- `Items/WeaponQualitySettings.json` — 品質乗算の基準。

参考パス:

`D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`

- `GM_STREAMING_ASSETS`: `StreamingAssets` フォルダを指す。
- `GOING_MEDIEVAL_ITEMS`: `Items` フォルダを指す（`tools/plot_weapon_quality_comparison.py` が利用）。

## 素体と製作品質（Q1–Q6）

- `Data/Models/Equipment.json` の値はバニラ素体への上書き分。省略キーはバニラ値を保持。
- 実効値は「合成後素体 × `WeaponQualitySettings` の該当 `weaponType` / `productQuality` 乗算」。
- 品質 `n` で目標値 `X` を狙う場合は、**素体 = X ÷ その品質行の乗算**で逆算する。
- `TwoHandBow` のように低品質側 `rangeMultiplier < 1` の系統は、低品質帯のズレを必ずチャートで確認する。

## Mod の WeaponQualitySettings 編集範囲（現状）

- `TwoHandBow`: 弓の品質曲線。差分は最小限で維持。
- `TwoHandCrossbow`: クロスの `rangeMultiplier` を品質段階で調整（高品質ほど射程が伸びる挙動）。

## 新しいセッション

作業再開時はこのファイルを `@` 参照し、`Data/Models/Equipment.json` を開く。  
弓／クロスを触るときは `BOW_MOD_INTEGRATION_POLICY.md`、防具／盾／近接メタを触るときは `EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md` を併読する。

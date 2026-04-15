# Equipment Overhaul — 作成方針（概論）

> **このファイルの役割** — Mod 全体の設計哲学・データ編集スコープ・参照元・品質計算・実装時の共通チェックを定義する。  
> 弓／クロスは入口 `**[BOW_MOD_INTEGRATION_POLICY.md](../ranged/BOW_MOD_INTEGRATION_POLICY.md)`**、設計 `**[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)`**、実装・現状 `**[BOW_IMPLEMENTATION_STATUS.md](../ranged/BOW_IMPLEMENTATION_STATUS.md)**`。早見は `**[POLICY_SESSION_QUICK.md](POLICY_SESSION_QUICK.md)**`。防具／盾／近接メタ／スリングは `**[EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../melee_armor/EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)**` を参照する。

**表示名とフォルダ名**: ゲーム・Workshop での Mod 名は `**ModInfo.json` の `name`（Equipment Overhaul）**。開発マシン上の **フォルダ名**は任意で、**ドキュメント・ルールではリポジトリルートからの相対パス**のみを正とする（古いフォルダ名に依存した記述は避ける）。

本 Mod は「射撃だけの再調整」から「装備全体のトレードオフ設計」へ拡張する。  
**武器素体の基準は常にバニラ `Items/Equipment.json`** であり、Mod 側には **バニラと異なる `id`・フィールドのみ**を置く。

## 生成 AI 向け（取り違え防止・固定ルール）

**以降の番号付きは省略せず守る。** 数値目標・再生成チェックリスト・プレイ検証シナリオの**本文**は `[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)` / `[BOW_IMPLEMENTATION_STATUS.md](../ranged/BOW_IMPLEMENTATION_STATUS.md)` / `[COMBAT_PLAYTEST_POLICY.md](COMBAT_PLAYTEST_POLICY.md)` に分離している。**本節だけでは弓の詳細バランスを新規に決めない**（設計ファイルを読む）。

1. **セッション開始**: 先に `[POLICY_SESSION_QUICK.md](POLICY_SESSION_QUICK.md)` を読む（正本の表・タスク→ファイル）。
2. **矛盾時の正本順**: `[BOW_MOD_INTEGRATION_POLICY.md](../ranged/BOW_MOD_INTEGRATION_POLICY.md)` の **Precedence**（実装 JSON ＞ 設計 MD のドラフト表）。**7 種の合成 `range` の狭義順序**は `[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)` の **Q3／Q4 で厳守**、Q1・Q2・Q5・Q6 は同ファイルの**ティア緩和**に従う。
3. `**requiredSkills`**: 門限なしは キー省略。`**Marksman` の `value: 0` は禁止**（バニラ門限が残る）。空配列 `[]` もマージで意図とずれることがある — 下記「スコープと編集原則」の箇条書きに従う。
4. **弓／クロス再生成のエントリ**: 本 Mod の `Equipment.json` を書き戻す通常手順は `**[scripts/apply_ranged_equipment_delta.py](scripts/apply_ranged_equipment_delta.py)`**（続けてスリング）。`**[tools/regenerate_ranged_from_vanilla.py](tools/regenerate_ranged_from_vanilla.py)` 単体**は 7 種＋WQS のみで、**スリング上書きは行わない**。
5. **参照範囲**: 装備の突き合わせは **バニラ `Items/Equipment.json` と本 Mod `Data/Models/Equipment.json` のみ**（他 Mod の `Equipment.json` は参照しない）。

## 核心設計（Core Philosophy）

- **万能装備を作らない**: すべての武器・防具に「強み」と「明確な弱み」を持たせる。
- **運依存から装備選択へ**: 防御は偶然任せではなく、装備と編成で再現可能な結果に寄せる。
- **擬似ロールを成立させる**: 遊撃・前衛・据え撃ちなど、配置と連携に意味が出る設計を優先する。

## ドキュメント構成（概論／各論）

- **セッション早見（最初に `@`）**: `**[POLICY_SESSION_QUICK.md](POLICY_SESSION_QUICK.md)`** — タスク別の参照先と正本の一行表。
- **概論（本書）**: 全カテゴリ共通のルール、データの参照順、変更時チェック。
- **各論 1（弓・クロス）**: 入口 `**[BOW_MOD_INTEGRATION_POLICY.md](../ranged/BOW_MOD_INTEGRATION_POLICY.md)`**（Precedence）。設計本文 `**[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)`**（四弓＝短弓＋長弓三種のコンセプト・数値目標）、実装・現状・チェックリスト `**[BOW_IMPLEMENTATION_STATUS.md](../ranged/BOW_IMPLEMENTATION_STATUS.md)**`。
- **各論 2（防具・盾・近接メタ）**: `**[EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md](../melee_armor/EQUIPMENT_OVERHAUL_INTEGRATION_POLICY.md)`**  
鎧／盾の役割、スリング・斧の対メタ設計、全装備の整合チェック。

## スコープと編集原則

`**Items/Equipment.json`（バニラ）をスコープ全体**とみなし、変更が必要な装備だけを本 Mod の `Data/Models/Equipment.json` に記述する。  
**ただし構造は必ず `Items/Equipment.json` 準拠**（`primaryWeaponMode` / `secondaryWeaponMode` 配下）とし、旧形式のトップレベル `range` / `damage` / `attackSpeed` は使わない。

- 各 `id` は **部分上書き**（変更したいキーのみ）。公式の「Mod には差分だけ書く」**スコープの原則は変えない**（触らない `id` は Mod に載せない）。
- **再生成ツールと「完全オブジェクト」について**: `[scripts/apply_ranged_equipment_delta.py](scripts/apply_ranged_equipment_delta.py)` は実行時にバニラ `Equipment.json` を読み、**変更対象 `id` だけ**バニラの**完全な**装備ブロックを土台にしてから門限・射程・攻速等を上書きし、Mod の `Data/Models/Equipment.json` に書き戻す。これは「Mod が全装備のフルコピーを配布する」ことではなく、**マージ後に本体が期待するネスト（`secondaryWeaponMode` 等）を欠かさないための実装手段**である。過去に同スクリプト名で `**primaryWeaponMode` の数列だけのスタブ**に差し替えた版があり、**公式の部分上書きと両立しない不完全データ**になった — それが劣化の原因であり、方針転換（差分禁止）ではない。
- `**requiredSkills` を消したいときは `[]` ではなく、方針どおりの配列を明示**する（空配列がマージで「未指定」扱いになり、バニラ門限が残ることがある）。`**{"key":"Marksman","value":0}` は上書きにならずバニラ門限が残る**（本体が 0 を「要求なし」と扱い、マージでバニラ値が勝つため）。門限なしは **バニラ同様 `requiredSkills` キー自体を書かない**（`short_bow` / `light_crossbow`）。門限ありは `**value` に意図した正の整数**を書く。
- バニラと同値にしたいキーは **Mod 側に書かない**。
- `Research.json` / `Production.json` は原則置かない（解禁・レシピはバニラ準拠）。
- 品質曲線を触るときだけ `WeaponQualitySettings.json` を任意同梱。
- 参照対象は **バニラ + 本 Mod 差分のみ**（他 Mod の `Equipment.json` は参照しない）。
- **弓／クロスをバニラから再同期する**: 7 種はバニラ装備の**完全ブロック**を土台に、`**requiredSkills`（門限表は `[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)`）**・射程／弓攻速／掩体の**ポストパス**・`**TwoHandBow` / `TwoHandCrossbow` の WQS 方針**（`[tools/regenerate_ranged_from_vanilla.py](tools/regenerate_ranged_from_vanilla.py)` の定数）を適用する。語り・バニラとの立脚の**理由**は `[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)` の「役割方針の決定背景」。実行の手順・チェックは `**[BOW_IMPLEMENTATION_STATUS.md](../ranged/BOW_IMPLEMENTATION_STATUS.md)`** の「再生成・ツール」。エントリポイントは `**[scripts/apply_ranged_equipment_delta.py](scripts/apply_ranged_equipment_delta.py)`**（続けてスリング）。環境変数 `**GOING_MEDIEVAL_ITEMS`** で `Items` を指定可能。

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
- `GOING_MEDIEVAL_ITEMS`: `Items` フォルダを指す（`tools/plot_weapon_quality_comparison.py` が利用）。同ツールの **層 1 補完**は `quality_charts/ranged/layer1_eval_bundle.md` を入口にする（`[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)` の帯域・階層節）。同バンドルに `**ignoresArmor` 方針 CSV**（`quality_charts/ranged/script/layer1_ignores_armor_policy_summary.csv`）と **Mod 参照線チャート**（`ignoresArmor_mod_policy_overlay.png`）が含まれる。

## 素体と製作品質（Q1–Q6）

- `Data/Models/Equipment.json` の値はバニラ素体への上書き分。省略キーはバニラ値を保持。
- 上書き対象の武器性能は `primaryWeaponMode`（必要時 `secondaryWeaponMode`）で編集する。
- 実効値は「合成後素体 × `WeaponQualitySettings` の該当 `weaponType` / `productQuality` 乗算」。
- 品質 `n` で目標値 `X` を狙う場合は、**素体 = X ÷ その品質行の乗算**で逆算する。
- `TwoHandBow` のように低品質側 `rangeMultiplier < 1` の系統は、低品質帯のズレを必ずチャートで確認する。
- **データ上の `productQuality`（1–6）＝本 Mod チャートの Q1–Q6** とする。DevTools の品質ラベルやスポーン可否は **ローカライズ名と 1:1 ではない**ことがある（観察・読み替えは `**[COMBAT_PLAYTEST_POLICY.md](COMBAT_PLAYTEST_POLICY.md)`** の「DevTools と製作品質」）。

## 数値の丸め（基本方針）

Mod に明示する **浮動小数の装備パラメータ**（例: `primaryWeaponMode` / `secondaryWeaponMode` の `range`, `attackSpeed`, `precisionFalloff`, `ignoresArmor` など、および `meleeCover` / `rangedCover`）は、**小数第2位まで**を正とする。

- **丸め方式**: 第3位を **四捨五入**（銀行丸めではない **half-up**）。実装・ツールでは `Decimal` で `quantize("0.01", ROUND_HALF_UP)` に相当する処理とする。
- **JSON 表記**: 丸めた結果が数学的に整数になる値は **整数として書く**（例: `12` / `1`）。不要な `12.0` は避ける。
- **適用範囲**: `Data/Models/Equipment.json` の上記フィールドに加え、チャート・表・集計ツール（例: `tools/plot_weapon_quality_comparison.py` の出力）も **同じ桁・同じ丸め**に揃え、ドキュメント上の数値とデータの食い違いを防ぐ。

ゲーム UI が内部 float を多桁表示する場合があるが、**データ側の正は第2位まで**とする。

## Mod の WeaponQualitySettings 編集範囲（現状）

弓／クロスの WQS は `**tools/regenerate_ranged_from_vanilla.py`** に集約（再生成で Mod の `WeaponQualitySettings.json` に反映）。`**TwoHandBow`** … `**TWO_HAND_BOW_QUALITY_DELTAS`**。`**TwoHandCrossbow`** … 命中系はバニラのまま、`**TWO_HAND_CROSSBOW_DAMAGE_ATTACK_OVERRIDES**` で damage／攻速を平坦化し、`**rangeMultiplier` で品質に応じた射程の微増**（素体は `ROLE_RANGE`）。意図は `[BOW_DESIGN_TARGETS.md](../ranged/BOW_DESIGN_TARGETS.md)`（決定背景・弓／クロスのデータ差分・WQS 明文化）。

## 新しいセッション

最初に `**[POLICY_SESSION_QUICK.md](POLICY_SESSION_QUICK.md)`** を `@` し、上記 **「ドキュメント構成（概論／各論）」** のリンクに従う（構造はバニラ `Items/Equipment.json` を正とする）。
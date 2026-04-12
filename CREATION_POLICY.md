# Ranged Weapons Overhaul — 作成方針

射撃武器のバランス用 Mod。数値の上書きは主にこのフォルダの `Data/Models` で行う。

**スコープ** — 主に `Data/Models/Equipment.json` の部分上書き。`Research.json` / `Production.json` は置かない（解禁・レシピはバニラのまま）。品質曲線を触るときだけ `WeaponQualitySettings.json` を任意で同梱・編集する。プレイはこの Mod 単体推奨。

## 弓とクロスボウの差別化（役割）

- **弓（TwoHandBow）**: **届く距離を取る**（上級弓はクロスより長い射程帯）。**試行回数**は `attackSpeed`（数値が小さいほど速い）で表現。遠距離では外れやすくするため **`precisionFalloff` はクロスより大きめ**にしがち。単発 `damage` は押し上げず（長弓はバニラ上限を超えない想定）、**射程・命中曲線・品質**で実効を取る。
- **クロスボウ（TwoHandCrossbow）**: **中射程の階段**（いずれも長弓より短く、ライト〜ヘビーで段差）。**据え撃ち・一発**向けに `attackSpeed` は遅め（数値大）、**`precisionFalloff` は小さめ**で距離減衰を緩め、`damage` / `ignoresArmor` で鎧向きの顔を出す。クロス 3 種の単発は**バニラ水準を超えない**方向（近接との兼ね合い）。射程を短めにする分、表上の期待火力はバニラ比で上がってよい、という整理がありうる（過剰インフレは避ける）。
- **本体の Marksman**: 命中・威力などへの補正は弓とクロスに**同様に掛かる**前提。違いは **`Equipment` の静特性**（＋任意で `WeaponQualitySettings`・`requiredSkills`）で出す。
- **調整の見方**: カタログ上の「期待 DPS」だけで裁かない。**届く距離・減衰・門限・品質**を並べ、プレイで確認する。対応ランク同士では弓の素体期待をクロスよりやや低めに寄せる、などの**相対**がありうる（具体数値は都度 `Equipment` と検証で決める）。
- **順序の約束**: 上級ラインでは `range` / `damage` / `ignoresArmor` / `attackSpeed` の **`<` 連鎖**（クロスと上級弓の段差）を崩さないこと。詳細の鎖は変更方針ドキュメント（弓 mod 統合・変更方針）に従う。

## バニラを正とする

本体の **`Going Medieval_Data/StreamingAssets/`** 以下を参照の起点にする。

- **`Items/Equipment.json`** — 各 `id` の `primaryWeaponMode`（`damage` / `range` / `attackSpeed` / `precision` / `precisionFalloff` / `ignoresArmor` など）が素体の基準。
- **`Items/WeaponQualitySettings.json`** — 製作品質ごとの乗算の基準。Mod 側で上書きする場合も、まずここを開いて差分だけに留める。

インストール先は環境ごとに違う。例（参考）:

`D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`

環境変数 **`GM_STREAMING_ASSETS`** に、上記のように **`StreamingAssets` フォルダそのもの**のパスを設定する（末尾は `StreamingAssets` で終わる）。ツールやスクリプトがこの変数から `Items\Equipment.json` 等を探せる。

変数を設定しない場合は、エクスプローラやエディタで上記フォルダを直接開き、バニラ JSON と Mod の `Data/Models` を手で突き合わせる。

## 新しいセッション

作業を再開するときは、このファイルを `@` 参照してから `Data/Models/Equipment.json` を開くとよい。

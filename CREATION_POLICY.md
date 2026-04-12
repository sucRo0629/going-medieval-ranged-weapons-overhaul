# Ranged Weapons Overhaul — 作成方針

射撃武器のバランス用 Mod。数値の上書きは主にこのフォルダの `Data/Models` で行う。

**スコープ** — 主に `Data/Models/Equipment.json` の部分上書き。`Research.json` / `Production.json` は置かない（解禁・レシピはバニラのまま）。品質曲線を触るときだけ `WeaponQualitySettings.json` を任意で同梱・編集する。プレイはこの Mod 単体推奨。

## 弓とクロスボウの差別化（役割）

- **弓（TwoHandBow）**: **届く距離を取る**（上級弓はクロスより長い射程帯）。**試行回数**は `attackSpeed`（数値が小さいほど速い）で表現。遠距離では外れやすくするため **`precisionFalloff` はクロスより大きめ**にしがち。単発 `damage` は押し上げず（長弓はバニラ上限を超えない想定）、**射程・命中曲線・品質**で実効を取る。
- **クロスボウ（TwoHandCrossbow）**: **中射程の階段**（いずれも長弓より短く、ライト〜ヘビーで段差）。**据え撃ち・一発**向けに `attackSpeed` は遅め（数値大）、**`precisionFalloff` は小さめ**で距離減衰を緩め、`damage` / `ignoresArmor` で鎧向きの顔を出す。**素体 `attackSpeed` はバニラのライト／標準／ヘビーと同値に寄せる**（据え撃ちの手触りをバニラに揃える）。**短射程・高精度・`ignoresArmor` の代償**として単発 `damage` はバニラ素体より上げてよいが、**過剰インフレは避け**、チャートとプレイで確認する。
- **本体の Marksman**: 命中・威力などへの補正は弓とクロスに**同様に掛かる**前提。違いは **`Equipment` の静特性**（＋任意で `WeaponQualitySettings`・`requiredSkills`）で出す。
- **調整の見方**: カタログ上の「期待 DPS」だけで裁かない。**届く距離・減衰・門限・品質**を並べ、プレイで確認する。対応ランク同士では弓の素体期待をクロスよりやや低めに寄せる、などの**相対**がありうる（具体数値は都度 `Equipment` と検証で決める）。
- **順序の約束**: 上級ラインでは `range` / `damage` / `ignoresArmor` / `attackSpeed` の **`<` 連鎖**（クロスと上級弓の段差）を崩さないこと。詳細の鎖は変更方針ドキュメント（弓 mod 統合・変更方針）に従う。
- **近接（`secondaryWeaponMode`）**: 弓・クロスボウも同一 `Equipment` エントリに **`TwoHandBowMelee`**（本体を振るストック殴り）が付く。戦闘中の武器持ち替えとは別に、**一装備のセカンダリ**として存在する。

## スリングの差別化（役割）

スリングは弓・クロスとは別レーン（`weaponType`: **OneHandSling** / **TwoHandSling**）。品質曲線は原則バニラ `WeaponQualitySettings` の該当ブロックのままとし、**Mod にスリング専用の品質ブロックは足さない**。遠隔の素体は **バニラと同値**に寄せ、役割の説明は上記コンセプトに従う（`secondaryWeaponMode` の `TwoHandStaff` はバニラのまま／上書きしない）。

- **片手スリング（`sling` / OneHandSling）**: **盾と両立できる**ため、射撃性能は「盾の分」を含めて設計する。**近距離の撹乱役**（届く距離・装甲貫通は弓の主役帯に届かせない）。重装相手のメイン火力や最長レンジの主役にはしない。数値だけの期待 DPS と盾を持てない弓などを並べるときは、**盾込みの実戦コスト**を頭に置く。
- **スタッフスリング（`sling_staff` / TwoHandSling）**: **両手・装備枠が重い**（バニラ `equipmentSlots: 3`）ため盾は持てない。**片手より届く／石の圧力は上げてよい**が、**重装キラー・最長レンジの主役**にはしない。遠隔は **中〜やや手前のハラス**が主。`secondaryWeaponMode` の **`TwoHandStaff`** は、弓・クロスと同様に **一装備のセカンダリ近接**だが、**`TwoHandBowMelee`（他の射撃武器のストック殴り）よりやや得意**がコンセプト（バニラでも単発 `damage` 等が上）。**本職近接や射撃主役の置き換え**にはせず、**詰まり時の保険・補刀**に留め、遠隔モードとのバランスを崩さない。

## バニラを基に調整する

本体の **`Going Medieval_Data/StreamingAssets/`** 以下を参照の起点にする。

- **`Items/Equipment.json`** — 各 `id` の `primaryWeaponMode`（`damage` / `range` / `attackSpeed` / `precision` / `precisionFalloff` / `ignoresArmor` など）が素体の基準。弓・クロス等は同一エントリに **`secondaryWeaponMode`**（例: `TwoHandBowMelee`）もある。
- **`Items/WeaponQualitySettings.json`** — 製作品質ごとの乗算の基準。Mod 側で上書きする場合も、まずここを開いて差分だけに留める。

インストール先は環境ごとに違う。例（参考）:

`D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`

環境変数 **`GM_STREAMING_ASSETS`** に、上記のように **`StreamingAssets` フォルダそのもの**のパスを設定する（末尾は `StreamingAssets` で終わる）。ツールやスクリプトがこの変数から `Items\Equipment.json` 等を探せる。

変数を設定しない場合は、エクスプローラやエディタで上記フォルダを直接開き、バニラ JSON と Mod の `Data/Models` を手で突き合わせる。

環境変数 **`GOING_MEDIEVAL_ITEMS`** に、バニラの **`Items` フォルダそのもの**のパスを設定すると、[`tools/plot_weapon_quality_comparison.py`](tools/plot_weapon_quality_comparison.py) が Steam レジストリに頼らず `Equipment.json` を解決できる（未設定時は Steam インストールから推測）。

## 素体と製作品質（Q1–Q6）

- `Data/Models/Equipment.json` に書く数値は **素体（テンプレ）**。ゲーム内や比較グラフの **Q1–Q6** は、素体に **`Items/WeaponQualitySettings.json` の該当 `weaponType` ブロック**（Mod 同梱ならそちら）の **該当 `productQuality` 行の各 `*Multiplier`** を掛けたあとの実効値。
- 「品質 _n_ で射程（や命中など）を _X_ にしたい」ときは **素体 = _X_ ÷ その品質行の乗算** で逆算する。弓の `TwoHandBow` では低品質の `rangeMultiplier` が 1 未満のため、素体だけ動かしても **チャート左端（低品質）の射程**が意図とずれることがある。変更時は品質行ごとに確認する。

## Mod の WeaponQualitySettings で触っている範囲

- **`TwoHandBow`**: 弓の品質曲線（ダメージ等）。弓の射程は品質別 `rangeMultiplier` があり得る。差分はバニラ `Items/WeaponQualitySettings.json` と突き合わせ、必要最小限に留める。
- **`TwoHandCrossbow`**: Mod 同梱で、バニラでは 1 固定の **`rangeMultiplier` を品質に応じて段階的に上げる**（高品質ほど届く距離が伸びる）。クロスだけ「品質で射程が伸びる」挙動の根拠はここ。

## 命中・装甲無視（調整の整理）

- **弓**: 段階は短 ＜ 戦 ＜ 曲 ＜ 長。曲弓の素体 `precision` は **最大 0.99**、長弓は品質乗算後に **Q3 以降で実効 1** になるよう素体を置く、といった整理でよい（具体数値は常に `Equipment` が正）。
- **クロスボウ**: 素体 `precision` はライト → 標準 → ヘビーで段を付け、ヘビーは高品質で頭打ち寄りにできる。**`ignoresArmor` はクロス系が弓より高い**前提で調整する。
- **曲弓 `ignoresArmor`**: バニラ `curved_bow` と同じ **0.8** に合わせる（バニラを正）。

## 新しいセッション

作業を再開するときは、このファイルを `@` 参照してから `Data/Models/Equipment.json` を開くとよい。

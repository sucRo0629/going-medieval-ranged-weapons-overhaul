# Ranged Weapons Overhaul — 作成方針

> **このファイルの役割** — Mod の目的・**スコープ**（バニラ `Items/Equipment.json` を全体とし、差分のみ本 Mod に書く）・バニラ／環境変数／ツールの参照先・スリング・素体×品質の読み方。弓／クロスの**長所分担・Q3 鎖・門限・被弾メタ前提・変更時チェック**は **[`BOW_MOD_INTEGRATION_POLICY.md`](BOW_MOD_INTEGRATION_POLICY.md)** を開く。

射撃武器のデータオーバーホール Mod。数値の上書きは主にこのフォルダの `Data/Models` で行う。**武器素体の基準は常にバニラ `Items/Equipment.json`** であり、本 Mod には **バニラと異なる `id`・フィールドだけ**を置く。

## 大きな変更点

- 射撃武器も近接武器のように品質と素材でダメージが増加するように変更する。
- ヘビィクロスボウ一択になるのを避けるため、弓を長射程、クロスボウを中射程として数値を調整する。

**スコープ** — **`Items/Equipment.json`（バニラ）をスコープの全体**とみなし、**変更が必要な武器だけ**を **本 Mod フォルダ**の `Data/Models/Equipment.json` に載せる。各エントリは **部分上書き**（変えたいキーだけ。バニラと同じままにしたい `id` は **本 Mod に書かない**）。`Research.json` / `Production.json` は置かない（解禁・レシピはバニラのまま）。品質曲線を触るときだけ `WeaponQualitySettings.json` を任意で同梱・編集する。武器のデータを変更する Mod とは競合する可能性が高いため単体推奨。**Steam ワークショップや別 Mod の `Equipment.json` は参照しない**。突き合わせ・レビューでは **バニラ `Items/Equipment.json`** と **本 Mod の差分**を見る（本 Mod 単体をフル定義として読まない）。

## 弓とクロスボウ（概要）

弓を**長射程・高回転**、クロスボウを**中射程・据え撃ち・鎧向き**に棲み分ける。**長所・短所の列挙、カタログ DPS の見方、Q3 の狭義連鎖、装備中の移動・掩体、Marksman 門限、近接との検証**はすべて **[`BOW_MOD_INTEGRATION_POLICY.md`](BOW_MOD_INTEGRATION_POLICY.md)** に集約している。

- **Marksman**: 本体の命中・威力補正は弓・クロス共通。装備門限（`requiredSkills`）のドラフト表と実装の正は **BOW** の「装備門限」節。
- **`secondaryWeaponMode`**: 弓・クロスは同一 `Equipment` エントリに **`TwoHandBowMelee`**（ストック殴り）がある。戦闘中の武器持ち替えとは別に、**一装備のセカンダリ近接**として存在する。

## スリングの差別化（役割）

スリングは弓・クロスとは別レーン（`weaponType`: **OneHandSling** / **TwoHandSling**）。品質曲線は原則バニラ `WeaponQualitySettings` の該当ブロックのままとし、**Mod にスリング専用の品質ブロックは足さない**。遠隔の素体は **バニラと同値**に寄せ、役割の説明は上記コンセプトに従う（`secondaryWeaponMode` の `TwoHandStaff` はバニラのまま／上書きしない）。

- **片手スリング（`sling` / OneHandSling）**: **盾と両立できる**ため、射撃性能は「盾の分」を含めて設計する。**近距離の撹乱役**（届く距離・装甲貫通は弓の主役帯に届かせない）。重装相手のメイン火力や最長レンジの主役にはしない。数値だけの期待 DPS と盾を持てない弓などを並べるときは、**盾込みの実戦コスト**を頭に置く。
- **スタッフスリング（`sling_staff` / TwoHandSling）**: **両手・装備枠が重い**（バニラ `equipmentSlots: 3`）ため盾は持てない。**片手より届く／石の圧力は上げてよい**が、**重装キラー・最長レンジの主役**にはしない。遠隔は **中〜やや手前のハラス**が主。`secondaryWeaponMode` の **`TwoHandStaff`** は、弓・クロスと同様に **一装備のセカンダリ近接**だが、**`TwoHandBowMelee`（他の射撃武器のストック殴り）よりやや得意**がコンセプト（バニラでも単発 `damage` 等が上）。**本職近接や射撃主役の置き換え**にはせず、**詰まり時の保険・補刀**に留め、遠隔モードとのバランスを崩さない。

## バニラを基に調整する

本体の **`Going Medieval_Data/StreamingAssets/`** 以下を参照の起点にする（**インストール済みゲームのバニラ**のみ。他 Mod の同梱 JSON は読まない）。

- **`Items/Equipment.json`** — 各 `id` の `primaryWeaponMode`（`damage` / `range` / `attackSpeed` / `precision` / `precisionFalloff` / `ignoresArmor` など）が素体の基準。弓・クロス等は同一エントリに **`secondaryWeaponMode`**（例: `TwoHandBowMelee`）もある。
- **`Items/WeaponQualitySettings.json`** — 製作品質ごとの乗算の基準。Mod 側で上書きする場合も、まずここを開いて差分だけに留める。

インストール先は環境ごとに違う。例（参考）:

`D:\SteamLibrary\steamapps\common\Going Medieval\Going Medieval_Data\StreamingAssets`

環境変数 **`GM_STREAMING_ASSETS`** に、上記のように **`StreamingAssets` フォルダそのもの**のパスを設定する（末尾は `StreamingAssets` で終わる）。ツールやスクリプトがこの変数から `Items\Equipment.json` 等を探せる。

変数を設定しない場合は、エクスプローラやエディタで上記フォルダを直接開き、バニラ JSON と Mod の `Data/Models` を手で突き合わせる。

環境変数 **`GOING_MEDIEVAL_ITEMS`** に、バニラの **`Items` フォルダそのもの**のパスを設定すると、[tools/plot_weapon_quality_comparison.py](tools/plot_weapon_quality_comparison.py) が Steam レジストリに頼らず `Equipment.json` を解決できる（未設定時は Steam インストールから推測）。

## 素体と製作品質（Q1–Q6）

- `Data/Models/Equipment.json` に書く数値は **バニラ素体に対する上書き分**（省略したキーはバニラの値のまま）。**合成後の素体**をテンプレとして、ゲーム内や比較グラフの **Q1–Q6** は、それに **`Items/WeaponQualitySettings.json` の該当 `weaponType` ブロック**（Mod 同梱ならそちら）の **該当 `productQuality` 行の各 `*Multiplier`** を掛けたあとの実効値。
- 「品質 *n* で射程（や命中など）を *X* にしたい」ときは **素体 = *X* ÷ その品質行の乗算** で逆算する。弓の `TwoHandBow` では低品質の `rangeMultiplier` が 1 未満のため、素体だけ動かしても **チャート左端（低品質）の射程**が意図とずれることがある。変更時は品質行ごとに確認する。

## Mod の WeaponQualitySettings で触っている範囲

- **`TwoHandBow`**: 弓の品質曲線（ダメージ等）。弓の射程は品質別 `rangeMultiplier` があり得る。差分はバニラ `Items/WeaponQualitySettings.json` と突き合わせ、必要最小限に留める。
- **`TwoHandCrossbow`**: Mod 同梱で、バニラでは 1 固定の **`rangeMultiplier` を品質に応じて段階的に上げる**（高品質ほど届く距離が伸びる）。クロスだけ「品質で射程が伸びる」挙動の根拠はここ。

## 新しいセッション

作業を再開するときは、このファイルを `@` 参照してから、**本 Mod リポジトリ内**の `Data/Models/Equipment.json` を開くとよい（別 Mod の `Equipment.json` と取り違えない）。弓／クロス数値を触るときは **`BOW_MOD_INTEGRATION_POLICY.md`** も併せて開く。

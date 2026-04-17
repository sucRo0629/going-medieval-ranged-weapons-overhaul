# 武器設計ティア（全種共通）

## 目的

- **レシピ・研究・作業台より先に**、武器 id ごとの進行帯（**T1〜T5**）を揃える。
- 数値の正本はリポジトリ内の **`scripts/weapon_table_common.py` の `DESIGN_TIER_ALL`**（`(並び用整数, "T1"|…|"T5"|"例")`）。

### 帯の決め方（CombatScore(Base)）

より精緻な進行管理のため、`scripts/mod_weapon_overview_table.py` では `damage / attackSpeed` をベースにした **CombatScore(Base)** を用いて種別横断の自動ティア判定を行っている。

- **Base 4.5 境界**: `CombatScore(Base)` が **4.5** を本 Mod の実質的な上限とする。
- **Steel 上限方針**: 金属武器の場合、**鋼（Steel）製** での性能がゲーム内バランスの事実上の上限となるよう調整する。目安として **T5: 5.0 以下** を維持する。

| ティア | CombatScore(Base) 閾値 |
| ------ | ---------------------- |
| **T1** | < 2.5                  |
| **T2** | 2.5 – 2.99             |
| **T3** | 3.0 – 3.49             |
| **T4** | 3.5 – 3.99             |
| **T5** | 4.0 – **4.5**          |

## ワークフロー

1. **ティア**: `DESIGN_TIER_ALL` を更新し、`docs/MOD_WEAPON_OVERVIEW.generated.md` を再生成する。冒頭の **「ティア調整用: 製作可＋計画武器」** で種別横断の帯を確認する（レシピ未整備の id は `mod_weapon_overview_table.py` の `TIER_PLANNING_EXTRA_WEAPON_IDS`）。続く weaponType 別の詳細表で個別データを見る。
2. **レシピ**: ティアが固まってから `Production` / `Research` / 作業台を合わせる（別ドキュメント・監査手順に従う）。

## 補足

- 弓の性能方針は `implementation_policies/ranged/BOW_DESIGN_TARGETS.md` と併読（ティア帯とは別軸）。
- `damage` を動かしたら上表に合わせ **`DESIGN_TIER_ALL` を更新**する。
- `DESIGN_TIER_ALL` に無い id は、表生成スクリプトが **弓／クロス＝ Marksman、スリング＝射程、その他＝レシピスキル**でフォールバックする。

## 武器種の特徴付け（コスト観点）

- ティア内の序列は、性能値だけでなく **制作コスト** も加味する。
- コスト序列（小 → 大）は以下を基本とする。
  **槍 < 投擲槍 < 斧 < メイス < 剣**
- **T1〜T3** は資源が潤沢でない前提で、上記コスト差を **強め** にティア内順位へ反映する。
- **T4 以降** は資源が潤沢な前提で、T1〜T3 より **僅差** の重みでティア内順位へ反映する。
- さらに、**金属を使っていない近接・投擲武器**は、同ティア内で順位を低めに抑える。
- この方針は `scripts/mod_weapon_overview_table.py` のティア内並びロジック（`CombatScore(Base)` の補正）に反映する。
- 投擲武器の調整時は `primaryWeaponMode` だけでなく `secondaryWeaponMode`（サイドアーム）のスコアも確認し、同ティア近接カテゴリ（槍/斧）との相対関係を崩さないように調整する。

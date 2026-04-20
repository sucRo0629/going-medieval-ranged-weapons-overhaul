# 注意

- 同じ id を Mod で定義すると、同じ key なら上書きするがそれ以外はバニラとマージされる
  そのため id 以外は差分だけ書けばいいし、バニラで使っていたパラメータを消したい場合は Mod 側で明示的に 0 にする必要がある

- バニラの鉄のインゴットを 0 にして金属類で作れるようにしても、制作時に鉄選ぶと作業台に追加 → 回収がループしてデッドロックになる
- produced が wood や iron だったものを出力 0 にしても元の武器名が見つからずエラーになって何も出ない
  バニラ版を鉄製として、鋼製を新規追加するしかなさそう

## ディレクトリ構造

Mod では Mod 名/Data/Models/がバニラの StreamingAssets/に相当するので構造を合わせる

# 装備のデータ構造

## Production

「何を作るか」を決めるレシピ層
produced[].blueprintID / customProducts[].output[].blueprintID で生成先 ID を指定

- iconPath: 作業台でのアイコン
- jobType: 256: 鍛冶、512: 大工

### 素材で性能差を追加する

```
"produced": [
  {
    "blueprintID": "iron_throwing_axes",
    "amount": 1
  },
  {
    "blueprintID": "ash",
    "amount": 25
  }
],
"recipe": [
  {
    "key": "iron_ingot",
    "value": 5
  },
  {
    "key": "wood",
    "value": 20
  }
],
```

↓

```
"produced": [
  {
    "blueprintID": "iron_throwing_axes",
    "amount": 0
  },
  {
    "blueprintID": "ash",
    "amount": 25
  }
],
"recipe": [
  {
    "key": "iron_ingot",
    "value": 0
  },
  {
    "key": 2048,
    "value": 15
  },
  {
    "key": "wood",
    "value": 20
  }
],
```

productionSteps の後に各素材用の ID 追加

```
"customProducts": [
  {
    "input": "iron_ingot",
    "output": [
      {
        "blueprintID": "iron_dagger",
        "amount": 1
      }
    ]
  },
  {
    "input": "steel_ingot",
    "output": [
      {
        "blueprintID": "steel_dagger",
        "amount": 1
      }
    ]
  }
]

```

追加装備の場合、武器名は以下のように書く
info は似た武器と同じにしてる例

```
"locKeys": [
  {
    "languageName": "Japanese",
    "name": "ジャベリン",
    "info": "equipment_info_light_javelins"
  }
],
```

## Resources

生成先 ID の実体（アイテムブループリント）層
見た目、素材、品質有無、スタック、耐久(HP)、カテゴリ等を持つ
Production の blueprintID はまずここで解決される

- id : Equipment の ID
- materials : Equipment の customProducts で指定した材料
- tooltipLines : 防具貫通大とかの表記
- groupIdentifier : Equipment の ID
- protoId : Equipment の ID
- itemMaterialCategory : 1:金属、2:皮革、3:木
- iconPath : 装備中アイコン

## Equipment

そのアイテムが武器/防具として使われる時の性能層
攻撃値、射程、武器モード、必要スキルなど
なのでイメージは:

Production (作成指示) → Resources (アイテム実体) ↔ Equipment (装備性能)

## Research

こっちはもしかしたら差分だけ書くだとエラーになるかも

# DevTools コンソールコマンド一覧（`list` 出力の転記）

ゲーム内で `list` を実行した際の表示を、スクショから手動転記したものです。  
**正本はゲーム内コンソール**／補助として元画像:

- `image01.png` … `activateAllResearch` 〜 `forceCropHarvestPhase` 付近
- `image02.png` … `forceGoal` 〜 `setNPCFaction`
- `image03.png` … `setPetAnimal` 〜 `toggleinstantdig`
- `image04.png` … `trackWorkerArea` 〜 `woundWorker`

バージョンやビルドでコマンドが増減する可能性があります。

---

## コマンド一覧（アルファベット順・説明は英語原文のまま）

| command | description |
|---------|-------------|
| `activateAllResearch` | Instant activation of all research. |
| `addExperience` | Increases / decreases the experience of the given skill to the humanoid you click on. |
| `animateWorkers` | Trigger animation on all workers. |
| `autoconstruct` | Toggles instant construction. |
| `autoprodResources` | Toggles automatic production without resources for all production buildings. |
| `autoprodWorkers` | Toggles automatic production without humanoid. |
| `changePrisonerRecruitStat` | Click on prisoner to change recruit stat in %. |
| `changeWorkerMood` | Click on humanoid to change mood. |
| `commandDisableSecondMapTimer` | Disables/enables second map timer. |
| `constructWithoutResources` | Allows construction without resources. |
| `constructionSpeedMax` | Max outs humanoid construction speed. |
| `convertAllBuildingsToEnemyOwned` | All player buildings are converted to enemy buildings. |
| `countResources` | Print resource counters. |
| `craftableBuildingsEnabled` | Toggles craftable buildings in UI. |
| `createCommanderGroupFromAll` | Creates a Commander AI group from all enemies on the map. |
| `createCommanderGroupFromSelection` | Creates a Commander AI group and lets you add units via left click. |
| `cropNextPhase` | Switch to next plant growth phase on selected crop. |
| `damageVoxel` | Damage voxels around the cursor in a range. |
| `dealDamage` | Damage anything you click on (except voxels). |
| `deleteMapMarker` | Click on any map marker on Region map to delete it. Right click to stop. |
| `destroyPile` | Click on pile to destroy it. |
| `drawEffectMap` | Draws in effect map. |
| `drawGrass` | Draw grass where the cursor is. Right click to disable this debug tool. |
| `drawMapMask` | Draws in map mask (terrain material). |
| `drawSnow` | Draw snow where the cursor is. Right click to disable this debug tool. |
| `drawWetness` | Draw wetness where the cursor is. Right click to disable this debug tool. |
| `enableManualCommanderInput` | Sets the first commander agent to the debug manual input one. |
| `enableManualConstructCommanderInput` | Sets the first commander agent to the debug manual construct one. |
| `enableManualDigCommanderInput` | Sets the first commander agent to the debug manual dig one. |
| `endEffector` | Click on a humanoid to end effector. |
| `fillStorage` | Click on storage to fill it with random allowed piles. |
| `findCastleBreachingPoint` | Returns a path of nodes from a greathall to a node that can reach edge of the map. |
| `finishAllBlueprints` | Turns all stable blueprints into finished buildings. |
| `finishAnimalProduction` | Force animal production to complete. |
| `fireEffector` | Click on a humanoid to apply effector to it. |
| `forceCropHarvestPhase` | Forces crops to harvest phase after planting. |
| `forceGoal` | Force run goal on the agent. |
| `forcePlantCrops` | Toggles spawning crops with planted seeds. |
| `gc` | Forces 2 passes of GC.Collect, logs out allocated memory. |
| `genRaidSpawnPoints` | Generates raid spawn points for N enemies every time you click and visualizes them with gizmos. |
| `giveBirth` | Completes pregnancy on selected female animal. |
| `help` | Shows full description of command. |
| `instantCut` | Toggles instant cutting of future marked plants. |
| `killAllFish` | Kills all fish on the map. |
| `killEnemies` | Kills all enemy NPCs on the map. |
| `killPiles` | Kills all piles on the map. |
| `killPlants` | Kills all plant map resources. |
| `ladderFalldown` | Selected agent will fall from ladder. |
| `list` | Lists all commands, or search along commands. |
| `listGlobalStats` | Lists out all global stats. |
| `makeNPCLeave` | Makes NPC retreat from map. |
| `markForRoping` | Click on a animal to give it 'rope' order. |
| `marketingMode` | Turns on marketing mode. |
| `pathCheck` | Check reachability between two points. Takes WalkableModel blueprint ID. |
| `plantNextPhase` | Switch to next plant growth phase. |
| `productionSpeed` | Sets production global multiplier speed (0-50). |
| `quit` | Quits the application. |
| `removeWorker` | Click on a humanoid to remove it. |
| `resetAchievements` | Resets all achievement progress. |
| `resetPrisonerRecruitAttempt` | Click on prisoner to reset their recruit attempt. |
| `resetTamingAndTraining` | Reset animal taming and training counters. |
| `resetTrap` | Reset selected trap. |
| `setAchievementStat` | Sets value to achievement stat. |
| `setConsciousness` | Set consciousness level of workers or enemies. |
| `setDebugCombatTarget` | Select target to be used for drawing targeting gizmos. |
| `setDomesticAnimal` | Sets animal as domestic. |
| `setFreshness` | Set freshness of piles and items in the storage of creatures you click on. |
| `setGlobalStat` | Sets the specified global stat's value. |
| `setHaulMode` | Changes global hauling mode for all agents. |
| `setHealth` | Set health level of creatures, plants or resources. |
| `setHunger` | Set creature's hunger level. |
| `setInteractionEventChance` | Set interaction event chance. |
| `setLowFuel` | Set fuel to very low. |
| `setNPCBehaviour` | Sets behaviour for a Humanoid on click. |
| `setNPCFaction` | Sets faction for any NPC on click. |
| `setPetAnimal` | Sets animal as a pet. |
| `setPregnantAnimal` | Force pregnancy on selected female animal. |
| `setSeason` | Sets season. |
| `setSleep` | Set creature's sleep level (if it has a sleep stat). |
| `setStat` | Set current level of the stat. |
| `setStunted` | Turns plant into a stunted one. |
| `setTimeInDay` | Sets to given time in day. |
| `setTradeDeal` | Sets up or breaks a trade deal with the selected faction. |
| `setWalkableModel` | Sets or gets the creature's walkable model on click. |
| `setWeatherEvent` | Sets weather event. |
| `setWildAggressiveAnimal` | Sets animal as wild aggressive. |
| `setWildAnimal` | Sets animal as wild. |
| `setWorkerStat` | Set humanoid stat by clicking on a humanoid. |
| `spawnAnimal` | Spawns animal(s) on mouse click. |
| `spawnBardVisitor` | Spawns a bard visitor on mouse click. |
| `spawnDomesticAnimal` | Spawns domestic animal(s) on mouse click. |
| `spawnEnemy` | Spawns enemy on mouse click. |
| `spawnFish` | Spawns fish on mouse click. |
| `spawnMaterialsWithBuilding` | Toggles spawning materials next to buildings. |
| `spawnMaturePlant` | Spawns mature plant on mouse click. |
| `spawnNPC` | Spawns Humanoid on mouse click. |
| `spawnParticleSystem` | Spawns the given particle system on mouse click. |
| `spawnPetAnimal` | Spawns pet animal(s) on mouse click. |
| `spawnPlant` | Spawns plant on mouse click. |
| `spawnPriestVisitor` | Spawns a priest visitor on mouse click. |
| `spawnRandomResources` | Spawns random resource piles on mouse click. |
| `spawnResource` | Spawns resource piles on mouse click. |
| `spawnResourceCtg` | Spawns resource piles by category on mouse click. |
| `spawnShamanVisitor` | Spawns a shaman visitor on mouse click. |
| `spawnTrader` | Spawns a trader on mouse click. |
| `spawnWorker` | Spawns humanoid on mouse click. |
| `switchFactionOwnership` | Toggles building and pile ownership between player and enemy. |
| `thunder` | Click to spawn a thunder (from thunderstorm). |
| `toggleAllowEdgePlacement` | Allow or forbid building placement on the edge of the map. |
| `toggleInvulnerability` | Toggles Creature's invulnerability. |
| `toggleTooltips` | Toggles Ingame Tooltips on/off. |
| `toggleUI` | Toggles Ingame UI on/off. |
| `toggleWeatherView` | Toggles weather debug view. It shows weather events for the whole season. |
| `toggleinstantdig` | Toggles between instant and goap dig. |
| `trackWorkerArea` | Periodically prints A* areas and humanoid count in them. |
| `triggerTrap` | Trigger selected trap. |
| `tryFishSpawn` | Force system to try to spawn a new fish. |
| `unlockAchievement` | Unlocks achievement. |
| `unlockAllVariants` | Toggles whether all building variants are unlocked or not. |
| `unlockEvent` | Unlocks the given game event type or player triggered event type. |
| `unlockRoomType` | Unlocks the given room type. |
| `voxelInfo` | Display info of the currently selected voxel. |
| `woundWorker` | Click on a humanoid to wound it. |

---

## 射撃・戦闘テストでよく触りそうなもの

| command | メモ |
|---------|------|
| `spawnEnemy` | 敵をクリック位置に出す |
| `spawnWorker` / `spawnNPC` | 味方・人型の追加（**テスト用の敵 `id`・variant の早見表**は [`../COMBAT_PLAYTEST_POLICY.md`](../COMBAT_PLAYTEST_POLICY.md) の「敵 NPC 早見」） |
| `killEnemies` | マップ上の敵一掃 |
| `setWorkerStat` / `addExperience` | 射撃スキルやステータス調整 |
| `setHealth` / `setConsciousness` / `woundWorker` | 被弾・状態の操作 |
| `toggleInvulnerability` | 撃ち比べ用ターゲットの無敵切替 |
| `setDebugCombatTarget` | ターゲットギズモ用 |
| `dealDamage` | クリック対象にダメージ |
| `genRaidSpawnPoints` | 襲撃スポーン点の可視化・検証 |

詳細は `help <commandName>`（スクショ上の説明）で確認できる想定です。

---

## 品質スポーン（観察メモ・2026-04）

アイテム生成で選べる品質について、プレイ側のメモ（**正本はゲーム挙動**）。

- **「もろい」**だけスポーンできない例がある（それ以外は可能、という報告）。
- UI に **「可・良・優秀・最高」** しか見えない例があり、**「最高」≒ `productQuality` 6（チャート Q6）** とみなすと、見えている 4 段は **Q3～Q6** に相当し得る。
- **「もろい」は従来の「Q1」ではなく Q2（`productQuality` 2）の可能性** — データ上の Q1–Q6 と Dev 表示の対応は **[`../COMBAT_PLAYTEST_POLICY.md`](../COMBAT_PLAYTEST_POLICY.md)** の「DevTools と製作品質」を参照。

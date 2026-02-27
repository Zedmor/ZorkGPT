# Zork I: Complete Victory Report

## Final Result

| Metric | Value |
|---|---|
| **Final Score** | **350/350** |
| **Rank** | **Master Adventurer** |
| **Total Turns** | 604 |
| **Treasures Collected** | 19/19 |
| **Checkpoints Used** | ~15 (key restores: `pre-thief-hunt-2`, `325pts-17-treasures`) |

## All 19 Treasures (Deposit Order)

| # | Treasure | Source Location | Points (carry + case) |
|---|---|---|---|
| 1 | Bag of coins | Maze skeleton room (ID: 167) | 10 + 5 |
| 2 | Crystal trident | Atlantis (ID: 187) | 4 + 11 |
| 3 | Trunk of jewels | Reservoir (crossed by boat/drained) | 15 + 5 |
| 4 | Sceptre | Inside gold coffin (Egyptian Room, ID: 175) | 4 + 6 |
| 5 | Pot of gold | End of Rainbow (ID: 136) — wave sceptre | 10 + 10 |
| 6 | Crystal skull | Land of the Dead (ID: 230) — Hades ritual | 10 + 5 |
| 7 | Gold coffin | Egyptian Room (ID: 175) | 10 + 5 |
| 8 | Painting | Gallery (ID: 148) | 6 + 4 |
| 9 | Platinum bar | Loud Room (ID: 138) — say "echo" | 10 + 5 |
| 10 | Sapphire bracelet | Gas Room area (ID: 124) | 5 + 5 |
| 11 | Huge diamond | Machine Room (ID: 157) — coal transformation | 10 + 10 |
| 12 | Ivory torch | Torch Room (ID: 105) | 6 + 6 |
| 13 | Golden clockwork canary | Inside egg (opened by thief) | 6 + 4 |
| 14 | Jewel-encrusted egg | Up a Tree (ID: 88) | 5 + 5 |
| 15 | Jade figurine | Bat Room area (ID: 222) | 5 + 5 |
| 16 | Silver chalice | Treasure Room (ID: 190) — thief's lair | 5 + 5 |
| 17 | Brass bauble | Forest (ID: 77) — wind canary | 1 + 1 |
| 18 | Large emerald | Red buoy on Frigid River | 5 + 10 |
| 19 | Beautiful jeweled scarab | Sandy Cave (ID: 126) — dig 4 times | 5 + 5 |

**Bonus points:** Cellar first entry (+25), Treasure Room first visit (+25), Behind House window entry (+10).

## Session Narrative

### Phase 1: Coal-to-Diamond Puzzle (Turns 303-388)

Starting from Coal Mine 19 with coal in the basket at Drafty Room, the first major challenge was the Machine Room puzzle. After placing coal in the machine and closing the lid, the switch required a screwdriver — not the torch. This triggered a 70+ turn logistics operation:

1. Transported torch via basket to Shaft Room
2. Navigated empty-handed through narrow passage to Timber Room
3. Took lantern and garlic for underground travel
4. Traversed coal mines → Gas Room → Shaft Room → Bat Room (garlic prevents bat) → Mine Entrance → Slide Room → Cold Passage → Mirror Room → Cave → Atlantis → Reservoir → Dam → Dam Lobby → **Maintenance Room**
5. Retrieved screwdriver
6. Made the entire return journey, transported screwdriver via basket to Drafty Room
7. `turn switch with screwdriver` → machine activated → **huge diamond** (+10 pts)

**Lesson:** The Machine Room puzzle is the most logistically complex in the game, requiring an item from the opposite end of the underground.

### Phase 2: Treasure Transport to Surface (Turns 389-418)

Transported diamond, bracelet, torch, and other items from the underground to the trophy case via the basket mechanism and Slide Room shortcut. Deposited treasures to reach **268 points**.

### Phase 3: Thief and Egg-Opening Sequence (Turns 419-472)

The critical insight was that the jewel-encrusted egg can ONLY be opened by the thief. The first attempt failed — killed the thief but the egg was still in the trophy case, so no canary appeared.

**Successful strategy (after checkpoint restore):**
1. Took egg from trophy case, dropped it in the Cellar for the thief to steal
2. Navigated through maze to Cyclops Room: 70 → 69 → 68 → 167 → 64 → 63 → 52 → SE → Cyclops Room
3. Said "odysseus" to scare Cyclops (opens east wall — permanent shortcut to Living Room!)
4. Visited Treasure Room (+25 bonus) but fled immediately (don't kill thief yet)
5. Waited 15 turns for thief to find and open the egg
6. Returned to Treasure Room, killed thief (4 hits with knife)
7. Thief's treasures reappeared: **opened egg with golden clockwork canary inside**
8. Collected canary (+6), chalice (+5), figurine (+5)
9. Reached **298 points** at Living Room

### Phase 4: Final Treasures — Bauble, Emerald, Scarab (Turns 472-595)

After depositing the first 17 treasures (325 pts), three more were needed:

**Brass Bauble:**
- Took canary from case, went to Forest (ID: 77)
- `wind canary` → songbird appeared, dropped brass bauble (+2 total)

**Large Emerald (Frigid River expedition):**
- Discovered Dam Base (ID: 140) by scrambling down from Dam — found pile of plastic with valve
- Retrieved air pump from Cyclops Room (ID: 185) — 12 moves round trip
- Inflated plastic at Dam Base: `inflate plastic with pump` → magic boat
- Launched into Frigid River, drifted downstream
- Found red buoy on river, took it
- Landed on Sandy Beach (ID: 120)
- `open buoy` → **large emerald** (+15 total)

**Beautiful Jeweled Scarab:**
- At Sandy Beach, took shovel
- Went NE to Sandy Cave (ID: 126)
- `dig in sand` (4 times) → scarab uncovered
- Took scarab (+10 total)

**Return route:** Sandy Beach → Shore → Aragain Falls → cross rainbow → End of Rainbow → Canyon Bottom → Rocky Ledge → Canyon View → Clearing → Behind House → Kitchen → Living Room.

### Phase 5: Endgame (Turns 595-604)

Deposited all 19 treasures. On the final deposit (torch), the game whispered: *"Look to your treasures for the final secret."*

An **ancient parchment map** appeared in the trophy case. Reading it revealed a path to the Stone Barrow. Followed the secret path southwest from West of House to the Stone Barrow, entered, and:

> *"All ye who stand before this bridge have completed a great and perilous adventure which has tested your wit and courage. You have mastered the first part of the ZORK trilogy."*
>
> **Your score is 350 (total of 350 points). This gives you the rank of Master Adventurer.**

## Key Puzzle Solutions Discovered

### Coal-to-Diamond Machine (ID: 157)
```
open lid → put coal in machine → close lid → turn switch with screwdriver
```
Requires: coal (Coal Mine 19), screwdriver (Maintenance Room, ID: 199). Both must be transported via basket mechanism through the narrow passage.

### Cyclops Room (ID: 185)
```
say "odysseus"
```
Cyclops flees, permanently opens east wall to Strange Passage → Living Room shortcut.

### Thief Egg-Opening Mechanic
1. Drop egg somewhere underground
2. Wait 15+ turns for thief to steal and open it
3. Kill thief in Treasure Room → all items reappear, egg now contains canary

### Inflatable Boat & Frigid River
```
(at Dam Base) inflate plastic with pump → board boat → launch → wait (drift) → land
```
Pump location: Cyclops Room (ID: 185). Plastic location: Dam Base (ID: 140).

### Sandy Cave Scarab
```
(at Sandy Cave) dig in sand × 4 → take scarab
```
Requires shovel from Sandy Beach (ID: 120).

## Map Statistics

| Metric | Value |
|---|---|
| Rooms explored | 85+ |
| Total connections mapped | 210+ |
| New rooms discovered this session | Dam Base (140), White Cliffs Beach (33, 32), Sandy Beach (120), Sandy Cave (126), Shore (30), Aragain Falls (29), Stone Barrow (178) |

## Critical Route Knowledge

| Route | Path |
|---|---|
| Living Room ↔ Cyclops Room | West → Strange Passage → West (after Cyclops scared) |
| Dam → Dam Base | Scramble down |
| Frigid River access | Inflate boat at Dam Base → launch |
| Sandy Beach → Surface | South → Aragain Falls → cross rainbow → canyon climb → Clearing → Behind House |
| Altar → Surface | Pray → Forest (ID: 78) |
| Endgame | West of House → southwest → Stone Barrow → enter |

## Errors and Recovery

| Error | Impact | Recovery |
|---|---|---|
| Machine switch needs screwdriver (not torch) | 70+ turn detour | Retrieved from Maintenance Room via full underground traversal |
| First thief kill: no canary (egg in trophy case) | Wasted ~80 turns | Restored `pre-thief-hunt-2` checkpoint, used egg-drop strategy |
| Death by grue (thief stole torch) | -10 score penalty | Restored checkpoint, changed waiting strategy |
| Maze direction assumptions wrong from map data | ~10 wasted turns | Tried alternative directions systematically |

## Final Thoughts

Zork I's 350-point completion requires finding all 19 treasures scattered across 85+ rooms, solving interconnected puzzles that require items from distant locations, managing a complex logistics chain (basket mechanism, boat inflation, narrow passages), and understanding NPC behavior (thief opens egg). The game rewards thorough exploration, systematic experimentation, and strategic checkpoint management.

The most challenging aspects were:
1. **The coal-to-diamond logistics** — requiring screwdriver transport across the entire underground
2. **The thief/egg mechanic** — non-obvious that the thief is the ONLY way to open the egg
3. **The Frigid River expedition** — discovering Dam Base, finding the pump in the Cyclops Room, and the multi-step boat sequence
4. **Inventory management** — the narrow passage (empty hands only) and basket mechanism create constant logistics puzzles

**Game completed. Master Adventurer achieved. 350/350.**

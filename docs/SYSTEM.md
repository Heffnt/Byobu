# The Three Feifs Perfume System — frequencies, ingredients & perfumes as a graph

This document captures the **complete magical-frequency / perfume-brewing system**
reverse-engineered from the two source PDFs in this repository, validated against
their ground truth, and re-expressed as a graph.

- **`Magical Frequencies.pdf`** — the *Magical Frequency Guide* (I, II, III). Defines
  every frequency that can appear in an ingredient, and how each named frequency is
  built from simpler ones.
- **`TTF Ingredients.pdf`** — the *Ingredients Table*. 96 ingredients, each printed
  with a pill-shaped "barcode" of the frequencies it emits (and, for a few, wildcard
  markers).

Everything below is generated/validated by [`app/build_data.py`](../app/build_data.py),
which reads the PDFs' structure and exports [`app/data.json`](../app/data.json).

---

## 1. How the system was decoded (the workflow)

The PDFs are almost entirely **vector artwork** — the frequencies are drawn as
emblems and as colored circles holding letters, so a plain text-extract is
misleading (the letter glyphs are painted in the page's background color and only
become legible where a colored circle sits behind them; "phantom" template letters
with no circle are *not* real frequencies). The decode workflow was therefore:

1. **Render** every page to high-resolution images with PyMuPDF.
2. **Crop** each frequency/ingredient "barcode" and read it visually, slot by slot,
   distinguishing fundamental **letters** from named-frequency **emblems**.
3. **Cross-check** letters against the PDF text layer's glyph positions.
4. **Calibrate the model** against the one worked example we were given:
   *"a Potion of Healing is made with En, Crallax and two A — an Aphasia Flower and
   a Noble Roses."* The decoded data reproduces this exactly
   (`Aphasia Flower → {Crallax, En}` + `Noble Roses → {A, A}` = `{En, Crallax, A, A}`),
   which confirms the **atomic-token** reading of the mechanic below. (In the real
   recipe table this frequency profile is **Swana's Serum**, d40 roll 2.)
5. **Validate** the whole export programmatically: every reference resolves, the
   decomposition graph is acyclic, and every perfume recipe is craftable.

---

## 2. The model

A **brew** is just a *multiset of frequency tokens*. Each token is either a
fundamental or a named frequency — they are **atomic** for brewing (a named
frequency is not "unpacked" into its parts when matching a recipe; its decomposition
is structural lore, captured as the graph in §4).

- An **ingredient** contributes a fixed multiset of tokens (its `emits`), and may
  carry **wildcard markers**.
- The **brew** = the multiset sum of the `emits` of every ingredient added.
- A **recipe** (perfume) is defined by one or more target multisets of tokens —
  its **tunings**. Where the source table lists slashed ingredient alternatives
  that emit *different* frequencies, each resulting profile is a valid tuning of
  the same perfume. A brew **satisfies** a recipe when it can be made *exactly
  equal* to any one tuning. The listed ingredients are only the *common* recipe;
  any ingredients producing the same frequencies work.

### Wildcard markers

| Marker | Meaning | Where |
|---|---|---|
| **⊖ remove** | Remove one token of the brewer's choice from the brew. | Shadow Demon Liver ×2, Ennerx Core ×3, Sheensacks ×1 |
| **⊕ add** | Add one token of the brewer's choice to the brew. | Southollow Royal Tulip ×1 |

The ⊕ marker is rare and important: four legendary frequencies
(**Laternical, Malvesian, Thurmistic, Saspacian**) are emitted by *no* ingredient,
so the only way to place one in a brew is to manifest it with a ⊕.

### Matching rule (exactly what the app implements)

```
B  = multiset of brew tokens (sum of all emits)
M  = total ⊖ markers in the brew     P = total ⊕ markers in the brew
For a recipe R:
   excess  = B - R      (too many of these)   -> must be removed with ⊖
   missing = R - B      (recipe still needs)   -> must be added with ⊕
   PERFECT   if  B == R
   CRAFTABLE if  |excess| <= M  and  |missing| <= P
   otherwise: off by (excess, missing)
```

---

## 3. The fundamental frequencies (9)

Annotated with letters standing for the D&D schools of magic. Eight map to the
classic schools; a ninth tone, **`E`**, appears only in ingredients and never inside
a named frequency's recipe (note it floats free in the graph below).

| Letter | School | | Letter | School |
|---|---|---|---|---|
| `A` | Abjuration | | `Ev` | Evocation |
| `C` | Conjuration | | `I` | Illusion |
| `D` | Divination | | `N` | Necromancy |
| `En` | Enchantment | | `T` | Transmutation |
| `E` | (ninth tone — ingredient-only) | | | |

---

## 4. The frequency decomposition graph

Each named frequency is *defined* by the Guide as a multiset of simpler frequencies.
That makes the 9 fundamentals + 17 named frequencies a directed acyclic graph that
climbs from raw tones up to the masterwork **Saspacian**. The **weight** column is
how many fundamentals a frequency expands to in total (its depth/complexity);
Saspacian expands to **95**.

![Frequency decomposition graph](frequency_graph.png)

> Arrows point from a frequency **down to its components** (e.g. `Ignetium → Ev, Ev,
> En, C`). The four roots of the named layer (Ignetium, Crallax, Yonescope,
> Chrysipil) are pure fundamentals; everything else is built on top of them.

### Named frequencies (decomposition graph)

| Frequency | Emblem | Composed of | Fundamental weight |
|---|---|---|---|
| **Ignetium** | flame | Ev×2, En, C | 4 |
| **Crallax** | sparkle | D×2, A, C | 4 |
| **Yonescope** | moon | I, N×2, T | 4 |
| **Chrysipil** | crystal | A×2, D, T | 4 |
| **Letchettin** | skull | Yonescope, Ignetium, C×2 | 10 |
| **Silentix** | bell | Crallax×3, I | 13 |
| **Draconil** | lizard | Ignetium×2, En, Crallax | 13 |
| **Myddenic** | birdcage | T, Chrysipil×2, Yonescope | 13 |
| **Persimmious** | lotus | Letchettin, Chrysipil×2 | 18 |
| **Albutian** | potion | Myddenic×2, T | 27 |
| **Korastic** | meteor | Draconil, Ignetium, Crallax | 21 |
| **Lythillious** | dagger | Silentix, Yonescope, N | 18 |
| **Malvesian** | mirror | Albutian, Lythillious | 45 |
| **Laternical** | lantern | Persimmious, Korastic | 39 |
| **Thurmistic** | bolt | Yonescope, Korastic | 25 |
| **Ontoligin** | scroll | Albutian, Chrysipil | 31 |
| **Saspacian** | planet | Laternical, Thurmistic, Ontoligin | 95 |

---

## 5. The ingredients (96)

Grouped into 12 plates in the source. Most emit two tokens; "Core"-type reagents and
gems vary from one to three; four ingredients carry only wildcard markers.

### Ingredients (96) — what each emits

| # | Ingredient | Emits | Markers |
|---|---|---|---|
| 1 | Ichorberries | N, En | — |
| 2 | Thistle Goblin Tooth | C, Yonescope | — |
| 3 | Blistermoss | T, Ev | — |
| 4 | Aphasia Flower | Crallax, En | — |
| 5 | Noble Roses | A×2 | — |
| 6 | Wailing Thrush Egg | Myddenic, En | — |
| 7 | Mourningweep | En, N | — |
| 8 | Shadow Demon Liver | — | ⊖×2 |
| 9 | Bitterhearts | N, D | — |
| 10 | Olgrumast Mushroom | I, A | — |
| 11 | Fjeldling Scale | Draconil, Ignetium | — |
| 12 | Northman's Beard | Ignetium, C | — |
| 13 | Pepperpops | Ev×2 | — |
| 14 | Banshee's Hair | N, T | — |
| 15 | Razorclam Pearl | Silentix, N | — |
| 16 | Brightflower (printed "Bright") | Ev, En | — |
| 17 | Sheensacks | — | ⊖×1 |
| 18 | Moonchalk | D, I | — |
| 19 | Ferrenocht Crystals | N, A | — |
| 20 | Redcaps | En×2 | — |
| 21 | Owlbear Saliva | C, Silentix | — |
| 22 | Elves Ear | D, A | — |
| 23 | Bulezau Horn | Letchettin, D | — |
| 24 | Bubble Blossoms | Chrysipil, En | — |
| 25 | Glitterflies | T, D | — |
| 26 | Great Cold Shard | Albutian, T | — |
| 27 | Pemneath Peat | N×2 | — |
| 28 | Blood Demon Eye | Letchettin, Ev | — |
| 29 | Jotuun Heart | A, Silentix | — |
| 30 | Cloud Lavender | C, T | — |
| 31 | Undead Heart | Myddenic, N | — |
| 32 | Melting Dewdrops | Chrysipil, N | — |
| 33 | Icecap Crabs | A×2 | — |
| 34 | Lady's Gold | Korastic, Ignetium | — |
| 35 | Weird Dog Foot | D, Ev | — |
| 36 | Sanguipoles | Ignetium, N | — |
| 37 | Quickfish | D, Crallax | — |
| 38 | Green Dragon Venom | Lythillious, Draconil | — |
| 39 | Mandrake | Yonescope, N | — |
| 40 | Ionillic Eggs | Yonescope, En | — |
| 41 | Oracite | D×3 | — |
| 42 | Lumpkins | C, I | — |
| 43 | Hyannis Syrup | D, Ev | — |
| 44 | Tekachapi Berries | Ignetium, N | — |
| 45 | Amiglia Core | Chrysipil×2, Ignetium | — |
| 46 | Flumph Core | Chrysipil×2, Crallax | — |
| 47 | Ennerx Core | — | ⊖×3 |
| 48 | Lemiwinkles | C×2 | — |
| 49 | Klyst | A, T, Silentix | — |
| 50 | Aurum | A, Draconil | — |
| 51 | Deadly Moonbloom | Ev, I | — |
| 52 | Rindergrapes | Ignetium, I | — |
| 53 | Mara Nur Cap | Chrysipil, E, C | — |
| 54 | Glass | Chrysipil, Letchettin | — |
| 55 | Evengeist Ear | N, C | — |
| 56 | Arcanavore Organ | Myddenic, Crallax | — |
| 57 | Ogre Hand | Letchettin | — |
| 58 | Katowician Honeyhive | T×2 | — |
| 59 | Sphynx Paw | Ev, Ontoligin | — |
| 60 | Wraith Whisps | Ignetium, Yonescope | — |
| 61 | Creeping Coriand | E, T | — |
| 62 | Seacursed Scale | C, T | — |
| 63 | Lake Gar Eye | Ev, C | — |
| 64 | Fulmiles | Ignetium, C | — |
| 65 | Goat Fat | A | — |
| 66 | Golden Trilobite | A, Yonescope | — |
| 67 | Trihorn | Ev, I | — |
| 68 | Chromatic Corpustules | Ignetium, I | — |
| 69 | Penchant Jellies | Korastic, E, D | — |
| 70 | Bramblechoke | Letchettin×2 | — |
| 71 | Scourge of the Inlet | T, D | — |
| 72 | Brain Lemming | Myddenic, E | — |
| 73 | Sevan Lotus | A, E, Persimmious | — |
| 74 | Southollow Royal Tulip | — | ⊕×1 |
| 75 | Treakbug | Ev, I | — |
| 76 | Sanguivore Organ | Lythillious, I | — |
| 77 | Baleful Rockfish | Chrysipil, E, C | — |
| 78 | Verdaux | E, En | — |
| 79 | Rotgulp Eggs | N, Silentix | — |
| 80 | Spearfisher Horns | A, Yonescope | — |
| 81 | Great Owl Egg | C, I, Silentix | — |
| 82 | Amber | T, Ignetium | — |
| 83 | Dwarf Tubers | C, Chrysipil | — |
| 84 | Symbiotic Barnacles | Ev, Korastic | — |
| 85 | Ooze Cube | T, E, N | — |
| 86 | Lornlarch | Ignetium, Letchettin | — |
| 87 | Cave Spider Venom | N, Ignetium | — |
| 88 | Stasis Muck | Albutian, T | — |
| 89 | Amethyst | A, T | — |
| 90 | Emerald | En, C | — |
| 91 | Sapphire | D, Ev | — |
| 92 | Ruby | A, Ev | — |
| 93 | Silver | C | — |
| 94 | Gold | T | — |
| 95 | Chrythsmeum | D | — |
| 96 | Platinum | A | — |

---

## 6. The perfume recipe book (41)

The real **d40 common-recipes table** from the source lore. Each roll names a
perfume and the *common* pair of ingredients used to brew it — but the recipe
itself is **defined by the frequencies** those ingredients emit, so any other
combination that reaches the same profile also works. Notes:

- A slash in the source (`A / B`) means either ingredient may be used. Where the
  alternatives emit **different** frequencies, each profile is a separate valid
  **tuning** of the same perfume.
- **Roll 16 is two recipes**: a Brightflower alone gives **Bright**; adding a
  Northman's Beard tips it into **Frenzy**.
- **Black Gas** is the one wildcard recipe: Shadow Demon Liver emits nothing but
  carries ⊖×2, which strips the off-tone from either berry — both listed combos
  land on the single Necromancy note that *is* Black Gas.
- *Were-Elk Antler* (Hag's Tincture) appears in the lore table but not in the
  Ingredients Table; the math uses the Bulezau Horn alternative (marked \*).
- Tiers are by the heaviest tuning's fundamental weight: **simple** ≤ 8,
  **advanced** ≤ 20, **legendary** > 20.

### Perfume recipe book (41)

| d40 | Perfume | Tier | Frequencies required (any tuning) | Common recipe |
|---|---|---|---|---|
| 1 | **Corpse Gas** | simple | C, Yonescope, T, Ev | Thistle Goblin Tooth + Blistermoss |
| 2 | **Swana's Serum** | simple | Crallax, En, A×2 | Aphasia Flower + Noble Roses |
| 3 | **Mourningweep Oil** | advanced | Myddenic, En×2, N | Wailing Thrush Egg + Mourningweep |
| 4 | **Black Gas** | simple | N | Shadow Demon Liver + Ichorberries / Bitterhearts |
| 5 | **Pepperpop Mixture** | advanced | Draconil, Ignetium, Ev×2 *or* Ignetium, C, Ev×2 | Fjeldling Scale / Northman's Beard + Pepperpops |
| 6 | **Saltpearl Spray** | advanced | N×2, T, Silentix | Banshee's Hair + Razorclam Pearl |
| 7 | **Auroniel's Aroma** | simple | D, I, Ev, En | Moonchalk + Brightflower |
| 8 | **Mindlock Mixture** | simple | N, A, En×2 | Ferrenocht Crystals + Redcaps |
| 9 | **Owlbear Pheromones** | advanced | C, Silentix, D, A | Owlbear Saliva + Elves Ear |
| 10 | **Hag's Tincture** | advanced | Letchettin, D, Chrysipil, En | Were-Elk Antler\* / Bulezau Horn + Bubble Blossoms |
| 11 | **Calming Cologne** | simple | Crallax, En, T, D | Aphasia Flower + Glitterflies |
| 12 | **Pensive Perfume** | legendary | Albutian, T, Chrysipil, N | Great Cold Shard + Melting Dewdrops |
| 13 | **Slippery Serum** | advanced | A×2, D, Crallax *or* A×2, D, I *or* A, Silentix, D, Crallax *or* A, Silentix, D, I | Icecap Crabs / Jotuun Heart + Quickfish / Moonchalk |
| 14 | **Solemn Stink** | advanced | Letchettin, D, N×2 *or* Myddenic, N×3 | Bulezau Horn / Undead Heart + Pemneath Peat |
| 15 | **Ghostwalk Grog** | simple | A×2, C, T *or* Yonescope, En, C, T | Icecap Crabs / Ionillic Eggs + Cloud Lavender |
| 16 | **Bright** | simple | Ev, En | Brightflower |
| 16 | **Frenzy** | simple | Ignetium, C, Ev, En | Northman's Beard + Brightflower |
| 17 | **Second Spark** | legendary | Letchettin, Ev, Korastic, Ignetium | Blood Demon Eye + Lady's Gold |
| 18 | **Potion of Peril** | legendary | Lythillious, Draconil, T, Ev | Green Dragon Venom + Blistermoss |
| 19 | **Magnis Mixture** | simple | Yonescope, En, A | Ionillic Eggs + Platinum |
| 20 | **Ox Odor** | advanced | C, Chrysipil, Letchettin | Dwarf Tubers + Ogre Hand |
| 21 | **Frenetic Fragrance** | advanced | En×2, Ignetium, Letchettin | Redcaps + Lornlarch |
| 22 | **Dribbleblight Draught** | advanced | Ignetium, I, Myddenic, N *or* Ignetium, I, Yonescope, N | Rindergrapes + Undead Heart / Mandrake |
| 23 | **Griminal Gas** | simple | Yonescope, N×2, T | Mandrake + Banshee's Hair |
| 24 | **Regenerative Reek** | simple | Chrysipil, E, C, T, Ev | Mara Nur Cap + Blistermoss |
| 25 | **Bombastic Brew** | simple | C×2, T, D | Lemiwinkles + Glitterflies |
| 26 | **Redroot Derivative** | legendary | E, T, Lythillious, I *or* E, T, Ignetium, N *or* T×2, Lythillious, I *or* T×2, Ignetium, N | Creeping Coriand / Katowician Honeyhive + Sanguivore Organ / Sanguipoles |
| 27 | **Shimmerskin Succulence** | advanced | Ev, I, D×3 *or* Ev, I, A, T, Silentix | Trihorn + Oracite / Klyst |
| 28 | **Parasitic Perfume** | legendary | N, Silentix, Ev, I *or* N, Silentix, Ev, Korastic | Rotgulp Eggs + Treakbug / Symbiotic Barnacles |
| 29 | **Awakening Auroma** | simple | D×2, Ev, T | Weird Dog Foot + Scourge of the Inlet |
| 30 | **Liquidation Liquer** | legendary | T×2, E, N, Albutian | Ooze Cube + Stasis Muck |
| 31 | **Antimagic Auroma** | legendary | Myddenic, Crallax, C, T *or* Myddenic×2, Crallax×2 *or* D×4, C, T *or* D×4, Myddenic, Crallax | Arcanavore Organ / Chrythsmeum ×4 + Seacursed Scale / Arcanavore Organ |
| 32 | **Energestic Emulsion** | advanced | Ignetium, C, A, Draconil | Fulmiles + Aurum |
| 33 | **Puppetry Perfumette** | legendary | Letchettin×2, Myddenic, E | Bramblechoke + Brain Lemming |
| 34 | **Invulnerability Ichor** | legendary | Korastic, E, D, A, Yonescope | Penchant Jellies + Golden Trilobite |
| 35 | **Nocturnal Nectar** | legendary | Ev, I, Albutian, T *or* Ev, I, N, C *or* Ev, I, C, T | Deadly Moonbloom + Great Cold Shard / Evengeist Ear / Cloud Lavender |
| 36 | **Histological Hairoil** | legendary | Ev, Ontoligin, Ignetium, Yonescope | Sphynx Paw + Wraith Whisps |
| 37 | **Redroot Deconcoctual Derivative** | legendary | A, E, Persimmious, Ignetium, N | Sevan Lotus + Tekachapi Berries |
| 38 | **Valuers Vapor** | advanced | A, Yonescope, T, Ignetium *or* A, Yonescope, T | Spearfisher Horns + Amber / Gold |
| 39 | **Greenery Gas** | advanced | E, En, Chrysipil, Letchettin | Verdaux + Glass |
| 40 | **Swimmer's Serum** | simple | Ev, C×2, Chrysipil, E | Lake Gar Eye + Baleful Rockfish |

The four **legendary frequencies** (Laternical, Malvesian, Thurmistic, Saspacian)
appear in *no* recipe — brewing one remains a ⊕-wildcard stunt rather than a
formula in the book.

---

## 7. The graph export

[`docs/graph.json`](graph.json) is a single typed graph over the **entire space** —
**163 nodes** (9 fundamentals, 17 named frequencies, 96 ingredients, 41 recipes) and
**482 edges**:

| Edge `rel` | From → To | Meaning |
|---|---|---|
| `decomposes_to` | named → frequency | the Guide's definition of a named frequency |
| `emits` | ingredient → frequency | an ingredient contributes this token |
| `requires` | recipe → frequency | a perfume calls for this token; recipes with several tunings carry a `tuning` index on each edge |

Node types: `fundamental`, `named`, `ingredient`, `recipe`. This is the
machine-readable form of everything in this document, suitable for loading into any
graph tool.

---

## 8. The brewing bench (interactive)

[`app/index.html`](../app/index.html) is a standalone page (no server needed — open
it directly) where you can combine ingredients, watch the frequency tally of your
brew assemble in real time, spend ⊖/⊕ wildcards, and see which of the 41 perfumes
your brew satisfies. See [`app/SPEC.md`](../app/SPEC.md) for the build brief.

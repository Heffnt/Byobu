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
   which confirms the **atomic-token** reading of the mechanic below.
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
- A **recipe** (perfume) is a target multiset of tokens. A brew **satisfies** a
  recipe when it can be made *exactly equal* to the target.

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
| 16 | Bright | Ev, En | — |
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

## 6. The perfume recipe book (19)

A theoretical but **fully craftable** set, designed to exercise as many different
frequencies and ingredients as possible. Tiers:

- **simple** — one or two ingredients, exact match, no wildcards.
- **advanced** — needs ⊖ trimming (Shadow Demon Liver / Ennerx Core / Sheensacks).
- **legendary** — calls for a frequency no ingredient emits; needs the ⊕ of a
  Southollow Royal Tulip to manifest it.

### Perfume recipe book (19)

| Perfume | School | Tier | Requires | Example craft |
|---|---|---|---|---|
| **Potion of Healing** | Restoration | simple | En, Crallax, A×2 | Aphasia Flower, Noble Roses |
| **Draught of Invisibility** | Illusion | advanced | I×2, Yonescope | Thistle Goblin Tooth, Olgrumast Mushroom, Moonchalk, Ennerx Core |
| **Elixir of Fire Breath** | Evocation | advanced | Ignetium, Ev×2 | Shadow Demon Liver, Fjeldling Scale, Pepperpops |
| **Oil of Feather Fall** | Abjuration | simple | A×3 | Noble Roses, Goat Fat |
| **Tincture of True Sight** | Divination | simple | D×3 | Oracite |
| **Veil of Silence** | Enchantment | simple | Silentix, N | Razorclam Pearl |
| **Balm of Dragonhide** | Transmutation | advanced | Draconil, T, Ev | Blistermoss, Shadow Demon Liver, Fjeldling Scale |
| **Spectral Lantern Perfume** | Conjuration | legendary | Laternical | Southollow Royal Tulip |
| **Mindward Mist** | Abjuration | advanced | Myddenic, C, A | Wailing Thrush Egg, Shadow Demon Liver, Goat Fat, Silver |
| **Stormcaller's Cologne** | Evocation | legendary | Thurmistic, N×2 | Pemneath Peat, Southollow Royal Tulip |
| **Moonlit Reverie** | Divination | advanced | Yonescope×2, C | Thistle Goblin Tooth, Shadow Demon Liver, Mandrake |
| **Bloomheart Attar** | Restoration | advanced | Persimmious, En×2 | Shadow Demon Liver, Redcaps, Sevan Lotus |
| **Mirror-Self Essence** | Illusion | legendary | Malvesian, I | Shadow Demon Liver, Olgrumast Mushroom, Southollow Royal Tulip |
| **Cosmic Saspacian No. 5** | Universal | legendary | Saspacian | Southollow Royal Tulip |
| **Emberward Eau** | Evocation | simple | Korastic, Ev, C | Symbiotic Barnacles, Silver |
| **Gravebind Anointment** | Necromancy | advanced | N×4 | Ichorberries, Mourningweep, Shadow Demon Liver, Pemneath Peat |
| **Prismatic Chrysipil Spritz** | Transmutation | advanced | Chrysipil×2, T | Shadow Demon Liver, Amiglia Core, Gold |
| **Echo of the Deep** | Conjuration | simple | Ontoligin, Ev | Sphynx Paw |
| **Verdigris Veil** | Evocation | simple | Chrysipil, E, C | Mara Nur Cap |

---

## 7. The graph export

[`docs/graph.json`](graph.json) is a single typed graph over the **entire space** —
**141 nodes** (9 fundamentals, 17 named frequencies, 96 ingredients, 19 recipes) and
**295 edges**:

| Edge `rel` | From → To | Meaning |
|---|---|---|
| `decomposes_to` | named → frequency | the Guide's definition of a named frequency |
| `emits` | ingredient → frequency | an ingredient contributes this token |
| `requires` | recipe → frequency | a perfume calls for this token |

Node types: `fundamental`, `named`, `ingredient`, `recipe`. This is the
machine-readable form of everything in this document, suitable for loading into any
graph tool.

---

## 8. The brewing bench (interactive)

[`app/index.html`](../app/index.html) is a standalone page (no server needed — open
it directly) where you can combine ingredients, watch the frequency tally of your
brew assemble in real time, spend ⊖/⊕ wildcards, and see which of the 19 perfumes
your brew satisfies. See [`app/SPEC.md`](../app/SPEC.md) for the build brief.

# Three Feifs — Magical Perfumery System

A complete, PDF-validated model of the magical-frequency / perfume-brewing system
described in **`Magical Frequencies.pdf`** (the *Magical Frequency Guide*, 3 pages)
and **`TTF Ingredients.pdf`** (the *Ingredients Table*, 12 pages), plus an
interactive brewing app (`perfume-lab.html`).

> TL;DR — Ingredients emit **magical frequencies**. Frequencies form a layered
> graph: 8 **fundamental** frequencies (the D&D schools of magic) at the bottom,
> 17 **named** frequencies built from them, up to a single apex (*Saspacian*).
> A **perfume recipe** is an exact multiset of frequencies; you satisfy it by
> combining ingredients (and trimming/adding with ± wildcard ingredients).

---

## 1. The frequency space

### 1a. Fundamental frequencies (8 + 1)
The fundamentals are annotated with **letters** instead of a symbol; each letter is
a **D&D school of magic**:

| Letter | School | | Letter | School |
|---|---|---|---|---|
| `A`  | Abjuration  | | `Ev` | Evocation |
| `C`  | Conjuration | | `I`  | Illusion |
| `D`  | Divination  | | `N`  | Necromancy |
| `En` | Enchantment | | `T`  | Transmutation |

A bare **`E`** also appears on a handful of ingredient cards (e.g. *Mara Nur Cap*,
*Verdaux*, *Ooze Cube*). It is shown as a bare letter, distinct from `En`/`Ev`, so it
is preserved verbatim as a 9th token ("Essence") to stay faithful to the source.

### 1b. Named frequencies (17)
Every named frequency has a **heraldic symbol** and is **defined as a small multiset
of sub-frequencies** in the Guide (children may be fundamentals *or* other named
frequencies). This makes the frequency space a **directed acyclic graph (DAG)**:

| Tier | Frequency | Symbol | Direct composition |
|---|---|---|---|
| 1 | Ignetium   | 🔥 flame     | Ev, Ev, En, C |
| 1 | Crallax    | ✦ sparkle    | D, D, A, C |
| 1 | Yonescope  | 🌙 moon      | I, N, N, T |
| 1 | Chrysipil  | 💎 crystal   | A, A, D, T |
| 2 | Letchettin | 🐂 bull      | Yonescope, Ignetium, C, C |
| 2 | Silentix   | 🔔 bell      | Crallax, Crallax, Crallax, I |
| 2 | Draconil   | 🐉 seahorse  | Ignetium, En, Ignetium, Crallax |
| 2 | Myddenic   | 🦜 birdcage  | T, Chrysipil, Chrysipil, Yonescope |
| 3 | Persimmious| 🪷 lotus     | Letchettin, Chrysipil, Chrysipil |
| 3 | Albutian   | ⚗️ potion    | Myddenic, Myddenic, T |
| 3 | Korastic   | ☄️ comet     | Draconil, Ignetium, Crallax |
| 3 | Lythillious| 🗡️ dagger    | Silentix, Yonescope, N |
| 4 | Malvesian  | 🪞 mirror    | Albutian, Lythillious |
| 4 | Laternical | 🏮 lantern   | Persimmious, Korastic |
| 4 | Thurmistic | ⚡ lightning | Yonescope, Korastic |
| 4 | Ontoligin  | 📜 scroll    | Albutian, Persimmious |
| 5 | Saspacian  | 🪐 planet    | Laternical, Thurmistic, Ontoligin |

**Fundamental spectrum.** Recursively expanding any named frequency to the leaves
yields its *spectrum* (a multiset of fundamentals). Examples:

- `Ignetium` → `{C×1, En×1, Ev×2}` (4 fundamentals)
- `Albutian` → `{A×8, D×4, I×2, N×4, T×9}` (27)
- **`Saspacian`** → `{A×20, C×16, D×16, En×10, Ev×16, I×5, N×10, T×16}` — **109 fundamentals**, the deepest harmonic in the whole guide.

---

## 2. Ingredients (96)

12 pages × 8 = **96 ingredients**, each emitting a small multiset of frequencies
(named symbols and/or fundamental letters). Three special mechanics were found:

- **Minus pills (⊖)** — "remove any one frequency of your choice" from the brew.
  *Sheensacks* (×1), *Shadow Demon Liver* (×2), *Ennerx Core* (×3).
- **Plus pill (⊕)** — "add any one frequency of your choice" to the brew.
  *Southollow Royal Tulip* (×1).
- The page-12 **gems** are pure fundamentals: *Silver*=C, *Gold*=T,
  *Chrythsmeum*=D, *Platinum*=A (and double-gems Amethyst/Emerald/Sapphire/Ruby).

The ± wildcards are what give the brewer "more control over the perfume recipe."

**Obtainable vs. legendary.** 13 of the 17 named frequencies are emitted by at least
one ingredient. The four apex frequencies — **Malvesian, Laternical, Thurmistic,
Saspacian** — appear in the Guide but are emitted by *no* ingredient, so they are
**theoretical / legendary**: they exist in the harmonic graph but cannot (yet) be put
in a brew. A nice in-world hook for unattainable masterwork perfumes.

---

## 3. Perfumes / potion recipes

A **recipe** is a target **multiset of surface frequencies** (named freqs are atomic
units, exactly as the canonical example states):

> *Healing Draught* = the fundamentals **En**, **A**, **A**, plus **Crallax** —
> craftable from one **Aphasia Flower** (Crallax, En) + one **Noble Roses** (A, A).

A brew **satisfies** a recipe when the brew's surface-frequency multiset, after any
chosen ± wildcard adjustments, **exactly equals** the recipe's target.

This repo ships **17 verified-craftable recipes** (`data/recipes.json`) spanning 35
distinct ingredients and 21 distinct frequencies, including three that showcase the
wildcard mechanics (*Purified Ember*, *Hollowed Essence*, *Gilded Trinity*).

---

## 4. Graph representation (the model)

Everything is one heterogeneous graph (`data/dataset.json → graph`,
**139 nodes / 293 edges**):

```
 nodes:  fundamental (9)   named (17)   ingredient (96)   recipe (17)
 edges:  named  --composes--> child freq        (the frequency DAG)
         ingr   --emits-----> freq              (what an ingredient contributes)
         recipe --requires--> freq (×count)     (what a perfume needs)
```

- The **composes** edges form the strict DAG of frequencies (tier 0 → tier 5).
- The **emits** edges connect the 96 ingredients into the frequency layer.
- The **requires** edges connect perfumes back down to the frequencies — so a recipe
  is "reachable" iff every required frequency is reachable from some ingredient.

![Magical Frequency Composition Graph](docs/frequency-graph.svg)

Querying this graph answers the system's core questions:
*what's in my brew?* (union of `emits`), *what does it decompose to?* (follow
`composes` to the leaves), and *what perfume did I make?* (match the brew multiset
against `requires`).

---

## 5. Validation against ground truth

The PDFs are **vector diagrams** (cards with a symbol + a row of frequency "pills"),
so the data was extracted by rendering every page at high resolution and reading each
card visually, then cross-checked against the PDFs' embedded text layer. A
per-ingredient **contact sheet** (real pill-row crop beside the decoded value) was
generated and reviewed for **all 96 ingredients + all 24 frequency cards** — every
entry matches. A build script re-validates that the frequency graph is acyclic, that
all references resolve, and that all 17 recipes are craftable (`errors: 0`).

---

## 6. Files

| File | What |
|---|---|
| `perfume-lab.html` | Self-contained brewing app (open in any browser, no server). |
| `data/dataset.json` | Consolidated model the app embeds (schools, named, ingredients, recipes, graph). |
| `data/perfume_data.json` | Raw fundamentals / named (with spectra) / ingredients. |
| `data/recipes.json` | The 17 verified recipes. |
| `Magical Frequencies.pdf`, `TTF Ingredients.pdf` | Original ground-truth sources. |

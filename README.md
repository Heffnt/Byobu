# Byobu — Three Feifs Magical Perfumery

A PDF-validated model of the *Three Feifs* magical-frequency / perfume-brewing system,
plus an interactive brewing lab you can open in a browser.

## Quick start
Open **[`perfume-lab.html`](perfume-lab.html)** in any browser (no server, no internet
needed). Add ingredients to the cauldron, watch the magical frequencies of your brew,
and see which perfume recipe you've satisfied.

## What's here
| File | What |
|---|---|
| [`perfume-lab.html`](perfume-lab.html) | Self-contained brewing app: ingredient shelf → cauldron → live brew frequencies → matched recipe, a fundamental-spectrum analysis, a Frequency Codex, and an interactive graph (Harmonic Atlas). |
| [`PERFUME_SYSTEM.md`](PERFUME_SYSTEM.md) | Full writeup of the system: the frequency graph, ingredients, recipes, and how it was validated against the PDFs. |
| [`docs/frequency-graph.svg`](docs/frequency-graph.svg) | The frequency composition DAG (fundamentals → named → apex). |
| `data/dataset.json` | Consolidated model the app embeds (schools, named freqs, 96 ingredients, recipes, graph). |
| `data/perfume_data.json`, `data/recipes.json` | Raw frequency/ingredient data and the 17 verified recipes. |
| `Magical Frequencies.pdf`, `TTF Ingredients.pdf` | Original ground-truth sources. |

## The system in one breath
**Ingredients** emit **magical frequencies**. There are **9 fundamental** frequencies
(the D&D schools of magic, written as letters) and **17 named** frequencies, each
*defined as a combination of simpler frequencies* — a layered graph rising from the
fundamentals up to the apex **Saspacian 🪐** (which expands to 109 fundamentals). A
**perfume** is an exact multiset of frequencies; you brew it by combining ingredients,
fine-tuning with ⊖ "remove" and ⊕ "add" wildcard ingredients.

See **[`PERFUME_SYSTEM.md`](PERFUME_SYSTEM.md)** for the full details.

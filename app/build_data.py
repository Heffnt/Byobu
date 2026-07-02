#!/usr/bin/env python3
"""Compile + validate the Three Feifs perfume-frequency system, then export data.json.
Ground truth read directly from 'Magical Frequencies.pdf' and 'TTF Ingredients.pdf'."""
import json, itertools
from collections import Counter

# ---------------------------------------------------------------- fundamentals
# Fundamental frequencies are annotated with letters (D&D schools of magic).
FUNDAMENTALS = [
    ("A",  "Abjuration",   "#4F8DD6"),
    ("C",  "Conjuration",  "#E0A23B"),
    ("D",  "Divination",   "#5BC0EB"),
    ("E",  "Evocation*",   "#7E57C2"),   # a 9th letter observed in the ground truth
    ("En", "Enchantment",  "#C0392B"),
    ("Ev", "Evocation",    "#E8542E"),
    ("I",  "Illusion",     "#ECEFF1"),
    ("N",  "Necromancy",   "#2C2C34"),
    ("T",  "Transmutation","#27AE60"),
]
FUND_IDS = {f[0] for f in FUNDAMENTALS}

# ------------------------------------------------------- named frequencies (DAG)
# Each named frequency decomposes into a multiset of component frequencies,
# exactly as drawn in the Magical Frequency Guide barcodes.
NAMED = {
    # Guide I -- composed of fundamentals
    "Ignetium":   dict(icon="flame",   comps=["Ev","Ev","En","C"]),
    "Crallax":    dict(icon="sparkle", comps=["D","D","A","C"]),
    "Yonescope":  dict(icon="moon",    comps=["I","N","N","T"]),
    "Chrysipil":  dict(icon="crystal", comps=["A","A","D","T"]),
    # Guide I -- composed of other Guide-I frequencies + fundamentals
    "Letchettin": dict(icon="skull",   comps=["Yonescope","Ignetium","C","C"]),
    "Silentix":   dict(icon="bell",    comps=["Crallax","Crallax","Crallax","I"]),
    "Draconil":   dict(icon="lizard",  comps=["Ignetium","En","Ignetium","Crallax"]),
    "Myddenic":   dict(icon="cage",    comps=["T","Chrysipil","Chrysipil","Yonescope"]),
    # Guide II
    "Persimmious":dict(icon="lotus",   comps=["Letchettin","Chrysipil","Chrysipil"]),
    "Albutian":   dict(icon="potion",  comps=["Myddenic","Myddenic","T"]),
    "Korastic":   dict(icon="meteor",  comps=["Draconil","Ignetium","Crallax"]),
    "Lythillious":dict(icon="dagger",  comps=["Silentix","Yonescope","N"]),
    "Malvesian":  dict(icon="mirror",  comps=["Albutian","Lythillious"]),
    "Laternical": dict(icon="lantern", comps=["Persimmious","Korastic"]),
    "Thurmistic": dict(icon="bolt",    comps=["Yonescope","Korastic"]),
    "Ontoligin":  dict(icon="scroll",  comps=["Albutian","Chrysipil"]),
    # Guide III
    "Saspacian":  dict(icon="planet",  comps=["Laternical","Thurmistic","Ontoligin"]),
}

# ------------------------------------------------------------------ ingredients
# emits = multiset of frequency ids ; minus = wildcard removals ; plus = wildcard adds
ING = {
 # page 0
 "Ichorberries":["N","En"], "Thistle Goblin Tooth":["C","Yonescope"],
 "Blistermoss":["T","Ev"], "Aphasia Flower":["Crallax","En"],
 "Noble Roses":["A","A"], "Wailing Thrush Egg":["Myddenic","En"],
 "Mourningweep":["En","N"], "Shadow Demon Liver":{"minus":2},
 # page 1
 "Bitterhearts":["N","D"], "Olgrumast Mushroom":["I","A"],
 "Fjeldling Scale":["Draconil","Ignetium"], "Northman's Beard":["Ignetium","C"],
 "Pepperpops":["Ev","Ev"], "Banshee's Hair":["N","T"],
 "Razorclam Pearl":["Silentix","N"], "Brightflower":["Ev","En"],  # drawn as "Bright" in the PDF
 # page 2
 "Sheensacks":{"minus":1}, "Moonchalk":["D","I"],
 "Ferrenocht Crystals":["N","A"], "Redcaps":["En","En"],
 "Owlbear Saliva":["C","Silentix"], "Elves Ear":["D","A"],
 "Bulezau Horn":["Letchettin","D"], "Bubble Blossoms":["Chrysipil","En"],
 # page 3
 "Glitterflies":["T","D"], "Great Cold Shard":["Albutian","T"],
 "Pemneath Peat":["N","N"], "Blood Demon Eye":["Letchettin","Ev"],
 "Jotuun Heart":["A","Silentix"], "Cloud Lavender":["C","T"],
 "Undead Heart":["Myddenic","N"], "Melting Dewdrops":["Chrysipil","N"],
 # page 4
 "Icecap Crabs":["A","A"], "Lady's Gold":["Korastic","Ignetium"],
 "Weird Dog Foot":["D","Ev"], "Sanguipoles":["Ignetium","N"],
 "Quickfish":["D","Crallax"], "Green Dragon Venom":["Lythillious","Draconil"],
 "Mandrake":["Yonescope","N"], "Ionillic Eggs":["Yonescope","En"],
 # page 5
 "Oracite":["D","D","D"], "Lumpkins":["C","I"],
 "Hyannis Syrup":["D","Ev"], "Tekachapi Berries":["Ignetium","N"],
 "Amiglia Core":["Chrysipil","Chrysipil","Ignetium"],
 "Flumph Core":["Chrysipil","Chrysipil","Crallax"],
 "Ennerx Core":{"minus":3}, "Lemiwinkles":["C","C"],
 # page 6
 "Klyst":["A","T","Silentix"], "Aurum":["A","Draconil"],
 "Deadly Moonbloom":["Ev","I"], "Rindergrapes":["Ignetium","I"],
 "Mara Nur Cap":["Chrysipil","E","C"], "Glass":["Chrysipil","Letchettin"],
 "Evengeist Ear":["N","C"], "Arcanavore Organ":["Myddenic","Crallax"],
 # page 7
 "Ogre Hand":["Letchettin"], "Katowician Honeyhive":["T","T"],
 "Sphynx Paw":["Ev","Ontoligin"], "Wraith Whisps":["Ignetium","Yonescope"],
 "Creeping Coriand":["E","T"], "Seacursed Scale":["C","T"],
 "Lake Gar Eye":["Ev","C"], "Fulmiles":["Ignetium","C"],
 # page 8
 "Goat Fat":["A"], "Golden Trilobite":["A","Yonescope"],
 "Trihorn":["Ev","I"], "Chromatic Corpustules":["Ignetium","I"],
 "Penchant Jellies":["Korastic","E","D"], "Bramblechoke":["Letchettin","Letchettin"],
 "Scourge of the Inlet":["T","D"], "Brain Lemming":["Myddenic","E"],
 # page 9
 "Sevan Lotus":["A","E","Persimmious"], "Southollow Royal Tulip":{"plus":1},
 "Treakbug":["Ev","I"], "Sanguivore Organ":["Lythillious","I"],
 "Baleful Rockfish":["Chrysipil","E","C"], "Verdaux":["E","En"],
 "Rotgulp Eggs":["N","Silentix"], "Spearfisher Horns":["A","Yonescope"],
 # page 10
 "Great Owl Egg":["C","I","Silentix"], "Amber":["T","Ignetium"],
 "Dwarf Tubers":["C","Chrysipil"], "Symbiotic Barnacles":["Ev","Korastic"],
 "Ooze Cube":["T","E","N"], "Lornlarch":["Ignetium","Letchettin"],
 "Cave Spider Venom":["N","Ignetium"], "Stasis Muck":["Albutian","T"],
 # page 11 (gems & metals -- pure tones)
 "Amethyst":["A","T"], "Emerald":["En","C"], "Sapphire":["D","Ev"],
 "Ruby":["A","Ev"], "Silver":["C"], "Gold":["T"],
 "Chrythsmeum":["D"], "Platinum":["A"],
}
PAGE_OF = {}  # page index per ingredient, in declaration order groups of 8
order=list(ING.keys())
for i,name in enumerate(order):
    PAGE_OF[name]=i//8

import os
HERE = os.path.dirname(os.path.abspath(__file__))
COLORS = json.loads(open(os.path.join(HERE, "ing_colors.json"), encoding="utf-8-sig").read())

# ------------------------------------------------------------------- validation
ALL_FREQ = FUND_IDS | set(NAMED)
errors=[]
for n,d in NAMED.items():
    for c in d["comps"]:
        if c not in ALL_FREQ: errors.append(f"named {n} bad comp {c}")
for n,v in ING.items():
    if isinstance(v,list):
        for c in v:
            if c not in ALL_FREQ: errors.append(f"ingredient {n} bad freq {c}")

def expand(fid, seen=None):
    """flatten a frequency to a Counter of fundamentals (full DAG expansion)."""
    if fid in FUND_IDS: return Counter([fid])
    tot=Counter()
    for c in NAMED[fid]["comps"]:
        tot+=expand(c)
    return tot

# check for cycles / expandability
for n in NAMED:
    try: expand(n)
    except RecursionError: errors.append(f"cycle at {n}")

assert not errors, errors
print("VALIDATION ok: %d fundamentals, %d named freqs, %d ingredients"%(
    len(FUNDAMENTALS), len(NAMED), len(ING)))

# ground-truth healing example: Aphasia Flower + Noble Roses == {En, Crallax, A, A}
brew = Counter(ING["Aphasia Flower"]) + Counter(ING["Noble Roses"])
assert brew == Counter(["En","Crallax","A","A"]), brew
print("HEALING example verified: Aphasia Flower + Noble Roses =", dict(brew))

# fundamental "weight" of each named freq (total fundamentals it expands to)
for n in NAMED:
    NAMED[n]["expanded"]=dict(expand(n))
    NAMED[n]["weight"]=sum(expand(n).values())

# --------------------------------------------------------------------- recipes
# Ground truth: the d40 "common recipes" table. A recipe is DEFINED by frequency
# multisets; the listed ingredients are just the common way to reach them.
# Slot syntax: each recipe has ingredient slots; a slot lists alternatives
# ("either combo of frequencies can be used"). Entries:
#   "Name"          -> 1x that ingredient
#   ("Name", k)     -> k x that ingredient (e.g. Chrythsmeum x4)
#   "?Name"         -> named in the lore table but absent from the Ingredients
#                      Table; shown in the UI, excluded from the math.
# Every distinct frequency profile a combo produces becomes a valid requirement
# ("tuning") of the recipe. reqOverride pins the requirement instead (Black Gas:
# the Shadow Demon Liver's two removals strip the off-tone from either berry,
# so the perfume itself is the lone Necromancy note -- the only reading where
# both listed combos yield the same perfume and the liver isn't dead weight).
RECIPES = [
 dict(roll=1,  id="corpse-gas", name="Corpse Gas",
      desc="A miasma of the freshly turned grave. Crowds part; carrion birds follow.",
      slots=[["Thistle Goblin Tooth"],["Blistermoss"]]),
 dict(roll=2,  id="swanas-serum", name="Swana's Serum",
      desc="Swana's gentle restorative -- enchantment folded into a sparkling Crallax heart.",
      slots=[["Aphasia Flower"],["Noble Roses"]]),
 dict(roll=3,  id="mourningweep-oil", name="Mourningweep Oil",
      desc="Anoint the brow and grieve beautifully. Sorrow, doubled and bound in Necromancy.",
      slots=[["Wailing Thrush Egg"],["Mourningweep"]]),
 dict(roll=4,  id="black-gas", name="Black Gas",
      desc="The liver's hollows strip every stray tone away, leaving one pure necrotic note.",
      slots=[["Shadow Demon Liver"],["Ichorberries","Bitterhearts"]],
      reqOverride=["N"]),
 dict(roll=5,  id="pepperpop-mixture", name="Pepperpop Mixture",
      desc="Crackles on the skin like chewed embers. Sneeze fire, politely.",
      slots=[["Fjeldling Scale","Northman's Beard"],["Pepperpops"]]),
 dict(roll=6,  id="saltpearl-spray", name="Saltpearl Spray",
      desc="Brine, hush, and mother-of-pearl -- the quiet of the tide going out.",
      slots=[["Banshee's Hair"],["Razorclam Pearl"]]),
 dict(roll=7,  id="auroniels-aroma", name="Auroniel's Aroma",
      desc="Auroniel's own moonlit glamour; chalk-light over a warm bright bloom.",
      slots=[["Moonchalk"],["Brightflower"]]),
 dict(roll=8,  id="mindlock-mixture", name="Mindlock Mixture",
      desc="Twin enchantments bolted to cold iron thought. The mind stays shut.",
      slots=[["Ferrenocht Crystals"],["Redcaps"]]),
 dict(roll=9,  id="owlbear-pheromones", name="Owlbear Pheromones",
      desc="Irresistible to owlbears. Wear at your own considerable risk.",
      slots=[["Owlbear Saliva"],["Elves Ear"]]),
 dict(roll=10, id="hags-tincture", name="Hag's Tincture",
      desc="A crone's disguise in a bottle -- horn-musk sweetened with bubble blossom.",
      slots=[["?Were-Elk Antler","Bulezau Horn"],["Bubble Blossoms"]]),
 dict(roll=11, id="calming-cologne", name="Calming Cologne",
      desc="Glitterwing dust over aphasia bloom. The pulse slows; the words come easy.",
      slots=[["Aphasia Flower"],["Glitterflies"]]),
 dict(roll=12, id="pensive-perfume", name="Pensive Perfume",
      desc="Cold-shard clarity with a dewdrop melt. For long thoughts by short candles.",
      slots=[["Great Cold Shard"],["Melting Dewdrops"]]),
 dict(roll=13, id="slippery-serum", name="Slippery Serum",
      desc="Nothing grips the wearer -- not hands, not ropes, not consequences.",
      slots=[["Icecap Crabs","Jotuun Heart"],["Quickfish","Moonchalk"]]),
 dict(roll=14, id="solemn-stink", name="Solemn Stink",
      desc="Peat and old horn. Commands a funeral's gravity in any room.",
      slots=[["Bulezau Horn","Undead Heart"],["Pemneath Peat"]]),
 dict(roll=15, id="ghostwalk-grog", name="Ghostwalk Grog",
      desc="Lavender over cold stillness; the dead mistake you for weather.",
      slots=[["Icecap Crabs","Ionillic Eggs"],["Cloud Lavender"]]),
 dict(roll=16, id="bright", name="Bright",
      desc="A single brightflower, distilled. Radiance you can wear.",
      slots=[["Brightflower"]]),
 dict(roll=16, id="frenzy", name="Frenzy",
      desc="Brightflower stoked with a northman's fire-beard -- brilliance tipped into mania.",
      slots=[["Northman's Beard"],["Brightflower"]]),
 dict(roll=17, id="second-spark", name="Second Spark",
      desc="For engines, hearts, and arguments that have gone out. Reignition guaranteed.",
      slots=[["Blood Demon Eye"],["Lady's Gold"]]),
 dict(roll=18, id="potion-of-peril", name="Potion of Peril",
      desc="Dragon venom on a moss fuse. Handle with tongs and good insurance.",
      slots=[["Green Dragon Venom"],["Blistermoss"]]),
 dict(roll=19, id="magnis-mixture", name="Magnis Mixture",
      desc="Platinum-bound moon-pull. Small metal objects (and admirers) drift closer.",
      slots=[["Ionillic Eggs"],["Platinum"]]),
 dict(roll=20, id="ox-odor", name="Ox Odor",
      desc="Tuber starch and ogre grip. Smell like you can carry the cart yourself.",
      slots=[["Dwarf Tubers"],["Ogre Hand"]]),
 dict(roll=21, id="frenetic-fragrance", name="Frenetic Fragrance",
      desc="Redcap fury lashed to burning larch -- the nose's equivalent of a war drum.",
      slots=[["Redcaps"],["Lornlarch"]]),
 dict(roll=22, id="dribbleblight-draught", name="Dribbleblight Draught",
      desc="It drips. It blights. The scent arrives three seconds after the dread.",
      slots=[["Rindergrapes"],["Undead Heart","Mandrake"]]),
 dict(roll=23, id="griminal-gas", name="Griminal Gas",
      desc="Mandrake scream settled over banshee hair. Strictly graveside wear.",
      slots=[["Mandrake"],["Banshee's Hair"]]),
 dict(roll=24, id="regenerative-reek", name="Regenerative Reek",
      desc="Foul going on, marvelous coming off -- flesh knits under the stench.",
      slots=[["Mara Nur Cap"],["Blistermoss"]]),
 dict(roll=25, id="bombastic-brew", name="Bombastic Brew",
      desc="Twinned conjured winks with a glitter fuse. Loud in every language.",
      slots=[["Lemiwinkles"],["Glitterflies"]]),
 dict(roll=26, id="redroot-derivative", name="Redroot Derivative",
      desc="The sanguivore's table wine, rooted red and faintly pulsing.",
      slots=[["Creeping Coriand","Katowician Honeyhive"],["Sanguivore Organ","Sanguipoles"]]),
 dict(roll=27, id="shimmerskin-succulence", name="Shimmerskin Succulence",
      desc="Scales of light across the skin. Best applied under a full moon.",
      slots=[["Trihorn"],["Oracite","Klyst"]]),
 dict(roll=28, id="parasitic-perfume", name="Parasitic Perfume",
      desc="Symbiotes find you charming. Everything else finds you occupied.",
      slots=[["Rotgulp Eggs"],["Treakbug","Symbiotic Barnacles"]]),
 dict(roll=29, id="awakening-auroma", name="Awakening Auroma",
      desc="Smelling salts of the inlet -- divination doubled through a cold snap.",
      slots=[["Weird Dog Foot"],["Scourge of the Inlet"]]),
 dict(roll=30, id="liquidation-liquer", name="Liquidation Liquer",
      desc="Everything solid remembers it was once soup. Assets included.",
      slots=[["Ooze Cube"],["Stasis Muck"]]),
 dict(roll=31, id="antimagic-auroma", name="Antimagic Auroma",
      desc="A null-scent that eats spellwork; the arcanavore's hunger, bottled.",
      slots=[["Arcanavore Organ",("Chrythsmeum",4)],["Seacursed Scale","Arcanavore Organ"]]),
 dict(roll=32, id="energestic-emulsion", name="Energestic Emulsion",
      desc="Golden dragon-oil charged with fulmile spark. Vigor with a metallic bite.",
      slots=[["Fulmiles"],["Aurum"]]),
 dict(roll=33, id="puppetry-perfumette", name="Puppetry Perfumette",
      desc="A dab behind the ears -- theirs, not yours. Strings sold separately.",
      slots=[["Bramblechoke"],["Brain Lemming"]]),
 dict(roll=34, id="invulnerability-ichor", name="Invulnerability Ichor",
      desc="Trilobite patience in jellied meteor-fire. Blades change the subject.",
      slots=[["Penchant Jellies"],["Golden Trilobite"]]),
 dict(roll=35, id="nocturnal-nectar", name="Nocturnal Nectar",
      desc="The night in three vintages -- choose your darkness, wear till dawn.",
      slots=[["Deadly Moonbloom"],["Great Cold Shard","Evengeist Ear","Cloud Lavender"]]),
 dict(roll=36, id="histological-hairoil", name="Histological Hairoil",
      desc="Sphynx-blessed follicle scripture. Regrows what the wraiths whisked away.",
      slots=[["Sphynx Paw"],["Wraith Whisps"]]),
 dict(roll=37, id="redroot-deconcoctual", name="Redroot Deconcoctual Derivative",
      desc="The antidote's antidote -- lotus logic unwinding the redroot knot.",
      slots=[["Sevan Lotus"],["Tekachapi Berries"]]),
 dict(roll=38, id="valuers-vapor", name="Valuers Vapor",
      desc="One sniff prices anything: amber honesty against a golden hunch.",
      slots=[["Spearfisher Horns"],["Amber","Gold"]]),
 dict(roll=39, id="greenery-gas", name="Greenery Gas",
      desc="Glass-cut chlorophyll. Rooms sprout; ledgers turn over new leaves.",
      slots=[["Verdaux"],["Glass"]]),
 dict(roll=40, id="swimmers-serum", name="Swimmer's Serum",
      desc="Gar-eyed and rock-calm below the surface. Breathe easy; swim rude.",
      slots=[["Lake Gar Eye"],["Baleful Rockfish"]]),
]

# --------------------------------------------- compile slots -> reqs + combos
def norm_entry(e):
    if isinstance(e, tuple): return dict(name=e[0], qty=e[1], known=True)
    if e.startswith("?"):    return dict(name=e[1:], qty=1, known=False)
    return dict(name=e, qty=1, known=True)

def ing_stats(name, qty):
    v = ING[name]
    if isinstance(v, dict):
        return Counter(), v.get("minus",0)*qty, v.get("plus",0)*qty
    c = Counter()
    for _ in range(qty): c += Counter(v)
    return c, 0, 0

def satisfies(brew, minus, plus, req):
    """can brew (+/- wildcards) be made EXACTLY equal to req?"""
    excess  = brew - req
    deficit = req - brew
    return sum(excess.values())<=minus and sum(deficit.values())<=plus

print("\nCompiling %d common recipes:" % len(RECIPES))
for r in RECIPES:
    slots = [[norm_entry(e) for e in slot] for slot in r["slots"]]
    for slot in slots:
        for e in slot:
            if e["known"]:
                assert e["name"] in ING, f"{r['name']}: unknown ingredient {e['name']}"
        assert any(e["known"] for e in slot), f"{r['name']}: slot has no known ingredient"

    reqs = []           # distinct requirement multisets (as sorted token lists)
    req_keys = []       # frozenset-of-items keys for dedupe
    combos = []
    for pick in itertools.product(*[[e for e in slot if e["known"]] for slot in slots]):
        ings = []
        brew = Counter(); minus = 0; plus = 0
        for e in pick:
            ings += [e["name"]] * e["qty"]
            c, m, p = ing_stats(e["name"], e["qty"])
            brew += c; minus += m; plus += p
        req = Counter(r["reqOverride"]) if "reqOverride" in r else brew
        assert satisfies(brew, minus, plus, req), f"{r['name']}: combo {ings} cannot reach req"
        assert sum((req - brew).values()) == 0, f"{r['name']}: combo {ings} would need +wildcards"
        key = tuple(sorted(req.items()))
        if key not in req_keys:
            req_keys.append(key); reqs.append(sorted(req.elements()))
        combos.append(dict(ings=ings, req=req_keys.index(key),
                           trim=sum((brew - req).values()), wildAdd=0))

    w = max(sum(sum(expand(t).values()) for t in q) for q in reqs)
    r["tier"] = "simple" if w<=8 else ("advanced" if w<=20 else "legendary")
    r["reqs"] = reqs; r["combos"] = combos
    r["slotsOut"] = [[dict(name=e["name"], qty=e["qty"], known=e["known"]) for e in slot]
                     for slot in slots]
    print(f"  d40:{r['roll']:>2} {r['name']:32s} [{r['tier']:9s}] w{w:<3} "
          f"{len(reqs)} tuning(s), {len(combos)} combo(s)")

# sanity: the two Black Gas combos both land on the lone-N requirement
bg = next(r for r in RECIPES if r["id"]=="black-gas")
assert bg["reqs"] == [["N"]] and len(bg["combos"]) == 2
# sanity: Swana's Serum is the old healing profile
sw = next(r for r in RECIPES if r["id"]=="swanas-serum")
assert Counter(sw["reqs"][0]) == Counter(["En","Crallax","A","A"])
# sanity: Bright is a strict subset of Frenzy (adding Northman's Beard upgrades it)
br = next(r for r in RECIPES if r["id"]=="bright")
fz = next(r for r in RECIPES if r["id"]=="frenzy")
assert not (Counter(br["reqs"][0]) - Counter(fz["reqs"][0]))

# which named frequencies are emitted by NO ingredient? (the "legendary" tier)
emitted=set()
for v in ING.values():
    if isinstance(v,list): emitted|=set(v)
LEGENDARY_FREQ=sorted(set(NAMED)-emitted)
print("\nLegendary frequencies (emitted by no ingredient):",LEGENDARY_FREQ)

# ------------------------------------------------------------------ export json
out=dict(
  fundamentals=[dict(id=i,school=s,color=c) for i,s,c in FUNDAMENTALS],
  named=[dict(id=n, icon=d["icon"], components=d["comps"],
             expanded=d["expanded"], weight=d["weight"]) for n,d in NAMED.items()],
  ingredients=[],
  recipes=[dict(id=r["id"], roll=r["roll"], name=r["name"], desc=r["desc"],
                tier=r["tier"], slots=r["slotsOut"], reqs=r["reqs"],
                combos=r["combos"]) for r in RECIPES],
)
for n,v in ING.items():
    e=dict(name=n, page=PAGE_OF[n], color=COLORS.get(n,"#888888"))
    if isinstance(v,dict):
        e["emits"]=[]; e["minus"]=v.get("minus",0); e["plus"]=v.get("plus",0)
    else:
        e["emits"]=v; e["minus"]=0; e["plus"]=0
    out["ingredients"].append(e)

open(os.path.join(HERE, "data.json"),"w",encoding="utf-8").write(
    json.dumps(out,ensure_ascii=False,indent=1))
print("\nWrote data.json:",len(out["ingredients"]),"ingredients,",
      len(out["named"]),"named freqs,",len(out["recipes"]),"recipes")

# ------------------------------------------- embed DATA blob into index.html
html_path = os.path.join(HERE, "index.html")
if os.path.exists(html_path):
    html = open(html_path, encoding="utf-8").read()
    start = html.index("const DATA = ")
    end = html.index("\n};\n", start) + len("\n};\n")
    html = html[:start] + "const DATA = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n" + html[end:]
    open(html_path, "w", encoding="utf-8").write(html)
    print("Embedded DATA into index.html")

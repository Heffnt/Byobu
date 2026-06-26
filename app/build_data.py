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
 "Razorclam Pearl":["Silentix","N"], "Bright":["Ev","En"],
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
COLORS = json.loads(open(os.path.join(HERE, "ing_colors.json")).read())

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
# A recipe is a target multiset of frequency tokens (named or fundamental).
RECIPES = [
 dict(id="healing", name="Potion of Healing", school="Restoration",
      desc="The canonical brew. Soft enchantment bound to a glittering Crallax core.",
      req=["En","Crallax","A","A"]),
 dict(id="invis", name="Draught of Invisibility", school="Illusion",
      desc="Bends light around the wearer with a doubled Illusion resonance.",
      req=["I","I","Yonescope"]),
 dict(id="firebreath", name="Elixir of Fire Breath", school="Evocation",
      desc="A roaring Ignetium flame fed by raw Evocation.",
      req=["Ignetium","Ev","Ev"]),
 dict(id="featherfall", name="Oil of Feather Fall", school="Abjuration",
      desc="Three steady Abjuration tones lighten any fall.",
      req=["A","A","A"]),
 dict(id="truesight", name="Tincture of True Sight", school="Divination",
      desc="An Oracite-clear triple Divination that pierces illusion.",
      req=["D","D","D"]),
 dict(id="silence", name="Veil of Silence", school="Enchantment",
      desc="The Silentix bell, hushed and rung once in Necromantic stillness.",
      req=["Silentix","N"]),
 dict(id="dragonhide", name="Balm of Dragonhide", school="Transmutation",
      desc="Scales of Draconil tempered by a Transmutation sheen.",
      req=["Draconil","T","Ev"]),
 dict(id="spectral", name="Spectral Lantern Perfume", school="Conjuration",
      desc="A Laternical glow that summons guiding spirits.",
      req=["Laternical"]),
 dict(id="mindward", name="Mindward Mist", school="Abjuration",
      desc="A caged Myddenic ward against intrusion, sealed with Conjuration.",
      req=["Myddenic","C","A"]),
 dict(id="stormcall", name="Stormcaller's Cologne", school="Evocation",
      desc="Thurmistic thunder over a low Necromantic hum.",
      req=["Thurmistic","N","N"]),
 dict(id="moonlit", name="Moonlit Reverie", school="Divination",
      desc="Yonescope twilight folded into pure Conjuration.",
      req=["Yonescope","Yonescope","C"]),
 dict(id="bloomheart", name="Bloomheart Attar", school="Restoration",
      desc="A Persimmious lotus opening over warm Enchantment.",
      req=["Persimmious","En","En"]),
 dict(id="mirrorself", name="Mirror-Self Essence", school="Illusion",
      desc="The Malvesian mirror, doubled by a flicker of Illusion.",
      req=["Malvesian","I"]),
 dict(id="cosmic", name="Cosmic Saspacian No. 5", school="Universal",
      desc="The masterwork. A single Saspacian chord -- every Guide woven into one planet.",
      req=["Saspacian"]),
 dict(id="emberward", name="Emberward Eau", school="Evocation",
      desc="Korastic meteor-fire balanced on a knife of Evocation and Conjuration.",
      req=["Korastic","Ev","C"]),
 dict(id="gravebind", name="Gravebind Anointment", school="Necromancy",
      desc="Four Necromantic tolls to bind what should stay buried.",
      req=["N","N","N","N"]),
 dict(id="prism", name="Prismatic Chrysipil Spritz", school="Transmutation",
      desc="Two Chrysipil crystals refracted through a Transmutation prism.",
      req=["Chrysipil","Chrysipil","T"]),
 dict(id="echo", name="Echo of the Deep", school="Conjuration",
      desc="An Ontoligin scroll read aloud beneath an Evocation tide.",
      req=["Ontoligin","Ev"]),
 dict(id="verdigris", name="Verdigris Veil", school="Evocation",
      desc="A rare E-tone caged in Chrysipil crystal and Conjuration -- the Mara Nur signature.",
      req=["Chrysipil","E","C"]),
]

# ---------------------------------------------------------- solver / solvability
items=[]  # (name, Counter(emits), minus, plus)
for n,v in ING.items():
    if isinstance(v,dict):
        items.append((n,Counter(),v.get("minus",0),v.get("plus",0)))
    else:
        items.append((n,Counter(v),0,0))

def satisfies(brew, minus, plus, req):
    """can brew (+/- wildcards) be made EXACTLY equal to req?"""
    excess = brew - req           # tokens we have too many of -> must remove
    deficit = req - brew          # tokens we are missing -> must add
    return sum(excess.values())<=minus and sum(deficit.values())<=plus

REMOVERS=[it for it in items if it[2]>0 or it[3]>0]
def best_solution(req, max_items=4):
    """Find the craft using the fewest wildcard-additions, then fewest ingredients,
    then least trimming. Prefilters candidates for speed."""
    req=Counter(req); rset=set(req)
    cand=[it for it in items if (set(it[1])&rset) or it[2] or it[3]]
    best=None
    for k in range(1,max_items+1):
        fk=None
        for combo in itertools.combinations(range(len(cand)),k):
            brew=Counter(); minus=0; plus=0
            for idx in combo:
                brew+=cand[idx][1]; minus+=cand[idx][2]; plus+=cand[idx][3]
            ex=sum((brew-req).values()); df=sum((req-brew).values())
            if ex<=minus and df<=plus:
                sc=(df,k,ex)
                if fk is None or sc<fk[0]:
                    fk=(sc,[cand[idx][0] for idx in combo])
        if fk and (best is None or fk[0]<best[0]): best=fk
        if best and best[0][0]==0: break   # honest solution found
    return best

# which named frequencies are emitted by NO ingredient? (the "legendary" tier)
emitted=set()
for _,c,_,_ in items: emitted|=set(c)
LEGENDARY_FREQ=sorted(set(NAMED)-emitted)
print("\nLegendary frequencies (emitted by no ingredient):",LEGENDARY_FREQ)

print("\nRecipe solvability (HONEST = craftable with no +wildcard):")
for r in RECIPES:
    (df,k,ex),sol = best_solution(r["req"])
    r["example"]=sol; r["trim"]=ex; r["wildAdd"]=df
    r["tier"]= "legendary" if df>0 else ("simple" if (k<=2 and ex==0) else "advanced")
    tag="HONEST" if df==0 else f"LEGENDARY(+{df})"
    print(f"  {r['name']:30s} {tag:14s} k{k} trim{ex} [{r['tier']:9s}] | "+", ".join(sol))

unsolved=[r['name'] for r in RECIPES if not r.get('example')]
print("\nUnsolved:", unsolved or "none -- every recipe is craftable")

# ------------------------------------------------------------------ export json
out=dict(
  fundamentals=[dict(id=i,school=s,color=c) for i,s,c in FUNDAMENTALS],
  named=[dict(id=n, icon=d["icon"], components=d["comps"],
             expanded=d["expanded"], weight=d["weight"]) for n,d in NAMED.items()],
  ingredients=[],
  recipes=RECIPES,
)
for n,v in ING.items():
    e=dict(name=n, page=PAGE_OF[n], color=COLORS.get(n,"#888888"))
    if isinstance(v,dict):
        e["emits"]=[]; e["minus"]=v.get("minus",0); e["plus"]=v.get("plus",0)
    else:
        e["emits"]=v; e["minus"]=0; e["plus"]=0
    out["ingredients"].append(e)

open(os.path.join(HERE, "data.json"),"w").write(
    json.dumps(out,ensure_ascii=False,indent=1))
print("\nWrote data.json:",len(out["ingredients"]),"ingredients,",
      len(out["named"]),"named freqs,",len(out["recipes"]),"recipes")

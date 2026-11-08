"""Shared paths, groupings and helpers for the asteroid-towns study ("Towns with an asteroid").

Raw inputs (read in place, never modified):
  RAW   /home/claude/newdata/raw_new8/asteroid_names.tsv
        Wikidata, queried through QLever (CC0). One row per combination of: an asteroid (?a, label ?al; instance of or
        subclass of asteroid) with a "named after" (P138) statement, its minor planet number (?mpn), discoverer (P61,
        ?disc/?discl), discovery site (P65, ?site/?sitel) with its coordinates (?sitecoord) and country (?sitec/?sitecl),
        discovery date (P575, ?ddate), the namesake (?n/?nl) with, if a place, its coordinates (P625, ?ncoord) and
        country (P17, ?nc/?ncl), its type (P31, ?ntype/?ntypel) and, if a person, the birthplace's coordinates and
        country (?nbp, ?nbpcoord, ?nbpcl). Rows repeat for every discoverer and type; 01_clean.py deduplicates.
  LABELS /home/claude/newdata/raw_new8/asteroid_labels.tsv: each asteroid's multilingual label (?mul) and a label in
        any language (?label), Wikidata via QLever (CC0); names use mul, then English, then any label.
  GEO   /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson (Natural Earth, public domain): modern country,
        continent and population estimate (POP_EST) for each named place and observatory, by point in polygon.
  FONTS /home/claude/ref/fonts; INK /home/claude/studies/colour-names (js/, fonts/ and data files of the Inked World style)
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("AT_RAW", "/home/claude/newdata/raw_new8/asteroid_names.tsv")
LABELS = os.environ.get("AT_LABELS", "/home/claude/newdata/raw_new8/asteroid_labels.tsv")
GEO = os.environ.get("AT_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("AT_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.environ.get("AT_WORK", "/tmp/claude-0/s/at/work")
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "asteroid-towns"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# Kinds of namesake place, tested in this order against all of a namesake's Wikidata types (lower case)
KINDS = [
    ("myth", "Mythical or fictional places", r"mythic|fictional|legendary|imaginary"),
    ("water", "Rivers, lakes and seas", r"river|lake\b|lake water|sea\b|bay\b|strait|waterfall|stream|lagoon|fjord|reservoir|canal|spring\b|gulf|ocean|tributary"),
    ("town", "Towns, cities and villages",
     r"city|town|village|municipal|commune|comune|settlement|capital|metropol|socken|polis|parish|borough|hamlet|suburb|"
     r"neighbo|quarter|seat|urban|ward\b|area of london|frazione|localit|gemeinde|ortsteil|population center|census-designated|"
     r"entity of population|ōaza"),
    ("country", "Countries", None),
    ("inst", "Observatories, universities and other institutions",
     r"observator|universit|institut|museum|school|college|academ|organi[sz]ation|publisher|castle|church|"
     r"archaeolog|building|library|station|planetarium|monaster|abbey|cathedral|company|hospital|bridge|tower|stadium|garden|"
     r"ministry|agency|laborator|club|theatre|theater|society|palace|temple|shrine|mosque|monument|heritage site|zoo|"
     r"fortress|spaceport|cosmodrome|landmark|lighthouse|studentenverbindung|telescope|astronomical survey|arts center|château|chateau|camp\\b"),
    ("nature", "Mountains, islands and other natural features",
     r"mountain|volcan|hill|peak|massif|summit|range|pass\b|valley|glacier|cave|plateau|island|archipelago|peninsula|cape\b|"
     r"desert|forest|wilderness|crater|caldera|canyon|gorge|cliff|plain|steppe|atoll|reef|heath|reserve|protected area|national park|rock formation|marsh|\\bfell\\b|basin|^area$"),
    ("region", "Regions, provinces and counties",
     r"region|province|prefecture|county|district|oblast|canton|federal subject|territor|department|state\b|krai|voivodeship|shire|"
     r"\bland\b|administrative|governorate|division|historical country"),
]
COUNTRY_T = {"country", "sovereign state", "historical country", "island country", "landlocked country", "kingdom", "empire",
             "unitary state", "federation", "constituent country", "republic", "federal republic", "city-state", "microstate"}
KIND_NAME = {k: n for k, n, _ in KINDS} | {"other": "Other places"}
KIND_COL = {"town": "#A3261B", "region": "#E0A11B", "country": "#7B57A8", "water": "#2F5FA7", "nature": "#55803A",
            "inst": "#2B2119", "other": "#8C8478", "myth": "#BBB3A6"}
PLACE_KINDS = ["town", "region", "country", "water", "nature", "inst", "other"]


# Namesakes with coordinates that are not places: myths and fiction, languages, taxa, ships, battles and other events,
# programmes, peoples and families. Tested against all of a namesake's Wikidata types (lower case); any match excludes.
NONPLACE = (r"mytholog|mythic|legendary|fictional|imaginary|deity|\bgod\b|goddess|character|language|taxon|species|"
            r"\bship\b(?! canal)|watercraft|vessel|schooner|brig\b|brig-|\bbark\b|submarine|collier|shipwreck|"
            r"battle|siege|armistice|treaty|\bwar\b|explosion|wildfire|gold rush|disaster|\bevent\b(?! venue)|"
            r"television|radio program|series|ethnic group|indigenous people|\bpeople\b(?!['’]s)|tribe|dynasty|noble family|"
            r"troupe|astronomical survey|studentenverbindung")
# Bodies with no place of their own: excluded when every one of their types is of this sort
ORG_ONLY = (r"organi[sz]ation|agency|society|ministry|confederation|publish|academy|league|survey|fraternity|"
            r"corporation|foundation|charit")


# Checked by hand: namesakes typed as places in Wikidata that are not places
NONPLACE_IDS = {"Q7708016": "Texas Star Party (an annual event, typed as an observatory)",
                "Q206936": "Protezione Civile (an Italian government department)"}


def nonplace(types, qid=None):
    if qid in NONPLACE_IDS: return True
    tl = [x.lower() for x in types]
    if any(re.search(NONPLACE, x) for x in tl): return True
    return bool(tl) and all(re.search(ORG_ONLY, x) for x in tl)


def kind(types):
    t = " | ".join(types).lower()
    tl = {x.lower() for x in types}
    # sovereign states first, so "country bordering the Baltic Sea" is not read as a sea
    if tl & {"country", "sovereign state", "island country", "landlocked country"} and not re.search(r"city|town|municipal", t): return "country"
    for k, _, rx in KINDS:
        if k == "country":
            if tl & COUNTRY_T and not re.search(r"city|town|municipal", t) or tl & {"city-state", "microstate"}: return k
            continue
        if re.search(rx, t): return k
    return "other"


def hav(lon1, lat1, lon2, lat2):
    import numpy as np
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)): return None
    if isinstance(v, dict): return {str(k): nonan(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)): return [nonan(x) for x in v]
    if hasattr(v, "item"): return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "word": return WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}"
    if f == "Word": return (WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}").capitalize()
    raise ValueError(f)


def fill(tpl, R, keep=("DOI", "DOI_URL", "BLOG_URL")):
    return re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}",
                  lambda m: m.group(0) if m.group(1) in keep else fmt(get(R, m.group(1)), m.group(3)), tpl)

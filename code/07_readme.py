"""Step 7: README.md from data/results.json."""
from common import *
R = jload(f"{DATA}/results.json"); S, D = R["source"], R["dist"]
uk = "\n".join(f"| {u['asteroid']} | {u['place']} | {u['site'] or ''} | {u['year'] or ''} |" for u in R["uk"]["list"])
t = f"""# Towns with an asteroid: the places on Earth that minor planets are named after

A map and analysis of the {S['place_asteroids']:,} asteroids ({S['place']:,} asteroid namings) in Wikidata that honour a place on Earth with coordinates (towns, villages, regions, rivers, mountains, institutions and countries), each joined by a great circle to the observatory where its asteroid was discovered: which places have an asteroid, which countries have most, who named them, and how close to home.

Interactive page: {PAGE}
Paper: https://doi.org/{{10.5281/zenodo.24052725}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/asteroid-towns/}}

## Headline results

- Of {S['pairs']:,} namings of {S['asteroids']:,} asteroids in Wikidata, {S['person_pct']:.1f}% honour people, {S['place_pct']:.1f}% places with coordinates and {S['other_pct']:.1f}% other things. Towns, cities and villages are {R['kinds']['town']['pct']:.1f}% of the places.
- Countries: Japan {R['countries'][0]['n']}, Germany {R['countries'][1]['n']}, Russia {R['countries'][2]['n']}, Italy {R['countries'][3]['n']}, United States {R['countries'][4]['n']}. Per million people: Finland {R['per_m'][0]['per_m']:.1f}, Czech Republic {R['per_m'][1]['per_m']:.1f}, Sweden {R['per_m'][2]['per_m']:.1f}.
- Observatories: La Silla named {R['obs'][0]['n']} places, only {R['obs'][0]['same_pct']:.1f}% Chilean (Eric Elst named {R['elst']['fr']} French and {R['elst']['be']} Belgian places there). Kleť Observatory named {R['obs'][3]['n']}, {R['obs'][3]['same_pct']:.1f}% Czech and {R['homeliest'][1]['w100_pct']:.1f}% within 100 km.
- Distance: median {D['median']:,} km from discovery site to place; {D['w100_pct']:.1f}% within 100 km; {D['same_pct']:.1f}% in the same country. {R['jp']['home_pct']:.1f}% of Japanese places were named from Japanese sites; none of Sweden's {R['se']['n']} from Sweden; all of Finland's {R['fi']['n']} from Finland.
- United Kingdom: {R['uk']['n']} asteroids, two of them found at Church Stretton (Church Stretton and Salopia) and one at Stakenbridge (Old Joe).

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/03_build_site.py`): MapLibre map in the Inked World style with places, observatories and great circle lines. |
| `header.png` | Social card, 1200 x 630. |
| `data/asteroids.csv` | One row per asteroid and namesake: number, name, discoverers, discovery site, coordinates and country, year, namesake, class (person, place, other), kind of place, place coordinates, modern and Wikidata country, distance in km. |
| `data/places.csv` | One row per named place, with its asteroids. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json` | Page data. Other files in `data/`, `js/` and `fonts/` belong to the Inked World map style. |
| `code/` | Scripts, run in order, and the page, paper and blog templates; `qa.js` for screenshots. |
| `release/` | Paper PDF and LaTeX (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots at desktop and phone widths. |

## Method in brief

- One Wikidata query (through QLever) for asteroids with a "named after" (P138) statement, with number, discoverer (P61), discovery site (P65) and date, and the namesake's type, coordinates and country. {S['rows']:,} rows deduplicated to {S['pairs']:,} asteroid and namesake pairs.
- Place: a namesake that is not human, has coordinates, is not mythical or fictional and is not a non-place (language, taxon, ship, battle or other event, television programme, people, dynasty, troupe, or a body whose types are all organisational; two more excluded by hand); the whole place list was read by eye. Kinds by keyword rules on Wikidata types (`code/common.py`).
- Asteroid names: Wikidata's multilingual label, then the English label, then a label in any language (`asteroid_labels.tsv`).
- Countries: Wikidata's country (P17) when it names one modern country and the point is within about 30 km of its Natural Earth outline (border towns); otherwise Natural Earth by point in polygon; continents get none; Crimea counted as Ukraine; per head with Natural Earth population estimates (mostly for 2019), for countries of at least a million people with five or more places. Populations are Natural Earth country figures, so Hong Kong and other territories count separately.
- Distances: great circle from discovery site to the place's point.

## Caveats

Wikidata records the namesake of only part of the named minor planets; this is the subset that Wikidata links to a namesake, not all named minor planets, and has not been compared with the Minor Planet Center's full list of names. The discovery site is where an asteroid was found, not necessarily where its name was chosen. Regions, rivers and countries are single points.

## British places with an asteroid

| Asteroid | Place | Discovery site | Year |
|---|---|---|---|
{uk}

## Sources and licences

- Wikidata contributors, Wikidata (CC0), queried with QLever.
- Minor Planet Center, How are asteroids named? https://docs.minorplanetcenter.net/mpc-ops-docs/designations/how-asteroids-are-named/ ; IAU WGSBN, https://www.wgsbn-iau.org/
- Natural Earth (public domain). Map style on OpenStreetMap data (ODbL) via OpenFreeMap.
- Text, figures and derived data CC BY 4.0; code MIT (see LICENSE).

## How to rerun

```
cd code
python3 01_clean.py && python3 02_analysis.py && python3 03_build_site.py && python3 04_figures.py && python3 05_paper.py
cd .. && python3 reddit/collage.py && python3 code/07_readme.py && cd code && python3 06_release.py
```
Raw input paths are documented in `code/common.py`.

## Citation

Hotham, T. (2026) Towns with an asteroid: the places on Earth that minor planets are named after. Zenodo. https://doi.org/{{10.5281/zenodo.24052725}}

{AI}
"""
chk = re.sub(r"^\|[-|]+\|$", "", t, flags=re.M)
for bad in ("—", "–", "--"): assert bad not in chk, bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(t)
print("README", len(t.split()), "words")

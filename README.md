# Towns with an asteroid: the places on Earth that minor planets are named after

A map and analysis of the 2,193 asteroids (2,206 asteroid namings) in Wikidata that honour a place on Earth with coordinates (towns, villages, regions, rivers, mountains, institutions and countries), each joined by a great circle to the observatory where its asteroid was discovered: which places have an asteroid, which countries have most, who named them, and how close to home.

Interactive page: https://maps.tristanhotham.com/asteroid-towns/
Paper: https://doi.org/10.5281/zenodo.24052725
Blog post: https://blog.tristanhotham.com/2026/10/31/asteroid-towns/

## Headline results

- Of 11,418 namings of 11,268 asteroids in Wikidata, 65.4% honour people, 19.3% places with coordinates and 15.3% other things. Towns, cities and villages are 52.1% of the places.
- Countries: Japan 421, Germany 153, Russia 137, Italy 135, United States 130. Per million people: Finland 11.8, Czech Republic 9.8, Sweden 8.1.
- Observatories: La Silla named 224 places, only 3.6% Chilean (Eric Elst named 36 French and 16 Belgian places there). Kleť Observatory named 98, 80.6% Czech and 50.0% within 100 km.
- Distance: median 508 km from discovery site to place; 27.1% within 100 km; 58.5% in the same country. 92.5% of Japanese places were named from Japanese sites; none of Sweden's 83 from Sweden; all of Finland's 65 from Finland.
- United Kingdom: 26 asteroids, two of them found at Church Stretton (Church Stretton and Salopia) and one at Stakenbridge (Old Joe).

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

- One Wikidata query (through QLever) for asteroids with a "named after" (P138) statement, with number, discoverer (P61), discovery site (P65) and date, and the namesake's type, coordinates and country. 22,704 rows deduplicated to 11,418 asteroid and namesake pairs.
- Place: a namesake that is not human, has coordinates, is not mythical or fictional and is not a non-place (language, taxon, ship, battle or other event, television programme, people, dynasty, troupe, or a body whose types are all organisational; two more excluded by hand); the whole place list was read by eye. Kinds by keyword rules on Wikidata types (`code/common.py`).
- Asteroid names: Wikidata's multilingual label, then the English label, then a label in any language (`asteroid_labels.tsv`).
- Countries: Wikidata's country (P17) when it names one modern country and the point is within about 30 km of its Natural Earth outline (border towns); otherwise Natural Earth by point in polygon; continents get none; Crimea counted as Ukraine; per head with Natural Earth population estimates (mostly for 2019), for countries of at least a million people with five or more places. Populations are Natural Earth country figures, so Hong Kong and other territories count separately.
- Distances: great circle from discovery site to the place's point.

## Caveats

Wikidata records the namesake of only part of the named minor planets; this is the subset that Wikidata links to a namesake, not all named minor planets, and has not been compared with the Minor Planet Center's full list of names. The discovery site is where an asteroid was found, not necessarily where its name was chosen. Regions, rivers and countries are single points.

## British places with an asteroid

| Asteroid | Place | Discovery site | Year |
|---|---|---|---|
| 758 Mancunia | Manchester | Union Observatory | 1912 |
| 1071 Brita | Great Britain | Simeiz Observatory | 1924 |
| 1244 Deira | Kingdom of Deira | Union Observatory | 1932 |
| 2531 Cambridge | Cambridge | Anderson Mesa Station | 1980 |
| 2830 Greenwich | Royal Observatory | Anderson Mesa Station | 1980 |
| 3009 Coventry | Coventry | Crimean Astrophysical Observatory | 1973 |
| 3858 Dorchester | Dorchester | Brorfelde Observatory | 1986 |
| 4206 Verulamium | Verulamium | La Silla Observatory | 1986 |
| 5677 Aberdonia | University of Aberdeen | Lowell Observatory | 1987 |
| 5805 Glasgow | Glasgow | Lowell Observatory | 1985 |
| 6939 Lestone | Leighton Buzzard | Mount Wilson Observatory | 1952 |
| 7603 Salopia | Shropshire | Church Stretton | 1995 |
| 8283 Edinburgh | Edinburgh | Siding Spring Observatory | 1991 |
| 8380 Tooting | Tooting | Palomar Observatory | 1992 |
| 8837 London | London | La Silla Observatory | 1989 |
| 8849 Brighton | Brighton | La Silla Observatory | 1990 |
| 9325 Stonehenge | Stonehenge | La Silla Observatory | 1989 |
| 9767 Midsomer Norton | Midsomer Norton | Siding Spring Observatory | 1992 |
| 10501 Ardmacha | Armagh | Palomar Observatory | 1987 |
| 10502 Armaghobs | Armagh Observatory | Palomar Observatory | 1987 |
| 10515 Old Joe | Joseph Chamberlain Memorial Clock Tower | Stakenbridge observatory | 1989 |
| 11626 Church Stretton | Church Stretton | Church Stretton | 1996 |
| 28220 York | York | Kleť Observatory | 1998 |
| 69423 Openuni | The Open University | Astronomical Observatory of Farra d'Isonzo | 1996 |
| 100604 Lundy | Lundy | Royal Observatory of Belgium | 1997 |
| 129092 Snowdonia | Snowdon | Haleakalā Observatory | 2004 |

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

Hotham, T. (2026) Towns with an asteroid: the places on Earth that minor planets are named after. Zenodo. https://doi.org/10.5281/zenodo.24052725

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.

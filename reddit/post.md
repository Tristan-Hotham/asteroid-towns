**Title:** [OC] Towns with an asteroid: 2,193 asteroids (2,206 namings) are named after places on Earth. Japan has 421, Finland the most per head (11.8 per million people)

**Body:**

I mapped every asteroid that Wikidata says is named after a place with coordinates, and drew a line from each place to the observatory that discovered its asteroid.

- About one asteroid namesake in five is a place (19%); 65% are people.
- Japan has 421 places in the sky, then Germany (153) and Russia (137). Per head: Finland 11.8, Czechia 9.8, Sweden 8.1 per million people.
- Big telescopes name the world: only 4% of La Silla's 224 places are in Chile. Small ones name the next valley: half of the Czech Kleť Observatory's 98 places are within 100 km of it.
- The UK has 26, including London, Brighton, Tooting and Midsomer Norton.

Interactive map (click a town or an observatory): https://maps.tristanhotham.com/asteroid-towns/

**Source comment:**

Data: Wikidata "named after" (P138) statements for asteroids, with discovery site (P65) and the namesake's coordinates, queried through QLever (CC0); countries from Wikidata with Natural Earth borders as a fallback; populations from Natural Earth (mostly 2019 estimates). Non-places (languages, ships, battles, TV programmes and so on) removed by rule and by eye. Wikidata records the namesake of only some named minor planets, so this is the subset that Wikidata links to a namesake, not all named minor planets. Tools: Python (pandas, geopandas, matplotlib), MapLibre. Paper, data and code: https://github.com/Tristan-Hotham/asteroid-towns

# asteroid-towns: working notes
- Pipeline: code/01_clean.py -> 02_analysis.py -> 03_build_site.py -> 04_figures.py -> 05_paper.py -> 07_readme.py -> 06_release.py; reddit/collage.py; code/qa.js (server on 8802).
- Ink map assets copied from moon-names/colour-names. Crimea counted as Ukraine.
- Coverage: Wikidata P138 for 11,268 asteroids only; not compared with MPC totals (not reachable).
- DONE: page (QA ok both widths), figures, paper 9 pp, blog 5 figs, zenodo, collage, post, README.
- REVIEW FIXES (2026): non-place rules (common.NONPLACE, ORG_ONLY, NONPLACE_IDS; whole place list read by eye), country = Wikidata P17 for border cases (within ~30 km of that country's NE outline) else NE, continents no country, asteroid names from asteroid_labels.tsv (mul, en, any), headline 2,193 asteroids (2,206 namings), MPC + WGSBN citations, collage La Silla label on sea. Pipeline rerun 01-07 + collage; QA ok at 1280 and 390.

"""Step 6: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24052725, https://doi.org/10.5281/zenodo.24052725 and https://blog.tristanhotham.com/2026/10/31/asteroid-towns/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Asteroid_Towns"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}

# facts in words in the blog and alt text
import pandas as pd
A = pd.read_csv(f"{DATA}/asteroids.csv"); p = A[A.ncls == "place"]
m = p[p.name == "758 Mancunia"].iloc[0]; assert m.site == "Union Observatory" and m.year == 1912 and m.site_iso3 == "ZAF"
klet = set(p[p.site == "Kleť Observatory"].namesake); assert {"Český Krumlov", "České Budějovice", "Malše"} <= klet
uk = set(p[p.iso3 == "GBR"].namesake); assert {"London", "Brighton", "Edinburgh", "Coventry", "Tooting", "Midsomer Norton", "Manchester"} <= uk
assert 2.5 < R["countries"][0]["n"] / R["countries"][1]["n"] < 3 and 45 <= R["kinds"]["town"]["pct"] <= 55
assert [round(c["n"]) for c in R["countries"][:8]] == [421, 153, 137, 135, 130, 120, 106, 104]
assert [round(c["per_m"], 1) for c in R["per_m"][:5]] == [11.8, 9.8, 8.1, 4.7, 4.6]
assert [round(R["kinds"][k]["pct"]) for k in ("town", "region", "nature", "inst")] == [52, 9, 13, 14] and round(R['source']['place_pct']) == 19 and round(R['source']['person_pct']) == 65 and round(R['source']['other_pct']) == 15
O = {o["site"]: o for o in R["obs"]}
assert round(O["Kitami Observatory"]["same_pct"]) == 96 and round(O["Ōizumi Observatory"]["same_pct"]) == 97 and [(o["n"], round(o["same_pct"])) for o in R["obs"][:4]] == [(224, 4), (164, 26), (99, 21), (98, 81)] and round(O["Purple Mountain Observatory"]["same_pct"]) == 99 and round(O["Geisei observatory"]["same_pct"]) == 85
assert R["se"]["home_pct"] == 0 and R["fi"]["home_pct"] == 100
post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
from PIL import Image
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used: os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Towns with an asteroid: the places on Earth that have a minor planet",
        "slug": "asteroid-towns",
        "excerpt": f"I mapped {R['source']['place_asteroids']:,} asteroids ({R['source']['place']:,} namings) named after places on Earth, each with a line to the observatory that found it. Japan has the most, Finland the most per head, and small observatories name the next valley.",
        "seo_description": f"{R['source']['place_asteroids']:,} asteroids named after towns, rivers and mountains, mapped with lines to the observatories that found them.",
        "tags": ["maps", "asteroids", "space", "place names", "Wikidata", "data visualisation", "astronomy", "geography"],
        "header_alt": f"Title card reading 'Towns with an asteroid' in black and red on parchment, beside a map of Europe, Africa and Asia covered in small coloured dots joined by faint arcs to black stars, with the lines '{R['source']['place_asteroids']:,} minor planets ({R['source']['place']:,} namings) named after places on Earth' and 'Japan: {R['countries'][0]['n']}. Finland: {R['per_m'][0]['per_m']:.1f} per million people. The UK: {R['uk']['n']}.'"}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z): os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith(".pyc") or fn == "__pycache__": continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in ("asteroids.csv", "places.csv", "results.json", "site.json"):
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
ab = re.sub(r"\\textit\{([^}]*)\}", r"\1", ab)
zmeta = {"title": "Towns with an Asteroid: the Places on Earth that Minor Planets Are Named After, and the Observatories that Named Them",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/asteroid-towns/}}.</p><p>Sources: Wikidata (CC0), queried with QLever; Natural Earth (public domain); map style on OpenStreetMap data (ODbL) via OpenFreeMap. Derived data and text CC BY 4.0, code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["minor planets", "asteroids", "nomenclature", "toponymy", "commemoration", "amateur astronomy", "Wikidata", "maps", "open data"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")

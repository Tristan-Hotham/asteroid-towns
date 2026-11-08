"""Step 3: build index.html from code/page_template.html and code/page_style.css. Every number in the text is a
{{path|format}} token filled from data/results.json (embedded); data/site.json is fetched by the page. Facts stated in
words are checked here. 10.5281/zenodo.24052725 and https://blog.tristanhotham.com/2026/10/31/asteroid-towns/ stay as placeholders for the publisher."""
import json
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/asteroids.csv"); p = A[A.ncls == "place"]
O = {o["site"]: o for o in R["obs"]}
assert [o["site"] for o in R["obs"][:3]] == ["La Silla Observatory", "Crimean Astrophysical Observatory", "Palomar Observatory"]
assert R["obs"][3]["site"] == "Kleť Observatory" and R["homeliest"][1]["site"] == "Kleť Observatory" and R["obs"][6]["site"] == "Purple Mountain Observatory"
assert R["obs"][0]["same_pct"] < 5 and R["obs"][6]["same_pct"] > 95
assert R["discoverers"][0]["name"] == "Eric Walter Elst" and R["elst"]["site"] == "La Silla Observatory" and R["elst"]["fr"] > R["elst"]["be"]
u = [d for d in R["discoverers"] if d["name"].startswith("Uppsala")][0]; assert u["site"] == "La Silla Observatory" and u["top"] == "Sweden" and u["top_n"] > 0.9 * u["n"]
assert [c["country"] for c in R["countries"][:5]] == ["Japan", "Germany", "Russia", "Italy", "United States"]
assert [c["country"] for c in R["per_m"][:3]] == ["Finland", "Czech Republic", "Sweden"]
assert R["source"]["person_pct"] > 60 and 15 < R["source"]["place_pct"] < 25          # "about one in five"
uk = p[p.iso3 == "GBR"]
assert set(uk[uk.site_iso3 == "GBR"].site) == {"Church Stretton", "Stakenbridge observatory"}
assert {"Church Stretton", "Shropshire"} <= set(uk[uk.site == "Church Stretton"].namesake) and "Joseph Chamberlain Memorial Clock Tower" in set(uk[uk.site == "Stakenbridge observatory"].namesake)
assert {"London", "Brighton", "Midsomer Norton"} <= set(uk.namesake) and not {"Blue Peter", "Department of Education of Northern Ireland"} & set(uk.namesake)
assert (uk.site_iso3 != "GBR").mean() > .85


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    tpl = tpl.replace("/*CSS*/", open(os.path.join(ROOT, "code", "page_style.css"), encoding="utf-8").read())
    html = fill(tpl, R)
    left = set(re.findall(r"\{\{[^}]*\}\}", html)); assert left <= {"10.5281/zenodo.24052725", "https://blog.tristanhotham.com/2026/10/31/asteroid-towns/"}, left
    html = html.replace("/*RESULTS*/", json.dumps(R, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S); vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"): assert bad not in vis, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()

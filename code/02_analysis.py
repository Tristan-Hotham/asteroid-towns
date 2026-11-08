"""Step 2: every number quoted anywhere goes into data/results.json; the page data into data/site.json.
Unit: an asteroid and one of its namesakes (a "naming"). "Places" are namesakes that are not people and have
coordinates (mythical and fictional places excluded). Countries are modern (Natural Earth; Crimea counted as Ukraine)."""
import pandas as pd, numpy as np
from common import *

A = pd.read_csv(f"{DATA}/asteroids.csv", keep_default_na=False, na_values=[""])
CM = jload(f"{WORK}/clean_meta.json"); POP = CM["pop"]
p = A[A.ncls == "place"].copy()
p["same"] = (p.iso3 == p.site_iso3)
pc = lambda a, b: round(100 * a / b, 2) if b else None
R = {"meta": {"page": PAGE, "repo": REPO}}
cls = A.ncls.value_counts()
R["source"] = {"rows": CM["rows"], "asteroids": int(A.aid.nunique()), "pairs": len(A), "numbered": int(A.drop_duplicates("aid").number.notna().sum()),
               "person": int(cls["person"]), "place": int(cls["place"]), "other": int(cls["other"]),
               "person_pct": pc(cls["person"], len(A)), "place_pct": pc(cls["place"], len(A)), "other_pct": pc(cls["other"], len(A)),
               "places_distinct": int(p.nid.nunique()), "place_asteroids": int(p.aid.nunique()), "with_site": int(p.site_lon.notna().sum()),
               "first_year": int(p.year.min()), "last_year": int(p.year.max()), "multi_namesake": int((A.groupby("aid").size() > 1).sum())}
k = p.kind.value_counts()
R["kinds"] = {kk: {"n": int(k.get(kk, 0)), "pct": pc(k.get(kk, 0), len(p)), "name": KIND_NAME[kk]} for kk in PLACE_KINDS}

# countries
c = p.groupby(["iso3"]).agg(n=("aid", "size"), country=("country", "first")).reset_index()
c["country"] = c.iso3.map(CM["cname"]).fillna(c.country)
c.loc[c.iso3 == "UKR", "country"] = "Ukraine"
c["pop_m"] = c.iso3.map(POP) / 1e6
c["per_m"] = c.n / c.pop_m
c = c.sort_values("n", ascending=False)
R["countries"] = [{"country": r.country, "iso3": r.iso3, "n": int(r.n), "pct": pc(r.n, len(p)), "per_m": round(float(r.per_m), 2)} for r in c.head(20).itertuples()]
pm = c[(c.pop_m >= 1) & (c.n >= 5)].sort_values("per_m", ascending=False)
R["per_m"] = [{"country": r.country, "n": int(r.n), "per_m": round(float(r.per_m), 2), "pop_m": round(float(r.pop_m), 1)} for r in pm.head(15).itertuples()]
R["n_countries"] = int(c.shape[0])
R["per_m_rule"] = "countries with at least 1 million people (Natural Earth POP_EST) and at least 5 place namings"

# distance and home-town bias
t = p[p.dist_km.notna()]; tw = t[t.kind == "town"]
R["dist"] = {"n": len(t), "median": round(float(t.dist_km.median())), "w50_pct": pc((t.dist_km < 50).sum(), len(t)), "w100_pct": pc((t.dist_km < 100).sum(), len(t)),
             "w10": int((t.dist_km < 10).sum()), "same_pct": pc(t.same.sum(), len(t)),
             "town_n": len(tw), "town_median": round(float(tw.dist_km.median())), "town_w100_pct": pc((tw.dist_km < 100).sum(), len(tw)), "town_same_pct": pc(tw.same.sum(), len(tw))}
o = t.groupby("site").agg(n=("aid", "size"), country=("site_country", "first"), same=("same", "mean"), med=("dist_km", "median"),
                          w100=("dist_km", lambda s: (s < 100).mean()), lon=("site_lon", "first"), lat=("site_lat", "first")).reset_index().sort_values("n", ascending=False)
R["obs"] = [{"site": r.site, "country": r.country, "n": int(r.n), "same_pct": round(100 * r.same, 1), "median_km": round(float(r.med)), "w100_pct": round(100 * r.w100, 1)} for r in o.head(15).itertuples()]
R["n_obs"] = int(o.shape[0])
big = o[o.n >= 20].sort_values("w100", ascending=False)
R["homeliest"] = [{"site": r.site, "country": r.country, "n": int(r.n), "w100_pct": round(100 * r.w100, 1), "median_km": round(float(r.med))} for r in big.head(6).itertuples()]
R["farthest"] = [{"site": r.site, "country": r.country, "n": int(r.n), "w100_pct": round(100 * r.w100, 1), "median_km": round(float(r.med))} for r in big.sort_values("med", ascending=False).head(4).itertuples()]
dsc = p.groupby("discoverers").agg(n=("aid", "size"), site=("site", lambda s: s.mode().iloc[0] if s.notna().any() else ""), top=("country", lambda s: s.mode().iloc[0] if s.notna().any() else ""),
                                   top_n=("country", lambda s: int(s.value_counts().iloc[0]) if s.notna().any() else 0)).reset_index().sort_values("n", ascending=False)
R["discoverers"] = [{"name": r.discoverers, "n": int(r.n), "site": r.site, "top": r.top, "top_n": r.top_n} for r in dsc.head(10).itertuples()]
el = p[p.discoverers == "Eric Walter Elst"]
R["elst"] = {"n": len(el), "fr": int((el.iso3 == "FRA").sum()), "be": int((el.iso3 == "BEL").sum()), "site": el.site.value_counts().index[0]}
self_obs = p[(p.kind == "inst") & p.namesake.str.contains("Observ|Station|Telescope", na=False)]
R["observatories_named"] = {"n": len(self_obs), "own": int((self_obs.dist_km < 5).sum())}

# by kind of place
R["kind_dist"] = {kk: round(float(t[t.kind == kk].dist_km.median())) for kk in PLACE_KINDS if (t.kind == kk).sum()}

# Japan, Czech Republic, Italy: national naming
for iso, key in (("JPN", "jp"), ("CZE", "cz"), ("ITA", "it"), ("SWE", "se"), ("FIN", "fi")):
    x = t[t.iso3 == iso]
    R[key] = {"n": int((p.iso3 == iso).sum()), "home_pct": pc((x.site_iso3 == iso).sum(), len(x)), "w100_pct": pc((x.dist_km < 100).sum(), len(x))}
R["jp"]["top_site"] = t[t.iso3 == "JPN"].site.value_counts().index[0]

# the UK
uk = p[p.iso3 == "GBR"].sort_values("number")
R["uk"] = {"n": len(uk), "places": int(uk.nid.nunique()), "towns": int((uk.kind == "town").sum()),
           "list": [{"asteroid": r.name, "place": r.namesake if isinstance(r.namesake, str) else f"{r.nid} (no English label)", "kind": r.kind, "site": r.site, "year": None if pd.isna(r.year) else int(r.year), "km": None if pd.isna(r.dist_km) else round(float(r.dist_km))} for r in uk.itertuples()],
           "home": [r.namesake for r in uk.itertuples() if not pd.isna(r.dist_km) and r.dist_km < 30]}
assert R["uk"]["n"] >= 20
cs = A[(A.site == "Church Stretton")]
R["church_stretton"] = {"n": len(cs), "places": cs[cs.ncls == "place"].namesake.tolist()}

# famous towns with several asteroids
mt = p.groupby(["nid", "namesake", "country"]).size().sort_values(ascending=False)
R["multi_towns"] = [{"place": n, "country": cn, "n": int(v)} for (i, n, cn), v in mt.head(8).items()]
R["kind_order"] = PLACE_KINDS; R["kind_cols"] = KIND_COL
R["checks"] = {"person_majority": R["source"]["person_pct"] > 50, "japan_top": R["countries"][0]["country"] == "Japan"}
assert all(R["checks"].values()), R["checks"]
jsave(R, f"{DATA}/results.json", indent=1)

# ---------- page data ----------
r4 = lambda v: None if pd.isna(v) else round(float(v), 4)
obs = o.reset_index(drop=True); oi = {s: i for i, s in enumerate(obs.site)}
site = {"kinds": [[kk, KIND_NAME[kk], KIND_COL[kk]] for kk in PLACE_KINDS],
        "obs": [[r.site, r4(r.lon), r4(r.lat), r.country, int(r.n)] for r in obs.itertuples()],
        "cols": ["aid", "num", "name", "disc", "obs", "year", "nid", "place", "kind", "lon", "lat", "country", "km", "types"],
        "rows": [[r.aid, None if pd.isna(r.number) else int(r.number), r.name, r.discoverers if isinstance(r.discoverers, str) else "", oi.get(r.site, -1),
                  None if pd.isna(r.year) else int(r.year), r.nid, r.namesake if isinstance(r.namesake, str) else r.nid, PLACE_KINDS.index(r.kind),
                  r4(r.lon), r4(r.lat), r.country if isinstance(r.country, str) else "", None if pd.isna(r.dist_km) else round(float(r.dist_km)),
                  r.types if isinstance(r.types, str) else ""] for r in p.itertuples()]}
jsave(site, f"{DATA}/site.json")
print({k: R["dist"][k] for k in ("median", "w100_pct", "same_pct", "town_median", "town_w100_pct")}, R["countries"][:5], R["per_m"][:6], R["homeliest"][:4], R["uk"]["n"], os.path.getsize(f"{DATA}/site.json") // 1024, "KB")

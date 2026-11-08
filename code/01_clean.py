"""Step 1: parse the Wikidata TSV, deduplicate and write the clean tables.

Outputs
  data/asteroids.csv  one row per asteroid and namesake: asteroid id, number, name, discoverers, discovery site and its
                      coordinates and modern country, discovery year, namesake id and name, namesake class (person,
                      place, other), place kind, place coordinates and modern country (Natural Earth, with Wikidata's
                      country kept beside it), distance from the discovery site to the place (km).
  data/places.csv     one row per named place (a place honoured by several asteroids appears once), with its asteroids.
"""
import pandas as pd, numpy as np, geopandas as gpd
from shapely.geometry import Point
from common import *

d = pd.read_csv(RAW, sep="\t", dtype=str, quoting=3)
d.columns = [c.lstrip("?") for c in d.columns]
n_rows = len(d)
for c in d.columns:
    d[c] = (d[c].fillna("").str.replace(r"^<http://www\.wikidata\.org/entity/(Q\d+)>$", r"\1", regex=True)
            .str.replace(r'^"(.*)"(@[\w-]+|\^\^.*)?$', r"\1", regex=True))


def xy(s):
    m = re.search(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)", s or "")
    return (float(m.group(1)), float(m.group(2))) if m else (np.nan, np.nan)


# asteroid names: the multilingual label (mul) first, then the English label, then a label in any language
LB = pd.read_csv(LABELS, sep="\t", dtype=str, quoting=3).fillna("")
LB.columns = [c.lstrip("?") for c in LB.columns]
unq = lambda v: re.sub(r'^"(.*)"(@[\w-]+)?$', r"\1", v)
LB["a"] = LB.a.str.replace(r"^<http://www\.wikidata\.org/entity/(Q\d+)>$", r"\1", regex=True)
LB["mul"] = LB["mul"].map(unq); LB["label"] = LB["label"].map(unq)
LB = LB.groupby("a").agg(mul=("mul", lambda s: next((x for x in s if x), "")), label=("label", lambda s: next((x for x in s if x), "")))
tidy = lambda v: re.sub(r"^\((\d+)\)\s+", r"\1 ", v.strip())   # "(2675) Tolkien" -> "2675 Tolkien"

rows = []
for (a, n), g in d.groupby(["a", "n"], sort=True):
    g0 = g.iloc[0]
    sites = g[g.site != ""].drop_duplicates("site")
    s0 = sites.iloc[0] if len(sites) else g0
    slon, slat = xy(s0.sitecoord)
    nlon, nlat = (np.nan, np.nan)
    cs = [c for c in g.ncoord.unique() if c]
    if cs: nlon, nlat = xy(sorted(cs)[0])
    types = sorted(set(t for t in g.ntypel if t))
    human = "Q5" in set(g.ntype)
    cls = "person" if human else ("place" if not np.isnan(nlat) else "other")
    k = kind(types) if cls == "place" else ""
    if cls == "place" and (k == "myth" or nonplace(types, n)): cls, k = "other", ""
    yr = re.match(r"^(\d{4})-", g0.ddate or "")
    lb = LB.loc[a] if a in LB.index else None
    name = tidy((lb["mul"] if lb is not None and lb["mul"] else "") or g0.al or (lb["label"] if lb is not None else "")) or (f"({g0.mpn})" if g0.mpn else a)
    rows.append(dict(aid=a, number=int(g0.mpn) if g0.mpn.isdigit() else None, name=name,
                     discoverers="; ".join(sorted(set(x for x in g.discl if x))), site_id=s0.site, site=s0.sitel,
                     site_lon=slon, site_lat=slat, site_wd_country=s0.sitecl, year=int(yr.group(1)) if yr else None,
                     nid=n, namesake=g0.nl or re.sub(r"^\d+\s+", "", name), ncls=cls, kind=k, types="; ".join(types[:4]), lon=nlon, lat=nlat,
                     wd_country="; ".join(sorted(set(x for x in g.ncl if x)))))
A = pd.DataFrame(rows)

ne = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson")[["ADM0_A3", "ADMIN", "CONTINENT", "POP_EST", "geometry"]]
ren = {"United States of America": "United States", "Republic of Serbia": "Serbia", "Czechia": "Czech Republic", "United Republic of Tanzania": "Tanzania"}


def locate(lon, lat, ids):
    ok = ~(np.isnan(lon) | np.isnan(lat))
    pts = gpd.GeoDataFrame({"i": ids[ok]}, geometry=[Point(x, y) for x, y in zip(lon[ok], lat[ok])], crs=ne.crs)
    j = gpd.sjoin(pts, ne, how="left", predicate="within").drop_duplicates("i").set_index("i")
    miss = j[j.ADM0_A3.isna()]
    if len(miss):
        mm = gpd.GeoDataFrame({"i": miss.index}, geometry=list(miss.geometry), crs=ne.crs).to_crs(3857)
        jn = gpd.sjoin_nearest(mm, ne.to_crs(3857), how="left", max_distance=30000).drop_duplicates("i").set_index("i")
        for c in ("ADM0_A3", "ADMIN", "CONTINENT"): j.loc[jn.index, c] = jn[c]
    return j


j = locate(A.lon.values, A.lat.values, A.index.values)
A["iso3"] = A.index.map(j.ADM0_A3); A["country"] = A.index.map(j.ADMIN).map(lambda c: ren.get(c, c)); A["continent"] = A.index.map(j.CONTINENT)
js = locate(A.site_lon.values, A.site_lat.values, A.index.values)
A["site_iso3"] = A.index.map(js.ADM0_A3); A["site_country"] = A.index.map(js.ADMIN).map(lambda c: ren.get(c, c))
# Country: Wikidata's country (P17) of the place or site when it names exactly one modern country that Natural Earth
# knows; when it names several, the Natural Earth country if it is one of them; otherwise (none, or only historical
# states) the Natural Earth country by point in polygon. Wikidata's country is used only when the point lies within
# about 30 km (0.3 degrees) of that country's Natural Earth outline, so a border town (Passau, Konstanz, Gorizia,
# Tornio) goes to its own country while a historical claim far away (Ingria to Sweden) does not.
NEP = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson", ignore_geometry=True)
WD2ISO = {}
for r in NEP.itertuples():
    for c in ("ADMIN", "NAME", "NAME_LONG", "FORMAL_EN", "NAME_EN", "GEOUNIT"):
        v = getattr(r, c, None)
        if isinstance(v, str) and v: WD2ISO.setdefault(v, r.ADM0_A3)
WD2ISO.update({"People's Republic of China": "CHN", "Kingdom of the Netherlands": "NLD", "Kingdom of Denmark": "DNK", "Czech Republic": "CZE",
               "United States": "USA", "United Kingdom": "GBR", "Russia": "RUS", "Taiwan": "TWN", "Republic of China": "TWN",
               "State of Palestine": "PSX", "Republic of Ireland": "IRL", "Ireland": "IRL", "Georgia": "GEO", "Serbia": "SRB",
               "North Macedonia": "MKD", "Eswatini": "SWZ", "Ivory Coast": "CIV", "Democratic Republic of the Congo": "COD",
               "Republic of the Congo": "COG", "The Gambia": "GMB", "The Bahamas": "BHS", "East Timor": "TLS", "Vatican City": "VAT",
               "Federated States of Micronesia": "FSM", "Kingdom of Norway": "NOR", "Turkey": "TUR", "Czechia": "CZE"})
CNAME = {r.ADM0_A3: ren.get(r.ADMIN, r.ADMIN) for r in NEP.itertuples()}
CONT = {r.ADM0_A3: r.CONTINENT for r in NEP.itertuples()}


GEOM = ne.set_index("ADM0_A3").geometry


def wd_pick(wd, ne_iso, lon, lat):
    isos = []
    for x in (wd or "").split("; "):
        i = WD2ISO.get(x.strip())
        if i and i not in isos: isos.append(i)
    if len(isos) == 1 and not isinstance(ne_iso, str): return isos[0]          # off Natural Earth's coastline
    if len(isos) == 1 and i in GEOM.index and not np.isnan(lon) and GEOM[isos[0]].distance(Point(lon, lat)) < 0.3: return isos[0]
    return ne_iso


NE0 = {p_: A[p_ + "iso3"].copy() for p_ in ("", "site_")}   # Natural Earth's own answer, used for Crimea below
for p_, wcol in (("", "wd_country"), ("site_", "site_wd_country")):
    lo_, la_ = ("site_lon", "site_lat") if p_ else ("lon", "lat")
    new = [wd_pick(w if isinstance(w, str) else "", i, x, y) for w, i, x, y in zip(A[wcol], A[p_ + "iso3"], A[lo_], A[la_])]
    ch = [k for k, (a_, b_) in enumerate(zip(new, A[p_ + "iso3"])) if isinstance(a_, str) and a_ != b_]
    A[p_ + "iso3"] = new
    A[p_ + "country"] = [CNAME.get(i, c) if isinstance(i, str) else c for i, c in zip(new, A[p_ + "country"])]
    if p_ == "": A["continent"] = [CONT.get(i, c) if isinstance(i, str) else c for i, c in zip(new, A.continent)]
    print(p_ or "place", "country changed by Wikidata P17:", len(ch))
# Crimea: Natural Earth's default places it in Russia; it is internationally recognised as part of Ukraine
cri = lambda lon, lat: (lon > 32.4) & (lon < 36.7) & (lat > 44.3) & (lat < 46.25)
for p_, lo, la in (("", "lon", "lat"), ("site_", "site_lon", "site_lat")):
    m = (NE0[p_] == "RUS") & A[p_ + "iso3"].isin(["RUS", "UKR"]) & cri(A[lo], A[la])
    A.loc[m, p_ + "iso3"] = "UKR"; A.loc[m, p_ + "country"] = "Ukraine (Crimea)"
# continents and parts of the world belong to no one country
cont = A.types.fillna("").str.contains(r"continent|part of the world")
A.loc[cont, ["iso3", "country", "continent"]] = np.nan
A["dist_km"] = np.round(hav(A.site_lon, A.site_lat, A.lon, A.lat), 1)
A.loc[A.ncls != "place", ["country", "iso3", "continent", "dist_km"]] = np.nan
A.to_csv(f"{DATA}/asteroids.csv", index=False)

pl = A[A.ncls == "place"]
P = (pl.groupby("nid").agg(name=("namesake", "first"), kind=("kind", "first"), types=("types", "first"), lon=("lon", "first"), lat=("lat", "first"),
                           country=("country", "first"), iso3=("iso3", "first"), wd_country=("wd_country", "first"), n=("aid", "size"),
                           asteroids=("name", lambda s: "; ".join(s)), min_dist_km=("dist_km", "min")).reset_index())
P.to_csv(f"{DATA}/places.csv", index=False)
pop = ne.set_index("ADM0_A3").POP_EST
jsave({"rows": n_rows, "pop": {k: float(v) for k, v in pop.items()}, "cname": {r.ADM0_A3: ren.get(r.ADMIN, r.ADMIN) for r in ne.itertuples()}}, f"{WORK}/clean_meta.json")
print(n_rows, "rows;", A.aid.nunique(), "asteroids;", len(A), "pairs;", A.ncls.value_counts().to_dict(), "; places", len(P),
      P.kind.value_counts().to_dict(), "; unmatched", int(pl.country.isna().sum()))

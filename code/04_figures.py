"""Step 4: static figures for the blog (release/blog/b_*.png, 1800 px wide), the paper (release/paper/f_*.png) and the
social card (header.png). Parchment, ink, Fraunces titles, IBM Plex Mono labels; labels on paper or sea."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
import numpy as np, pandas as pd, geopandas as gpd, textwrap
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf"); DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"): fm.fontManager.addfont(f"{FONTS}/{f}")
plt.rcParams.update({"font.family": "IBM Plex Mono", "font.size": 12})
BG, FG, MUT, SEA, LAND = "#F6EED8", "#2B2119", "#6E604E", "#DCE6E4", "#EFE2BF"
HALO = [pe.withStroke(linewidth=3.5, foreground="white")]
R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/asteroids.csv"); p = A[A.ncls == "place"].copy()
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper")
for d in (BL, PA): os.makedirs(d, exist_ok=True)
land = gpd.read_file(f"{GEO}/ne_50m_land.geojson")
cty = gpd.read_file(f"{GEO}/ne_50m_admin_0_countries.geojson")


def save(fig, name):
    fig.savefig(f"{BL}/b_{name}.png", dpi=200, facecolor=BG); fig.savefig(f"{PA}/f_{name}.png", dpi=150, facecolor=BG); plt.close(fig)


def title(fig, t, sub, y=.965):
    h = fig.get_size_inches()[1]
    fig.text(.03, y, t, fontproperties=DISP, fontsize=25, color=FG, va="top")
    fig.text(.03, y - .5 / h, "\n".join(textwrap.wrap(sub, 84)), fontsize=11.5, color=MUT, va="top", linespacing=1.35)


def foot(fig): fig.text(.03, .015, "Data: Wikidata (CC0); Natural Earth. maps.tristanhotham.com/asteroid-towns", fontsize=9.5, color=MUT)


def earth(ax, ext, borders=False):
    ax.set_facecolor(SEA); land.plot(ax=ax, color=LAND, edgecolor="#8C7A58", linewidth=.35, zorder=1)
    if borders: cty.boundary.plot(ax=ax, color="#B9AC8E", linewidth=.3, zorder=1)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values(): s.set_edgecolor(FG)


def gc(lon1, lat1, lon2, lat2, n=40):
    r = np.radians; v1 = np.array([np.cos(r(lat1)) * np.cos(r(lon1)), np.cos(r(lat1)) * np.sin(r(lon1)), np.sin(r(lat1))])
    v2 = np.array([np.cos(r(lat2)) * np.cos(r(lon2)), np.cos(r(lat2)) * np.sin(r(lon2)), np.sin(r(lat2))])
    d = np.arccos(np.clip(v1 @ v2, -1, 1))
    if d < 1e-6: return np.array([lon1, lon2]), np.array([lat1, lat2])
    t = np.linspace(0, 1, n)[:, None]; v = (np.sin((1 - t) * d) * v1 + np.sin(t * d) * v2) / np.sin(d)
    lo = np.degrees(np.arctan2(v[:, 1], v[:, 0])); la = np.degrees(np.arctan2(v[:, 2], np.hypot(v[:, 0], v[:, 1])))
    lo = np.degrees(np.unwrap(np.radians(lo)))
    return lo, la


def lines(ax, rows, lw=.35, alpha=.18):
    for r in rows.itertuples():
        if np.isnan(r.site_lon): continue
        lo, la = gc(r.site_lon, r.site_lat, r.lon, r.lat)
        for sh in (0, -360, 360): ax.plot(lo + sh, la, color=KIND_COL[r.kind], lw=lw, alpha=alpha, zorder=2)


def dots(ax, rows, s=10):
    for k in PLACE_KINDS[::-1]:
        x = rows[rows.kind == k]; ax.scatter(x.lon, x.lat, s=s, c=KIND_COL[k], edgecolor=FG, linewidth=.25, zorder=4)


def stars(ax, rows, mn=1):
    o = rows.groupby("site").agg(lon=("site_lon", "first"), lat=("site_lat", "first"), n=("aid", "size"))
    o = o[o.n >= mn]; ax.scatter(o.lon, o.lat, s=25 + 1.2 * o.n, marker="*", c=FG, edgecolor="white", linewidth=.6, zorder=5)
    return o


def world():
    fig = plt.figure(figsize=(9, 5.6)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.03, .1, .94, .72]); earth(ax, (-170, 180, -58, 80))
    lines(ax, p, .3, .12); dots(ax, p, 8); stars(ax, p, 3)
    hs = [plt.scatter([], [], s=40, c=KIND_COL[k], edgecolor=FG, linewidth=.3) for k in PLACE_KINDS] + [plt.scatter([], [], s=70, marker="*", c=FG)]
    fig.legend(hs, [KIND_NAME[k].replace(", universities and other institutions", " and institutions").replace(", islands and other natural features", " and islands") for k in PLACE_KINDS] + ["Discovery site"], loc="lower center", ncol=4, frameon=False, fontsize=8.5, bbox_to_anchor=(.5, .025))
    title(fig, "Every place on Earth with an asteroid", f"{R['source']['place_asteroids']:,} asteroids ({R['source']['place']:,} namings) named after places, by kind of place, with a line to the observatory that found each one.")
    save(fig, "world")


def kinds():
    fig = plt.figure(figsize=(9, 4.4)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.17, .2, .8, .5]); ax.set_facecolor(BG)
    S = R["source"]; x = 0
    for k, v, c in (("People", S["person"], "#8C8478"), ("Places", S["place"], "#A3261B"), ("Other", S["other"], "#D3C29A")):
        ax.barh(1, v, left=x, color=c, edgecolor=BG, height=.6); ax.text(x + 80, 1, f"{k} {100 * v / S['pairs']:.0f}%", va="center", color="white" if c != "#D3C29A" else FG, fontsize=11); x += v
    x = 0; tot = S["place"]
    for k in PLACE_KINDS:
        v = R["kinds"][k]["n"]; ax.barh(0, v * S["pairs"] / tot, left=x, color=KIND_COL[k], edgecolor=BG, height=.6)
        if v / tot > .07: ax.text(x + 80, 0, f"{100 * v / tot:.0f}%", va="center", color="white", fontsize=11)
        x += v * S["pairs"] / tot
    ax.set_yticks([1, 0]); ax.set_yticklabels(["All namings", "Places"], fontsize=12); ax.set_xticks([]); [s.set_visible(False) for s in ax.spines.values()]; ax.tick_params(length=0)
    hs = [plt.Rectangle((0, 0), 1, 1, color=KIND_COL[k]) for k in PLACE_KINDS]
    fig.legend(hs, [KIND_NAME[k] for k in PLACE_KINDS], loc="lower center", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(.55, -.01))
    title(fig, "One asteroid in five is named after a place", f"Namings of {S['asteroids']:,} asteroids with a recorded namesake (top), and the {S['place']:,} place namings by kind (bottom).")
    save(fig, "kinds")


def countries():
    fig, axs = plt.subplots(1, 2, figsize=(9, 5.6)); fig.patch.set_facecolor(BG)
    plt.subplots_adjust(left=.17, right=.96, top=.7, bottom=.08, wspace=.75)
    for ax, rows, key, c, t in ((axs[0], R["countries"][:12], "n", "#A3261B", "Place namings"), (axs[1], R["per_m"][:12], "per_m", "#2F5FA7", "Per million people")):
        ax.set_facecolor(BG); ax.barh(range(len(rows)), [r[key] for r in rows], color=c, height=.7)
        for i, r in enumerate(rows): ax.text(r[key] * 1.02, i, f"{r[key]:,}" if key == "n" else f"{r[key]:.1f}", va="center", fontsize=9.5)
        ax.set_yticks(range(len(rows))); ax.set_yticklabels([r["country"].replace("United States", "US").replace("United Kingdom", "UK").replace("Czech Republic", "Czechia") for r in rows], fontsize=10)
        ax.invert_yaxis(); ax.set_xticks([]); ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
        ax.set_xlim(0, max(r[key] for r in rows) * 1.25); ax.set_title(t, fontproperties=DISPB, fontsize=14, loc="left", color=FG)
    title(fig, "Japan has the most, Finland the most per head", "Asteroids named after places, by modern country. Per head: countries of a million people or more with at least five.")
    foot(fig); save(fig, "countries")


def observatories():
    O = R["obs"][:12][::-1]
    fig = plt.figure(figsize=(9, 5.8)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.36, .08, .6, .64]); ax.set_facecolor(BG)
    for i, o in enumerate(O):
        own = o["n"] * o["same_pct"] / 100
        ax.barh(i, o["n"], color="#D3C29A", height=.7); ax.barh(i, own, color="#A3261B", height=.7)
        ax.text(o["n"] + 3, i, f"{o['n']}  ({o['same_pct']:.0f}% home)", va="center", fontsize=9.5)
    ax.set_yticks(range(len(O))); ax.set_yticklabels([f"{o['site'].replace(' Observatory', '').replace('Astrophysical', 'Astroph.')}, {o['country'].replace('United States', 'US').replace('Czech Republic', 'Czechia').replace('Ukraine (Crimea)', 'Crimea')}" for o in O], fontsize=9.5)
    ax.set_xticks([]); ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]; ax.set_xlim(0, 300)
    hs = [plt.Rectangle((0, 0), 1, 1, color="#A3261B"), plt.Rectangle((0, 0), 1, 1, color="#D3C29A")]
    fig.legend(hs, ["Place in the observatory's own country", "Elsewhere"], loc="upper left", ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(.35, .79))
    title(fig, "Who named the places", "The twelve discovery sites with the most place namings, and how many of those places are in the observatory's own country.")
    foot(fig); save(fig, "observatories")


def distance():
    t = p[p.dist_km.notna()]
    edges = [0, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 20100]; lab = ["<10", "10", "25", "50", "100", "250", "500", "1k", "2.5k", "5k", "10k+"]
    n, _ = np.histogram(t.dist_km, bins=edges)
    fig = plt.figure(figsize=(9, 4.8)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.08, .16, .89, .58]); ax.set_facecolor(BG)
    ax.bar(range(len(n)), n, color=["#A3261B" if e <= 100 else "#B9AC8E" for e in edges[1:]], width=.8)
    for i, v in enumerate(n): ax.text(i, v + 4, str(v), ha="center", fontsize=9.5)
    ax.set_xticks(range(len(n))); ax.set_xticklabels(lab, fontsize=10); ax.set_yticks([]); [ax.spines[s].set_visible(False) for s in ("top", "right", "left")]
    ax.set_xlabel("kilometres from the discovery site to the place (bins start at the label)", fontsize=10, color=MUT)
    title(fig, "How far from the telescope", f"All {len(t):,} place namings with both positions. Red: under 100 km ({R['dist']['w100_pct']:.0f}%). Median {R['dist']['median']:,} km.")
    save(fig, "distance")


def home():
    fig = plt.figure(figsize=(9, 5.4)); fig.patch.set_facecolor(BG)
    for k, (site, ext, t) in enumerate((("Kleť Observatory", (11.6, 19.2, 47.4, 51.3), "Kleť Observatory, Czech Republic"),
                                        (None, (128.5, 146, 30.5, 45.8), "Japan's observatories"))):
        ax = fig.add_axes([.03 + k * .49, .07, .45, .6]); earth(ax, ext, borders=True)
        rows = p[p.site == site] if site else p[(p.site_iso3 == "JPN") & (p.iso3 == "JPN")]
        inn = rows[(rows.lon.between(ext[0], ext[1])) & (rows.lat.between(ext[2], ext[3]))]
        lines(ax, inn, .7, .55); dots(ax, inn, 16); stars(ax, inn)
        ax.set_title(t, fontproperties=DISPB, fontsize=13, loc="left", color=FG)
        ax.text(.02, .03, f"{len(inn)} of {len(rows)} places shown", transform=ax.transAxes, fontsize=9.5, color=FG, path_effects=HALO)
    title(fig, "Naming the next valley", f"Places named from Kleť ({R['homeliest'][1]['w100_pct']:.0f}% within 100 km) and Japanese places named from Japanese observatories, with lines to the discovery site.")
    foot(fig); save(fig, "home")


def header():
    fig = plt.figure(figsize=(12, 6.3), dpi=100); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.42, .08, .56, .84]); earth(ax, (-20, 150, -45, 72)); lines(ax, p, .35, .15); dots(ax, p, 9); stars(ax, p, 5)
    fig.text(.04, .8, "Towns with", fontproperties=DISP, fontsize=46, color=FG)
    fig.text(.04, .67, "an asteroid", fontproperties=DISP, fontsize=46, color="#A3261B")
    fig.text(.04, .55, f"{R['source']['place_asteroids']:,} minor planets\n({R['source']['place']:,} namings) named\nafter places on Earth", fontsize=17, color=FG, va="top", linespacing=1.4)
    fig.text(.04, .27, f"Japan: {R['countries'][0]['n']}. Finland: {R['per_m'][0]['per_m']:.1f}\nper million people. The UK: {R['uk']['n']}.", fontsize=14, color=MUT, va="top", linespacing=1.4)
    fig.text(.04, .06, "maps.tristanhotham.com/asteroid-towns", fontsize=11, color=MUT)
    fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)


world(); kinds(); countries(); observatories(); distance(); home(); header()
from PIL import Image
assert Image.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
print(sorted(os.listdir(BL)))

"""Reddit collage (r/dataisbeautiful style): light parchment poster, 2560 x 1760 px. Run from the study root after
code/02_analysis.py and code/04_figures.py (fonts). Labels sit on sea or paper with a halo, never over land or data."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
import numpy as np, pandas as pd, geopandas as gpd
from common import *

FD = os.path.join(WORK, "fonts")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf"); DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"): fm.fontManager.addfont(f"{FONTS}/{f}")
plt.rcParams.update({"font.family": "IBM Plex Mono"})
BG, FG, MUT, SEA, LAND = "#F7F0DC", "#2B2119", "#6E604E", "#DDE7E5", "#EFE2BF"
HALO = [pe.withStroke(linewidth=4, foreground="white")]
R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/asteroids.csv"); p = A[A.ncls == "place"]
land = gpd.read_file(f"{GEO}/ne_50m_land.geojson"); cty = gpd.read_file(f"{GEO}/ne_50m_admin_0_countries.geojson")


def earth(ax, ext, borders=False):
    ax.set_facecolor(SEA); land.plot(ax=ax, color=LAND, edgecolor="#8C7A58", linewidth=.4)
    if borders: cty.boundary.plot(ax=ax, color="#B9AC8E", linewidth=.4)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values(): s.set_edgecolor(FG)


def gc(lon1, lat1, lon2, lat2, n=40):
    r = np.radians; v1 = np.array([np.cos(r(lat1)) * np.cos(r(lon1)), np.cos(r(lat1)) * np.sin(r(lon1)), np.sin(r(lat1))])
    v2 = np.array([np.cos(r(lat2)) * np.cos(r(lon2)), np.cos(r(lat2)) * np.sin(r(lon2)), np.sin(r(lat2))])
    d = np.arccos(np.clip(v1 @ v2, -1, 1))
    if d < 1e-6: return np.array([lon1, lon2]), np.array([lat1, lat2])
    t = np.linspace(0, 1, n)[:, None]; v = (np.sin((1 - t) * d) * v1 + np.sin(t * d) * v2) / np.sin(d)
    lo = np.degrees(np.unwrap(np.arctan2(v[:, 1], v[:, 0]))); la = np.degrees(np.arctan2(v[:, 2], np.hypot(v[:, 0], v[:, 1])))
    return lo, la


def draw(ax, rows, lw, al, s):
    for r in rows.itertuples():
        if np.isnan(r.site_lon): continue
        lo, la = gc(r.site_lon, r.site_lat, r.lon, r.lat)
        for sh in (0, -360, 360): ax.plot(lo + sh, la, color=KIND_COL[r.kind], lw=lw, alpha=al)
    for k in PLACE_KINDS[::-1]:
        x = rows[rows.kind == k]; ax.scatter(x.lon, x.lat, s=s, c=KIND_COL[k], edgecolor=FG, linewidth=.3, zorder=4)
    o = rows.groupby("site").agg(lon=("site_lon", "first"), lat=("site_lat", "first"), n=("aid", "size"))
    ax.scatter(o.lon, o.lat, s=40 + 2 * o.n, marker="*", c=FG, edgecolor="white", linewidth=.8, zorder=5)


fig = plt.figure(figsize=(16, 11), dpi=160); fig.patch.set_facecolor(BG)
fig.text(.03, .955, "Towns with an asteroid", fontproperties=DISP, fontsize=44, color=FG, va="top")
fig.text(.03, .885, f"{R['source']['place_asteroids']:,} asteroids ({R['source']['place']:,} namings) named after places on Earth, each joined to the observatory (black star) that found it", fontsize=14, color=MUT, va="top")
ax = fig.add_axes([.03, .41, .66, .45]); earth(ax, (-125, 155, -48, 75)); draw(ax, p, .35, .16, 9)
ls = p[p.site == "La Silla Observatory"].iloc[0]
ax.annotate(f"La Silla, Chile:\n{R['obs'][0]['n']} places,\nonly {R['obs'][0]['same_pct']:.0f}% of\nthem Chilean", (ls.site_lon, ls.site_lat), (-123, -6), textcoords="data", va="top", ha="left", fontsize=12, color=FG, path_effects=HALO,
            arrowprops=dict(arrowstyle="-", color=FG, lw=.9, shrinkB=4))
for k, (rows, ext, t, sub) in enumerate(((p[p.site == "Kleť Observatory"], (11.8, 19.0, 47.6, 51.2), "Kleť Observatory, Czech Republic", f"{R['obs'][3]['n']} places, {R['homeliest'][1]['w100_pct']:.0f}% within 100 km"),
                                         (p[(p.site_iso3 == "JPN") & (p.iso3 == "JPN")], (129, 146, 30.5, 45.6), "Japan, named from Japan", f"{R['jp']['home_pct']:.0f}% of Japan's {R['jp']['n']} places"))):
    a = fig.add_axes([.03 + k * .25, .06, .23, .255]); earth(a, ext, borders=True)
    inn = rows[rows.lon.between(ext[0], ext[1]) & rows.lat.between(ext[2], ext[3])]
    draw(a, inn, .8, .6, 16)
    fig.text(.03 + k * .25, .36, t, fontproperties=DISPB, fontsize=15, color=FG)
    fig.text(.03 + k * .25, .345, sub, fontsize=11.5, color=MUT, va="top")

x0 = .73
def stat(y, big, small):
    fig.text(x0, y, big, fontproperties=DISP, fontsize=40, color="#A3261B", va="top")
    fig.text(x0, y - .065, small, fontsize=13, color=FG, va="top", linespacing=1.4)
stat(.85, f"{R['countries'][0]['n']}", f"places in Japan, the most;\nGermany {R['countries'][1]['n']}, Russia {R['countries'][2]['n']}")
stat(.68, f"{R['per_m'][0]['per_m']:.1f}", f"per million people in Finland,\nthe most per head; Czechia\n{R['per_m'][1]['per_m']:.1f}, Sweden {R['per_m'][2]['per_m']:.1f}")
stat(.48, f"{R['source']['place_pct']:.0f}%", f"of asteroid namesakes are places;\n{R['source']['person_pct']:.0f}% are people")
stat(.31, f"{R['dist']['median']} km", "median distance from the\nobservatory to the place")

fig.text(.53, .345, "Kind of place", fontsize=13, color=FG, fontweight="medium")
names = {"town": "Town, city or village", "region": "Region or province", "country": "Country", "water": "River or lake",
         "nature": "Mountain or island", "inst": "Institution", "other": "Other place"}
for i, k in enumerate(PLACE_KINDS):
    yy = .31 - i * .03
    fig.patches.append(plt.Circle((.538, yy + .006), .0062, transform=fig.transFigure, fc=KIND_COL[k], ec=FG, lw=.5))
    fig.text(.55, yy, names[k], fontsize=12, color=FG)
from matplotlib.lines import Line2D
fig.lines.append(Line2D([.538], [.31 - 7 * .03 + .006], marker="*", ms=16, color=FG, mec="white", transform=fig.transFigure)); fig.text(.55, .31 - 7 * .03, "Discovery site", fontsize=12, color=FG)
fig.text(.03, .022, "Source: Wikidata (CC0) via QLever, only the asteroids Wikidata links to a namesake; Natural Earth.   Dr Tristan Hotham · maps.tristanhotham.com/asteroid-towns",
         fontsize=10.5, color=MUT)
out = os.path.join(ROOT, "reddit", "asteroid_towns_collage.png")
fig.savefig(out, dpi=160, facecolor=BG); plt.close(fig)
from PIL import Image
print(out, Image.open(out).size)

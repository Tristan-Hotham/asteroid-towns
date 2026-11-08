"""Step 5: the paper, from code/paper_template.tex and data/results.json, compiled with xelatex.
Output: release/paper/Hotham_Asteroid_Towns.pdf and .tex beside the f_*.png figures. The DOI stays as 10.5281/zenodo.24052725."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Asteroid_Towns"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")
A = pd.read_csv(f"{DATA}/asteroids.csv"); p = A[A.ncls == "place"]
fi = p[p.iso3 == "FIN"]; assert (fi.site_iso3 == "FIN").all() and fi.site.value_counts().index[0] == "Iso-Heikkilä Observatory" and fi.site.value_counts().iloc[0] > len(fi) / 2
se = p[p.iso3 == "SWE"]; assert (se.site_iso3 != "SWE").all()
assert R["homeliest"][0]["site"] == "Nanyo Observatory" and R["homeliest"][2]["site"] == "Geisei observatory"


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


rows = "".join(f"{tex(c['country'])} & {c['n']:,} & {c['pct']:.1f} & {c['per_m']:.2f}\\\\\n" for c in R["countries"][:15])
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{The fifteen countries with the most place namings.}\\label{tab:cty}\\begin{tabular}{lrrr}\\toprule "
      "Country & Places & Share (\\%) & Per million\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(o['site'])} & {tex(o['country'])} & {o['n']} & {o['same_pct']:.1f} & {o['median_km']:,} & {o['w100_pct']:.1f}\\\\\n" for o in R["obs"])
TO = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{The fifteen discovery sites with the most place namings: share in the site's own country, median distance and share within 100 km.}\\label{tab:obs}"
      "\\begin{tabular}{llrrrr}\\toprule Site & Country & Places & Own (\\%) & Median km & $<$100 km (\\%)\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(u['asteroid'])} & {tex(u['place'])} & {tex(u['site'] or '')} & {u['year'] or ''} & {'' if u['km'] is None else f'{u[chr(107)+chr(109)]:,}'}\\\\\n" for u in R["uk"]["list"])
TU = ("{\\footnotesize\\begin{longtable}{p{3.4cm}p{4.2cm}p{4.6cm}rr}\\caption{Asteroids named after places in the United Kingdom.}\\label{tab:uk}\\\\\\toprule Asteroid & Place & Discovery site & Year & km\\\\\\midrule\\endfirsthead"
      "\\toprule Asteroid & Place & Discovery site & Year & km\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\url{{{meta.page}}}", "\\url{%s}" % PAGE).replace("\\url{{{meta.repo}}}", "\\url{%s}" % REPO)
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("CTY", TC), ("OBS", TO), ("UK", TU)): t = t.replace("{{TABLE_%s}}" % k, v)
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower()][:10])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))

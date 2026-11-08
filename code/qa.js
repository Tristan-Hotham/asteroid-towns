// QA: open index.html at desktop and phone widths, log console errors, exercise the map, screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server 8802).
const { chromium } = require("playwright");
const ML = process.env.MAPLIBRE_DIST || "/tmp/ml/node_modules/maplibre-gl/dist";
(async () => {
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const errs = [], checks = [], ok = (c, m) => checks.push((c ? "ok   " : "FAIL ") + m);
  for (const [nm, vw, vh] of [["desktop", 1280, 900], ["phone", 390, 844]]) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/googleapis|gstatic|amazonaws|site-nav/, r => r.abort());
    await p.route(/maplibre-gl\.js$/, r => r.fulfill({ path: ML + "/maplibre-gl.js" }));
    await p.route(/maplibre-gl\.css$/, r => r.fulfill({ path: ML + "/maplibre-gl.css" }));
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::|Failed to load resource|AJAXError|tiles?|terrarium/i.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + (process.env.PORT || 8802) + "/index.html", { waitUntil: "load" });
    await p.waitForTimeout(9000);
    await p.screenshot({ path: `qa/${nm}_top.png` });
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(700); await p.locator(sel).screenshot({ path: `qa/${nm}_${f}.png` }); };
    await shot("#atlas", "map");
    ok(await p.evaluate(() => ready && map.querySourceFeatures("pl").length > 500), `${nm}: places drawn`);
    await p.evaluate(() => pickPlace(Object.values(PL).find(q => q.name === "Midsomer Norton").nid, true)); await p.waitForTimeout(2200);
    ok(await p.locator(".maplibregl-popup").count() === 1, `${nm}: place popup`);
    await shot("#atlas", "pick_midsomer");
    await p.evaluate(() => pickObs(SITE.obs.findIndex(o => o[0] === "Kleť Observatory"), true)); await p.waitForTimeout(2200);
    ok(await p.evaluate(() => map.getSource("ln")._data.features.length > 50), `${nm}: Kleť lines`);
    await shot("#atlas", "kleť");
    await p.evaluate(() => pickObs(SITE.obs.findIndex(o => o[0] === "La Silla Observatory"), true)); await p.waitForTimeout(2200);
    await shot("#atlas", "lasilla");
    await p.fill("#q", "brighton"); await p.waitForTimeout(400); ok(await p.locator("#sug li").count() > 0, `${nm}: search`);
    await p.keyboard.press("Enter"); await p.waitForTimeout(2200);
    ok(await p.evaluate(() => S.place && PL[S.place].name === "Brighton"), `${nm}: search picks Brighton`);
    await p.click('#kindRow [data-k="0"]'); await p.waitForTimeout(500);
    ok(await p.evaluate(() => S.off.has(0)), `${nm}: kind filter`); await p.click('#kindRow [data-k="0"]');
    await p.locator(".lyrBtn").click(); await p.waitForTimeout(300);
    await p.locator('.lyrPanel [data-k="lines"]').uncheck(); await p.waitForTimeout(300);
    ok(await p.evaluate(() => map.getLayoutProperty("ln", "visibility") === "none"), `${nm}: lines toggle`);
    await shot("#map", "layers"); await p.locator('.lyrPanel [data-k="lines"]').check(); await p.locator(".lyrBtn").click();
    for (const c of ["kindChart", "ctyChart", "obsTable", "distChart", "ukTable"]) await shot("#" + c, c);
    await p.locator("#atlas").scrollIntoViewIfNeeded();
    ok(await p.locator(".mfs-btn").count() === 1, `${nm}: full-screen button`);
    await p.locator(".mfs-btn").click(); await p.waitForTimeout(1200);
    ok(await p.evaluate(() => !!document.fullscreenElement || document.getElementById("map").classList.contains("mfs-fake")), `${nm}: full screen on`);
    await p.screenshot({ path: `qa/${nm}_fullscreen.png` }); await p.locator(".mfs-btn").click(); await p.waitForTimeout(500);
    if (nm === "phone") { await p.click("#theme"); await p.waitForTimeout(600); await shot("#ctyChart", "dark_cty"); }
    ok(await p.evaluate(() => document.documentElement.scrollWidth - innerWidth) <= 0, `${nm}: no horizontal overflow`);
    await p.close();
  }
  console.log(checks.join("\n")); console.log("errors:", errs.length ? errs : "none"); await b.close();
})();

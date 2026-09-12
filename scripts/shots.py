"""Render PNG stills of a champion with headless Chromium and the project's own replay page.

    ./v/bin/python scripts/shots.py RUN KIND GEN OUTDIR [SEED]

Records one solo bout (the run's config, opponent proxy on, spawn from SEED),
writes the replay HTML with three.js inlined from a local copy if present
(OUTDIR/three.min.js; otherwise the CDN, which needs network), then
screenshots frames at 0, 5, 10 and 15 s from an isometric and a side camera
plus two close-ups, and assembles OUTDIR/<name>_sheet.png.  Needs the
``playwright`` and ``pillow`` packages and a Chromium at
/opt/pw-browsers/chromium (or set CHROMIUM).
"""
import asyncio, json, os, sys
from dataclasses import replace

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.visualizer import THREE_JS_URL, to_html

run, kind, gen, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 3
name = f"{os.path.basename(run.rstrip('/'))}-{kind}-g{gen}"
os.makedirs(out, exist_ok=True)
cfg = replace(SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"]), opponent_proxy=True)
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
sim = Simulation([g], cfg, spawns=[spawn_layout(2, cfg, seed)[0]]); sim.start_recording(); sim.run()
html = to_html(sim.trajectory, title=name)
if os.path.exists(f"{out}/three.min.js"):
    html = html.replace(THREE_JS_URL, "three.min.js")
html = html.replace("replay.load(DATA); transport.reload();", "replay.load(DATA); transport.reload(); window.replay = replay; window.transport = transport; transport.playing = false;")
html = html.replace('<div id="hud">', '<div id="hud" style="display:none">').replace('<div id="help">', '<div id="help" style="display:none">')
page_path = f"{out}/{name}.html"; open(page_path, "w").write(html)
n = sim.trajectory.n_frames
FRAME_JS = """([k, theta, phi, radius]) => {
  transport.playing = false; replay.applyFrame(k);
  const c = new THREE.Vector3(); let n = 0; for (const m of replay.meshes) { c.add(m.position); n++; } c.multiplyScalar(1 / Math.max(1, n));
  replay.target.set(c.x, c.z + 0.05, -c.y); replay.theta = theta; replay.phi = phi; replay.radius = radius; replay.render(); }"""
SHOTS = [("rest", 0, 0.8, 1.1, 2.6), ("t05", int(0.33 * (n - 1)), 0.8, 1.1, 2.6), ("t10", int(0.66 * (n - 1)), 0.8, 1.1, 2.6), ("end", n - 1, 0.8, 1.1, 2.6),
         ("close1", 30, 0.6, 1.15, 1.5), ("close2", 30, 2.4, 1.0, 1.5)]


async def shoot():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium"), args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1400, "height": 900})
        await pg.goto(f"file://{os.path.abspath(page_path)}"); await pg.wait_for_function("window.replay && replay.frameCount > 0")
        for tag, k, theta, phi, r in SHOTS:
            await pg.evaluate(FRAME_JS, [k, theta, phi, r]); await pg.wait_for_timeout(150)
            await pg.locator("#view canvas").screenshot(path=f"{out}/{name}_{tag}.png")
        await b.close()


asyncio.run(shoot())
from PIL import Image, ImageDraw, ImageFont

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22); small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    font = small = ImageFont.load_default()
W, H = 700, 450
sheet = Image.new("RGB", (2 * W + 30, 60 + 3 * (H + 10) + 10), (28, 30, 36)); d = ImageDraw.Draw(sheet)
d.text((15, 14), f"{name}: solo bout, spawn seed {seed}, progress {sim.distance_from_center(0):.2f} m", fill=(235, 235, 235), font=font)
labels = {"rest": "t = 0 s (after settling)", "t05": "t = 5 s", "t10": "t = 10 s", "end": "t = 15 s", "close1": "close-up, t = 1.2 s", "close2": "close-up, t = 1.2 s"}
for i, (tag, *_) in enumerate(SHOTS):
    im = Image.open(f"{out}/{name}_{tag}.png").resize((W, H)); x = 10 + (i % 2) * (W + 10); y = 60 + (i // 2) * (H + 10)
    sheet.paste(im, (x, y)); d.text((x + 10, y + 8), labels[tag], fill=(235, 235, 235), font=small)
sheet.save(f"{out}/{name}_sheet.png"); print(f"wrote {out}/{name}_sheet.png")

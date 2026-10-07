"""Render the fictional demo report and page images (dev helper)."""
import glob, subprocess, sys
from pathlib import Path
from PIL import Image
from fra.demo import demo_case, AUDIT_DATE
from fra.engine.audit import run_audit
from fra.report.render import render_pdf

out = Path("data/out"); out.mkdir(parents=True, exist_ok=True)
c = demo_case(); r = run_audit(c, AUDIT_DATE)
render_pdf(c, r, out=out / "demo.pdf")
png = out / "png"; subprocess.run(["rm", "-rf", str(png)]); png.mkdir()
subprocess.run(["pdftoppm", "-r", "60", "-png", str(out / "demo.pdf"), str(png / "p")], check=True)
fs = sorted(glob.glob(str(png / "p-*.png")))
print("pages", len(fs))
for i in range(0, len(fs), 8):
    ims = [Image.open(f) for f in fs[i:i + 8]]
    w, h = ims[0].size
    S = Image.new("RGB", (w * 4, h * 2), "white")
    for j, im in enumerate(ims):
        S.paste(im.resize((w, h)), ((j % 4) * w, (j // 4) * h))
    S.save(png / f"sheet{i // 8 + 1}.png")

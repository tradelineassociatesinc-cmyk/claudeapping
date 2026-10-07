"""Render the fictional demo report to data/out/demo.pdf.
Pass --images to also write page images (needs pdftoppm and Pillow)."""
import glob
import subprocess
import sys
from pathlib import Path

from fra.demo import AUDIT_DATE, demo_case
from fra.engine.audit import run_audit
from fra.report.render import find_forbidden, render_html, render_pdf

out = Path("data/out")
out.mkdir(parents=True, exist_ok=True)
case = demo_case()
result = run_audit(case, AUDIT_DATE)
bad = find_forbidden(render_html(case, result))
if bad:
    sys.exit(f"Report contains prohibited phrases: {bad}")
render_pdf(case, result, out=out / "demo.pdf")
print("wrote", out / "demo.pdf")

if "--images" in sys.argv:
    from PIL import Image
    png = out / "png"
    subprocess.run(["rm", "-rf", str(png)])
    png.mkdir()
    subprocess.run(["pdftoppm", "-r", "60", "-png", str(out / "demo.pdf"), str(png / "p")], check=True)
    fs = sorted(glob.glob(str(png / "p-*.png")))
    print("pages", len(fs))
    for i in range(0, len(fs), 8):
        ims = [Image.open(f) for f in fs[i:i + 8]]
        w, h = ims[0].size
        sheet = Image.new("RGB", (w * 4, h * 2), "white")
        for j, im in enumerate(ims):
            sheet.paste(im.resize((w, h)), ((j % 4) * w, (j // 4) * h))
        sheet.save(png / f"sheet{i // 8 + 1}.png")

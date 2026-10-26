import base64, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
tpl  = open(os.path.join(HERE, "src/template.html"), encoding="utf-8").read()

# ---- sprites ----
entries = []
for f in sorted(glob.glob(os.path.join(HERE, "sprites/*.png"))):
    key = os.path.splitext(os.path.basename(f))[0]
    b64 = base64.b64encode(open(f, "rb").read()).decode()
    entries.append(f'  {key}: "data:image/png;base64,{b64}"')
out = tpl.replace("/*__SPRITES__*/{}", "{\n" + ",\n".join(entries) + "\n}")

# ---- video: any .mp4/.webm dropped into game/video/ ----
vids = sorted(glob.glob(os.path.join(HERE, "video/*.mp4")) +
              glob.glob(os.path.join(HERE, "video/*.webm")))
if vids:
    f = vids[0]
    mime = "video/mp4" if f.endswith(".mp4") else "video/webm"
    raw = open(f, "rb").read()
    b64 = base64.b64encode(raw).decode()
    out = out.replace("/*__VIDEO__*/{}", '{\n  1: "data:%s;base64,%s"\n}' % (mime, b64))
    print(f"video: {os.path.basename(f)} - {len(raw)/1048576:.1f} MB "
          f"({len(b64)/1048576:.1f} MB embedded)")
    if len(vids) > 1:
        print(f"  note: {len(vids)} files found, using {os.path.basename(f)} only")
else:
    print("video: none (drop one .mp4 into game/video/ - the step is skipped)")

dst = os.path.join(HERE, "alisa_obby.html")
open(dst, "w", encoding="utf-8").write(out)
size = len(out) / 1048576
print(f"built {dst} — {size:.1f} MB")
if size > 15:
    print("  !! over 15 MB — compress the videos more (page limit is 16 MB)")

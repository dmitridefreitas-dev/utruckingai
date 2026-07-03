import sys, json, pathlib, html
from pypdf import PdfReader

out_dir = pathlib.Path(sys.argv[1])   # where the component PDFs live (root)
src_dir = pathlib.Path(sys.argv[2])   # where to write temp files (source)

sections = [
    ("Executive Brief - Start Here", "EXEC_BRIEF.pdf"),
    ("The Plan - Done, Value, Next & Required", "PLAN.pdf"),
    ("Phone & SMS - Setup Plan", "PHONE_SMS_PLAN.pdf"),
    ("The Numbers - Data & Revenue Audit", "UTrucking_Data_Audit.pdf"),
    ("Reference: Call Journey", "UTrucking_Call_Journey.pdf"),
    ("Reference: Agent Flow (Conversation Map)", "UTrucking_Voice_Agent_Flow.pdf"),
    ("Reference: Connections & Infrastructure", "CONNECTIONS.pdf"),
    ("Reference: QA & Testing Log", "TEST_LOG.pdf"),
    ("Visual Recap - Executive Slides", "UTrucking_Executive_Deck.pdf"),
]

# --- Layout constants, in CSS px. The page is forced to Letter with margin:0,
# so 816x1056 CSS px maps 1:1 onto a 612x792 pt PDF page (factor 0.75).
# The SAME numbers are reused below to compute click rectangles, so the
# invisible link band always sits exactly under the visible row. ---
PX2PT      = 0.75
PAGE_H_PT  = 792.0
LEFT_PX    = 82        # left edge of content / click band
RIGHT_PX   = 734       # right edge of content / click band  (816 - 82)
ROW_TOP0   = 285       # top of the first row band
ROW_STEP   = 46        # vertical distance between rows
ROW_H      = 40        # height of each clickable band

# Which component PDFs actually exist, and where each one starts (page 1 = Contents)
present, page = [], 2
for title, f in sections:
    p = out_dir / f
    if not p.exists():
        continue
    n = len(PdfReader(str(p)).pages)
    present.append({"title": title, "file": f, "page": page})
    page += n

rows_html = []
for i, s in enumerate(present):
    top = ROW_TOP0 + i * ROW_STEP
    rows_html.append(
        "<div class='row' style='top:{top}px'>"
        "<span class='t'>{t}</span><span class='dots'></span><span class='p'>{pg}</span>"
        "</div>".format(top=top, t=html.escape(s["title"]), pg=s["page"])
    )
    # matching link rectangle, in PDF points (origin bottom-left)
    y_top = PAGE_H_PT - top * PX2PT
    y_bot = PAGE_H_PT - (top + ROW_H) * PX2PT
    s["rect"] = [LEFT_PX * PX2PT, y_bot, RIGHT_PX * PX2PT, y_top]
    s["target_index"] = s["page"] - 1     # 0-based page index in the merged PDF

foot_top = ROW_TOP0 + len(present) * ROW_STEP + 18
rows = "\n".join(rows_html)

doc = """<!doctype html><html><head><meta charset='utf-8'><style>
@page {{ size:letter; margin:0; }}
* {{ box-sizing:border-box; }}
body {{ position:relative; width:816px; height:1056px; margin:0;
       font-family:'Segoe UI',Arial,sans-serif; color:#1f2933; }}
.bar {{ position:absolute; top:0; left:0; width:816px; height:8px; background:#f5a623; }}
.eyebrow {{ position:absolute; top:70px; left:82px; text-transform:uppercase;
            letter-spacing:.18em; font-size:11px; font-weight:700; color:#f5a623; }}
h1 {{ position:absolute; top:86px; left:82px; margin:0; color:#14335f; font-size:40px; }}
.sub {{ position:absolute; top:150px; left:82px; color:#5b6b7f; font-size:17px; }}
.conh {{ position:absolute; top:224px; left:82px; width:652px; color:#14335f;
         font-size:20px; font-weight:700; padding-bottom:8px;
         border-bottom:2px solid #e3e9f2; }}
.row {{ position:absolute; left:82px; width:652px; height:40px;
        display:flex; align-items:center; font-size:17px; }}
.t {{ font-weight:600; color:#14335f; }}
.dots {{ flex:1; border-bottom:2px dotted #cdd6e4; margin:0 10px; transform:translateY(-5px); }}
.p {{ color:#1e5aa8; font-weight:700; }}
.foot {{ position:absolute; left:82px; top:{foot}px; color:#9aa7b8; font-size:10pt; }}
</style></head><body>
<div class="bar"></div>
<div class="eyebrow">University Trucking</div>
<h1>AI Phone Assistant - Full Report</h1>
<div class="sub">Progress, roadmap, and complete documentation &middot; July 2026</div>
<div class="conh">Contents</div>
{rows}
<div class="foot">Generated from source. Rebuild anytime with source/build.ps1 &nbsp;&middot;&nbsp; entries below are clickable.</div>
</body></html>""".format(foot=foot_top, rows=rows)

(src_dir / "_toc.html").write_text(doc, encoding="utf-8")
json.dump({"sections": present}, open(src_dir / "_manifest.json", "w"))
print("TOC rows:", [(s["title"], s["page"]) for s in present])

import sys, pathlib, html, markdown

src, out, title = sys.argv[1], sys.argv[2], sys.argv[3]
text = pathlib.Path(src).read_text(encoding="utf-8")
body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])

css = """
@page { size: letter; margin: 0.7in; }
body { font-family:'Segoe UI',Arial,sans-serif; color:#1f2933; font-size:12pt; line-height:1.5; }
h1 { color:#14335f; font-size:24pt; border-bottom:3px solid #f5a623; padding-bottom:8px; margin-bottom:6px; }
h2 { color:#14335f; font-size:16pt; margin-top:22px; }
h3 { color:#1e5aa8; font-size:13pt; margin-top:16px; }
table { border-collapse:collapse; width:100%; margin:14px 0; font-size:10.5pt; }
th,td { border:1px solid #d6deea; padding:7px 10px; text-align:left; vertical-align:top; }
th { background:#eef3fa; color:#14335f; }
tr:nth-child(even) td { background:#fafbfe; }
code { background:#f2f4f7; padding:1px 5px; border-radius:4px; font-family:Consolas,monospace; font-size:10.5pt; }
pre { background:#f7f9fc; border:1px solid #e3e9f2; border-radius:6px; padding:12px; overflow:auto; }
pre code { background:none; padding:0; }
ul,ol { margin:10px 0 10px 22px; } li { margin:5px 0; }
hr { border:none; border-top:1px solid #e3e9f2; margin:20px 0; }
strong { color:#14335f; }
a { color:#1e5aa8; word-break:break-all; }
"""

doc = ("<!doctype html><html><head><meta charset='utf-8'><title>"
       + html.escape(title) + "</title><style>" + css + "</style></head><body>"
       + body + "</body></html>")
pathlib.Path(out).write_text(doc, encoding="utf-8")
print("wrote", out)

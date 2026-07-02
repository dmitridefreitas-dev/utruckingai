import sys, json, pathlib
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DictionaryObject, ArrayObject, NameObject, NumberObject, FloatObject,
)

out_dir = pathlib.Path(sys.argv[1])   # component PDFs + final report (root)
src_dir = pathlib.Path(sys.argv[2])   # temp files (source)

man = json.load(open(src_dir / "_manifest.json"))
w = PdfWriter()

# Contents page first
for pg in PdfReader(str(src_dir / "_toc.pdf")).pages:
    w.add_page(pg)
w.add_outline_item("Contents", 0)

# each section: append its pages, drop a sidebar bookmark at its first page
for s in man["sections"]:
    idx = len(w.pages)
    for pg in PdfReader(str(out_dir / s["file"])).pages:
        w.add_page(pg)
    w.add_outline_item(s["title"], idx)


def make_link(rect, page_ref):
    """A /Link annotation whose destination is a real indirect page ref
    ([page /Fit]) — the spec-correct form every PDF viewer resolves."""
    d = DictionaryObject()
    d[NameObject("/Type")] = NameObject("/Annot")
    d[NameObject("/Subtype")] = NameObject("/Link")
    d[NameObject("/Rect")] = ArrayObject([FloatObject(x) for x in rect])
    d[NameObject("/Border")] = ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)])
    d[NameObject("/H")] = NameObject("/N")   # no highlight box on click
    d[NameObject("/Dest")] = ArrayObject([page_ref, NameObject("/Fit")])
    return d


toc_page = w.pages[0]
annots = ArrayObject()
for s in man["sections"]:
    page_ref = w.pages[s["target_index"]].indirect_reference
    link_ref = w._add_object(make_link(s["rect"], page_ref))
    annots.append(link_ref)
toc_page[NameObject("/Annots")] = annots

outp = out_dir / "UTrucking_AI_Assistant_Full_Report.pdf"
with open(outp, "wb") as fh:
    w.write(fh)
print("wrote", outp.name, len(w.pages), "pages, ", len(man["sections"]), "TOC links")

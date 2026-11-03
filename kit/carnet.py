"""Build Kevin's "Briefing et pitch — carnet quotidien" (.docx) from content.json.

Usage: python3 kit/carnet.py content.json OUT.docx

Standard trame (same as the 2 and 3 Nov 2026 carnets): the 6 numbers, three
economic headlines with the effect for a client or a structured product, the
geopolitical topic and the day's appointments, then the 5-step 90-second pitch
in English with the French version in grey italics below. No emoji; the boxes
stay empty (☐) as in the blank template.
"""
import json, pathlib, sys
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

GREY = RGBColor(0x59, 0x59, 0x59)
NAVY = RGBColor(0x1F, 0x1F, 0x1F)


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def cell_text(cell, text, bold=False, size=9, color=None):
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.bold = bold; r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color


def table(doc, headers, rows, widths_cm):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        cell_text(c, h, bold=True)
        shade(c, "E7E9EE")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cell_text(cells[i], v)
    tblPr = t._tbl.tblPr
    layout = OxmlElement("w:tblLayout"); layout.set(qn("w:type"), "fixed"); tblPr.append(layout)
    for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths_cm):
        gc.set(qn("w:w"), str(int(w * 567)))
    for i, w in enumerate(widths_cm):
        t.columns[i].width = Cm(w)
    for row in t.rows:
        for i, w in enumerate(widths_cm):
            row.cells[i].width = Cm(w)
    return t


def heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(12.5); r.font.color.rgb = NAVY


def main():
    C = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))["carnet"]
    out = pathlib.Path(sys.argv[2])
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    for side in ("left_margin", "right_margin"):
        setattr(sec, side, Cm(1.8))
    sec.top_margin = sec.bottom_margin = Cm(1.6)
    st = doc.styles["Normal"]
    st.font.name = "Calibri"; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    p = doc.add_paragraph()
    r = p.add_run("Briefing et pitch — carnet quotidien"); r.bold = True; r.font.size = Pt(18)
    p = doc.add_paragraph()
    r = p.add_run("Date : "); r.bold = True
    p.add_run(C["date_label"])

    heading(doc, "1. Les 6 chiffres")
    rows = [[x["label"], x["niveau"], x["variation"], x["plus_gros"], x["commentaire"]] for x in C["six"]]
    table(doc, ["Indicateur", "Niveau", "Variation", "Plus gros mouvement ?", "Commentaire"], rows, [3.0, 2.3, 2.6, 2.0, 7.5])

    heading(doc, "2. Trois titres économiques")
    rows = [[str(i), x["titre"], x["contexte"], x["effet"], x["source"]] for i, x in enumerate(C["titres"], 1)]
    table(doc, ["#", "Titre", "Contexte", "Effet pour un client ou un produit structuré", "Source"], rows, [0.8, 3.8, 4.1, 6.0, 2.7])

    heading(doc, "3. Géopolitique et rendez-vous")
    for label, key in (("☐ Sujet géopolitique :", "geopolitique"),
                       ("☐ Rendez-vous (décision de banque centrale, inflation, emploi ou résultats) :", "rendez_vous"),
                       ("☐ Heure et impact attendu :", "heure_impact")):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(label); r.bold = True
        p.add_run(" " + C[key])

    heading(doc, "4. Pitch de 90 secondes")
    for step in C["pitch"]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(7)
        r = p.add_run(step["etape"]); r.bold = True
        p.add_run(": " + step["en"])
        p.add_run().add_break(WD_BREAK.LINE)
        r = p.add_run(step["fr"]); r.italic = True; r.font.color.rgb = GREY

    if C.get("a_verifier"):
        heading(doc, "À vérifier avant le pitch")
        doc.add_paragraph(C["a_verifier"])

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    r = p.add_run("Sources"); r.bold = True; r.font.size = Pt(9)
    for s in C["sources"]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(s); r.font.size = Pt(8); r.font.color.rgb = GREY

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    print("written", out)


if __name__ == "__main__":
    main()

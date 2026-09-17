"""Word (DOCX) Document Generator with Native OpenXML RTL and BiDi Support.

Applies real OpenXML RTL attributes:
- `<w:bidi/>` and `<w:jc w:val="right"/>` on Paragraphs
- `<w:rtl/>` and `<w:rFonts w:cs="Vazirmatn"/>` on Runs
- `<w:bidiVisual/>` on Tables for authentic right-to-left column layout
"""
from typing import List, Dict, Any, Optional
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

from bot.services.bidi_engine import BiDiEngine, Direction
from bot.services.normalizer import PersianNormalizer


class DocxBuilder:
    """Builder for Persian DOCX documents with native RTL and BiDi OpenXML styling."""

    def __init__(
        self,
        default_font_fa: str = "Vazirmatn",
        default_font_en: str = "Arial",
        default_font_size: int = 12
    ):
        self.default_font_fa = default_font_fa
        self.default_font_en = default_font_en
        self.default_font_size = default_font_size
        self.normalizer = PersianNormalizer(convert_digits_to_persian=True)
        self.bidi_engine = BiDiEngine()

    def create_document(self) -> Document:
        """Initializes a new Document with Persian RTL page setup and margins."""
        doc = Document()

        # Set 1 inch margins
        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

            # Mark section as RTL if supported
            sectPr = section._sectPr
            bidi_sect = parse_xml(r'<w:bidi xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
            sectPr.append(bidi_sect)

        # Configure Normal style
        normal_style = doc.styles['Normal']
        normal_style.font.name = self.default_font_fa
        normal_style.font.size = Pt(self.default_font_size)
        normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

        return doc

    def add_rtl_paragraph(
        self,
        doc: Document,
        text: str,
        is_heading: bool = False,
        heading_level: int = 1,
        is_bullet: bool = False
    ) -> Any:
        """Adds a paragraph with genuine OpenXML RTL properties and direction-aware runs."""
        normalized_text = self.normalizer.normalize(text)
        if not normalized_text.strip():
            return None

        p = doc.add_paragraph()
        direction = self.bidi_engine.detect_paragraph_direction(normalized_text)

        pPr = p._p.get_or_add_pPr()

        if direction == "rtl":
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            # Inject <w:bidi/> into paragraph properties
            bidi_elem = OxmlElement('w:bidi')
            pPr.append(bidi_elem)
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Apply heading or bullet spacing
        if is_heading:
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            font_size = 18 if heading_level == 1 else (15 if heading_level == 2 else 13)
            is_bold = True
        elif is_bullet:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.right_indent = Inches(0.25) if direction == "rtl" else Inches(0)
            font_size = self.default_font_size
            is_bold = False
        else:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.25
            font_size = self.default_font_size
            is_bold = False

        # Split into directional runs (mixed Persian/English)
        runs = self.bidi_engine.split_into_directional_runs(normalized_text)
        for run_text, run_dir in runs:
            run = p.add_run(run_text)
            run.bold = is_bold
            run.font.size = Pt(font_size)

            rPr = run._r.get_or_add_rPr()

            # Set fonts for both complex script (cs) and ascii/hAnsi
            rFonts = OxmlElement('w:rFonts')
            if run_dir == "rtl":
                rFonts.set(qn('w:cs'), self.default_font_fa)
                rFonts.set(qn('w:ascii'), self.default_font_fa)
                rFonts.set(qn('w:hAnsi'), self.default_font_fa)
                rPr.append(rFonts)

                # OpenXML <w:rtl/> on the run
                rtl_run_elem = OxmlElement('w:rtl')
                rPr.append(rtl_run_elem)
            else:
                rFonts.set(qn('w:ascii'), self.default_font_en)
                rFonts.set(qn('w:hAnsi'), self.default_font_en)
                rFonts.set(qn('w:cs'), self.default_font_fa)
                rPr.append(rFonts)

        return p

    def add_rtl_table(
        self,
        doc: Document,
        table_data: List[List[str]],
        col_widths: Optional[List[float]] = None
    ) -> Any:
        """Adds a table with real OpenXML <w:bidiVisual/> so columns render Right-to-Left."""
        if not table_data or not table_data[0]:
            return None

        rows = len(table_data)
        cols = len(table_data[0])
        table = doc.add_table(rows=rows, cols=cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Apply Table Properties: <w:bidiVisual/> makes table order right-to-left
        tblPr = table._tbl.tblPr
        bidi_visual = parse_xml(r'<w:bidiVisual xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
        tblPr.append(bidi_visual)

        for row_idx, row in enumerate(table_data):
            for col_idx, cell_text in enumerate(row):
                cell = table.cell(row_idx, col_idx)
                cell_text_clean = self.normalizer.normalize(cell_text)

                # Clear default paragraph
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = p._p.get_or_add_pPr()
                pPr.append(OxmlElement('w:bidi'))

                run = p.add_run(cell_text_clean)
                run.font.name = self.default_font_fa
                run.font.size = Pt(10)
                if row_idx == 0:
                    run.bold = True

                rPr = run._r.get_or_add_rPr()
                rtl_elem = OxmlElement('w:rtl')
                rPr.append(rtl_elem)

        # Space after table
        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_before = Pt(4)
        spacer.paragraph_format.space_after = Pt(4)

        return table

    def build_from_extracted_content(
        self,
        content_pages: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """Assembles extracted PDF pages (paragraphs, headings, tables) into a final DOCX file.

        Args:
            content_pages: List of dictionaries with 'blocks' containing type, text, and metadata.
            output_path: Destination path for the .docx file.

        Returns:
            Path to the saved DOCX file.
        """
        doc = self.create_document()

        for page_idx, page in enumerate(content_pages):
            if page_idx > 0:
                doc.add_page_break()

            blocks = page.get("blocks", [])
            for block in blocks:
                b_type = block.get("type", "paragraph")
                if b_type == "heading":
                    self.add_rtl_paragraph(
                        doc,
                        block.get("text", ""),
                        is_heading=True,
                        heading_level=block.get("level", 1)
                    )
                elif b_type == "table":
                    self.add_rtl_table(doc, block.get("data", []))
                elif b_type == "bullet":
                    self.add_rtl_paragraph(
                        doc,
                        "• " + block.get("text", ""),
                        is_bullet=True
                    )
                else:
                    self.add_rtl_paragraph(
                        doc,
                        block.get("text", ""),
                        is_heading=False
                    )

        doc.save(output_path)
        return output_path

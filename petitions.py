"""Geração local e determinística de rascunhos de petição em DOCX."""

from __future__ import annotations

import io
import re
import urllib.parse
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.opc.constants import RELATIONSHIP_TYPE

import telos


FAVORABLE_LABEL = "FAVORÁVEL AO CLIENTE"


def case_number(case: dict) -> int | None:
    number = case.get("numero_caso")
    if isinstance(number, int) and number > 0:
        return number
    match = re.match(r"(?i)^caso\s+(\d+)\b", str(case.get("titulo", "")).strip())
    return int(match.group(1)) if match else None


def theme_number(notice: dict) -> int | None:
    value = notice.get("tema_repetitivo")
    if value:
        match = re.search(r"\d+", str(value))
        if match:
            return int(match.group())
    url = str(notice.get("link", ""))
    if not telos.is_official_stj_link(url):
        return None
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    values = query.get("cod_tema_inicial", [])
    if len(values) != 1 or not values[0].isdigit():
        return None
    final_values = query.get("cod_tema_final", [])
    if final_values and (len(final_values) != 1 or final_values[0] != values[0]):
        return None
    return int(values[0])


def load_theme(number: int) -> tuple[str, str] | None:
    """Return the tese and official theme URL from a saved STJ source file."""
    candidates = [
        telos.STJ_PRECEDENTS_DIR / f"tema_{number:04d}.txt",
        *telos.DECISIONS_DIR.rglob(f"tema_{number:04d}.txt"),
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            contents = telos.read_document(path)
        except Exception:
            continue
        number_match = re.search(r"(?mi)^Tema repetitivo STJ:\s*(\d+)\s*$", contents)
        if not number_match or int(number_match.group(1)) != number:
            continue
        thesis_match = re.search(
            r"(?ms)^Tese firmada:\s*(.+?)(?=^[^\n:]{2,80}:\s*|\Z)", contents
        )
        link_match = re.search(r"(?mi)^Link oficial:\s*(https://\S+)\s*$", contents)
        if not thesis_match or not link_match:
            continue
        thesis = " ".join(line.strip() for line in thesis_match.group(1).splitlines()).strip()
        link = link_match.group(1).rstrip(".,;)")
        if (
            not thesis
            or "ainda não consta tese firmada" in thesis.casefold()
            or "sem mérito publicado" in thesis.casefold()
            or not telos.is_official_stj_link(link)
        ):
            continue
        query = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
        if query.get("cod_tema_inicial") != [str(number)]:
            continue
        return thesis, link
    return None


def can_generate(notice: dict, case: dict) -> bool:
    if str(case.get("favorabilidade", "")).strip().upper() != FAVORABLE_LABEL:
        return False
    if case_number(case) is None:
        return False
    reason = str(case.get("motivo_aplicacao", "")).strip()
    if not reason or telos.EMAIL_JSON_KEYS.search(reason):
        return False
    number = theme_number(notice)
    return number is not None and load_theme(number) is not None


def _add_hyperlink(paragraph, label: str, url: str) -> None:
    relationship_id = paragraph.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship_id)
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "5558B8")
    properties.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    properties.append(underline)
    run.append(properties)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def _set_cell_shading(paragraph, fill: str) -> None:
    properties = paragraph._p.get_or_add_pPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def _portuguese_date(value: date) -> str:
    months = (
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    )
    return f"{value.day} de {months[value.month - 1]} de {value.year}"


def create_petition_docx(
    *,
    title: str,
    number: int,
    theme: int,
    official_url: str,
    thesis: str,
    reason: str,
    today: date | None = None,
) -> io.BytesIO:
    """Create a Word petition draft from verified notice and STJ theme data."""
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)
    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(35, 37, 53)
    normal.paragraph_format.space_after = Pt(8)

    warning = document.add_paragraph()
    warning.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_cell_shading(warning, "E9E9FF")
    run = warning.add_run("Rascunho gerado pelo Telos: revisar antes de protocolar")
    run.bold = True
    run.font.color.rgb = RGBColor(70, 72, 150)
    warning.paragraph_format.space_after = Pt(16)

    court = document.add_paragraph()
    court.alignment = WD_ALIGN_PARAGRAPH.CENTER
    court.paragraph_format.space_after = Pt(14)
    court_run = court.add_run("Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito\n[Juízo da causa — preencher antes do protocolo]")
    court_run.bold = True

    document.add_paragraph(f"Processo nº: [preencher número dos autos]")
    document.add_paragraph(f"Identificação do caso: Caso {number} — {title}")
    document.add_heading("Requerimento de aplicação de tese repetitiva", level=1)
    document.add_paragraph(
        "[Nome da parte], já qualificada nos autos, por seu advogado, vem, respeitosamente, "
        f"requerer a aplicação da tese firmada pelo Superior Tribunal de Justiça no Tema Repetitivo {theme}, "
        "pelos fundamentos a seguir."
    )

    document.add_heading(f"Tema Repetitivo {theme} do STJ", level=2)
    document.add_paragraph(thesis)
    link_paragraph = document.add_paragraph()
    link_paragraph.add_run("Consulta oficial do tema: ")
    _add_hyperlink(link_paragraph, official_url, official_url)

    document.add_heading("Relação com o caso", level=2)
    document.add_paragraph(
        f"O aviso do Telos identificou relação direta entre a tese e o Caso {number} — {title}: {reason}"
    )

    document.add_heading("Fundamento legal", level=2)
    document.add_paragraph(
        "O art. 927, III, do Código de Processo Civil determina que os juízes e os tribunais "
        "observarão “os acórdãos em incidente de assunção de competência ou de resolução de "
        "demandas repetitivas e em julgamento de recursos extraordinário e especial repetitivos”."
    )

    document.add_heading("Pedido", level=2)
    document.add_paragraph(
        f"Diante do exposto, requer que a tese firmada pelo STJ no Tema Repetitivo {theme} "
        "seja observada e aplicada à questão jurídica correspondente nestes autos, após o exame "
        "da aderência entre a tese e os fatos comprovados no processo."
    )

    document.add_paragraph("Termos em que, pede deferimento.")
    local_date = today or date.today()
    place_date = document.add_paragraph(f"[Cidade], {_portuguese_date(local_date)}.")
    place_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph("\n________________________________________")
    signature = document.add_paragraph("[Nome do advogado]\nOAB/[UF] nº [número]")
    signature.alignment = WD_ALIGN_PARAGRAPH.CENTER

    output = io.BytesIO()
    document.save(output)
    output.seek(0)
    return output

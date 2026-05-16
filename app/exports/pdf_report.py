"""PDF report exporter.

Renders a structured decision report (combination of ADR + discussion trail)
from the conversation state plus a pre-generated markdown report body.

Discussion participants are anonymized to ROLE labels only; no personal names
appear anywhere in the document.
"""
import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
)

from app.state import BrainstormState


# Role labels used in the report. Marcus's intake/summary/conclude all map to
# "Moderator" so the report reads naturally without personal names.
ROLE_LABELS: dict[str, str] = {
    "moderator":          "Moderator",
    "intake":             "Moderator",
    "summary":            "Moderator",
    "conclude":           "Moderator",
    "ai_architect":       "AI Systems Architect",
    "fullstack":          "Senior Full Stack Engineer",
    "qa":                 "QA & Reliability Engineer",
    "ml_scientist":       "ML Scientist",
    "php_plugin":         "Plugin Developer",
    "php_theme":          "Theme Developer",
    "wp_theme_reviewer":  "WordPress Theme Reviewer",
    "wp_plugin_reviewer": "WordPress Plugin Reviewer",
    "ux_engineer":        "UI / UX Engineer",
}


# Per-role display colors used for the small chip in the discussion trail.
ROLE_COLORS: dict[str, str] = {
    "Moderator":                    "#7C3AED",  # purple
    "AI Systems Architect":         "#2563EB",  # blue
    "Senior Full Stack Engineer":   "#16A34A",  # green
    "QA & Reliability Engineer":    "#DC2626",  # red
    "ML Scientist":                 "#EA580C",  # orange
    "Plugin Developer":             "#4F46E5",  # indigo
    "Theme Developer":              "#DB2777",  # pink
    "WordPress Theme Reviewer":     "#B45309",  # amber
    "WordPress Plugin Reviewer":    "#E11D48",  # rose
    "UI / UX Engineer":             "#0F766E",  # teal
    "User":                         "#1D4ED8",  # dark blue
}


def _role_for(item: dict) -> str:
    role_key = (item.get("role") or "").strip()
    return ROLE_LABELS.get(role_key, role_key.replace("_", " ").title() or "Speaker")


def _role_color_hex(role_label: str) -> str:
    return ROLE_COLORS.get(role_label, "#374151")


# ── Markdown-light → ReportLab helpers (unchanged from prior version) ─────

def _markdown_to_html(text: str) -> str:
    if not text:
        return ""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" backColor="#F3F4F6">\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    return text


def _make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=22, leading=28, spaceAfter=10, textColor=HexColor("#111827"),
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontSize=11, leading=16,
            textColor=HexColor("#6B7280"), spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=22, spaceBefore=18, spaceAfter=10,
            textColor=HexColor("#111827"),
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=17, spaceBefore=14, spaceAfter=6,
            textColor=HexColor("#111827"),
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=15, spaceBefore=8, spaceAfter=4,
            textColor=HexColor("#1F2937"),
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=HexColor("#1F2937"),
            alignment=TA_LEFT, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=HexColor("#1F2937"),
            leftIndent=14, spaceAfter=3,
        ),
        "role_name": ParagraphStyle(
            "role_name", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=14, spaceAfter=2,
        ),
        "turn_body": ParagraphStyle(
            "turn_body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=14, textColor=HexColor("#374151"),
            spaceAfter=4,
        ),
        "turn_bullet": ParagraphStyle(
            "turn_bullet", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=14, textColor=HexColor("#374151"),
            leftIndent=12, spaceAfter=2,
        ),
        "turn_heading": ParagraphStyle(
            "turn_heading", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=14, textColor=HexColor("#111827"),
            spaceBefore=3, spaceAfter=2,
        ),
        "chirp_body": ParagraphStyle(
            "chirp_body", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9.5, leading=13, textColor=HexColor("#4B5563"),
            leftIndent=12, spaceAfter=2,
        ),
    }


def _render_markdown(text: str, styles) -> list:
    """Turn a chunk of markdown into a flow of ReportLab elements (report body)."""
    flow: list = []
    if not text or not text.strip():
        return flow

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        if not line.strip():
            flow.append(Spacer(1, 4))
            continue

        if line.startswith("### "):
            flow.append(Paragraph(_markdown_to_html(line[4:]), styles["h3"]))
        elif line.startswith("## "):
            flow.append(Paragraph(_markdown_to_html(line[3:]), styles["h2"]))
        elif line.startswith("# "):
            flow.append(Paragraph(_markdown_to_html(line[2:]), styles["h1"]))
        elif line.lstrip().startswith(("- ", "* ")):
            stripped = line.lstrip()[2:]
            flow.append(Paragraph("• " + _markdown_to_html(stripped), styles["bullet"]))
        elif re.match(r"^\d+\.\s+", line.lstrip()):
            flow.append(Paragraph(_markdown_to_html(line.lstrip()), styles["bullet"]))
        else:
            flow.append(Paragraph(_markdown_to_html(line), styles["body"]))

    return flow


def _render_turn_content(text: str, styles, body_key: str = "turn_body") -> list:
    """Lighter markdown renderer used inside discussion turns."""
    flow: list = []
    if not text or not text.strip():
        return flow

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        if not line.strip():
            flow.append(Spacer(1, 3))
            continue

        if line.startswith("### "):
            flow.append(Paragraph(_markdown_to_html(line[4:]), styles["turn_heading"]))
        elif line.startswith("## "):
            flow.append(Paragraph(_markdown_to_html(line[3:]), styles["turn_heading"]))
        elif line.startswith("# "):
            flow.append(Paragraph(_markdown_to_html(line[2:]), styles["turn_heading"]))
        elif line.lstrip().startswith(("- ", "* ")):
            stripped = line.lstrip()[2:]
            flow.append(Paragraph("• " + _markdown_to_html(stripped), styles["turn_bullet"]))
        elif re.match(r"^\d+\.\s+", line.lstrip()):
            flow.append(Paragraph(_markdown_to_html(line.lstrip()), styles["turn_bullet"]))
        else:
            flow.append(Paragraph(_markdown_to_html(line), styles[body_key]))

    return flow


# ── Discussion trail (role-only) ─────────────────────────────────────────

def _turn_card(role_label: str, content: str, is_chirp: bool, styles) -> KeepTogether:
    color_hex = _role_color_hex(role_label)
    chirp_suffix = ' <font color="#9CA3AF">· chirp-in</font>' if is_chirp else ""
    label = f'<font color="{color_hex}">●</font> <b>{role_label}</b>{chirp_suffix}'
    body_flow = _render_turn_content(
        content,
        styles,
        body_key="chirp_body" if is_chirp else "turn_body",
    )
    return KeepTogether([
        Paragraph(label, styles["role_name"]),
        *body_flow,
        Spacer(1, 8),
    ])


def _user_card(content: str, styles) -> KeepTogether:
    return KeepTogether([
        Paragraph('<font color="#1D4ED8">▸</font> <b>User</b>', styles["role_name"]),
        *_render_turn_content(content, styles),
        Spacer(1, 8),
    ])


# ── Public API ───────────────────────────────────────────────────────────

def render_pdf(state: BrainstormState, report_md: str) -> bytes:
    """Render the report PDF.

    `report_md` is Nora Patel's structured report markdown (Problem, Recommended
    Solution, How We Arrived at This, Parameters Considered, Key Decisions, Open
    Risks and Questions). This function lays that out as the body, then appends a
    role-only "Discussion Trail" so a reader can audit how the recommendation
    was reached.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="Brainstorming Session Report",
    )

    styles = _make_styles()
    flow: list = []

    # ── Cover ─────────────────────────────────────────────────────────────
    flow.append(Paragraph("Brainstorming Decision Report", styles["title"]))
    flow.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles["subtitle"],
    ))

    # Role-only roster.
    roles_present: list[str] = []
    seen: set[str] = set()
    for d in state.get("discussions", []):
        label = _role_for(d)
        if label and label not in seen:
            roles_present.append(label)
            seen.add(label)
    if roles_present:
        flow.append(Paragraph(
            f"Panel: {' · '.join(roles_present)}",
            styles["subtitle"],
        ))

    flow.append(Spacer(1, 8))

    # ── Body: Nora's structured report ─────────────────────────────────────
    if report_md and report_md.strip():
        flow.extend(_render_markdown(report_md, styles))
    else:
        # Fallback if the report body could not be generated.
        flow.append(Paragraph("Problem", styles["h1"]))
        flow.extend(_render_markdown(state.get("user_goal", ""), styles))

    # ── Discussion Trail (role-only) ──────────────────────────────────────
    discussions = state.get("discussions", [])
    user_inputs = state.get("user_inputs", [])
    if discussions or user_inputs:
        flow.append(PageBreak())
        flow.append(Paragraph("Discussion Trail", styles["h1"]))
        flow.append(Paragraph(
            "The full exchange that led to the recommendation. Participants are "
            "labelled by role.",
            styles["body"],
        ))
        flow.append(Spacer(1, 6))

        merged: list[tuple[str, dict]] = (
            [(d["timestamp"], {"kind": "agent", **d}) for d in discussions]
            + [(u["timestamp"], {"kind": "user", **u}) for u in user_inputs]
        )
        merged.sort(key=lambda x: x[0])

        for _, item in merged:
            if item["kind"] == "user":
                flow.append(_user_card(item.get("content", ""), styles))
            else:
                flow.append(_turn_card(
                    role_label=_role_for(item),
                    content=item.get("content", ""),
                    is_chirp=bool(item.get("is_chirp")),
                    styles=styles,
                ))

    doc.build(flow, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(HexColor("#9CA3AF"))
    canvas.drawString(0.85 * inch, 0.55 * inch, "AI Brainstorming Board · Decision Report")
    canvas.drawRightString(
        LETTER[0] - 0.85 * inch, 0.55 * inch, f"Page {doc.page}"
    )
    canvas.restoreState()

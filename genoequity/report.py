"""PDF report generator using ReportLab Platypus."""

from __future__ import annotations

from datetime import date
from io import BytesIO
from typing import List, Tuple

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import AuditResult

ANCESTRY_ORDER = ["AFR", "AMR", "ASJ", "EAS", "FIN", "NFE", "SAS"]


def _build_score_table(audit: AuditResult) -> Tuple[List[List[str]], List[str]]:
    data = [["Population", "Coverage", "Reliability", "Gap"]]
    for ancestry in ANCESTRY_ORDER:
        data.append(
            [
                ancestry,
                f"{audit.summary.coverage_scores.get(ancestry, 0.0):.3f}",
                f"{audit.summary.reliability_scores.get(ancestry, 0.0):.3f}",
                f"{audit.summary.gap_index.get(ancestry, 0.0):.3f}",
            ]
        )
    return data, ["Population", "Coverage", "Reliability", "Gap"]


def _build_flagged_table(audit: AuditResult) -> List[List[str]]:
    data = [["rsID", "Effect Size"]]
    effect_map = {v.rsid or v.variant_id: v.effect_size for v in audit.variants}
    for variant_id in audit.summary.flagged_variants:
        effect = effect_map.get(variant_id)
        effect_str = f"{effect:.4f}" if effect is not None else "N/A"
        data.append([variant_id, effect_str])
    if len(data) == 1:
        data.append(["None", "-"])
    return data


def _build_heatmap_image(audit: AuditResult) -> BytesIO:
    matrix = [
        [
            audit.summary.coverage_scores.get(a, 0.0),
            audit.summary.reliability_scores.get(a, 0.0),
            audit.summary.gap_index.get(a, 0.0),
        ]
        for a in ANCESTRY_ORDER
    ]
    fig, ax = plt.subplots(figsize=(4.2, 3.5))
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks([0, 1, 2], labels=["Coverage", "Reliability", "Gap"])
    ax.set_yticks(range(len(ANCESTRY_ORDER)), labels=ANCESTRY_ORDER)
    ax.tick_params(axis="x", rotation=30)

    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="white", fontsize=8)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def generate_report(audit: AuditResult) -> bytes:
    """Generate a PDF report and return it as bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    story: List = []
    story.append(Paragraph("GenoEquity Audit Report", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Accession ID: {audit.summary.accession}", styles["Normal"]))
    story.append(
        Paragraph(f"Cancer Type: {audit.summary.model_name or 'N/A'}", styles["Normal"])
    )
    story.append(Paragraph(f"Date Generated: {date.today().isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    score_data, _ = _build_score_table(audit)
    score_table = Table(score_data, hAlign="LEFT")
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D8C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )
    story.append(Paragraph("Audit Scores", styles["Heading2"]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    heatmap_buffer = _build_heatmap_image(audit)
    story.append(Paragraph("Coverage / Reliability / Gap Heatmap", styles["Heading2"]))
    story.append(Image(heatmap_buffer, width=360, height=300))
    story.append(Spacer(1, 12))

    flagged_table = Table(_build_flagged_table(audit), hAlign="LEFT")
    flagged_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3C5E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
        )
    )
    story.append(Paragraph("Flagged High-Impact Variants", styles["Heading2"]))
    story.append(flagged_table)
    story.append(Spacer(1, 12))

    limitations = (
        "Limitations: Effect sizes may not transfer across ancestries. gnomAD is a reference "
        "dataset and not a disease cohort. LD structure differences are not modeled here. "
        "Scores reflect coverage and data support, not clinical validity."
    )
    story.append(Paragraph("Limitations", styles["Heading2"]))
    story.append(Paragraph(limitations, styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()

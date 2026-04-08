"""PDF report generator using ReportLab."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import AuditResult


def generate_report(audit: AuditResult, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 40, "GenoEquity Audit Report")

    c.setFont("Helvetica", 12)
    c.drawString(40, height - 70, f"Accession: {audit.summary.accession}")
    if audit.summary.model_name:
        c.drawString(40, height - 90, f"Model: {audit.summary.model_name}")

    y = height - 130
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Coverage Scores")
    y -= 18
    c.setFont("Helvetica", 10)
    for ancestry, score in audit.summary.coverage_scores.items():
        c.drawString(60, y, f"{ancestry}: {score:.2f}")
        y -= 14

    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Reliability Scores")
    y -= 18
    c.setFont("Helvetica", 10)
    for ancestry, score in audit.summary.reliability_scores.items():
        c.drawString(60, y, f"{ancestry}: {score:.2f}")
        y -= 14

    c.showPage()
    c.save()
    return output_path

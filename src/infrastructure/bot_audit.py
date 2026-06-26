import asyncio
import os
import sys
import aiohttp
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuration layer
FEDRAMP_REGISTRY_URL = "https://githubusercontent.com" 
OUTPUT_PDF_PATH = "fedramp_realtime_audit.pdf"

def _build_pdf_worker(data_matrix: list) -> str:
    """
    CPU-heavy PDF construction callback. Run inside an isolated execution thread context 
    to prevent blocking the async loop.
    """
    doc = SimpleDocTemplate(OUTPUT_PDF_PATH, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom architectural style configurations
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=22, spaceAfter=12, textColor=colors.HexColor('#1A365D'))
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=10, leading=14)
    
    story.append(Paragraph("AxiomStream Automated Security Compliance Audit Report", title_style))
    story.append(Paragraph(f"<b>Target Baseline:</b> FedRAMP Authorization Matrix Registry Context Data", body_style))
    story.append(Spacer(1, 12))
    
    # Build structural tabular layout arrays
    table_data = [["Index Offset", "Identified Dependency Component Requirement / Package Profile"]]
    for idx, line in enumerate(data_matrix[:25]): # Cap reporting frame for speed optimizations
        if line.strip():
            table_data.append([str(idx + 1), Paragraph(line.strip(), body_style)])
            
    audit_table = Table(table_data, colWidths=[80, 440])
    audit_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    
    story.append(audit_table)
    doc.build(story)
    return OUTPUT_PDF_PATH

async def fetch_compliance_telemetry(session: aiohttp.ClientSession) -> list:
    """Performs ultra-low latency, non-blocking asynchronous HTTP network stream reads."""
    try:
        print(f"🌐 [INGESTION] Fetching live compliance vectors from upstream endpoint registry...")
        async with session.get(FEDRAMP_REGISTRY_URL, timeout=10) as response:
            if response.status != 200:
                print(f"⚠️ Unexpected upstream connection response token status: {response.status}")
                return []
            raw_text = await response.text()
            return raw_text.split("\n")
    except Exception as e:
        print(f"❌ Network collection pipeline blocked by connection fault: {str(e)}", file=sys.stderr)
        return []

async def run_compliance_audit_cycle():
    """Main non-blocking execution lifecycle loop wrapper."""
    async with aiohttp.ClientSession() as session:
        # Step 1: Low-latency async data ingestion
        telemetry_lines = await fetch_compliance_telemetry(session)
        
        if not telemetry_lines:
            print("🛑 Ingested compliance data metrics are empty. Aborting report render pass.")
            return

        print(f"📥 [PARSING] Successfully ingested {len(telemetry_lines)} compliance nodes.")
        
        # Step 2: Offload CPU-heavy ReportLab PDF compilation safely to a background worker thread
        print(f"🖨️ [COMPILING] Generating formal audit report via background worker threading pools...")
        loop = asyncio.get_running_loop()
        pdf_path = await loop.run_in_executor(None, _build_pdf_worker, telemetry_lines)
        
        print(f"✨ [SUCCESS] Compliance asset generated securely at target footprint path: '{pdf_path}'\n")

if __name__ == "__main__":
    print("🤖 Launching High-Throughput Compliance Auditing Daemon Core...")
    asyncio.run(run_compliance_audit_cycle())

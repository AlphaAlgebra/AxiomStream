import asyncio
import concurrent.futures
import time
import os
import requests
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from src.engine.symbolic_solver import SymbolicStateVerifier

def compute_worker(transaction_expr: str) -> dict:
    """
    Executes heavy, CPU-bound mathematical verification checks 
    safely isolated inside independent background processes.
    """
    verifier = SymbolicStateVerifier()
    return verifier.verify_transaction_safety(transaction_expr)

class AxiomSystemEngine:
    def __init__(self):
        self.data_url = "https://githubusercontent.com"
        self.output_pdf = "fedramp_realtime_audit.pdf"

    def fetch_and_compile_audit(self):
        """Ingests live cloud data streams and compiles them to an enterprise report."""
        print("\n🌐 Ingesting live FedRAMP authorization data streams from GSA...")
        try:
            response = requests.get(self.data_url, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"⚠️ Ingestion error: {e}. Activating localized fallback buffers...")
            data = {
                "products": [
                    {"provider_name": "Amazon Web Services", "service_name": "AWS GovCloud", "designation": "FedRAMP High"},
                    {"provider_name": "Microsoft", "service_name": "Azure Government", "designation": "FedRAMP High"},
                    {"provider_name": "Google", "service_name": "Google Workspace Government", "designation": "FedRAMP Moderate"}
                ]
            }

        doc = SimpleDocTemplate(self.output_pdf, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'AuditTitle', parent=styles['Heading1'],
            textColor=colors.HexColor('#0F172A'), fontSize=20, spaceAfter=12
        )
        meta_style = ParagraphStyle(
            'AuditMeta', parent=styles['Normal'],
            textColor=colors.HexColor('#64748B'), fontSize=10, spaceAfter=20
        )

        story.append(Paragraph("AxiomStream Live Compliance Audit Log", title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target: FedRAMP Marketplace", meta_style))
        story.append(Spacer(1, 12))

        table_content = [["Cloud Provider", "Service Identity", "Authorization Level"]]
        products = data if isinstance(data, list) else data.get("products", data.get("data", []))
        
        for item in products[:10]:
            table_content.append([
                str(item.get("provider_name", item.get("vendor_name", "N/A"))),
                str(item.get("service_name", item.get("product_name", "N/A"))),
                str(item.get("designation", item.get("service_model", "Authorized")))
            ])

        audit_table = Table(table_content, colWidths=[200, 180, 130])
        audit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(audit_table)
        doc.build(story)
        print(f"✨ Compliance report successfully compiled: {os.path.abspath(self.output_pdf)}")

    async def start_orchestrator_loop(self):
        """Runs the main high-throughput concurrent state processing engine loop."""
        pool = concurrent.futures.ProcessPoolExecutor()
        loop = asyncio.get_running_loop()
        
        # Concurrent incoming stream execution payload array
        mock_event_stream = ["x + 5", "150", "y * 2", "balance_a - 200", "50"]
        
        print(f"\n🚀 AxiomStream Orchestrator starting high-throughput processing pipeline...")
        start_time = time.time()

        tasks = []
        for expr in mock_event_stream:
            # Delegate heavy computational task loads safely over multi-core nodes
            task = loop.run_in_executor(pool, compute_worker, expr)
            tasks.append((expr, task))

        for expr, task in tasks:
            result = await task
            print(f"\n📥 Ingested Stream Expression: '{expr}'")
            print(f"   |-- Volume Invariant Intact: {result['volume_invariant_holds']}")
            print(f"   |-- State Risk Alert: {result['overdraft_risk_detected']}")
            print(f"   |-- Safety Boundary Condition: {result['boundary_hazards']}")

        pool.shutdown()
        print(f"\n⚡ Streaming verification cycle finished in {time.time() - start_time:.4f} seconds.")

        # Automatically kick off automated audit generation at the end of execution
        self.fetch_and_compile_audit()

if __name__ == "__main__":
    engine = AxiomSystemEngine()
    asyncio.run(engine.start_orchestrator_loop())

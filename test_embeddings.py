import os
import sys
sys.path.append('.')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create a sample PDF
def create_sample_pdf():
    c = canvas.Canvas("law_pdfs/sample.pdf", pagesize=letter)
    c.drawString(100, 750, "Indian Penal Code Section 378: Theft")
    c.drawString(100, 730, "Whoever, intending to take dishonestly any movable property out of the possession")
    c.drawString(100, 710, "of any person without that person's consent, moves that property in order to such taking,")
    c.drawString(100, 690, "is said to commit theft.")
    c.drawString(100, 670, "Penalty: Punishment for theft is imprisonment of either description for a term which may")
    c.drawString(100, 650, "extend to three years, or with fine, or with both.")
    c.drawString(100, 630, "Under the new Bharatiya Nyaya Sanhita (BNS), the penalty for theft is similar.")
    c.save()

if __name__ == "__main__":
    os.makedirs("law_pdfs", exist_ok=True)
    create_sample_pdf()
    print("Sample PDF created.")

    # Import and test
    from engine.rag_engine import index_pdfs, search_pdfs

    # Index PDFs
    index_pdfs()

    # Test without embeddings
    os.environ["LTA_USE_EMBEDDINGS"] = "0"
    result_kw = search_pdfs("penalty for theft")
    print("Keyword search result:")
    print(result_kw)

    # Test with embeddings (rebuild index with embeddings enabled)
    os.environ["LTA_USE_EMBEDDINGS"] = "1"
    index_pdfs()  # Rebuild index with embeddings
    result_emb = search_pdfs("penalty for theft")
    print("Embedding search result:")
    print(result_emb)

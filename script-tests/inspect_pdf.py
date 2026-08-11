import pdfplumber

def inspect_pdf(path):
    print(f"=== Inspecting {path} ===")
    with pdfplumber.open(path) as pdf:
        print(f"Number of pages: {len(pdf.pages)}")
        for idx, page in enumerate(pdf.pages):
            print(f"--- Page {idx+1} ---")
            text = page.extract_text()
            print("PAGE TEXT PREVIEW:")
            print("\n".join(text.splitlines()[:10]) if text else "No text extracted")
            
            tables = page.extract_tables()
            print(f"Found {len(tables)} tables")
            for t_idx, table in enumerate(tables):
                print(f"Table {t_idx+1}: {len(table)} rows, {len(table[0]) if table else 0} cols")
                # print first 4 rows
                for r in table[:4]:
                    print(r)
                print("...")

inspect_pdf("pdf/laboratorios-2026b.pdf")
inspect_pdf("pdf/teoria-2026b.pdf")

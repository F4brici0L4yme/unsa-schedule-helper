import pdfplumber

def inspect_mismatches(filepath):
    print(f"=== Mismatches in {filepath} ===")
    with pdfplumber.open(filepath) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                # check if it is a schedule table
                if not table or not any("HORA" in str(cell).upper() for cell in table[0] if cell):
                    continue
                # print any row containing weird strings
                for r_idx, row in enumerate(table):
                    for cell in row:
                        if cell and any(x in str(cell) for x in ["NEGOCIOS", "ORGANIZACIÓN", "POLITICAS"]):
                            print(f"Page {p_idx+1}, Table {t_idx+1}, Row {r_idx}: {row}")
                            break

inspect_mismatches("pdf/laboratorios-2026b.pdf")
inspect_mismatches("pdf/teoria-2026b.pdf")

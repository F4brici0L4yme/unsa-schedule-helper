import pdfplumber

with pdfplumber.open("pdf/laboratorios-2026b.pdf") as pdf:
    page = pdf.pages[1]
    tables = page.extract_tables()
    table = tables[5] # Table 6
    for idx, row in enumerate(table):
        print(f"Row {idx:2d} (len {len(row)}): {row}")

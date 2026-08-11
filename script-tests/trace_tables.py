import pdfplumber

def trace_schedule_tables(filepath):
    print(f"=== Tracing {filepath} ===")
    with pdfplumber.open(filepath) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                if not table:
                    continue
                first_row = [str(c).replace('\n', ' ')[:30] if c else "" for c in table[0]]
                # check matching days
                matching_days = sum(1 for col in table[0] if col and str(col).upper().strip() in ["LUNES", "MARTES", "MIERCOLES", "MIÉRCOLES", "JUEVES", "VIERNES"])
                print(f"  Page {p_idx+1}, Table {t_idx+1}: rows={len(table)}, cols={len(table[0])}, matching_days={matching_days}")
                print(f"    Header: {first_row}")

trace_schedule_tables("pdf/laboratorios-2026b.pdf")
trace_schedule_tables("pdf/teoria-2026b.pdf")

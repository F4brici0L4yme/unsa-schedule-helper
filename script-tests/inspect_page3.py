import pdfplumber

with pdfplumber.open("pdf/laboratorios-2026b.pdf") as pdf:
    page = pdf.pages[2] # Page 3
    print("=== Text on Page 3 ===")
    words = page.extract_words()
    lines = {}
    for w in words:
        top = round(w['top'], 1)
        found = False
        for t in lines:
            if abs(t - top) < 3:
                lines[t].append(w)
                found = True
                break
        if not found:
            lines[top] = [w]
            
    for top in sorted(lines.keys()):
        line_str = " ".join([w['text'] for w in sorted(lines[top], key=lambda x: x['x0'])])
        print(f"Top {top:6.1f}: {line_str}")
        
    print("\n=== Tables on Page 3 ===")
    tables = page.find_tables()
    for t_idx, table in enumerate(tables):
        print(f"Table {t_idx+1} bbox: {table.bbox}")
        data = table.extract()
        print(f"  Rows: {len(data)}, Cols: {len(data[0]) if data else 0}")
        print(f"  First Row: {data[0]}")

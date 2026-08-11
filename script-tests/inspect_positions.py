import pdfplumber

def inspect_details(path):
    print(f"\n===== DETAILS FOR {path} =====")
    with pdfplumber.open(path) as pdf:
        for idx, page in enumerate(pdf.pages):
            print(f"\n--- Page {idx+1} ---")
            # Extract text elements with their positions
            words = page.extract_words()
            # Group words into lines based on vertical position (top)
            lines = {}
            for w in words:
                top = round(w['top'], 1)
                found = False
                for t in lines:
                    if abs(t - top) < 3: # group words within 3 units vertically
                        lines[t].append(w)
                        found = True
                        break
                if not found:
                    lines[top] = [w]
            
            # Sort lines vertically
            sorted_line_tops = sorted(lines.keys())
            for top in sorted_line_tops[:20]: # print top 20 lines
                line_words = sorted(lines[top], key=lambda x: x['x0'])
                line_str = " ".join([w['text'] for w in line_words])
                print(f"Top {top:6.1f}: {line_str}")
            
            # Print info about tables
            tables = page.find_tables()
            print(f"\nFound {len(tables)} tables on page")
            for t_idx, table in enumerate(tables):
                print(f"Table {t_idx+1} bbox: {table.bbox}")

inspect_details("pdf/laboratorios-2026b.pdf")
inspect_details("pdf/teoria-2026b.pdf")

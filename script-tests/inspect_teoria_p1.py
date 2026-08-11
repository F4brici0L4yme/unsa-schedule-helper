import pdfplumber

with pdfplumber.open("pdf/teoria-2026b.pdf") as pdf:
    page = pdf.pages[0]
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

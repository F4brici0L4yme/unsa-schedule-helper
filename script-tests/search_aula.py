import pdfplumber

with pdfplumber.open("pdf/laboratorios-2026b.pdf") as pdf:
    for p_idx, page in enumerate(pdf.pages):
        print(f"=== Page {p_idx+1} ===")
        words = page.extract_words()
        for w in words:
            if "302" in w['text'] or "305" in w['text'] or "201" in w['text'] or "202" in w['text'] or "AULA" in w['text'].upper():
                print(f"  {w['text']} at top={w['top']}, x0={w['x0']}")

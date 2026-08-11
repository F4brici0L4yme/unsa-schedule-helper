import pdfplumber

with pdfplumber.open("../pdf/teoria-2026b.pdf") as pdf:
    first_page = pdf.pages[0]
    im = first_page.to_image()
    im.draw_rects(first_page.extract_words())
    im.save("word_detection.png")

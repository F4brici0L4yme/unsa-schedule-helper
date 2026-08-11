import pdfplumber

with pdfplumber.open("../pdf/teoria-2026b.pdf") as pdf:
    first_page = pdf.pages[0]
    print(first_page.chars[0])

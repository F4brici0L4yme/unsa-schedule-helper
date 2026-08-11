import pdfplumber

with pdfplumber.open("../pdf/teoria-2026b.pdf") as pdf:
    page = pdf.pages[0]
    table = page.extract_table()
    im = page.to_image()
    debugged = im.debug_tablefinder()
    debugged.save("../export/imgs/table_detection.png")
#    first_page = pdf.pages[0]
#    im = first_page.to_image()
#    im.draw_rects(first_page.extract_words())
#    im.save("word_detection.png")




import fitz


def extract_text_from_pdf(pdf_bytes, progress_callback=None):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    page_count = len(doc)

    for i, page in enumerate(doc):
        extracted = page.get_text()
        text += extracted + "\n"

        if progress_callback:
            progress_callback(i + 1, page_count)

    doc.close()
    return text.strip(), page_count

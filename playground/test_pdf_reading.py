import os
import json
from PyPDFForm import PdfWrapper
from docling.document_converter import DocumentConverter


def load_pdf(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    pdf = PdfWrapper(file_path, use_full_widget_name=True)
    print(f'Loaded PDF "{pdf.title}".')
    return pdf


def convert_pdf_to(file_path):
    converter = DocumentConverter()
    content = converter.convert(file_path).document
    return content


def extract_fields(pdf):
    return pdf.schema


def main():
    pdf = load_pdf("data\\Anmeldung_Meldeschein_20220622.pdf")
    fields = extract_fields(pdf)
    with open("output\\pdf_fields.json", "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=4, ensure_ascii=False)

    pdf_content = convert_pdf_to("data\\Anmeldung_Meldeschein_20220622.pdf")
    with open("output\\pdf_content.md", "w", encoding="utf-8") as f:
        f.write(pdf_content.export_to_markdown())

    with open("output\\pdf_content.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(pdf_content.export_to_dict(), indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()

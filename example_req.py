import requests

file_path = "docs/diploma_lib.docx"

data = {
    "pdf_with_text_layer": "auto_tabby",
    "document_type": "diploma",
    "language": "rus",
    "need_pdf_table_analysis": "true",
    "need_header_footer_analysis": "false",
    "is_one_column_document": "true",
    #"return_format": 'html'
}
with open(file_path, "rb") as file:
    files = {"file": (file_path, file)}
    r = requests.post("http://localhost:1231/upload", files=files, data=data)
    result = r.content.decode("utf-8")
    print(result)

# docker run -p 1231:1231 --rm dedocproject/dedoc python3 /dedoc_root/dedoc/main.py



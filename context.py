from pypdf import PdfReader

reader = PdfReader("linkedin.pdf")

linkedin = ''
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

print(linkedin)
print(summary)
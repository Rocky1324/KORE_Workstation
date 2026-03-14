import fitz
import sys

def inspect_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        print(f"File: {filepath}")
        print(f"Pages: {len(doc)}")
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text()
            print(f"Page {i+1} text length: {len(text)}")
            print(f"Page {i+1} text: '{text}'")
        doc.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_pdf(sys.argv[1])

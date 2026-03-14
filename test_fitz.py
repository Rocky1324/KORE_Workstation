import fitz
import os

def test_pdf_save():
    content = "This is a test note content to verify PDF export."
    filepath = "test_note.pdf"
    
    try:
        doc = fitz.open()
        page = doc.new_page() 
        rect = fitz.Rect(50, 50, 545, 792) 
        res = page.insert_textbox(rect, content, fontsize=11, fontname="helv", align=0)
        print(f"Insert textbox result: {res}")
        doc.save(filepath)
        doc.close()
        print(f"File saved to {filepath}")
        if os.path.exists(filepath):
            print(f"File size: {os.path.getsize(filepath)} bytes")
        else:
            print("File DOES NOT exist after save!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pdf_save()

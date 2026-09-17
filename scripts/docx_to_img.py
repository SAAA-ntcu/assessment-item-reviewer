"""
Convert specific pages of a DOCX to PNG images using Word COM + PyMuPDF.
Usage: python docx_to_img.py <docx_path> <page_num> <output_img>
"""
import sys
import os
import win32com.client
import pymupdf

def convert_page_to_image(docx_path, page_num, out_img):
    docx_path = os.path.abspath(docx_path)
    pdf_path = docx_path.replace('.docx', '_temp.pdf')
    
    # Step 1: Convert DOCX -> PDF via Word COM
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(docx_path)
        doc.SaveAs2(pdf_path, FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
    finally:
        word.Quit()
    
    # Step 2: Render specific page -> PNG via PyMuPDF
    pdf = pymupdf.open(pdf_path)
    page = pdf[page_num - 1]
    mat = pymupdf.Matrix(2, 2)  # 2x zoom for clarity
    pix = page.get_pixmap(matrix=mat)
    pix.save(out_img)
    pdf.close()
    
    os.remove(pdf_path)
    print(f"Saved page {page_num} to {out_img}")

if __name__ == '__main__':
    convert_page_to_image(sys.argv[1], int(sys.argv[2]), sys.argv[3])

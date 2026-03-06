import io
import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image
from typing import Optional
import pdfplumber

# Initialize easyocr reader (this may take time on first run)
# We use cpu=True to be safe since CUDA may not be available
reader = None

def get_ocr_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF while handling multi-column layouts.
    Uses PyMuPDF (fitz) with block analysis and fallback to pdfplumber.
    """
    text_parts = []
    
    try:
        # 1. Primary Method: PyMuPDF with block sorting
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            # get_text("blocks") returns a list of tuples: (x0, y0, x1, y1, "text", block_no, block_type)
            blocks = page.get_text("blocks")
            # Sort blocks: First by top Y (vertical), then by left X (horizontal)
            # This helps reconstruct columns: if Y is significantly different, it's a new row.
            # If Y is similar, we sort by X.
            blocks.sort(key=lambda b: (b[1], b[0]))
            
            page_text = ""
            for b in blocks:
                if b[4].strip():
                    page_text += b[4] + "\n"
            text_parts.append(page_text)
        doc.close()
    except Exception as e:
        print(f"PyMuPDF extraction failed: {e}")
        text_parts = []

    # 2. Secondary/Fallback: pdfplumber with layout preservation
    if not text_parts or len("\n".join(text_parts).strip()) < 20:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    # layout=True helps with simple column layouts
                    t = page.extract_text(layout=True)
                    if t:
                        text_parts.append(t)
        except Exception:
            pass

    # 3. Last Resort: OCR (limit to first 5 pages for stability)
    full_text = "\n".join(text_parts).strip()
    if len(full_text) < 10:
        print("Standard parsing failed. Using OCR for first 5 pages...")
        text_parts = []
        doc = None
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            ocr_reader = get_ocr_reader()
            for i, page in enumerate(doc):
                if i >= 5: 
                    print(f"Skipping OCR for page {i+1} (Limit reached)")
                    break
                
                print(f"OCR-ing page {i+1}...")
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # Scale down slightly for speed/RAM
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    results = ocr_reader.readtext(np.array(img), detail=0)
                    if results:
                        text_parts.append(" ".join(results))
                except Exception as page_e:
                    print(f"Page {i+1} OCR failed: {page_e}")
        except Exception as e:
            print(f"OCR Initialization failed: {e}")
            raise ValueError(f"Failed to parse PDF via OCR: {e}")
        finally:
            if doc: doc.close()

    final_text = "\n".join(text_parts).strip()
    if not final_text:
        raise ValueError("Could not extract any text from this PDF.")
    
    return final_text


def validate_pdf(filename: str, content_type: Optional[str], file_size: int) -> None:
    """
    Validate that uploaded file is a valid PDF by checking extension, MIME type, and size.
    Raises ValueError with a descriptive message if validation fails.
    """
    max_size_mb = 10
    max_size_bytes = max_size_mb * 1024 * 1024

    if not filename.lower().endswith(".pdf"):
        raise ValueError(
            f"Only PDF files are accepted. Received file: '{filename}'"
        )

    allowed_mimes = {"application/pdf", "application/x-pdf", "binary/octet-stream"}
    if content_type and content_type not in allowed_mimes:
        # Be lenient with MIME type — some browsers send octet-stream
        if "pdf" not in content_type.lower():
            raise ValueError(
                f"Invalid file type. Expected PDF but received MIME type: '{content_type}'"
            )

    if file_size > max_size_bytes:
        raise ValueError(
            f"File too large: {file_size / (1024*1024):.1f} MB. Maximum allowed is {max_size_mb} MB."
        )

    if file_size == 0:
        raise ValueError("Uploaded file is empty.")

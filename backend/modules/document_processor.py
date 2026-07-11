import os
import pypdf

def extract_pdf_text(filepath: str) -> dict:
    """
    Extracts text page-by-page from a PDF file. Calculates metadata
    such as page and word counts, generates a 500-character preview,
    and caches the full extracted text locally as a .txt file.
    
    Args:
        filepath (str): Absolute file path to the PDF on disk.
        
    Returns:
        dict: A dictionary containing 'pages', 'wordCount', and 'preview'.
        
    Raises:
        ValueError: If the PDF is encrypted or has no readable text.
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The PDF file at '{filepath}' does not exist.")
        
    try:
        reader = pypdf.PdfReader(filepath)
        
        # 1. Error handling: Encrypted PDFs
        if reader.is_encrypted:
            raise ValueError("This PDF document is encrypted and cannot be processed.")
            
        pages_count = len(reader.pages)
        if pages_count == 0:
            raise ValueError("This PDF document has zero pages.")
            
        extracted_pages = []
        for index, page in enumerate(reader.pages):
            page_text = page.extract_text()
            extracted_pages.append(page_text if page_text else "")
            
        full_text = " ".join(extracted_pages).strip()
        
        # 2. Error handling: Empty or Image-Only PDFs
        if not full_text:
            raise ValueError(
                "No readable text could be extracted. The PDF is empty or contains "
                "only scanned images that require optical character recognition (OCR)."
            )
            
        # 3. Calculate word count
        words = full_text.split()
        word_count = len(words)
        
        # 4. Cache the extracted text on the server for future NLP processing
        # E.g., backend/uploads/incoming/<uuid>.txt next to the PDF
        cached_txt_path = filepath.rsplit('.', 1)[0] + '.txt'
        with open(cached_txt_path, 'w', encoding='utf-8') as cache_file:
            cache_file.write(full_text)
            
        # 5. Generate a 500-character preview
        preview = full_text[:500]
        if len(full_text) > 500:
            preview += "..."
            
        return {
            "pages": pages_count,
            "wordCount": word_count,
            "preview": preview
        }
        
    except Exception as e:
        # If it's already a ValueError (from our checks), re-raise it
        if isinstance(e, ValueError):
            raise e
        # Otherwise, wrap other reading errors
        raise ValueError(f"Failed to parse PDF document: {str(e)}")

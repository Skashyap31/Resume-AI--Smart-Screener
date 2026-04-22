import io


def extract_resume_text(uploaded_file) -> str:
    """Extract text from uploaded PDF or TXT file."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    elif filename.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except ImportError:
            pass

        # Fallback: try pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(uploaded_file.read()))
            return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
        except ImportError:
            pass

        return "⚠️ Could not extract PDF. Install pypdf: pip install pypdf"

    return uploaded_file.read().decode("utf-8", errors="ignore")

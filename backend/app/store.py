"""Module-level state for the current uploaded document.
Day 3: just the raw text. Day 4 will add chunks + embeddings here.
"""

from . import rag

_doc_text: str = ""
_filename: str = ""

def set_document(filename: str, text: str) -> None:
    global _doc_text, _filename
    _doc_text = text
    _filename = filename

def get_text() -> str:
    return _doc_text

def get_filename() -> str:
    return _filename

def has_document() -> bool:
    return bool(_doc_text)

def clear() -> None:
    global _doc_text, _filename
    _doc_text = ""
    _filename = ""
    rag.clear()

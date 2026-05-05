"""Keyword stub classifier. Day 9 replaces this with a remote ML call,
keeping the same function signature."""
from __future__ import annotations

_DEF_KW  = ("what is", "what's", "define", "definition of", "meaning of")
_EX_KW   = ("example", "for instance", "give me an example", "show me")
_COMP_KW = ("difference", " vs ", "versus", "compare", "compared to")

def classify(q: str) -> str:
    ql = f" {q.lower().strip()} "  # pad so " vs " matches at edges
    if any(k in ql for k in _COMP_KW): return "comparison"
    if any(k in ql for k in _EX_KW):   return "example"
    if any(k in ql for k in _DEF_KW):  return "definition"
    return "definition"  # safe default

# AskMyNotes

Day 3 of 9 — PDF upload + text extraction.

## Run Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/
```

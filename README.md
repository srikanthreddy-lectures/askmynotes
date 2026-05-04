# AskMyNotes

Day 2 of 9 — backend live, single-port architecture working.

## Run Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/
```

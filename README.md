# ATS Resume Scorer API

A FastAPI service that scores how well a resume matches a job description, similar to how Applicant Tracking Systems (ATS) screen resumes.

I built this after improving my own resume's ATS score from 52 to 88 through manual iteration. I wanted to understand how that scoring works under the hood and automate it myself.

## Features

- Upload a resume (PDF) and paste a job description
- Get a 0-100 match score based on TF-IDF + cosine similarity
- See exactly which keywords matched and which are missing
- Input validation and clean error responses (wrong file type, empty input, unreadable PDFs)
- Interactive API docs (Swagger UI) generated automatically by FastAPI

## Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | API framework |
| Uvicorn | ASGI server that runs the app |
| python-multipart | Parses file uploads and form data |
| pdfplumber | Extracts text from PDF resumes |
| scikit-learn | TF-IDF vectorization and cosine similarity |

## Project Structure

```
ats-resume-scorer/
├── app/
│   ├── __init__.py
│   ├── main.py          # API routes and request validation
│   ├── pdf_utils.py     # PDF text extraction
│   └── scoring.py       # TF-IDF scoring and keyword gap analysis
├── requirements.txt
├── .gitignore
└── README.md
```

Business logic (PDF parsing, scoring) is kept out of the route handlers so each piece can be tested and extended independently.

## How It Works

1. The resume PDF is read in memory (using `BytesIO`, no temp files on disk) and converted to text with `pdfplumber`.
2. A `TfidfVectorizer` is fitted on the job description only, so the vocabulary and term weights come from what the job actually asks for.
3. Both the job description and the resume are transformed using that vocabulary.
4. Cosine similarity between the two vectors, scaled to 0-100, gives the match score.
5. A separate keyword step (regex + set operations) lists matched and missing terms, so the score is explainable and not just a number.

### Why the vectorizer is fitted on the job description only

My first version fitted TF-IDF on both documents together. Testing showed scores far lower than expected, because with a corpus of only two documents the IDF weighting works against us:

- Words present in both documents (the real matches) get a lower weight than words present in only one.
- A long resume with many unrelated sections (contact info, education) dilutes the similarity.

Fitting on the job description alone turns the score into "how well does the resume cover what this job asks for", which is what an ATS-style score should measure. On my test set (one resume, three job descriptions of decreasing relevance), the scores moved from roughly 47 / 25 / 5 to 79 / 72 / 49, with the ranking preserved.

## Running Locally

```bash
# 1. Clone and enter the project
git clone https://github.com/YOUR_USERNAME/ats-resume-scorer.git
cd ats-resume-scorer

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## API Reference

### `GET /health`

Returns `{"status": "ok"}`.

### `POST /score`

Request type: `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `resume` | file (PDF) | The resume to score |
| `job_description` | string | The job description text |

Example response:

```json
{
  "filename": "resume.pdf",
  "score": 78.98,
  "matched_keywords": ["developer", "git", "mysql", "python", "sql"],
  "missing_keywords": ["docker", "fastapi", "rest"]
}
```

### Error responses

| Status | When |
|---|---|
| 400 | File is not a PDF, job description is empty, or uploaded file is empty |
| 422 | PDF is corrupted/password-protected, or contains no extractable text (scanned image) |

Example: `{"detail": "Only PDF files are supported. Got: image/jpeg"}`

## Design Decisions

- **`Form` fields instead of a JSON body:** file uploads require `multipart/form-data`, which cannot be combined with a JSON body, so the job description is sent as a form field.
- **`async` endpoint:** reading an uploaded file is I/O-bound, so async lets the server handle other requests while waiting.
- **400 vs 422:** 400 means the request itself was invalid; 422 means the request was well-formed but the content could not be processed.
- **Two complementary mechanisms:** TF-IDF + cosine similarity gives the overall score, and keyword set operations explain what is matched or missing.

## Known Limitations

- **No OCR:** scanned or image-based PDFs return a 422 because no text can be extracted.
- **Simple keyword extraction:** it uses regex and a small stopword list, so generic words from a job posting (for example "looking" or "plus") can appear in the missing list. spaCy or NLTK with part-of-speech filtering would improve this.
- **Generic word noise:** words like "experience" or "strong" can inflate the score for an unrelated job description.
- **Lexical, not semantic, matching:** "REST API" and "web services" are treated as different terms.
- **PDF only:** DOCX resumes are not supported yet.

## Future Improvements

- OCR fallback (Tesseract) for scanned resumes
- spaCy-based keyword extraction with part-of-speech filtering
- DOCX support
- Sentence embeddings (for example sentence-transformers) for semantic matching
- Automated tests with pytest
- Rate limiting and file size limits
- Deployment (Render / Railway) with a live demo link

## Author

Pranav Chavan

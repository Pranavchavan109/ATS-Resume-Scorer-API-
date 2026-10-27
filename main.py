from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.pdf_utils import extract_text_from_pdf
from app.scoring import compute_match_score, get_keyword_gaps

app = FastAPI(
    title="ATS Resume Scorer API",
    description="Upload a resume + job description, get an ATS-style match score.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/score")
async def score_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    # 1. Validate file type
    if resume.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are supported. Got: {resume.content_type}",
        )

    # 2. Validate job description isn't just whitespace
    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="job_description cannot be empty.",
        )

    file_bytes = await resume.read()

    # 3. Validate the file isn't empty
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 4. Handle corrupted/unreadable PDFs
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not read the PDF. It may be corrupted or password-protected.",
        )

    # 5. Handle PDFs with no extractable text (e.g. scanned images)
    if not resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No extractable text found in this PDF. It may be a scanned image (OCR not supported yet).",
        )

    score = compute_match_score(resume_text, job_description)
    keyword_gaps = get_keyword_gaps(resume_text, job_description)

    return {
        "filename": resume.filename,
        "score": score,
        "matched_keywords": keyword_gaps["matched_keywords"],
        "missing_keywords": keyword_gaps["missing_keywords"],
    }




















### first code 

# from fastapi import FastAPI

# app = FastAPI(
#     title="ATS Resume Scorer API",
#     description="Upload a resume + job description, get an ATS-style match score.",
#     version="1.0.0",
# )


# @app.get("/health")              # decorator
# def health():
#     return {"status": "ok"}



### second code

# from fastapi import FastAPI, UploadFile, File, Form

# app = FastAPI(
#     title="ATS Resume Scorer API",
#     description="Upload a resume + job description, get an ATS-style match score.",
#     version="1.0.0",
# )


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# @app.post("/score")
# async def score_resume(
#     resume: UploadFile = File(...),
#     job_description: str = Form(...),
# ):
    
#     # Step 5: just prove the request/response cycle works, before adding real logic
#     return {
#         "filename": resume.filename,
#         "content_type": resume.content_type,
#         "job_description_length": len(job_description),
#         "score": 0,
#         "matched_keywords": [],
#         "missing_keywords": [],
#     }



## fourth code


# from fastapi import FastAPI, UploadFile, File, Form
# from app.pdf_utils import extract_text_from_pdf
# from app.scoring import compute_match_score, get_keyword_gaps

# app = FastAPI(
#     title="ATS Resume Scorer API",
#     description="Upload a resume + job description, get an ATS-style match score.",
#     version="1.0.0",
# )


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# @app.post("/score")
# async def score_resume(
#     resume: UploadFile = File(...),
#     job_description: str = Form(...),
# ):
#     file_bytes = await resume.read()
#     resume_text = extract_text_from_pdf(file_bytes)

#     score = compute_match_score(resume_text, job_description)
#     keyword_gaps = get_keyword_gaps(resume_text, job_description)

#     return {
#         "filename": resume.filename,
#         "score": score,
#         "matched_keywords": keyword_gaps["matched_keywords"],
#         "missing_keywords": keyword_gaps["missing_keywords"],
#     }
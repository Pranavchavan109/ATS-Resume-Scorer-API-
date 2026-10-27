from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


# def compute_match_score(resume_text: str, job_description: str) -> float:
#     """
#     Returns a 0-100 score representing how well the resume matches the job description.
#     """
#     documents = [resume_text, job_description]

#     vectorizer = TfidfVectorizer(stop_words="english")
#     tfidf_matrix = vectorizer.fit_transform(documents)

#     # cosine_similarity returns a 2x2 matrix comparing every doc to every other doc.
#     # [0][1] = similarity between resume (doc 0) and job description (doc 1)
    
#     similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

#     return round(similarity * 100, 2)


def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Returns a 0-100 score representing how well the resume covers the job description's
    important terms.

    DESIGN CHOICE: the TF-IDF vectorizer is fit ONLY on the job description, not on both
    documents together. Fitting on both (the naive approach) computes IDF weights over
    just a 2-document corpus, which causes two problems:
      1. Words appearing in BOTH docs (real matches) get LOWER IDF weight than words
         appearing in only one doc -- the opposite of what we want.
      2. A long resume's many JD-irrelevant sections (education, contact info, etc.)
         dilute the similarity, since they add "mass" to the resume vector that has
         nothing to do with the job.

    Fitting the vectorizer on the JD alone means the vocabulary and importance weights
    come purely from what the job asks for. The resume is then scored against that same
    vocabulary -- so only JD-relevant terms in the resume count at all. This turns the
    score into "how well does the resume cover the JD's important terms" rather than
    "how similar are these two documents overall" -- which is what an ATS-style match
    score should actually measure.
    """
    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit([job_description])  # vocabulary + IDF weights come from the JD only

    jd_vector = vectorizer.transform([job_description])
    resume_vector = vectorizer.transform([resume_text])  # scored against JD's vocabulary

    similarity = cosine_similarity(resume_vector, jd_vector)[0][0]

    return round(similarity * 100, 2)



def extract_keywords(text: str) -> set:
    """
    Very simple keyword extraction: lowercase, strip punctuation, split into words,
    remove very short/common words. Not NLP-grade, but transparent and explainable.
    """
    words = re.findall(r"[a-zA-Z\+\#]+", text.lower())
    stop_words = {
        "and", "or", "the", "a", "an", "in", "on", "with", "for", "to", "of",
        "is", "are", "will", "we", "you", "your", "our", "as", "be", "at",
    }
    return {w for w in words if len(w) > 2 and w not in stop_words}



def get_keyword_gaps(resume_text: str, job_description: str) -> dict:
    """
    Compares keyword sets to find what's matched vs missing.
    """
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    matched = sorted(jd_keywords & resume_keywords)      # intersection
    missing = sorted(jd_keywords - resume_keywords)       # in JD but not in resume

    return {"matched_keywords": matched, "missing_keywords": missing}
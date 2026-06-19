import re

from rapidfuzz import process, fuzz


MEDICINE_MASTER = [
    "Paracetamol",
    "Calpol",
    "Crocin",
    "Dolo 650",

    "Amoxicillin",
    "Augmentin",

    "Azithromycin",
    "Azithral",

    "Pantoprazole",
    "Pantocid",
    "Pan-D",

    "Cetirizine",
    "Levocetirizine",

    "Ibuprofen",
    "Aspirin",

    "Metformin",

    "Vitamin D3",

    "Levolin",
    "Meftal-P",

    "Betaloc",
    "Metoprolol",

    "Amlodipine",
    "Losartan",
    "Telmisartan",

    "Atorvastatin",
    "Rosuvastatin",

    "Omeprazole",
    "Rabeprazole",

    "Dorzolamide",
    "Cimetidine"
]


IGNORE_WORDS = [
    "hospital",
    "medical centre",
    "medical center",
    "doctor",
    "mbbs",
    "md",
    "address",
    "street",
    "road",
    "avenue",
    "signature",
    "refill",
    "phone",
    "ph",
    "mobile",
    "date",
    "name",
    "gender",
    "weight",
    "age",
    "registration",
    "reg no",
    "usa"
]


MEDICINE_PREFIXES = [
    "tab",
    "tablet",
    "cap",
    "capsule",
    "syp",
    "syrup",
    "inj",
    "injection",
    "drops",
    "neb"
]

def is_candidate_medicine(text: str) -> bool:

    text = text.strip()

    if len(text) < 3:
        return False

    lower_text = text.lower()

    # Ignore known junk

    for word in IGNORE_WORDS:
        if word in lower_text:
            return False

    # URLs

    if ".com" in lower_text:
        return False

    # phone numbers

    if re.search(r"\d{8,}", text):
        return False

    # mostly numbers

    letters = sum(c.isalpha() for c in text)

    if letters < 3:
        return False

    return True

def find_best_medicine_match(text: str):

    if not is_candidate_medicine(text):
        return None

    match = process.extractOne(
        query=text,
        choices=MEDICINE_MASTER,
        scorer=fuzz.WRatio
    )

    if not match:
        return None

    medicine_name, score, _ = match

    return {
        "raw_text": text,
        "suggested_name": medicine_name,
        "confidence_score": round(score, 2),
        "needs_review": score < 70
    }


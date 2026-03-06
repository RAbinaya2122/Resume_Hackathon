import re
from typing import List

# Common first names used for bias-free stripping
COMMON_NAMES = {
    "james", "john", "robert", "michael", "william", "david", "richard", "joseph", "charles", "thomas",
    "mary", "patricia", "linda", "barbara", "elizabeth", "jennifer", "maria", "susan", "margaret", "dorothy",
    "priya", "rahul", "amit", "neha", "anjali", "vikram", "pooja", "arjun", "kavya", "rohit",
    "aisha", "fatima", "omar", "hassan", "layla", "ali", "sara", "ahmed", "zara", "ibrahim",
    "wei", "li", "zhang", "liu", "chen", "yang", "huang", "zhao", "wu", "zhou",
    "raj", "ravi", "sita", "rani", "kumar", "suresh", "ramesh", "geeta", "sunita", "anita"
}

# Common Indian/global college patterns for bias-free mode
COLLEGE_PATTERNS = [
    r'\b(iit|iim|nit|bits|vit|mit|stanford|harvard|oxford|cambridge|yale|princeton)\b',
    r'\b(university|college|institute|school of|faculty of)\s+[\w\s]+',
    r'\b[\w\s]+(university|college|institute)\b',
]

# Gender indicator words
GENDER_INDICATORS = [
    r'\b(mr|mrs|ms|miss|sir|madam|he|she|his|her|him|himself|herself)\b',
    r'\b(male|female|man|woman|boy|girl|gentleman|lady)\b',
]

# Location patterns (cities/states/countries) - a representative set
LOCATION_PATTERNS = [
    r'\b(mumbai|delhi|bangalore|bengaluru|hyderabad|chennai|kolkata|pune|ahmedabad|jaipur)\b',
    r'\b(new york|los angeles|san francisco|chicago|boston|seattle|austin|london|paris|berlin|tokyo|dubai)\b',
    r'\b(india|usa|uk|canada|australia|germany|france|singapore|uae)\b',
    r'\b(state|city|town|village|district|province|county)\b:\s*[\w\s]+',
    r'\d{3}[-\s]?\d{3}[-\s]?\d{4}',  # phone numbers
    r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',  # email
    r'\b\d{6}\b',  # PIN codes
]


def clean_text(text: str) -> str:
    """Basic text cleanup: normalize whitespace, remove special chars."""
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def strip_bias_indicators(text: str) -> str:
    """
    Remove name, college, gender, and location indicators from text
    to enable bias-free evaluation.
    """
    result = text

    # Remove gender indicators
    for pattern in GENDER_INDICATORS:
        result = re.sub(pattern, '[REDACTED]', result, flags=re.IGNORECASE)

    # Remove location patterns
    for pattern in LOCATION_PATTERNS:
        result = re.sub(pattern, '[REDACTED]', result, flags=re.IGNORECASE)

    # Remove college/university references
    for pattern in COLLEGE_PATTERNS:
        result = re.sub(pattern, '[INSTITUTION REDACTED]', result, flags=re.IGNORECASE)

    # Remove common first names (only standalone words)
    words = result.split()
    cleaned_words = []
    for word in words:
        clean_word = re.sub(r'[^a-zA-Z]', '', word).lower()
        if clean_word in COMMON_NAMES:
            cleaned_words.append('[NAME REDACTED]')
        else:
            cleaned_words.append(word)
    result = ' '.join(cleaned_words)

    return result


def extract_years_of_experience(text: str) -> float:
    """
    Extract number of years of experience from resume text.
    Conservative approach: focuses on 'Experience' section and avoids education dates.
    """
    # 1. Look for explicit "X years experience" patterns first (highest confidence)
    patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+(?:professional\s+)?experience',
        r'(\d+(?:\.\d+)?)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+(?:\.\d+)?)\+?\s*years?',
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*years?\s+(?:of\s+)?experience',
        r'(\d+(?:\.\d+)?)\+?\s*yrs?\s+(?:of\s+)?experience',
        r'worked\s+for\s+(\d+(?:\.\d+)?)\+?\s*years?',
        r'(\d+(?:\.\d+)?)\+?\s*years?\s+(?:in|of)\s+(?:the\s+)?(?:industry|field|domain)',
        r'(?:total|overall|summary)\s*:\s*(\d+(?:\.\d+)?)\+?\s*years?',
    ]

    years_found: List[float] = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                try:
                    low, high = float(match[0]), float(match[1])
                    years_found.append((low + high) / 2)
                except (ValueError, IndexError): pass
            else:
                try: years_found.append(float(match))
                except ValueError: pass

    if years_found:
        return max(years_found)

    # 2. Date Math Fallback (Focus on Experience Section)
    exp_headers = r'\b(experience|employment|work history|professional background|career)\b'
    edu_headers = r'\b(education|academic|qualification|university|college|schooling)\b'
    
    segments = re.split(f'({exp_headers}|{edu_headers})', text, flags=re.IGNORECASE)
    
    total_years = 0.0
    current_year = 2025
    is_in_exp_section = False
    
    date_range_pattern = r'\b(19\d{2}|20\d{2})\s*[-–to]+\s*(20\d{2}|present|current|now)\b'

    for i in range(len(segments)):
        if segments[i] is None:
            continue
        seg = segments[i].lower()
        if re.search(exp_headers, seg):
            is_in_exp_section = True
            continue
        if re.search(edu_headers, seg):
            is_in_exp_section = False
            continue
        
        if is_in_exp_section:
            ranges = re.findall(date_range_pattern, seg, re.IGNORECASE)
            min_y, max_y = float('inf'), float('-inf')
            for start, end in ranges:
                try:
                    s = int(start)
                    e = current_year if end.strip().lower() in ('present', 'current', 'now') else int(end)
                    if 1970 < s <= current_year and s <= e:
                        min_y, max_y = min(min_y, s), max(max_y, e)
                except ValueError: pass
            
            if max_y > min_y:
                total_years += (max_y - min_y)

    return min(total_years, 45.0) if total_years > 0 else 0.0


def extract_contact_info(text: str) -> dict:
    """
    Extract candidate name, email, and phone number from resume text.
    Uses regex for email/phone and heuristics for name.
    """
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    # Handles various phone formats
    phone_pattern = r'(?:\+?\d{1,3}[-\.\s]?)?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}'

    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)

    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0) if phone_match else None

    # Name extraction heuristic:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = None

    # First, look for an explicit "Name: " prefix anywhere in the first 20 lines
    for line in lines[:20]:
        if re.search(r'^(?:Name|Candidate Name|Full Name)\s*[:\-]\s*', line, flags=re.IGNORECASE):
            clean_line = re.sub(r'^(?:Name|Candidate Name|Full Name)\s*[:\-]\s*', '', line, flags=re.IGNORECASE).strip()
            # Basic validation
            if 2 < len(clean_line) < 50 and not re.search(r'\d', clean_line):
                name = clean_line
                break
    
    if name:
        return {"name": name, "email": email, "phone": phone}

    # Second pass: heuristic for the first reasonable line
    skip_word_list = [
        "resume", "curriculum", "vitae", "summary", "objective", "experience", 
        "education", "skills", "contact", "profile", "links", "github", 
        "linkedin", "portfolio", "address", "phone", "email", "mobile",
        "professional", "background", "awards", "projects", "certifications",
        "engineer", "developer", "manager", "lead", "analyst", "specialist", 
        "designer", "consultant", "intern", "associate", "expert", "student",
        "university", "college", "institute", "school", "page", "location"
    ]
    skip_words = set(skip_word_list)

    # We look at fewer lines (10) for the aggressive first-pass name detection
    # because typically names are at the very top.
    for i, line in enumerate(lines[:15]):
        # Remove common contact labels and noise
        clean_line = re.sub(r'^(Email|Phone|Mobile|Contact|Address|Location|LinkedIn|GitHub|Website)\s*[:\-]\s*', '', line, flags=re.IGNORECASE)
        # Remove phrases like "Curriculum Vitae" or "Resume"
        clean_line = re.sub(r'\b(Curriculum Vitae|Resume|Profile Summary)\b', '', clean_line, flags=re.IGNORECASE)
        clean_line = clean_line.strip()
        
        # Strip trailing things like phone/email if they were on the same line
        if email and email.lower() in clean_line.lower():
            clean_line = clean_line.lower().replace(email.lower(), "").strip()
        if phone and phone in clean_line:
            clean_line = clean_line.replace(phone, "").strip()
        
        # Remove common symbols often found in headers
        clean_line = re.sub(r'[|•·\*]', ' ', clean_line).strip()
        
        # Remove titles/certifications after the name if present (e.g. "John Doe, PMP")
        if ',' in clean_line:
            parts = clean_line.split(',')
            if len(parts[1].strip().split()) <= 2:
                clean_line = parts[0].strip()

        # Name should be fairly short and mostly alphabetical
        if 2 < len(clean_line) < 60 and re.match(r'^[a-zA-Z\s\.\-\']+$', clean_line):
            words = clean_line.split()
            
            # Skip if any word is a definitive skip word
            if any(w.lower() in skip_words for w in words):
                continue
                
            # Names are usually Title Case (John Doe)
            if not any(w[0].isupper() for w in words if len(w) > 0):
                continue

            # Page numbers or dates - ignore if digits found
            if re.search(r'\d', clean_line):
                continue
            
            # THE FIRST REASONABLE LINE (usually lines[0] or lines[1]) is highly likely the name
            # Even if it's 1 word (like "Adhip"), if it's at the very top, we can trust it.
            if i < 3:
                name = clean_line.strip()
                break
            
            # For lines further down, we require at least 2 words to be sure
            if len(words) >= 2:
                name = clean_line.strip()
                break

    return {
        "name": name,
        "email": email,
        "phone": phone
    }

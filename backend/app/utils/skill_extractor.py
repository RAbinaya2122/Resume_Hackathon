import re
from typing import List, Set

# Comprehensive skill taxonomy covering major tech and non-tech domains
SKILL_TAXONOMY = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
    "rust", "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "perl",
    "bash", "shell", "powershell", "dart", "elixir", "haskell", "lua", "julia",

    # Web Frameworks & Libraries
    "react", "reactjs", "react.js", "angular", "angularjs", "vue", "vuejs", "vue.js",
    "svelte", "next.js", "nextjs", "nuxt", "gatsby", "remix", "fastapi", "flask",
    "django", "express", "expressjs", "fastify", "nestjs", "spring", "spring boot",
    "asp.net", "laravel", "rails", "ruby on rails", "strapi", "graphql",

    # Databases
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "cassandra", "elasticsearch",
    "dynamodb", "firestore", "neo4j", "mssql", "oracle", "mariadb", "influxdb",
    "supabase", "planetscale", "cockroachdb",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform",
    "ansible", "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
    "helm", "argocd", "prometheus", "grafana", "nginx", "apache", "linux",
    "devops", "ci/cd", "infrastructure as code", "iac",

    # Data Science & Machine Learning
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "data science", "data analysis", "data engineering",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
    "matplotlib", "seaborn", "plotly", "spark", "hadoop", "airflow", "mlflow",
    "hugging face", "transformers", "bert", "gpt", "llm", "langchain",
    "feature engineering", "model training", "xgboost", "lightgbm", "catboost",
    "neural networks", "cnn", "rnn", "lstm", "gans", "reinforcement learning",

    # Mobile
    "android", "ios", "react native", "flutter", "xamarin", "ionic", "cordova",

    # Security
    "cybersecurity", "penetration testing", "pentesting", "ethical hacking",
    "owasp", "vulnerability assessment", "soc", "siem", "firewall", "encryption",
    "ssl", "tls", "oauth", "jwt", "cryptography", "network security",

    # Version Control & Collaboration
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "notion",
    "agile", "scrum", "kanban", "waterfall", "sdlc",

    # APIs & Integration
    "rest", "restful", "rest api", "graphql", "soap", "grpc", "websocket",
    "microservices", "api design", "swagger", "openapi", "postman",

    # Design & UX
    "figma", "adobe xd", "sketch", "photoshop", "illustrator", "ui/ux",
    "user research", "wireframing", "prototyping", "design systems",

    # Data & Analytics
    "tableau", "power bi", "looker", "metabase", "excel", "sql",
    "data visualization", "etl", "data warehouse", "dbt", "bigquery",
    "snowflake", "redshift", "statistics", "hypothesis testing",

    # Soft Skills & Management
    "project management", "product management", "leadership", "communication",
    "problem solving", "critical thinking", "team collaboration", "mentoring",
    "stakeholder management", "risk management", "budget management",

    # Networking & Infrastructure
    "networking", "tcp/ip", "dns", "load balancing", "cdn", "vpn",
    "aws ec2", "aws s3", "aws lambda", "aws rds",

    # Testing
    "unit testing", "integration testing", "selenium", "cypress", "jest",
    "pytest", "junit", "mocha", "test driven development", "tdd", "bdd",

    # Blockchain
    "blockchain", "solidity", "ethereum", "smart contracts", "web3",

    # Other Tech
    "rabbitmq", "kafka", "celery", "redis queue", "websockets",
    "linux", "unix", "bash scripting", "regex", "xml", "json", "yaml",
    "sass", "css", "html", "tailwindcss", "bootstrap", "material ui",
}

# Soft Skills Taxonomy
SOFT_SKILLS_TAXONOMY = {
    "communication", "leadership", "teamwork", "collaboration", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity", "emotional intelligence",
    "conflict resolution", "negotiation", "decision making", "public speaking", "active listening",
    "mentoring", "coaching", "organization", "work ethic", "interpersonal skills",
    "presentation skills", "customer service", "strategic thinking", "attention to detail",
}

# Languages Taxonomy
LANGUAGES_TAXONOMY = {
    "english", "spanish", "french", "german", "mandarin", "chinese", "japanese",
    "korean", "hindi", "arabic", "portuguese", "russian", "italian", "dutch",
    "turkish", "tamil", "telugu", "marathi", "bengali", "gujarati", "malayalam",
}

# Multi-word skill phrases that need special handling
MULTI_WORD_SKILLS = [s for s in SKILL_TAXONOMY if ' ' in s]
SINGLE_WORD_SKILLS = {s for s in SKILL_TAXONOMY if ' ' not in s}


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from text using keyword matching.
    Returns a deduplicated, sorted list of found skills.
    """
    text_lower = text.lower()
    found: Set[str] = set()

    # First pass: match multi-word skills (order matters — longer first)
    sorted_multi = sorted(MULTI_WORD_SKILLS, key=len, reverse=True)
    for skill in sorted_multi:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)

    # Second pass: match single-word skills
    # Tokenize text to avoid partial matches
    tokens = set(re.findall(r'\b[a-z][a-z0-9+#./\-]*\b', text_lower))
    for token in tokens:
        if token in SINGLE_WORD_SKILLS:
            found.add(token)

    # Normalize common aliases
    normalized = set()
    alias_map = {
        "reactjs": "react",
        "react.js": "react",
        "vuejs": "vue",
        "vue.js": "vue",
        "nextjs": "next.js",
        "sklearn": "scikit-learn",
        "golang": "go",
        "k8s": "kubernetes",
        "nodejs": "node.js",
    }
    for skill in found:
        normalized.add(alias_map.get(skill, skill))

    return sorted(normalized)


def extract_soft_skills(text: str) -> List[str]:
    """Extract soft skills from text."""
    text_lower = text.lower()
    found = set()
    for skill in SOFT_SKILLS_TAXONOMY:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found.add(skill)
    return sorted(list(found))


def extract_languages(text: str) -> List[str]:
    """Extract languages from text."""
    text_lower = text.lower()
    found = set()
    for lang in LANGUAGES_TAXONOMY:
        if re.search(r'\b' + re.escape(lang) + r'\b', text_lower):
            found.add(lang)
    return sorted(list(found))


def extract_projects(text: str) -> List[str]:
    """
    Extract project-like titles or sentences.
    Simplified: Look for paragraphs/lines starting with 'Project:' or containing 'Implemented'.
    """
    projects = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if re.search(r'\b(Project|Develop|Build|Implemented)\b', line, re.IGNORECASE) and len(line) > 20:
            projects.append(line)
    return projects[:5] # Return top 5 findings


def get_domain_from_skills(skills: List[str]) -> str:
    """
    Classify a candidate's domain based on their skill set.
    """
    skill_set = set(s.lower() for s in skills)

    domain_profiles = {
        "Data Science / ML": {
            "machine learning", "deep learning", "data science", "tensorflow", "pytorch",
            "keras", "scikit-learn", "nlp", "computer vision", "pandas", "numpy",
            "mlflow", "hugging face", "transformers", "statistical analysis"
        },
        "Backend Engineering": {
            "python", "java", "go", "rust", "fastapi", "django", "flask", "spring",
            "express", "microservices", "rest api", "grpc", "postgresql", "mysql",
            "mongodb", "redis", "kafka", "rabbitmq"
        },
        "Frontend Engineering": {
            "react", "angular", "vue", "next.js", "typescript", "javascript",
            "html", "css", "sass", "tailwindcss", "bootstrap", "figma",
            "svelte", "gatsby", "remix", "webpack"
        },
        "Full Stack Engineering": {
            "react", "node.js", "python", "javascript", "typescript",
            "rest api", "postgresql", "mongodb", "docker"
        },
        "DevOps / Cloud Engineering": {
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
            "jenkins", "ci/cd", "linux", "nginx", "prometheus", "grafana",
            "github actions", "helm"
        },
        "Mobile Development": {
            "android", "ios", "react native", "flutter", "swift", "kotlin",
            "xamarin", "ionic", "dart"
        },
        "Cybersecurity": {
            "cybersecurity", "penetration testing", "ethical hacking", "owasp",
            "vulnerability assessment", "soc", "encryption", "ssl", "network security"
        },
        "Data Engineering": {
            "spark", "hadoop", "airflow", "etl", "data warehouse", "dbt",
            "bigquery", "snowflake", "redshift", "kafka", "sql",
            "data engineering", "data pipelines"
        },
        "Product Management": {
            "product management", "agile", "scrum", "jira", "stakeholder management",
            "roadmap", "user research", "wireframing"
        },
    }

    scores = {}
    for domain, signature_skills in domain_profiles.items():
        overlap = len(skill_set & signature_skills)
        scores[domain] = overlap

    if not any(v > 0 for v in scores.values()):
        return "General / Other"

    return max(scores, key=scores.get)

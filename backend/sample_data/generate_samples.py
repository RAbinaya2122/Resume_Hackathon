from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_resume_pdf(filename, content):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50
    
    for line in content.split('\n'):
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    print(f"Created {filename}")

# Sample 1: Strong ML Candidate
ml_candidate = """
John Doe
123 ML Street, San Francisco, CA
Email: john.doe@example.com

SUMMARY
Highly experienced Machine Learning Engineer with 6 years of experience in deep learning and NLP.

SKILLS
Programming: Python, C++, SQL, Bash
Frameworks: TensorFlow, PyTorch, scikit-learn, Keras
Tools: Docker, AWS, Git, MLflow, Airflow
Data: pandas, numpy, matplotlib, Spark
Domains: NLP, Computer Vision, Statistics

EXPERIENCE
Senior ML Engineer | TechCorp | 2020 - Present
- Built production NLP pipelines using transformers and BERT models.
- Optimized model deployment using Docker and AWS SageMaker.
- Mentored junior engineers and led model architecture reviews.

ML Engineer | StartupAI | 2018 - 2020
- Developed computer vision models for object detection.
- Scaled data pipelines using Spark and Airflow.

EDUCATION
Master of Science in Computer Science | Stanford University
"""

# Sample 2: Full Stack Developer
fs_candidate = """
Jane Smith
456 Web Lane, New York, NY
Email: jane.smith@example.com

SUMMARY
Full Stack Developer with 4 years of experience building modern web applications.

SKILLS
Frontend: React, TypeScript, Redux, Tailwind CSS, HTML, CSS
Backend: Node.js, Express, FastAPI, Python
Databases: PostgreSQL, MongoDB, Redis
DevOps: Docker, AWS, GitHub Actions, Git
Other: GraphQL, REST API, Jest

EXPERIENCE
Full Stack Engineer | WebFlow | 2021 - Present
- Developed high-performance React applications with TypeScript.
- Built scalable backend services using Node.js and FastAPI.
- automated deployments via GitHub Actions and Docker.

Junior Developer | CodeBase | 2020 - 2021
- Maintained legacy JavaScript applications.
- Assisted in migration to PostgreSQL from MySQL.

EDUCATION
Bachelor of Engineering | Massachusetts Institute of Technology
"""

# Sample 3: Early Career Data Analyst (Lower match for ML roles)
da_candidate = """
Alex Johnson
789 Data Road, Austin, TX
Email: alex.j@example.com

SUMMARY
Aspiring Data Analyst with 1 year of experience in data visualization and SQL.

SKILLS
Tools: Excel, Tableau, Power BI, SQL
Tech: Python, pandas, Git, statistics
Other: Communication, Project Management

EXPERIENCE
Data Analyst Intern | RetailData | 2023 - 2024
- Created dashboards using Tableau and Power BI.
- Wrote SQL queries to extract business insights.

EDUCATION
Bachelor of Science in Statistics | University of Texas
"""

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    create_resume_pdf(os.path.join(output_dir, "ml_expert_resume.pdf"), ml_candidate)
    create_resume_pdf(os.path.join(output_dir, "full_stack_resume.pdf"), fs_candidate)
    create_resume_pdf(os.path.join(output_dir, "data_analyst_resume.pdf"), da_candidate)

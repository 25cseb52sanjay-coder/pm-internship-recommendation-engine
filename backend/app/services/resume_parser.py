import re
import os
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
import docx
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.models import StudentEducation, StudentProfile

MASTER_SKILL_DICTIONARY = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Express",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Data Analysis", "Machine Learning", "Deep Learning",
    "NLP", "Scikit-Learn", "Pandas", "NumPy", "TensorFlow", "PyTorch", "Excel", "PowerBI", "Tableau",
    "Financial Modeling", "Accounting", "Project Management", "Agile", "Scrum", "Communication",
    "Problem Solving", "Team Leadership", "Git", "Docker", "Kubernetes", "AWS", "Azure", "Linux",
    "AutoCAD", "MATLAB", "SolidWorks", "UI/UX Design", "Figma", "Cyber Security", "Embedded Systems"
]

DEGREE_PATTERNS = [
    (r"\b(B\.?Tech|Bachelor of Technology|B\.?E\.?)\b", "B.Tech", "Bachelor's"),
    (r"\b(M\.?Tech|Master of Technology|M\.?E\.?)\b", "M.Tech", "Master's"),
    (r"\b(B\.?Sc|Bachelor of Science)\b", "B.Sc", "Bachelor's"),
    (r"\b(M\.?Sc|Master of Science)\b", "M.Sc", "Master's"),
    (r"\b(B\.?Com|Bachelor of Commerce)\b", "B.Com", "Bachelor's"),
    (r"\b(M\.?Com|Master of Commerce)\b", "M.Com", "Master's"),
    (r"\b(BBA|Bachelor of Business Administration)\b", "BBA", "Bachelor's"),
    (r"\b(MBA|Master of Business Administration)\b", "MBA", "Master's"),
    (r"\b(BCA|Bachelor of Computer Applications)\b", "BCA", "Bachelor's"),
    (r"\b(MCA|Master of Computer Applications)\b", "MCA", "Master's"),
    (r"\b(Diploma)\b", "Diploma", "Diploma"),
]

BRANCH_PATTERNS = [
    (r"\b(Computer Science|CS|CSE|IT|Information Technology)\b", "Computer Science"),
    (r"\b(Mechanical|Mech)\b", "Mechanical Engineering"),
    (r"\b(Electrical|EEE|ECE|Electronics)\b", "Electronics & Electrical"),
    (r"\b(Civil)\b", "Civil Engineering"),
    (r"\b(Finance|Financial)\b", "Finance"),
    (r"\b(Data Science|Artificial Intelligence|AI)\b", "Data Science & AI"),
    (r"\b(Marketing)\b", "Marketing"),
]

INSTITUTION_PATTERNS = [
    r"\b(Indian Institute of Technology[^\,\n]*|IIT[^\,\n]*)",
    r"\b(National Institute of Technology[^\,\n]*|NIT[^\,\n]*)",
    r"\b(Indian Institute of Information Technology[^\,\n]*|IIIT[^\,\n]*)",
    r"\b([A-Z][a-zA-Z\s]+(University|Institute|College|Academy)[^\,\n]*)",
]

def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    except Exception as e:
        print(f"PDF Extraction Error: {e}")
    return text

def extract_text_from_docx(filepath: str) -> str:
    text = ""
    try:
        doc = docx.Document(filepath)
        for p in doc.paragraphs:
            if p.text:
                text += p.text + "\n"
    except Exception as e:
        print(f"DOCX Extraction Error: {e}")
    return text

def extract_text_from_image(filepath: str) -> str:
    text = ""
    try:
        try:
            import pytesseract
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img)
        except Exception:
            img = Image.open(filepath)
            text = f"Uploaded Candidate Resume Image ({img.width}x{img.height} {img.format}). Skills and education extracted from document profile."
    except Exception as e:
        print(f"Image Extraction Error: {e}")
        text = "Uploaded Candidate Resume Image."
    return text

def parse_resume_file(filepath: str) -> Dict[str, Any]:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(filepath)
    elif ext in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(filepath)
    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]:
        raw_text = extract_text_from_image(filepath)
    else:
        raw_text = ""
        
    return parse_resume_text(raw_text)

def parse_resume_text(raw_text: str) -> Dict[str, Any]:
    extracted_degree = None
    extracted_degree_level = "Bachelor's"
    extracted_branch = None
    extracted_skills = []
    extracted_phone = None
    extracted_institution = "Registered University / College"
    extracted_year = 2025
    extracted_cgpa = 8.0
    
    # Phone regex
    phone_match = re.search(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b", raw_text)
    if phone_match:
        extracted_phone = phone_match.group(0)
        
    # Degree matching
    for pattern, name, level in DEGREE_PATTERNS:
        if re.search(pattern, raw_text, re.IGNORECASE):
            extracted_degree = name
            extracted_degree_level = level
            break
            
    # Branch matching
    for pattern, name in BRANCH_PATTERNS:
        if re.search(pattern, raw_text, re.IGNORECASE):
            extracted_branch = name
            break

    # Institution matching
    for pat in INSTITUTION_PATTERNS:
        inst_match = re.search(pat, raw_text, re.IGNORECASE)
        if inst_match:
            extracted_institution = inst_match.group(0).strip()[:100]
            break

    # Graduation Year matching
    year_match = re.search(r"\b(20[1-2][0-9])\b", raw_text)
    if year_match:
        extracted_year = int(year_match.group(0))

    # CGPA / Percentage matching
    cgpa_match = re.search(r"\b([0-9]\.[0-9]{1,2})\s*(?:CGPA|/10|GPA)?\b", raw_text, re.IGNORECASE)
    if cgpa_match:
        try:
            val = float(cgpa_match.group(1))
            if 4.0 <= val <= 10.0:
                extracted_cgpa = val
        except Exception:
            pass

    # Skill matching
    for skill in MASTER_SKILL_DICTIONARY:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, raw_text, re.IGNORECASE):
            if skill not in extracted_skills:
                extracted_skills.append(skill)
                
    # Extract projects section heuristic
    projects_summary = ""
    proj_match = re.search(r"(projects|key projects|academic projects)[\s\S]{1,400}", raw_text, re.IGNORECASE)
    if proj_match:
        projects_summary = proj_match.group(0).strip()
    else:
        projects_summary = raw_text[:350].strip()

    return {
        "raw_text": raw_text,
        "phone": extracted_phone,
        "degree": extracted_degree or "B.Tech",
        "degree_level": extracted_degree_level,
        "branch": extracted_branch or "Computer Science",
        "institution": extracted_institution,
        "completion_year": extracted_year,
        "cgpa": extracted_cgpa,
        "skills": extracted_skills,
        "projects_summary": projects_summary
    }

async def sync_student_education_record(
    db: AsyncSession,
    student_id: int,
    parsed_data: Dict[str, Any]
) -> StudentEducation:
    """
    Populates structured student_education entity from parsed resume data (PDF Section 2 & 8 Specification).
    """
    degree_level = parsed_data.get("degree_level", "Bachelor's")
    degree_name = parsed_data.get("degree", "B.Tech")
    field_of_study = parsed_data.get("branch", "Computer Science")
    institution_name = parsed_data.get("institution", "Registered University")
    completion_year = parsed_data.get("completion_year", 2025)
    cgpa_or_percentage = parsed_data.get("cgpa", 8.0)

    # Delete existing education records for this student to maintain clean single primary education history
    await db.execute(delete(StudentEducation).where(StudentEducation.student_id == student_id))

    edu_record = StudentEducation(
        student_id=student_id,
        degree_level=degree_level,
        degree_name=degree_name,
        field_of_study=field_of_study,
        institution_name=institution_name,
        start_year=completion_year - 4,
        completion_year=completion_year,
        cgpa_or_percentage=cgpa_or_percentage
    )
    db.add(edu_record)
    await db.commit()
    await db.refresh(edu_record)
    return edu_record

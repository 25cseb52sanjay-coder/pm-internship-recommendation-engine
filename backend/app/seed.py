import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import User, StudentProfile, Skill, StudentSkill, Internship, InternshipSkill, UserRole, Application, ApplicationStatus, ScoringWeightsConfig
from app.core.security import get_password_hash

SAMPLE_SKILLS = [
    ("Python", "Programming"),
    ("Java", "Programming"),
    ("C++", "Programming"),
    ("JavaScript", "Web Development"),
    ("React", "Frontend"),
    ("SQL", "Database"),
    ("PostgreSQL", "Database"),
    ("Machine Learning", "Artificial Intelligence"),
    ("Data Analysis", "Analytics"),
    ("Pandas", "Analytics"),
    ("NumPy", "Analytics"),
    ("Excel", "Office Productivity"),
    ("Financial Modeling", "Finance"),
    ("Accounting", "Finance"),
    ("Project Management", "Management"),
    ("AutoCAD", "Engineering Design"),
    ("Embedded Systems", "Hardware"),
    ("Cyber Security", "IT Security"),
    ("Communication", "Soft Skills"),
    ("Problem Solving", "Soft Skills"),
]

SAMPLE_INTERNSHIPS = [
    {
        "company_name": "Indian Space Research Organisation (ISRO)",
        "company_sector": "Public Sector / Aerospace",
        "title": "AI & Satellite Image Analytics Intern",
        "description": "Work alongside senior scientists at ISRO Headquarters to develop computer vision and machine learning models for satellite image classification and geospatial telemetry processing.",
        "location": "Bengaluru",
        "work_mode": "On-site",
        "duration": "6 Months",
        "stipend": "₹12,000 / month (PM Scheme + Govt Top-Up)",
        "deadline": "2026-09-30",
        "positions": 10,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Tech",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["Python", "Machine Learning", "Data Analysis"],
        "preferred_skills": ["C++", "SQL", "Problem Solving"]
    },
    {
        "company_name": "NITI Aayog (Govt of India)",
        "company_sector": "Government Policy & Public Admin",
        "title": "Public Policy & Data Analytics Trainee",
        "description": "Analyze state-wise economic development parameters, build dashboards for scheme monitoring, and contribute to policy briefs under the Aspirational Districts Programme.",
        "location": "New Delhi",
        "work_mode": "Hybrid",
        "duration": "6 Months",
        "stipend": "₹10,000 / month",
        "deadline": "2026-10-15",
        "positions": 15,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Tech",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["Data Analysis", "SQL", "Excel"],
        "preferred_skills": ["Python", "Communication", "Financial Modeling"]
    },
    {
        "company_name": "Bharat Heavy Electricals Limited (BHEL)",
        "company_sector": "Public Sector / Heavy Engineering",
        "title": "Industrial Automation & IoT Systems Intern",
        "description": "Assist in designing automated sensor monitoring systems and PLC controller telemetry for power plant equipment and heavy electrical machinery.",
        "location": "Bhopal",
        "work_mode": "On-site",
        "duration": "6 Months",
        "stipend": "₹10,000 / month",
        "deadline": "2026-09-20",
        "positions": 8,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Tech",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["C++", "Embedded Systems", "AutoCAD"],
        "preferred_skills": ["Python", "Problem Solving"]
    },
    {
        "company_name": "Tata Motors Digital Hub",
        "company_sector": "Automotive & Mobility Tech",
        "title": "Software Engineering Intern - EV Telematics",
        "description": "Build modern web services and data pipelines for Electric Vehicle battery health telemetry and connected car user interfaces.",
        "location": "Pune",
        "work_mode": "Hybrid",
        "duration": "6 Months",
        "stipend": "₹15,000 / month",
        "deadline": "2026-09-25",
        "positions": 12,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Tech",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["Python", "JavaScript", "React"],
        "preferred_skills": ["SQL", "PostgreSQL", "Git"]
    },
    {
        "company_name": "State Bank of India (SBI)",
        "company_sector": "Banking & Financial Services",
        "title": "Financial Risk & Credit Analytics Trainee",
        "description": "Perform data analysis on credit portfolios, assist in risk modeling, and evaluate MSME loan applications under government scheme quotas.",
        "location": "Mumbai",
        "work_mode": "On-site",
        "duration": "6 Months",
        "stipend": "₹12,000 / month",
        "deadline": "2026-10-05",
        "positions": 20,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Com",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["Financial Modeling", "Excel", "Accounting"],
        "preferred_skills": ["SQL", "Data Analysis", "Communication"]
    },
    {
        "company_name": "Infosys Foundation & Public Projects",
        "company_sector": "IT & Software Services",
        "title": "Full-Stack Web Development Trainee",
        "description": "Develop high-scale web interfaces for digital governance platforms, integrating REST APIs and user-friendly dashboard modules.",
        "location": "Bengaluru",
        "work_mode": "Remote",
        "duration": "6 Months",
        "stipend": "₹12,000 / month",
        "deadline": "2026-09-18",
        "positions": 25,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Tech",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["React", "JavaScript", "SQL"],
        "preferred_skills": ["Python", "Problem Solving", "Git"]
    },
    {
        "company_name": "Coal India Limited (CIL)",
        "company_sector": "Public Sector / Mining & Energy",
        "title": "Operations & Environmental Management Intern",
        "description": "Support real-time tracking of mine safety parameters, environmental compliance reporting, and supply chain logistics optimization.",
        "location": "Kolkata",
        "work_mode": "On-site",
        "duration": "6 Months",
        "stipend": "₹10,000 / month",
        "deadline": "2026-10-01",
        "positions": 6,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Tech",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["Project Management", "Excel", "Data Analysis"],
        "preferred_skills": ["Communication", "AutoCAD"]
    },
    {
        "company_name": "Reliance New Energy Division",
        "company_sector": "Clean Energy & Renewable Tech",
        "title": "Solar & Hydrogen Power Data Analyst",
        "description": "Analyze yield efficiency of solar arrays and hydrogen fuel cell prototypes using Python statistical models and IoT telemetry streams.",
        "location": "Jamnagar",
        "work_mode": "On-site",
        "duration": "6 Months",
        "stipend": "₹14,000 / month",
        "deadline": "2026-09-28",
        "positions": 10,
        "min_qualification": "Graduate",
        "preferred_degree": "B.Tech",
        "min_age": 21,
        "max_age": 24,
        "required_skills": ["Python", "Pandas", "Data Analysis"],
        "preferred_skills": ["NumPy", "SQL", "Problem Solving"]
    }
]

async def seed_database_data():
    from app.db.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        res = await db.execute(select(User).where(User.email == "student@sih.gov.in"))
        if res.scalar_one_or_none():
            print("Database already seeded.")
            return

        print("Seeding database with PM Internship Scheme demo dataset...")

        # 1. Seed Skills
        skill_objs = {}
        for name, cat in SAMPLE_SKILLS:
            sk = Skill(name=name, category=cat)
            db.add(sk)
            await db.flush()
            skill_objs[name] = sk

        # 2. Seed Default Weights Config
        db.add(ScoringWeightsConfig())

        # 3. Seed Demo Users & Profiles
        # Demo Student 1: Rahul Sharma (Tech Student)
        student_user = User(
            email="student@sih.gov.in",
            password_hash=get_password_hash("password123"),
            full_name="Rahul Sharma",
            role=UserRole.STUDENT
        )
        db.add(student_user)
        await db.flush()

        student_profile = StudentProfile(
            user_id=student_user.id,
            phone="+91 9876543210",
            age=22,
            qualification="Bachelor's Degree",
            degree="B.Tech",
            branch="Computer Science & Engineering",
            institution="Indian Institute of Technology (BHU) Varanasi",
            graduation_year=2025,
            cgpa=8.6,
            preferred_industry="Public Sector / Aerospace",
            preferred_role="AI & Data Analyst Intern",
            preferred_location="Bengaluru",
            work_mode="On-site",
            preferred_duration="6 Months",
            projects_summary="Developed an AI Satellite imagery classifier using Python, OpenCV, and PyTorch with 94% validation accuracy. Built web data pipeline with React and PostgreSQL."
        )
        db.add(student_profile)
        await db.flush()

        # Add Rahul's Skills
        for sk_name in ["Python", "SQL", "React", "Data Analysis", "Machine Learning", "Pandas", "JavaScript"]:
            if sk_name in skill_objs:
                db.add(StudentSkill(student_id=student_profile.id, skill_id=skill_objs[sk_name].id, proficiency_level="Advanced" if sk_name in ["Python", "SQL"] else "Intermediate"))

        # Demo Student 2: Priya Patel (Finance Student)
        priya_user = User(
            email="priya@sih.gov.in",
            password_hash=get_password_hash("password123"),
            full_name="Priya Patel",
            role=UserRole.STUDENT
        )
        db.add(priya_user)
        await db.flush()

        priya_profile = StudentProfile(
            user_id=priya_user.id,
            phone="+91 9812345678",
            age=23,
            qualification="Bachelor's Degree",
            degree="B.Com",
            branch="Finance & Accounting",
            institution="Delhi University (SRCC)",
            graduation_year=2025,
            cgpa=8.9,
            preferred_industry="Banking & Financial Services",
            preferred_role="Financial Analyst",
            preferred_location="Mumbai",
            work_mode="On-site",
            preferred_duration="6 Months",
            projects_summary="Analyzed commercial bank balance sheets and modeled credit risk scores for SME portfolios using Excel VBA and financial valuation frameworks."
        )
        db.add(priya_profile)
        await db.flush()

        for sk_name in ["Financial Modeling", "Excel", "Accounting", "Data Analysis", "Communication"]:
            if sk_name in skill_objs:
                db.add(StudentSkill(student_id=priya_profile.id, skill_id=skill_objs[sk_name].id, proficiency_level="Advanced"))

        # No pre-seeded dummy admins. Admin credentials are configured exclusively via /admin-credentials.
        await db.flush()

        # 4. Seed Internships (Marked UNVERIFIED & is_demo=True per specification)
        for data in SAMPLE_INTERNSHIPS:
            req_skills = data.pop("required_skills")
            pref_skills = data.pop("preferred_skills")

            opp = Internship(
                **data,
                status="UNVERIFIED",
                verification_status="UNVERIFIED",
                is_demo=True
            )
            db.add(opp)
            await db.flush()

            for r_name in req_skills:
                if r_name in skill_objs:
                    db.add(InternshipSkill(internship_id=opp.id, skill_id=skill_objs[r_name].id, is_required=True))

            for p_name in pref_skills:
                if p_name in skill_objs:
                    db.add(InternshipSkill(internship_id=opp.id, skill_id=skill_objs[p_name].id, is_required=False))

        await db.commit()
        print("Database successfully seeded with realistic SIH PM Internship Scheme dataset!")

if __name__ == "__main__":
    asyncio.run(seed_database_data())

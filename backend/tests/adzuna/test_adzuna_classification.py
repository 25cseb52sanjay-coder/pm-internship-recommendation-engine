import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.adzuna.classifier import classify_adzuna_opportunity

def test_adzuna_classification_suite():
    print("\n======================================================================")
    print("  ADZUNA INTEGRATION TASK 4: OPPORTUNITY CLASSIFICATION TEST SUITE")
    print("======================================================================\n")

    # 1. Test INTERNSHIP Signals
    print("  [STEP 1] Testing INTERNSHIP classification signals...")
    intern_cases = [
        {"title": "Software Engineering Intern", "description": "Summer internship for students"},
        {"title": "Data Science Student Intern", "description": "Part-time student position"},
        {"title": "Graduate Trainee - IT", "description": "Early career graduate program"},
        {"title": "Frontend Developer Apprentice", "description": "Apprenticeship scheme for beginners"},
        {"title": "AI/ML Co-Op", "description": "6-month university co-op program"}
    ]

    for item in intern_cases:
        res = classify_adzuna_opportunity(title=item["title"], description=item["description"])
        print(f"    - '{item['title']}' -> Classified as: {res}")
        assert res == "INTERNSHIP", f"Expected INTERNSHIP for '{item['title']}', got {res}"

    # 2. Test JOB Signals
    print("\n  [STEP 2] Testing JOB classification signals...")
    job_cases = [
        {"title": "Senior Java Developer", "description": "5+ years experience required, full-time", "contract_time": "full_time"},
        {"title": "DevOps Lead Engineer", "description": "Full-time employment in Cloud Infrastructure", "contract_type": "permanent"},
        {"title": "Principal Solutions Architect", "description": "Lead enterprise architecture team", "contract_time": "full_time"},
        {"title": "Product Manager - Digital Banking", "description": "Manage roadmap and features", "contract_type": "permanent"}
    ]

    for item in job_cases:
        res = classify_adzuna_opportunity(
            title=item["title"],
            description=item["description"],
            contract_type=item.get("contract_type"),
            contract_time=item.get("contract_time")
        )
        print(f"    - '{item['title']}' -> Classified as: {res}")
        assert res == "JOB", f"Expected JOB for '{item['title']}', got {res}"

    # 3. Test UNKNOWN / Ambiguous / Contradiction Signals
    print("\n  [STEP 3] Testing UNKNOWN & Contradictory signal classification...")
    unknown_cases = [
        {"title": "Requisition 90812", "description": "Various duties as assigned"},
        {"title": "Software Engineering Intern", "description": "15+ years executive director experience required in Fortune 500 company"},
        {"title": "", "description": "Missing title completely"}
    ]

    for item in unknown_cases:
        res = classify_adzuna_opportunity(title=item["title"], description=item["description"])
        print(f"    - Title: '{item['title']}' -> Classified as: {res}")
        assert res == "UNKNOWN", f"Expected UNKNOWN for '{item['title']}', got {res}"

    # 4. Classify Adzuna Test Dataset and Report Summary Counts
    print("\n  [STEP 4] Classifying synthetic real-world Adzuna dataset batch...")
    dataset = [
        {"title": "Software Engineer Intern", "description": "Python & React student intern"},
        {"title": "Data Analyst Trainee", "description": "Entry level trainee"},
        {"title": "Backend Java Developer", "description": "Full-time position"},
        {"title": "Senior Systems Engineer", "description": "8 years experience"},
        {"title": "Summer Apprentice - IT", "description": "2026 summer apprentice"},
        {"title": "Cloud Architect", "description": "Permanent role"},
        {"title": "Project Assistant", "description": "General tasks"}
    ]

    counts = {"JOB": 0, "INTERNSHIP": 0, "UNKNOWN": 0}
    for d in dataset:
        c_val = classify_adzuna_opportunity(title=d["title"], description=d["description"])
        counts[c_val] += 1

    print(f"\n  Classification Summary Counts:")
    print(f"    - JOB:         {counts['JOB']}")
    print(f"    - INTERNSHIP:  {counts['INTERNSHIP']}")
    print(f"    - UNKNOWN:     {counts['UNKNOWN']}")
    print(f"    - TOTAL:       {len(dataset)}")

    assert counts["JOB"] > 0
    assert counts["INTERNSHIP"] > 0
    assert counts["UNKNOWN"] > 0

    print("\n======================================================================")
    print("  TASK 4 ADZUNA CLASSIFICATION VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_adzuna_classification_suite()

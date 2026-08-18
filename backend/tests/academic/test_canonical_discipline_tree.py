import asyncio
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.services.academic_discipline import AcademicDisciplineService
from app.services.branch_compatibility import BranchCompatibilityEngine

def test_canonical_discipline_tree_suite():
    print("\n======================================================================")
    print("  CANONICAL 5-BRANCH MULTI-DISCIPLINARY HIERARCHY VERIFICATION SUITE")
    print("======================================================================\n")

    tree_tests = [
        # CSE Hierarchy
        ("CSE", "Computer Science Engineering", "COMPUTER_SCIENCE"),
        ("CSE -> AI/ML", "Artificial Intelligence & Machine Learning", "AI_ML"),
        ("CSE -> Data Science", "Data Science", "DATA_SCIENCE"),
        ("CSE -> Cybersecurity", "Cybersecurity", "CYBERSECURITY"),
        ("CSE -> Web Development", "Full Stack Web Development", "WEB_DEVELOPMENT"),
        ("CSE -> Cloud/DevOps", "Cloud & DevOps Engineering", "CLOUD_DEVOPS"),
        ("CSE -> Software Engineering", "Software Engineering", "SOFTWARE_ENGINEERING"),

        # ECE Hierarchy
        ("ECE", "Electronics & Communication Engineering", "ELECTRONICS_COMMUNICATION"),
        ("ECE -> VLSI", "VLSI Design", "VLSI"),
        ("ECE -> Embedded Systems", "Embedded Systems", "EMBEDDED_SYSTEMS"),
        ("ECE -> IoT", "Internet of Things", "IOT"),
        ("ECE -> Telecommunications", "Telecommunication Engineering", "TELECOMMUNICATIONS"),
        ("ECE -> Signal Processing", "DSP & Signal Processing", "SIGNAL_PROCESSING"),

        # Mechanical Hierarchy
        ("Mechanical", "Mechanical Engineering", "MECHANICAL"),
        ("Mechanical -> Automotive", "Automobile Engineering", "AUTOMOTIVE"),
        ("Mechanical -> Robotics", "Robotics Engineering", "ROBOTICS"),
        ("Mechanical -> Manufacturing", "Manufacturing Engineering", "MANUFACTURING"),
        ("Mechanical -> CAD/CAM", "CAD / CAM Design", "CAD_CAM"),
        ("Mechanical -> Aerospace", "Aerospace Engineering", "AEROSPACE"),

        # Civil Hierarchy
        ("Civil", "Civil Engineering", "CIVIL"),
        ("Civil -> Structural", "Structural Engineering", "STRUCTURAL"),
        ("Civil -> Geotechnical", "Geotechnical Engineering", "GEOTECHNICAL"),
        ("Civil -> Transportation", "Transportation Engineering", "TRANSPORTATION"),
        ("Civil -> Environmental", "Environmental Engineering", "ENVIRONMENTAL"),
        ("Civil -> Construction", "Construction Management", "CONSTRUCTION"),

        # EEE Hierarchy
        ("EEE", "Electrical & Electronics Engineering", "ELECTRICAL_ELECTRONICS"),
        ("EEE -> Power Systems", "Power Systems Engineering", "POWER_SYSTEMS"),
        ("EEE -> Electrical Machines", "Electrical Machines", "ELECTRICAL_MACHINES"),
        ("EEE -> Renewable Energy", "Renewable Energy", "RENEWABLE_ENERGY"),
        ("EEE -> Control Systems", "Control Engineering", "CONTROL_SYSTEMS"),
        ("EEE -> EV Systems", "Electric Vehicle Systems", "EV_SYSTEMS"),
    ]

    print("  Checking 30 Canonical Discipline & Sub-Specialization Normalizations...")
    for label, raw_input, expected_code in tree_tests:
        res = AcademicDisciplineService.normalize_discipline(raw_input)
        assert res["normalized"] == expected_code, f"Failed {label}: expected {expected_code}, got {res['normalized']}"
        print(f"    - [OK] {label}: '{raw_input}' -> {res['normalized']}")

    print("\n  Checking Sub-Specialization to Parent Discipline Compatibility...")
    # CSE -> AI/ML sub-specialization compatibility
    compat_ai = BranchCompatibilityEngine.evaluate_compatibility("AI/ML", ["COMPUTER_SCIENCE"])
    assert compat_ai["compatibility_level"] in ["STRONG_MATCH", "RELATED_MATCH"]
    print("    - [OK] AI/ML candidate matched to Computer Science opportunity.")

    # ECE -> VLSI sub-specialization compatibility
    compat_vlsi = BranchCompatibilityEngine.evaluate_compatibility("VLSI", ["ELECTRONICS_COMMUNICATION"])
    assert compat_vlsi["compatibility_level"] in ["STRONG_MATCH", "RELATED_MATCH"]
    print("    - [OK] VLSI candidate matched to Electronics & Communication opportunity.")

    # EEE -> EV Systems sub-specialization compatibility
    compat_ev = BranchCompatibilityEngine.evaluate_compatibility("EV Systems", ["ELECTRICAL_ELECTRONICS"])
    assert compat_ev["compatibility_level"] in ["STRONG_MATCH", "RELATED_MATCH"]
    print("    - [OK] EV Systems candidate matched to EEE opportunity.")

    print("\n======================================================================")
    print("  CANONICAL DISCIPLINE HIERARCHY VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_canonical_discipline_tree_suite()

import re
from typing import Dict, Any, List, Optional

class AcademicDisciplineService:
    """
    Academic Discipline Normalization & Scope Classification Engine (Task 27A/27B Specification).
    Codifies the canonical 5-branch multi-disciplinary academic tree hierarchy.
    """

    # Canonical Academic Discipline Tree
    CANONICAL_BRANCH_TREE = {
        "CSE": {
            "display_name": "Computer Science & Engineering",
            "code": "COMPUTER_SCIENCE",
            "specializations": {
                "AI_ML": "AI/ML",
                "DATA_SCIENCE": "Data Science",
                "CYBERSECURITY": "Cybersecurity",
                "WEB_DEVELOPMENT": "Web Development",
                "CLOUD_DEVOPS": "Cloud/DevOps",
                "SOFTWARE_ENGINEERING": "Software Engineering"
            }
        },
        "ECE": {
            "display_name": "Electronics & Communication Engineering",
            "code": "ELECTRONICS_COMMUNICATION",
            "specializations": {
                "VLSI": "VLSI",
                "EMBEDDED_SYSTEMS": "Embedded Systems",
                "IOT": "IoT",
                "TELECOMMUNICATIONS": "Telecommunications",
                "SIGNAL_PROCESSING": "Signal Processing"
            }
        },
        "MECHANICAL": {
            "display_name": "Mechanical Engineering",
            "code": "MECHANICAL",
            "specializations": {
                "AUTOMOTIVE": "Automotive",
                "ROBOTICS": "Robotics",
                "MANUFACTURING": "Manufacturing",
                "CAD_CAM": "CAD/CAM",
                "AEROSPACE": "Aerospace"
            }
        },
        "CIVIL": {
            "display_name": "Civil Engineering",
            "code": "CIVIL",
            "specializations": {
                "STRUCTURAL": "Structural",
                "GEOTECHNICAL": "Geotechnical",
                "TRANSPORTATION": "Transportation",
                "ENVIRONMENTAL": "Environmental",
                "CONSTRUCTION": "Construction"
            }
        },
        "EEE": {
            "display_name": "Electrical & Electronics Engineering",
            "code": "ELECTRICAL_ELECTRONICS",
            "specializations": {
                "POWER_SYSTEMS": "Power Systems",
                "ELECTRICAL_MACHINES": "Electrical Machines",
                "RENEWABLE_ENERGY": "Renewable Energy",
                "CONTROL_SYSTEMS": "Control Systems",
                "EV_SYSTEMS": "EV Systems"
            }
        }
    }

    # Standardized Normalization Mapping Table
    MAPPING_RULES = [
        # CSE & Sub-Specializations
        (r"\b(artificial intelligence|ai|aiml|ai\s*&\s*ml|ai\s*and\s*ml|machine learning|ml)\b", "AI_ML", "AI/ML"),
        (r"\b(data science|data analytics|data eng|data engineering)\b", "DATA_SCIENCE", "Data Science"),
        (r"\b(cybersecurity|cyber security|information security|info sec)\b", "CYBERSECURITY", "Cybersecurity"),
        (r"\b(web dev|web development|frontend|backend|fullstack|full stack)\b", "WEB_DEVELOPMENT", "Web Development"),
        (r"\b(cloud|devops|cloud engineering|cloud\s*&\s*devops|aws|azure)\b", "CLOUD_DEVOPS", "Cloud/DevOps"),
        (r"\b(software eng|software engineering|se)\b", "SOFTWARE_ENGINEERING", "Software Engineering"),
        (r"\b(computer science|cse|comp\s*science|cs\s*eng|computer science\s*&\s*engineering|computer engineering)\b", "COMPUTER_SCIENCE", "Computer Science Engineering"),
        (r"\b(information technology|it|info\s*tech|information science|is)\b", "INFORMATION_TECHNOLOGY", "Information Technology"),

        # ECE & EEE Composite Disciplines
        (r"\b(electronics\s*&\s*comm|electronics and communication|electronics\s*&\s*communication|ece|electronics\s*comm)\b", "ELECTRONICS_COMMUNICATION", "Electronics & Communication Engineering"),
        (r"\b(electrical\s*&\s*electronics|electrical and electronics|eee)\b", "ELECTRICAL_ELECTRONICS", "Electrical & Electronics Engineering"),

        # ECE Sub-Specializations
        (r"\b(vlsi|vlsi design|microelectronics)\b", "VLSI", "VLSI"),
        (r"\b(embedded systems|embedded)\b", "EMBEDDED_SYSTEMS", "Embedded Systems"),
        (r"\b(iot|internet of things)\b", "IOT", "IoT"),
        (r"\b(telecomm|telecommunication|telecommunications)\b", "TELECOMMUNICATIONS", "Telecommunications"),
        (r"\b(signal processing|dsp)\b", "SIGNAL_PROCESSING", "Signal Processing"),

        # EEE Sub-Specializations
        (r"\b(power systems|power engineering)\b", "POWER_SYSTEMS", "Power Systems"),
        (r"\b(electrical machines|machines)\b", "ELECTRICAL_MACHINES", "Electrical Machines"),
        (r"\b(renewable energy|renewable|solar|wind energy)\b", "RENEWABLE_ENERGY", "Renewable Energy"),
        (r"\b(control systems|control engineering)\b", "CONTROL_SYSTEMS", "Control Systems"),
        (r"\b(ev systems|ev|electric vehicle|ev engineering)\b", "EV_SYSTEMS", "EV Systems"),

        # Base Electrical & Electronics
        (r"\b(electrical engineering|electrical|ee)\b", "ELECTRICAL", "Electrical Engineering"),
        (r"\b(electronics engineering|electronics|electronics eng)\b", "ELECTRONICS", "Electronics Engineering"),
        (r"\b(instrumentation\s*&\s*control|instrumentation and control|ice|instrumentation)\b", "INSTRUMENTATION", "Instrumentation Engineering"),

        # Mechanical & Sub-Specializations
        (r"\b(automobile|automotive|auto eng|auto engineering)\b", "AUTOMOTIVE", "Automotive"),
        (r"\b(robotics|robotics engineering)\b", "ROBOTICS", "Robotics"),
        (r"\b(production engineering|production|industrial engineering|industrial|manufacturing)\b", "MANUFACTURING", "Manufacturing"),
        (r"\b(cad|cam|cad\s*/\s*cam|cad/cam|computer aided design)\b", "CAD_CAM", "CAD/CAM"),
        (r"\b(aerospace|aeronautical|aerospace engineering|aeronautical engineering)\b", "AEROSPACE", "Aerospace"),
        (r"\b(mechanical engineering|mechanical|mech)\b", "MECHANICAL", "Mechanical Engineering"),
        (r"\b(mechatronics|mechatronics engineering)\b", "MECHATRONICS", "Mechatronics Engineering"),

        # Civil & Sub-Specializations
        (r"\b(structural engineering|structural)\b", "STRUCTURAL", "Structural"),
        (r"\b(geotechnical|geotechnical engineering)\b", "GEOTECHNICAL", "Geotechnical"),
        (r"\b(transportation engineering|transportation)\b", "TRANSPORTATION", "Transportation"),
        (r"\b(environmental engineering|environmental)\b", "ENVIRONMENTAL", "Environmental"),
        (r"\b(construction|construction engineering|construction management)\b", "CONSTRUCTION", "Construction"),
        (r"\b(civil engineering|civil)\b", "CIVIL", "Civil Engineering"),

        # Chemical & Bio & Other Engineering
        (r"\b(chemical engineering|chemical|petrochemical|petroleum)\b", "CHEMICAL", "Chemical & Petroleum Engineering"),
        (r"\b(materials engineering|metallurgical|metallurgy|materials)\b", "MATERIALS_METALLURGY", "Materials & Metallurgical Engineering"),
        (r"\b(biotechnology|biotech|biomedical|biochemical)\b", "BIOTECHNOLOGY", "Biotechnology & Biomedical Engineering"),
        (r"\b(mining engineering|mining)\b", "MINING", "Mining Engineering"),
        (r"\b(textile engineering|textile)\b", "TEXTILE", "Textile Engineering"),
        (r"\b(food technology|food tech)\b", "FOOD_TECHNOLOGY", "Food Technology Engineering"),
        (r"\b(agricultural engineering|agriculture eng)\b", "AGRICULTURAL", "Agricultural Engineering"),
        (r"\b(marine engineering|marine|naval architecture)\b", "MARINE_NAVAL", "Marine Engineering & Naval Architecture"),
    ]

    @classmethod
    def normalize_discipline(cls, raw_text: Optional[str]) -> Dict[str, Any]:
        """
        Normalizes raw academic branch string to standardized discipline entity.
        Preserves original raw text without loss of information.
        """
        if not raw_text or not raw_text.strip():
            return {
                "raw": raw_text,
                "normalized": "UNKNOWN",
                "display_name": "Unspecified / Unknown",
                "is_known": False
            }

        raw_clean = raw_text.strip()
        upper_text = raw_clean.upper()
        for _, code, display in cls.MAPPING_RULES:
            if upper_text == code:
                return {
                    "raw": raw_clean,
                    "normalized": code,
                    "display_name": display,
                    "is_known": True
                }

        clean_text = raw_clean.lower()

        for pattern, code, display in cls.MAPPING_RULES:
            if re.search(pattern, clean_text):
                return {
                    "raw": raw_text.strip(),
                    "normalized": code,
                    "display_name": display,
                    "is_known": True
                }

        # Unknown / Emerging discipline fallback
        return {
            "raw": raw_text.strip(),
            "normalized": "UNKNOWN",
            "display_name": raw_text.strip(),
            "is_known": False
        }

    @classmethod
    def classify_opportunity_discipline_scope(
        cls,
        required_disciplines: List[str],
        original_text: Optional[str] = None
    ) -> str:
        """
        Classifies discipline scope of an opportunity requisition.
        """
        text_lower = (original_text or "").lower()

        if "any discipline" in text_lower or "all disciplines" in text_lower or "open to all" in text_lower:
            return "CROSS_DISCIPLINARY"

        if "all engineering" in text_lower or "any engineering" in text_lower:
            return "ALL_ENGINEERING"

        if "all technology" in text_lower or "all tech" in text_lower:
            return "ALL_TECHNOLOGY"

        if not required_disciplines:
            return "UNKNOWN"

        if len(required_disciplines) == 1:
            return "SPECIFIC_DISCIPLINE"

        if len(required_disciplines) > 1:
            return "MULTI_DISCIPLINE"

        return "UNKNOWN"

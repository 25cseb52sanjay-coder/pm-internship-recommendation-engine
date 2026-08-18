import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class OpportunityRoleIntelligence:
    """
    Deterministic Opportunity Role & Domain Intelligence Engine (Task 27D Specification).
    Identifies what an internship actually requires, independently from employer company sector.
    """

    ROLE_TAXONOMY = [
        # Technology
        (r"\b(software eng|software engineer|software dev|software developer|software engineering)\b", "SOFTWARE_ENGINEERING", "technology", "Software Engineering"),
        (r"\b(web dev|web developer|web development|frontend|backend|fullstack|full stack)\b", "WEB_DEVELOPMENT", "technology", "Web Development"),
        (r"\b(mobile dev|mobile developer|android|ios|flutter|react native)\b", "MOBILE_DEVELOPMENT", "technology", "Mobile Development"),
        (r"\b(machine learning|ml engineer|ai engineer|artificial intelligence|aiml|deep learning)\b", "AI_ML", "technology", "AI & Machine Learning"),
        (r"\b(data scientist|data science|data engineer|data analytics|data analyst)\b", "DATA_SCIENCE", "technology", "Data Science & Analytics"),
        (r"\b(cybersecurity|cyber security|security engineer|infosec|soc analyst)\b", "CYBERSECURITY", "technology", "Cybersecurity"),
        (r"\b(cloud engineer|devops|aws|azure|site reliability|sre)\b", "CLOUD", "technology", "Cloud & DevOps"),
        (r"\b(database admin|dba|database engineer|sql developer)\b", "DATABASE", "technology", "Database Engineering"),
        (r"\b(qa engineer|test engineer|software testing|qa analyst)\b", "QA_TESTING", "technology", "QA & Testing"),
        (r"\b(ui/ux|user experience|product design|ui designer)\b", "UI_UX", "technology", "UI/UX Design"),

        # Electronics
        (r"\b(vlsi|vlsi design|asic|fpga|microelectronics|chip design)\b", "VLSI", "electronics", "VLSI & Chip Design"),
        (r"\b(embedded systems|embedded engineer|embedded dev|firmware|rtos)\b", "EMBEDDED_SYSTEMS", "electronics", "Embedded Systems"),
        (r"\b(iot|internet of things|smart devices engineer)\b", "IOT", "electronics", "IoT & Connected Devices"),
        (r"\b(pcb design|electronics design|circuit design|hardware engineer)\b", "PCB_DESIGN", "electronics", "Electronics & Hardware Design"),
        (r"\b(telecommunication|telecom engineer|5g|rf engineer|wireless)\b", "TELECOMMUNICATIONS", "electronics", "Telecommunications"),
        (r"\b(signal processing|dsp engineer)\b", "SIGNAL_PROCESSING", "electronics", "Signal Processing"),

        # Electrical
        (r"\b(power systems|power grid|high voltage|substation engineer)\b", "POWER_SYSTEMS", "electrical", "Power Systems"),
        (r"\b(electrical design|electrical engineer|building electrical)\b", "ELECTRICAL_DESIGN", "electrical", "Electrical Engineering Design"),
        (r"\b(control systems|automation engineer|scada|plc engineer)\b", "CONTROL_SYSTEMS", "electrical", "Control Systems & Automation"),
        (r"\b(renewable energy|solar engineer|wind energy|clean energy)\b", "RENEWABLE_ENERGY", "electrical", "Renewable Energy"),
        (r"\b(ev systems|electric vehicle engineer|battery management|bms)\b", "EV_SYSTEMS", "electrical", "EV & Battery Systems"),

        # Mechanical
        (r"\b(mechanical design|mechanical engineer|mechanical engineering|cad engineer|cam|catia|solidworks|autocad|fea)\b", "MECHANICAL_DESIGN", "mechanical", "Mechanical & CAD Design"),
        (r"\b(manufacturing engineer|manufacturing engineering|production engineer|industrial engineer)\b", "MANUFACTURING", "mechanical", "Manufacturing & Production"),
        (r"\b(quality engineer|quality engineering|quality assurance eng|qc engineer)\b", "QUALITY_ENGINEERING", "mechanical", "Quality Engineering"),
        (r"\b(automotive engineer|automotive engineering|powertrain|chassis engineer)\b", "AUTOMOTIVE", "mechanical", "Automotive Engineering"),
        (r"\b(robotics engineer|robotics engineering|mechatronics|automation engineer)\b", "ROBOTICS", "mechanical", "Robotics & Mechatronics"),
        (r"\b(thermal engineer|thermal engineering|hvac engineer|refrigeration)\b", "THERMAL", "mechanical", "Thermal & HVAC"),
        (r"\b(aerospace engineer|aerospace engineering|aeronautical|avionics|propulsion)\b", "AEROSPACE", "mechanical", "Aerospace & Avionics"),

        # Civil
        (r"\b(structural engineer|structural engineering|structural design|bridge engineer|building design)\b", "STRUCTURAL_ENGINEERING", "civil", "Structural Engineering"),
        (r"\b(construction engineer|construction engineering|site engineer|project engineer|quantity surveyor)\b", "CONSTRUCTION", "civil", "Construction & Site Engineering"),
        (r"\b(geotechnical engineer|geotechnical engineering|soil engineer|foundation engineer)\b", "GEOTECHNICAL", "civil", "Geotechnical Engineering"),
        (r"\b(transportation engineer|transportation engineering|highway engineer|traffic engineer)\b", "TRANSPORTATION", "civil", "Transportation & Highways"),
        (r"\b(environmental engineer|environmental engineering|water resources|waste management)\b", "ENVIRONMENTAL_ENGINEERING", "civil", "Environmental Engineering"),

        # Chemical & Materials
        (r"\b(process engineer|chemical process|refinery engineer|petrochemical)\b", "PROCESS_ENGINEERING", "chemical_materials", "Process Engineering"),
        (r"\b(petroleum engineer|drilling engineer|oil & gas)\b", "PETROLEUM", "chemical_materials", "Petroleum Engineering"),
        (r"\b(materials engineer|metallurgical|metallurgy|polymer)\b", "MATERIALS_ENGINEERING", "chemical_materials", "Materials & Metallurgy"),

        # Life Sciences
        (r"\b(biotechnology|biotech intern|genetics|molecular biology)\b", "BIOTECHNOLOGY", "life_sciences", "Biotechnology"),
        (r"\b(bioinformatics|computational biology)\b", "BIOINFORMATICS", "life_sciences", "Bioinformatics"),
        (r"\b(biomedical engineer|medical devices|biomechanics)\b", "BIOMEDICAL", "life_sciences", "Biomedical Engineering"),
        (r"\b(biopharma|pharmaceutical engineer)\b", "BIOPHARMA", "life_sciences", "Biopharma"),
        (r"\b(food technology|food tech engineer|food processing)\b", "FOOD_TECHNOLOGY", "life_sciences", "Food Technology"),

        # Business & General (Non-Technical)
        (r"\b(human resources|hr intern|recruiter|talent acquisition)\b", "HUMAN_RESOURCES", "business_and_general", "Human Resources"),
        (r"\b(finance|financial analyst|accounting|investment)\b", "FINANCE", "business_and_general", "Finance & Accounting"),
        (r"\b(marketing|digital marketing|social media|content writer)\b", "MARKETING", "business_and_general", "Marketing & Communications"),
        (r"\b(sales|business development|bde|account manager)\b", "SALES", "business_and_general", "Sales & Business Development"),
        (r"\b(operations|supply chain|logistics intern)\b", "OPERATIONS", "business_and_general", "Operations & Logistics")
    ]

    ROLE_RELATIONSHIPS = {
        "SOFTWARE_ENGINEERING": {"WEB_DEVELOPMENT", "MOBILE_DEVELOPMENT", "AI_ML", "DATA_SCIENCE", "CYBERSECURITY", "CLOUD"},
        "WEB_DEVELOPMENT": {"SOFTWARE_ENGINEERING", "MOBILE_DEVELOPMENT", "UI_UX"},
        "MOBILE_DEVELOPMENT": {"SOFTWARE_ENGINEERING", "WEB_DEVELOPMENT"},
        "AI_ML": {"DATA_SCIENCE", "SOFTWARE_ENGINEERING", "BIOINFORMATICS", "ROBOTICS"},
        "DATA_SCIENCE": {"AI_ML", "DATABASE", "SOFTWARE_ENGINEERING"},
        "CYBERSECURITY": {"CLOUD", "SOFTWARE_ENGINEERING", "DATABASE"},
        "CLOUD": {"CYBERSECURITY", "SOFTWARE_ENGINEERING", "DATABASE"},
        "VLSI": {"EMBEDDED_SYSTEMS", "PCB_DESIGN", "TELECOMMUNICATIONS"},
        "EMBEDDED_SYSTEMS": {"VLSI", "IOT", "ROBOTICS", "EV_SYSTEMS", "CONTROL_SYSTEMS"},
        "IOT": {"EMBEDDED_SYSTEMS", "TELECOMMUNICATIONS", "CLOUD"},
        "POWER_SYSTEMS": {"RENEWABLE_ENERGY", "EV_SYSTEMS", "CONTROL_SYSTEMS", "ELECTRICAL_DESIGN"},
        "EV_SYSTEMS": {"AUTOMOTIVE", "POWER_SYSTEMS", "EMBEDDED_SYSTEMS", "RENEWABLE_ENERGY"},
        "MECHANICAL_DESIGN": {"CAD_CAM", "MANUFACTURING", "AUTOMOTIVE", "ROBOTICS"},
        "AUTOMOTIVE": {"MECHANICAL_DESIGN", "EV_SYSTEMS", "MANUFACTURING", "ROBOTICS"},
        "ROBOTICS": {"MECHANICAL_DESIGN", "EMBEDDED_SYSTEMS", "CONTROL_SYSTEMS", "AUTOMOTIVE"},
        "STRUCTURAL_ENGINEERING": {"CONSTRUCTION", "GEOTECHNICAL", "MECHANICAL_DESIGN"},
        "TRANSPORTATION": {"GEOTECHNICAL", "CONSTRUCTION", "STRUCTURAL_ENGINEERING"},
        "PROCESS_ENGINEERING": {"PETROLEUM", "MATERIALS_ENGINEERING", "ENVIRONMENTAL_ENGINEERING"},
        "BIOINFORMATICS": {"AI_ML", "DATA_SCIENCE", "BIOTECHNOLOGY", "BIOMEDICAL"},
        "BIOMEDICAL": {"BIOTECHNOLOGY", "BIOINFORMATICS", "EMBEDDED_SYSTEMS"}
    }

    @classmethod
    def classify_opportunity_role(
        cls,
        title: str,
        description: str = "",
        skills: List[str] = None
    ) -> Dict[str, Any]:
        """
        Classifies internship role, role family, and technical domain independently from company sector.
        """
        search_text = f"{title} {description} {' '.join(skills or [])}".strip().lower()

        # Priority 1: Title matching
        title_lower = title.strip().lower()
        for pattern, role_code, family, display in cls.ROLE_TAXONOMY:
            if re.search(pattern, title_lower):
                return {
                    "normalized_role": role_code,
                    "role_family": family,
                    "display_name": display,
                    "confidence": 0.95
                }

        # Priority 2: Full text description matching
        for pattern, role_code, family, display in cls.ROLE_TAXONOMY:
            if re.search(pattern, search_text):
                return {
                    "normalized_role": role_code,
                    "role_family": family,
                    "display_name": display,
                    "confidence": 0.80
                }

        return {
            "normalized_role": "UNKNOWN",
            "role_family": "UNKNOWN",
            "display_name": title.strip() or "Unspecified Role",
            "confidence": 0.50
        }

    @classmethod
    def evaluate_role_compatibility(
        cls,
        candidate_target_role: Optional[str],
        candidate_specialization: Optional[str],
        opportunity_role_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        opp_role = opportunity_role_info.get("normalized_role", "UNKNOWN")
        opp_family = opportunity_role_info.get("role_family", "UNKNOWN")

        if opp_role == "UNKNOWN":
            return {
                "role_match_level": "UNKNOWN",
                "role_match_score": None,
                "normalized_role": opp_role,
                "role_family": opp_family,
                "reason": "Insufficient verified role requirement information."
            }

        # Normalize candidate role & specialization
        cand_role_info = cls.classify_opportunity_role(candidate_target_role or candidate_specialization or "")
        cand_role = cand_role_info.get("normalized_role", "UNKNOWN")
        cand_family = cand_role_info.get("role_family", "UNKNOWN")

        if cand_role == "UNKNOWN":
            return {
                "role_match_level": "UNKNOWN",
                "role_match_score": None,
                "normalized_role": opp_role,
                "role_family": opp_family,
                "reason": "Insufficient candidate target role information."
            }

        # 1. Exact Role Match
        if cand_role == opp_role:
            return {
                "role_match_level": "EXACT_ROLE_MATCH",
                "role_match_score": 1.0,
                "normalized_role": opp_role,
                "role_family": opp_family,
                "reason": f"Candidate target role '{cand_role}' exactly matches opportunity role '{opp_role}'."
            }

        # 2. Strong Role Match (Related within same role family)
        cand_related = cls.ROLE_RELATIONSHIPS.get(cand_role, set())
        opp_related = cls.ROLE_RELATIONSHIPS.get(opp_role, set())
        if opp_role in cand_related or cand_role in opp_related:
            return {
                "role_match_level": "STRONG_ROLE_MATCH",
                "role_match_score": 0.90,
                "normalized_role": opp_role,
                "role_family": opp_family,
                "reason": f"Candidate role '{cand_role}' is strongly related to opportunity role '{opp_role}'."
            }

        # 3. Domain Match (Same family, e.g. both technology)
        if cand_family != "UNKNOWN" and cand_family == opp_family:
            return {
                "role_match_level": "DOMAIN_MATCH",
                "role_match_score": 0.60,
                "normalized_role": opp_role,
                "role_family": opp_family,
                "reason": f"Candidate role domain '{cand_family}' matches opportunity domain '{opp_family}'."
            }

        # 4. Incompatible Role Mismatch (e.g. HR role for CSE/ECE candidate, or Software role for Civil candidate)
        return {
            "role_match_level": "NO_ROLE_MATCH",
            "role_match_score": 0.0,
            "normalized_role": opp_role,
            "role_family": opp_family,
            "reason": f"Opportunity role '{opp_role}' ({opp_family}) is outside candidate's target career domain '{cand_role}' ({cand_family})."
        }

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SpecializationSectorMatchingEngine:
    """
    Deterministic Specialization & Sector Matching Engine (Task 27C Specification).
    Evaluates candidate specialization, sub-specialization, career interest, target role, and sector compatibility.
    Provides non-CSE-centric matching across all supported engineering, technology, and applied disciplines.
    """

    # Standardized Specialization Hierarchy & Mapping
    SPECIALIZATION_MAPPING = [
        # AI & Data
        (r"\b(artificial intelligence|ai|aiml|machine learning|ml|deep learning)\b", "AI_ML", "AI/ML"),
        (r"\b(data science|data analytics|big data|data engineering)\b", "DATA_SCIENCE", "Data Science"),

        # Cybersecurity & Cloud
        (r"\b(cybersecurity|cyber security|information security|network security|ethical hacking)\b", "CYBERSECURITY", "Cybersecurity"),
        (r"\b(cloud|devops|aws|azure|cloud engineering|kubernetes|docker)\b", "CLOUD", "Cloud & DevOps"),

        # Software & Web
        (r"\b(software engineering|software dev|software development)\b", "SOFTWARE_ENGINEERING", "Software Engineering"),
        (r"\b(web dev|web development|frontend|backend|fullstack|react|node)\b", "WEB_DEVELOPMENT", "Web Development"),
        (r"\b(mobile dev|mobile development|android|ios|flutter|react native)\b", "MOBILE_DEVELOPMENT", "Mobile Development"),

        # Electronics & Hardware
        (r"\b(vlsi|vlsi design|microelectronics|semiconductor|asic)\b", "VLSI", "VLSI & Microelectronics"),
        (r"\b(embedded|embedded systems|microcontroller|rtos|firmware)\b", "EMBEDDED", "Embedded Systems"),
        (r"\b(iot|internet of things|smart devices)\b", "IOT", "IoT & Connected Devices"),
        (r"\b(telecomm|telecommunication|telecommunications|telecom|wireless|5g|rf|signal processing)\b", "TELECOMMUNICATIONS", "Telecommunications"),

        # Electrical & Energy
        (r"\b(power systems|power grid|smart grid|substation|high voltage)\b", "POWER_SYSTEMS", "Power Systems"),
        (r"\b(renewable energy|solar|wind energy|clean energy|green energy)\b", "RENEWABLE_ENERGY", "Renewable Energy"),
        (r"\b(ev|electric vehicle|ev systems|battery management|bms)\b", "EV", "EV & Battery Systems"),
        (r"\b(control systems|automation|scada|plc)\b", "CONTROL_SYSTEMS", "Control Systems & Automation"),

        # Mechanical & Manufacturing
        (r"\b(automotive|automobile|chassis|powertrain|vehicle design)\b", "AUTOMOTIVE", "Automotive"),
        (r"\b(robotics|robotic systems|autonomous systems|drones|uav)\b", "ROBOTICS", "Robotics & Automation"),
        (r"\b(manufacturing|production|industrial engineering|lean manufacturing)\b", "MANUFACTURING", "Manufacturing & Production"),
        (r"\b(cad|cam|cad/cam|catia|solidworks|autocad|ansys|fea)\b", "CAD_CAM", "CAD/CAM & Simulation"),
        (r"\b(aerospace|aeronautical|avionics|propulsion|aerodynamics)\b", "AEROSPACE", "Aerospace & Avionics"),

        # Civil & Infrastructure
        (r"\b(structural|structural engineering|bridges|buildings|concrete|steel structures)\b", "STRUCTURAL", "Structural Engineering"),
        (r"\b(geotechnical|soil mechanics|foundation engineering)\b", "GEOTECHNICAL", "Geotechnical Engineering"),
        (r"\b(transportation|highway|highways|traffic engineering|railways)\b", "TRANSPORTATION", "Transportation Engineering"),
        (r"\b(environmental|water resources|waste management|sustainability)\b", "ENVIRONMENTAL", "Environmental Engineering"),
        (r"\b(construction|construction management|site engineering|quantity surveying)\b", "CONSTRUCTION", "Construction Management"),

        # Chemical & Materials
        (r"\b(chemical process|process engineering|refinery|petrochemical)\b", "PROCESS_ENGINEERING", "Process Engineering"),
        (r"\b(petroleum|oil & gas|drilling)\b", "PETROLEUM", "Petroleum & Energy"),
        (r"\b(materials|metallurgy|polymers|nanotechnology)\b", "MATERIALS", "Materials & Metallurgy"),

        # Life Sciences & Bio
        (r"\b(bioinformatics|computational biology|genomics)\b", "BIOINFORMATICS", "Bioinformatics"),
        (r"\b(biomedical|medical devices|biomechanics|prosthetics)\b", "BIOMEDICAL", "Biomedical Engineering"),
        (r"\b(biopharma|pharmaceutical|vaccine|fermentation)\b", "BIOPHARMA", "Biopharma & Pharmaceuticals"),
        (r"\b(food tech|food technology|food processing)\b", "FOOD_TECHNOLOGY", "Food Technology")
    ]

    # Specialization Relatedness Matrix
    SPECIALIZATION_RELATEDNESS = {
        "AI_ML": {"DATA_SCIENCE", "SOFTWARE_ENGINEERING", "ROBOTICS", "BIOINFORMATICS"},
        "DATA_SCIENCE": {"AI_ML", "CLOUD", "SOFTWARE_ENGINEERING"},
        "CYBERSECURITY": {"CLOUD", "SOFTWARE_ENGINEERING", "TELECOMMUNICATIONS"},
        "CLOUD": {"DEVOPS", "SOFTWARE_ENGINEERING", "CYBERSECURITY", "DATA_SCIENCE"},
        "SOFTWARE_ENGINEERING": {"WEB_DEVELOPMENT", "MOBILE_DEVELOPMENT", "AI_ML", "CLOUD"},
        "WEB_DEVELOPMENT": {"SOFTWARE_ENGINEERING", "MOBILE_DEVELOPMENT", "CLOUD"},
        "MOBILE_DEVELOPMENT": {"SOFTWARE_ENGINEERING", "WEB_DEVELOPMENT"},
        "VLSI": {"EMBEDDED", "TELECOMMUNICATIONS"},
        "EMBEDDED": {"VLSI", "IOT", "ROBOTICS", "EV", "CONTROL_SYSTEMS"},
        "IOT": {"EMBEDDED", "TELECOMMUNICATIONS", "CLOUD"},
        "TELECOMMUNICATIONS": {"IOT", "VLSI", "SIGNAL_PROCESSING"},
        "POWER_SYSTEMS": {"RENEWABLE_ENERGY", "EV", "CONTROL_SYSTEMS"},
        "RENEWABLE_ENERGY": {"POWER_SYSTEMS", "EV", "ENVIRONMENTAL"},
        "EV": {"AUTOMOTIVE", "POWER_SYSTEMS", "EMBEDDED", "RENEWABLE_ENERGY"},
        "CONTROL_SYSTEMS": {"ROBOTICS", "POWER_SYSTEMS", "EMBEDDED"},
        "AUTOMOTIVE": {"EV", "MECHANICAL", "CAD_CAM", "MANUFACTURING", "ROBOTICS"},
        "ROBOTICS": {"AUTOMOTIVE", "EMBEDDED", "CONTROL_SYSTEMS", "CAD_CAM"},
        "MANUFACTURING": {"CAD_CAM", "AUTOMOTIVE", "MATERIALS"},
        "CAD_CAM": {"MANUFACTURING", "AUTOMOTIVE", "AEROSPACE", "STRUCTURAL"},
        "AEROSPACE": {"AUTOMOTIVE", "CAD_CAM", "ROBOTICS"},
        "STRUCTURAL": {"CONSTRUCTION", "GEOTECHNICAL", "CAD_CAM"},
        "GEOTECHNICAL": {"STRUCTURAL", "CONSTRUCTION", "TRANSPORTATION"},
        "TRANSPORTATION": {"GEOTECHNICAL", "CONSTRUCTION", "CIVIL"},
        "ENVIRONMENTAL": {"RENEWABLE_ENERGY", "PROCESS_ENGINEERING", "CIVIL"},
        "CONSTRUCTION": {"STRUCTURAL", "GEOTECHNICAL", "TRANSPORTATION"},
        "PROCESS_ENGINEERING": {"PETROLEUM", "MATERIALS", "ENVIRONMENTAL"},
        "PETROLEUM": {"PROCESS_ENGINEERING", "MATERIALS"},
        "MATERIALS": {"PROCESS_ENGINEERING", "MANUFACTURING"},
        "BIOINFORMATICS": {"AI_ML", "BIOMEDICAL", "BIOPHARMA"},
        "BIOMEDICAL": {"BIOINFORMATICS", "BIOPHARMA", "EMBEDDED"},
        "BIOPHARMA": {"BIOMEDICAL", "BIOINFORMATICS", "FOOD_TECHNOLOGY"},
        "FOOD_TECHNOLOGY": {"BIOPHARMA", "PROCESS_ENGINEERING"}
    }

    # Sector Taxonomy Normalization
    SECTOR_MAPPING = [
        (r"\b(software|it services|it consulting|saas|app dev)\b", "SOFTWARE", "Software & IT Services"),
        (r"\b(semiconductor|semiconductors|vlsi|chip design|microelectronics)\b", "SEMICONDUCTOR", "Semiconductors & VLSI"),
        (r"\b(embedded|iot|hardware|electronics manufacturing)\b", "EMBEDDED", "Electronics & Embedded Hardware"),
        (r"\b(telecomm|telecommunication|networking|5g|telecom)\b", "TELECOMMUNICATIONS", "Telecommunications"),
        (r"\b(automotive|automobile|ev|electric vehicle|mobility)\b", "AUTOMOTIVE", "Automotive & EV Mobility"),
        (r"\b(aerospace|defence|aviation|drones|uav)\b", "AEROSPACE", "Aerospace & Defence"),
        (r"\b(power|electrical equipment|power grid|utilities)\b", "POWER_SYSTEMS", "Power & Electrical Utilities"),
        (r"\b(renewable energy|solar|wind|clean energy)\b", "RENEWABLE_ENERGY", "Renewable Energy"),
        (r"\b(construction|infrastructure|real estate|civil engineering)\b", "CONSTRUCTION", "Construction & Infrastructure"),
        (r"\b(chemical|petrochemical|oil & gas|refinery|polymers)\b", "CHEMICAL_PROCESSING", "Chemicals, Oil & Gas"),
        (r"\b(biotech|pharmaceutical|biopharma|healthcare|medical devices)\b", "BIOTECHNOLOGY", "Biotechnology & Healthcare"),
        (r"\b(food|agritech|food processing)\b", "FOOD_TECHNOLOGY", "Food & Agricultural Technology")
    ]

    @classmethod
    def normalize_specialization(cls, raw_spec: Optional[str]) -> Dict[str, Any]:
        if not raw_spec or not raw_spec.strip():
            return {"raw": raw_spec, "normalized": "UNKNOWN", "display_name": "Unspecified", "is_known": False}

        clean = raw_spec.strip().lower()
        for pattern, code, display in cls.SPECIALIZATION_MAPPING:
            if re.search(pattern, clean):
                return {"raw": raw_spec.strip(), "normalized": code, "display_name": display, "is_known": True}

        return {"raw": raw_spec.strip(), "normalized": "UNKNOWN", "display_name": raw_spec.strip(), "is_known": False}

    @classmethod
    def normalize_sector(cls, raw_sector: Optional[str]) -> Dict[str, Any]:
        if not raw_sector or not raw_sector.strip():
            return {"raw": raw_sector, "normalized": "UNKNOWN", "display_name": "Unspecified Sector", "is_known": False}

        clean = raw_sector.strip().lower()
        for pattern, code, display in cls.SECTOR_MAPPING:
            if re.search(pattern, clean):
                return {"raw": raw_sector.strip(), "normalized": code, "display_name": display, "is_known": True}

        return {"raw": raw_sector.strip(), "normalized": "UNKNOWN", "display_name": raw_sector.strip(), "is_known": False}

    @classmethod
    def evaluate_specialization_compatibility(
        cls,
        candidate_raw_spec: Optional[str],
        opportunity_raw_spec: Optional[str],
        opportunity_title: str = "",
        opportunity_description: str = ""
    ) -> Dict[str, Any]:
        cand = cls.normalize_specialization(candidate_raw_spec)
        opp = cls.normalize_specialization(opportunity_raw_spec or f"{opportunity_title} {opportunity_description}")

        if cand["normalized"] == "UNKNOWN" or opp["normalized"] == "UNKNOWN":
            return {
                "specialization_match_level": "UNKNOWN",
                "specialization_match_score": None,
                "candidate_specialization": cand["raw"] or "Unspecified",
                "opportunity_specialization": opp["raw"] or "Unspecified",
                "reason": "Insufficient verified specialization data."
            }

        if cand["normalized"] == opp["normalized"]:
            return {
                "specialization_match_level": "SPECIALIZATION_EXACT",
                "specialization_match_score": 1.0,
                "candidate_specialization": cand["raw"],
                "opportunity_specialization": opp["raw"],
                "reason": f"Candidate specialization '{cand['raw']}' exactly matches opportunity requirement '{opp['raw']}'."
            }

        related_set = cls.SPECIALIZATION_RELATEDNESS.get(cand["normalized"], set())
        if opp["normalized"] in related_set:
            return {
                "specialization_match_level": "SPECIALIZATION_RELATED",
                "specialization_match_score": 0.80,
                "candidate_specialization": cand["raw"],
                "opportunity_specialization": opp["raw"],
                "reason": f"Candidate specialization '{cand['raw']}' is academically related to opportunity requirement '{opp['raw']}'."
            }

        return {
            "specialization_match_level": "BROAD_DISCIPLINE_MATCH",
            "specialization_match_score": 0.50,
            "candidate_specialization": cand["raw"],
            "opportunity_specialization": opp["raw"],
            "reason": f"Candidate specialization '{cand['raw']}' differs from opportunity specialization '{opp['raw']}'."
        }

    @classmethod
    def evaluate_sector_compatibility(
        cls,
        candidate_target_sector: Optional[str],
        opportunity_sector: Optional[str]
    ) -> Dict[str, Any]:
        cand_sec = cls.normalize_sector(candidate_target_sector)
        opp_sec = cls.normalize_sector(opportunity_sector)

        if cand_sec["normalized"] == "UNKNOWN" or opp_sec["normalized"] == "UNKNOWN":
            return {
                "sector_match_level": "UNKNOWN",
                "sector_match_score": None,
                "candidate_sector_interest": cand_sec["raw"] or "Unspecified",
                "opportunity_sector": opp_sec["raw"] or "Unspecified",
                "reason": "Insufficient verified sector data."
            }

        if cand_sec["normalized"] == opp_sec["normalized"]:
            return {
                "sector_match_level": "SECTOR_EXACT",
                "sector_match_score": 0.75,
                "candidate_sector_interest": cand_sec["raw"],
                "opportunity_sector": opp_sec["raw"],
                "reason": f"Candidate target sector '{cand_sec['raw']}' matches opportunity sector '{opp_sec['raw']}'."
            }

        return {
            "sector_match_level": "SECTOR_RELATED",
            "sector_match_score": 0.60,
            "candidate_sector_interest": cand_sec["raw"],
            "opportunity_sector": opp_sec["raw"],
            "reason": f"Candidate target sector '{cand_sec['raw']}' differs from opportunity sector '{opp_sec['raw']}'."
        }

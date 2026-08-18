import json
import logging
from typing import Dict, Any, List, Optional
from app.services.academic_discipline import AcademicDisciplineService

logger = logging.getLogger(__name__)

class BranchCompatibilityEngine:
    """
    Deterministic Academic Branch Compatibility Engine (Task 27B Specification).
    Evaluates academic discipline compatibility between a candidate and an opportunity requirement.
    """

    # Discipline & Sub-Specialization Relationship Graph
    DISCIPLINE_RELATIONSHIPS = {
        # CSE & Sub-Specializations
        "COMPUTER_SCIENCE": {
            "AI_ML", "DATA_SCIENCE", "CYBERSECURITY", "WEB_DEVELOPMENT", "CLOUD_DEVOPS", "SOFTWARE_ENGINEERING", "INFORMATION_TECHNOLOGY"
        },
        "AI_ML": {"COMPUTER_SCIENCE", "DATA_SCIENCE", "SOFTWARE_ENGINEERING"},
        "DATA_SCIENCE": {"COMPUTER_SCIENCE", "AI_ML", "CLOUD_DEVOPS", "INFORMATION_TECHNOLOGY"},
        "CYBERSECURITY": {"COMPUTER_SCIENCE", "CLOUD_DEVOPS", "SOFTWARE_ENGINEERING", "INFORMATION_TECHNOLOGY"},
        "WEB_DEVELOPMENT": {"COMPUTER_SCIENCE", "SOFTWARE_ENGINEERING", "CLOUD_DEVOPS"},
        "CLOUD_DEVOPS": {"COMPUTER_SCIENCE", "CYBERSECURITY", "WEB_DEVELOPMENT", "SOFTWARE_ENGINEERING"},
        "SOFTWARE_ENGINEERING": {"COMPUTER_SCIENCE", "WEB_DEVELOPMENT", "AI_ML", "CYBERSECURITY"},
        "INFORMATION_TECHNOLOGY": {"COMPUTER_SCIENCE", "SOFTWARE_ENGINEERING", "CYBERSECURITY", "DATA_SCIENCE", "WEB_DEVELOPMENT"},

        # ECE & Sub-Specializations
        "ELECTRONICS_COMMUNICATION": {
            "VLSI", "EMBEDDED_SYSTEMS", "IOT", "TELECOMMUNICATIONS", "SIGNAL_PROCESSING", "ELECTRONICS"
        },
        "VLSI": {"ELECTRONICS_COMMUNICATION", "EMBEDDED_SYSTEMS", "ELECTRONICS"},
        "EMBEDDED_SYSTEMS": {"ELECTRONICS_COMMUNICATION", "VLSI", "IOT", "CONTROL_SYSTEMS", "COMPUTER_SCIENCE"},
        "IOT": {"ELECTRONICS_COMMUNICATION", "EMBEDDED_SYSTEMS", "TELECOMMUNICATIONS", "COMPUTER_SCIENCE"},
        "TELECOMMUNICATIONS": {"ELECTRONICS_COMMUNICATION", "SIGNAL_PROCESSING", "IOT"},
        "SIGNAL_PROCESSING": {"ELECTRONICS_COMMUNICATION", "TELECOMMUNICATIONS", "CONTROL_SYSTEMS"},
        "ELECTRONICS": {"ELECTRONICS_COMMUNICATION", "VLSI", "EMBEDDED_SYSTEMS", "ELECTRICAL_ELECTRONICS"},

        # Mechanical & Sub-Specializations
        "MECHANICAL": {
            "AUTOMOTIVE", "ROBOTICS", "MANUFACTURING", "CAD_CAM", "AEROSPACE", "MECHATRONICS"
        },
        "AUTOMOTIVE": {"MECHANICAL", "EV_SYSTEMS", "MANUFACTURING", "ROBOTICS", "CAD_CAM"},
        "ROBOTICS": {"MECHANICAL", "AUTOMOTIVE", "EMBEDDED_SYSTEMS", "CONTROL_SYSTEMS", "MANUFACTURING"},
        "MANUFACTURING": {"MECHANICAL", "CAD_CAM", "AUTOMOTIVE", "ROBOTICS"},
        "CAD_CAM": {"MECHANICAL", "MANUFACTURING", "AUTOMOTIVE", "AEROSPACE"},
        "AEROSPACE": {"MECHANICAL", "AUTOMOTIVE", "CAD_CAM", "MANUFACTURING"},
        "MECHATRONICS": {"MECHANICAL", "ROBOTICS", "AUTOMOTIVE", "EMBEDDED_SYSTEMS"},

        # Civil & Sub-Specializations
        "CIVIL": {
            "STRUCTURAL", "GEOTECHNICAL", "TRANSPORTATION", "ENVIRONMENTAL", "CONSTRUCTION"
        },
        "STRUCTURAL": {"CIVIL", "CONSTRUCTION", "GEOTECHNICAL"},
        "GEOTECHNICAL": {"CIVIL", "STRUCTURAL", "TRANSPORTATION"},
        "TRANSPORTATION": {"CIVIL", "GEOTECHNICAL", "CONSTRUCTION"},
        "ENVIRONMENTAL": {"CIVIL", "CHEMICAL"},
        "CONSTRUCTION": {"CIVIL", "STRUCTURAL", "TRANSPORTATION"},

        # EEE & Sub-Specializations
        "ELECTRICAL_ELECTRONICS": {
            "POWER_SYSTEMS", "ELECTRICAL_MACHINES", "RENEWABLE_ENERGY", "CONTROL_SYSTEMS", "EV_SYSTEMS", "ELECTRICAL", "ELECTRONICS"
        },
        "POWER_SYSTEMS": {"ELECTRICAL_ELECTRONICS", "ELECTRICAL_MACHINES", "RENEWABLE_ENERGY", "CONTROL_SYSTEMS"},
        "ELECTRICAL_MACHINES": {"ELECTRICAL_ELECTRONICS", "POWER_SYSTEMS", "EV_SYSTEMS", "CONTROL_SYSTEMS"},
        "RENEWABLE_ENERGY": {"ELECTRICAL_ELECTRONICS", "POWER_SYSTEMS", "EV_SYSTEMS", "ENVIRONMENTAL"},
        "CONTROL_SYSTEMS": {"ELECTRICAL_ELECTRONICS", "POWER_SYSTEMS", "ROBOTICS", "SIGNAL_PROCESSING"},
        "EV_SYSTEMS": {"ELECTRICAL_ELECTRONICS", "AUTOMOTIVE", "RENEWABLE_ENERGY", "POWER_SYSTEMS", "ELECTRICAL_MACHINES"},
        "ELECTRICAL": {"ELECTRICAL_ELECTRONICS", "POWER_SYSTEMS", "ELECTRICAL_MACHINES"},

        # Other Engineering
        "CHEMICAL": {"ENVIRONMENTAL", "MATERIALS_METALLURGY"},
        "MATERIALS_METALLURGY": {"CHEMICAL", "MECHANICAL"},
        "BIOTECHNOLOGY": {"FOOD_TECHNOLOGY"},
        "FOOD_TECHNOLOGY": {"BIOTECHNOLOGY"}
    }

    ENGINEERING_DISCIPLINES = {
        "COMPUTER_SCIENCE", "AI_ML", "DATA_SCIENCE", "CYBERSECURITY", "WEB_DEVELOPMENT", "CLOUD_DEVOPS", "SOFTWARE_ENGINEERING", "INFORMATION_TECHNOLOGY",
        "ELECTRONICS_COMMUNICATION", "VLSI", "EMBEDDED_SYSTEMS", "IOT", "TELECOMMUNICATIONS", "SIGNAL_PROCESSING", "ELECTRONICS",
        "MECHANICAL", "AUTOMOTIVE", "ROBOTICS", "MANUFACTURING", "CAD_CAM", "AEROSPACE", "MECHATRONICS",
        "CIVIL", "STRUCTURAL", "GEOTECHNICAL", "TRANSPORTATION", "ENVIRONMENTAL", "CONSTRUCTION",
        "ELECTRICAL_ELECTRONICS", "POWER_SYSTEMS", "ELECTRICAL_MACHINES", "RENEWABLE_ENERGY", "CONTROL_SYSTEMS", "EV_SYSTEMS", "ELECTRICAL",
        "CHEMICAL", "MATERIALS_METALLURGY", "BIOTECHNOLOGY", "MINING", "TEXTILE", "FOOD_TECHNOLOGY", "AGRICULTURAL", "MARINE_NAVAL"
    }

    TECHNOLOGY_DISCIPLINES = {
        "COMPUTER_SCIENCE", "AI_ML", "DATA_SCIENCE", "CYBERSECURITY", "WEB_DEVELOPMENT", "CLOUD_DEVOPS", "SOFTWARE_ENGINEERING", "INFORMATION_TECHNOLOGY",
        "VLSI", "EMBEDDED_SYSTEMS", "IOT", "TELECOMMUNICATIONS", "SIGNAL_PROCESSING", "EV_SYSTEMS", "FOOD_TECHNOLOGY"
    }

    @classmethod
    def evaluate_compatibility(
        cls,
        candidate_raw_branch: Optional[str],
        required_disciplines: Optional[List[str]] = None,
        accepted_disciplines: Optional[List[str]] = None,
        discipline_scope: str = "UNKNOWN",
        original_requirement_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates candidate discipline compatibility against opportunity requirements.
        Returns a structured decision payload with machine-readable reasons.
        """
        cand_norm = AcademicDisciplineService.normalize_discipline(candidate_raw_branch)
        cand_code = cand_norm["normalized"]

        req_list = required_disciplines or []
        acc_list = accepted_disciplines or []
        all_allowed_raw = list(dict.fromkeys(req_list + acc_list))
        all_allowed = []
        for item in all_allowed_raw:
            n_code = AcademicDisciplineService.normalize_discipline(item)["normalized"]
            if n_code != "UNKNOWN":
                all_allowed.append(n_code)

        # 1. Unknown Candidate Discipline Handling
        if cand_code == "UNKNOWN":
            return {
                "compatibility_level": "UNKNOWN",
                "compatibility_score": None,
                "candidate_discipline": cand_norm["raw"] or "Unspecified",
                "matched_opportunity_discipline": None,
                "matched_related_discipline": None,
                "discipline_scope": discipline_scope,
                "reason": "Insufficient candidate academic discipline information.",
                "source_evidence": original_requirement_text or "No discipline requirement provided.",
                "confidence": 0.5
            }

        # 2. Scope-based Broad Matching (ALL_ENGINEERING / ALL_TECHNOLOGY / CROSS_DISCIPLINARY)
        if discipline_scope == "CROSS_DISCIPLINARY":
            return {
                "compatibility_level": "CROSS_DISCIPLINARY_MATCH",
                "compatibility_score": 0.65,
                "candidate_discipline": cand_norm["raw"],
                "matched_opportunity_discipline": "CROSS_DISCIPLINARY",
                "matched_related_discipline": None,
                "discipline_scope": discipline_scope,
                "reason": f"Candidate discipline '{cand_norm['raw']}' falls within cross-disciplinary opportunity scope.",
                "source_evidence": original_requirement_text or "Open to all disciplines.",
                "confidence": 0.90
            }

        if discipline_scope == "ALL_ENGINEERING":
            if cand_code in cls.ENGINEERING_DISCIPLINES:
                return {
                    "compatibility_level": "BROAD_SCOPE_MATCH",
                    "compatibility_score": 0.60,
                    "candidate_discipline": cand_norm["raw"],
                    "matched_opportunity_discipline": "ALL_ENGINEERING",
                    "matched_related_discipline": None,
                    "discipline_scope": discipline_scope,
                    "reason": f"Candidate engineering discipline '{cand_norm['raw']}' satisfies All Engineering scope.",
                    "source_evidence": original_requirement_text or "All Engineering disciplines accepted.",
                    "confidence": 0.95
                }
            else:
                return {
                    "compatibility_level": "INCOMPATIBLE",
                    "compatibility_score": 0.0,
                    "candidate_discipline": cand_norm["raw"],
                    "matched_opportunity_discipline": None,
                    "matched_related_discipline": None,
                    "discipline_scope": discipline_scope,
                    "reason": f"Candidate non-engineering discipline '{cand_norm['raw']}' does not satisfy All Engineering scope.",
                    "source_evidence": original_requirement_text or "Engineering discipline required.",
                    "confidence": 1.0
                }

        if discipline_scope == "ALL_TECHNOLOGY":
            if cand_code in cls.TECHNOLOGY_DISCIPLINES:
                return {
                    "compatibility_level": "BROAD_SCOPE_MATCH",
                    "compatibility_score": 0.60,
                    "candidate_discipline": cand_norm["raw"],
                    "matched_opportunity_discipline": "ALL_TECHNOLOGY",
                    "matched_related_discipline": None,
                    "discipline_scope": discipline_scope,
                    "reason": f"Candidate technology discipline '{cand_norm['raw']}' satisfies All Technology scope.",
                    "source_evidence": original_requirement_text or "All Technology disciplines accepted.",
                    "confidence": 0.95
                }
            else:
                return {
                    "compatibility_level": "INCOMPATIBLE",
                    "compatibility_score": 0.0,
                    "candidate_discipline": cand_norm["raw"],
                    "matched_opportunity_discipline": None,
                    "matched_related_discipline": None,
                    "discipline_scope": discipline_scope,
                    "reason": f"Candidate discipline '{cand_norm['raw']}' is outside All Technology scope.",
                    "source_evidence": original_requirement_text or "Technology discipline required.",
                    "confidence": 1.0
                }

        # 3. Specific or Multi-Discipline Requirement List Matching
        if not all_allowed:
            return {
                "compatibility_level": "UNKNOWN",
                "compatibility_score": None,
                "candidate_discipline": cand_norm["raw"],
                "matched_opportunity_discipline": None,
                "matched_related_discipline": None,
                "discipline_scope": discipline_scope,
                "reason": "Opportunity provides no specific discipline requirements.",
                "source_evidence": original_requirement_text or "No discipline specified by opportunity source.",
                "confidence": 0.5
            }

        # Direct Exact Match (STRONG_MATCH)
        if cand_code in all_allowed:
            return {
                "compatibility_level": "STRONG_MATCH",
                "compatibility_score": 1.0,
                "candidate_discipline": cand_norm["raw"],
                "matched_opportunity_discipline": cand_code,
                "matched_related_discipline": None,
                "discipline_scope": discipline_scope,
                "reason": f"Candidate discipline '{cand_norm['raw']}' directly matches required discipline '{cand_code}'.",
                "source_evidence": original_requirement_text or f"Requires {cand_code}",
                "confidence": 1.0
            }

        # Related Discipline Match (RELATED_MATCH)
        related_set = cls.DISCIPLINE_RELATIONSHIPS.get(cand_code, set())
        for req_code in all_allowed:
            if req_code in related_set:
                return {
                    "compatibility_level": "RELATED_MATCH",
                    "compatibility_score": 0.75,
                    "candidate_discipline": cand_norm["raw"],
                    "matched_opportunity_discipline": req_code,
                    "matched_related_discipline": cand_code,
                    "discipline_scope": discipline_scope,
                    "reason": f"Candidate discipline '{cand_code}' is academically related to required discipline '{req_code}'.",
                    "source_evidence": original_requirement_text or f"Requires {req_code}",
                    "confidence": 0.90
                }

        # Explicit Incompatibility Fallback
        return {
            "compatibility_level": "INCOMPATIBLE",
            "compatibility_score": 0.0,
            "candidate_discipline": cand_norm["raw"],
            "matched_opportunity_discipline": None,
            "matched_related_discipline": None,
            "discipline_scope": discipline_scope,
            "reason": f"Candidate discipline '{cand_norm['raw']}' is incompatible with required disciplines ({', '.join(all_allowed)}).",
            "source_evidence": original_requirement_text or f"Requires {', '.join(all_allowed)}",
            "confidence": 1.0
        }
